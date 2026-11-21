"""Paired export failures, rollback, identities and cancellation."""
import json
import os
from pathlib import Path
from PIL import Image
import pytest
from data.export_manager import ExportCancelled, ExportError
from data.png_bundle import export_png_bundle, verify_png_bundle


def previous_bundle(tmp_path):
    png = tmp_path / 'result.png'
    metadata = png.with_suffix('.png.json')
    Image.new('RGB', (9, 7), 'red').save(png)
    metadata.write_text('{"previous":"record"}')
    return png, metadata, (png.read_bytes(), metadata.read_bytes())


def test_success_exports_matching_identity_and_can_verify_after_copy(tmp_path):
    png = tmp_path / '组织结果.png'
    metadata = {'classification_analysis': {'presentation': {'opacity': .3}}}
    export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, metadata)
    saved = verify_png_bundle(png, png.with_suffix('.png.json'))
    assert saved['classification_analysis'] == metadata['classification_analysis']
    assert 'export_bundle' not in metadata
    assert not list(tmp_path.glob('.zy-path-png-*'))
    with Image.open(png) as image:
        assert image.getpixel((0, 0)) == (0, 0, 255)


def test_sidecar_staging_failure_never_replaces_either_previous_file(tmp_path, monkeypatch):
    png, sidecar, old = previous_bundle(tmp_path)
    write = Path.write_text
    def fail_json(path, *args, **kwargs):
        if path.name == 'new.json':
            raise OSError('Disk write failed')
        return write(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'write_text', fail_json)
    with pytest.raises(ExportError):
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, {})
    assert (png.read_bytes(), sidecar.read_bytes()) == old
    assert not list(tmp_path.glob('.zy-path-png-*'))


@pytest.mark.parametrize('existing', [False, True])
def test_second_replace_failure_restores_pair_or_removes_only_new_output(tmp_path, monkeypatch, existing):
    if existing:
        png, sidecar, old = previous_bundle(tmp_path)
    else:
        png = tmp_path / 'result.png'
        sidecar = png.with_suffix('.png.json')
    replace = os.replace
    def fail_second(source, destination):
        if Path(source).name == 'new.json':
            raise PermissionError('Cannot replace JSON')
        return replace(source, destination)
    monkeypatch.setattr('data.png_bundle.os.replace', fail_second)
    with pytest.raises(ExportError, match='restored'):
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, {})
    if existing:
        assert (png.read_bytes(), sidecar.read_bytes()) == old
    else:
        assert not png.exists() and not sidecar.exists()
    assert not list(tmp_path.glob('.zy-path-png-*'))


def test_rollback_failure_keeps_recovery_copy_and_reports_its_location(tmp_path, monkeypatch):
    png, sidecar, old = previous_bundle(tmp_path)
    replace = os.replace
    def fail_second_and_rollback(source, destination):
        if Path(source).name in ('new.json', 'previous-0'):
            raise PermissionError('File busy')
        return replace(source, destination)
    monkeypatch.setattr('data.png_bundle.os.replace', fail_second_and_rollback)
    with pytest.raises(ExportError, match='Recovery copies') as failure:
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, {})
    recovery, = tmp_path.glob('.zy-path-png-*')
    assert str(recovery) in str(failure.value)
    assert (recovery / 'previous-0').read_bytes() == old[0]
    assert sidecar.read_bytes() == old[1]
    assert (recovery / 'transaction.json').is_file()


@pytest.mark.parametrize('percent', [30, 85, 98])
def test_cancel_before_commit_keeps_both_previous_files(tmp_path, percent):
    png, sidecar, old = previous_bundle(tmp_path)
    def cancel(_message, done):
        if done == percent:
            raise ExportCancelled('Cancelled')
    with pytest.raises(ExportCancelled):
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, {}, progress=cancel)
    assert (png.read_bytes(), sidecar.read_bytes()) == old
    assert not list(tmp_path.glob('.zy-path-png-*'))


def test_wrong_export_sidecar_is_detected(tmp_path):
    png, other = tmp_path / 'a.png', tmp_path / 'b.png'
    for path in (png, other):
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), path, {})
    png.with_suffix('.png.json').write_bytes(other.with_suffix('.png.json').read_bytes())
    with pytest.raises(ValueError, match='different exports'):
        verify_png_bundle(png, png.with_suffix('.png.json'))


def test_interruption_during_commit_keeps_recovery_journal_and_old_files(tmp_path, monkeypatch):
    png, sidecar, old = previous_bundle(tmp_path)
    replace = os.replace

    def interrupt_second(source, destination):
        if Path(source).name == 'new.json':
            raise KeyboardInterrupt
        return replace(source, destination)

    monkeypatch.setattr('data.png_bundle.os.replace', interrupt_second)
    with pytest.raises(KeyboardInterrupt):
        export_png_bundle(Image.new('RGB', (12, 8), 'blue'), png, {})
    recovery, = tmp_path.glob('.zy-path-png-*')
    assert (recovery / 'previous-0').read_bytes() == old[0]
    assert (recovery / 'previous-1').read_bytes() == old[1]
    assert (recovery / 'transaction.json').is_file()
    assert sidecar.read_bytes() == old[1]
    with pytest.raises(ValueError):
        verify_png_bundle(png, sidecar)


def test_cancel_inside_hash_is_not_reported_as_corrupt_artifact(tmp_path):
    from data.artifact_integrity import artifact_manifest, verify_saved_artifacts
    from core.image_source import image_checksum
    path = tmp_path / 'synthetic.bin'
    path.write_bytes(b'x' * (3 * 1024 * 1024))
    analysis = {'artifact_manifest': artifact_manifest({'result': path})}
    calls = []
    def cancel_during_read():
        calls.append(1)
        if len(calls) >= 2:
            raise InterruptedError('Cancelled')
    with pytest.raises(InterruptedError):
        verify_saved_artifacts(analysis, check_cancelled=cancel_during_read)
    calls.clear()
    with pytest.raises(InterruptedError):
        image_checksum(path, check_cancelled=cancel_during_read)
