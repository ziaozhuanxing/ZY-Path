"""Stage a PNG and its metadata together, restoring previous files on failure."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
from uuid import uuid4

from PIL import Image, PngImagePlugin
from core.model_profile import file_sha256
from data.export_manager import ExportCancelled, ExportError

_BUNDLE_LOCK = threading.Lock()


def export_png_bundle(image, destination, metadata, *, progress=None):
    """Commit a matching pair. Two filesystem replacements are not crash-atomic.

    Both complete outputs and backups exist before replacement starts. Ordinary
    commit errors restore originals. A journal and backups are kept if rollback
    itself fails or the process is interrupted during the commit.
    """
    destination = Path(destination)
    sidecar = destination.with_suffix(destination.suffix + '.json')
    notify = progress or (lambda *_: None)
    stage = None
    keep_recovery = False
    with _BUNDLE_LOCK:
        try:
            notify('Preparing PNG and metadata', 30)
            destination.parent.mkdir(parents=True, exist_ok=True)
            for path in (destination, sidecar):
                if path.exists() and not path.is_file():
                    raise ExportError(f'Export destination is not a regular file: {path.name}')
            stage = Path(tempfile.mkdtemp(prefix='.zy-path-png-', dir=destination.parent))
            export_id = uuid4().hex
            staged_png, staged_json = stage / 'new.png', stage / 'new.json'
            png_info = PngImagePlugin.PngInfo()
            png_info.add_text('zypath.export_id', export_id)
            image.save(staged_png, format='PNG', pnginfo=png_info)
            output_metadata = deepcopy(metadata)
            output_metadata['export_bundle'] = {
                'schema': 'zypath.png-export.v1', 'export_id': export_id,
                'image_filename': destination.name, 'image_sha256': file_sha256(staged_png),
            }
            staged_json.write_text(json.dumps(output_metadata, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')
            targets = (destination, sidecar)
            backups = {}
            for index, path in enumerate(targets):
                if path.exists():
                    backup = stage / f'previous-{index}'
                    shutil.copy2(path, backup)
                    backups[path] = backup
            journal = {'schema': 'zypath.png-transaction.v1', 'export_id': export_id,
                       'targets': [str(p.resolve()) for p in targets],
                       'backups': {str(p.resolve()): b.name for p, b in backups.items()}}
            (stage / 'transaction.json').write_text(json.dumps(journal, indent=2), encoding='utf-8')
            notify('Checking complete export bundle', 85)
            verify_png_bundle(staged_png, staged_json, expected_filename=destination.name)
            for path in targets:
                if path in backups:
                    if not path.is_file() or file_sha256(path) != file_sha256(backups[path]):
                        raise ExportError('An export destination changed while preparing the bundle. Existing files were kept.')
                elif path.exists():
                    raise ExportError('An export destination appeared while preparing the bundle. Existing files were kept.')
            notify('Saving complete PNG bundle', 98)
            # No cancellation between replacements: commit/rollback is one unit.
            # Keep the journal if an unexpected interruption bypasses the
            # ordinary filesystem-error rollback (for example KeyboardInterrupt).
            keep_recovery = True
            replaced = []
            try:
                for prepared, target in zip((staged_png, staged_json), targets):
                    os.replace(prepared, target)
                    replaced.append(target)
            except OSError as error:
                rollback_errors = []
                for target in reversed(replaced):
                    try:
                        if target in backups:
                            os.replace(backups[target], target)
                        else:
                            target.unlink(missing_ok=True)
                    except OSError as rollback_error:
                        rollback_errors.append(rollback_error)
                if rollback_errors:
                    raise ExportError(f'PNG bundle could not be restored automatically. Recovery copies and transaction.json were kept in: {stage}') from error
                keep_recovery = False
                raise ExportError('The PNG bundle could not be saved. Previous PNG and metadata files were restored.') from error
            keep_recovery = False
            return destination
        except (ExportError, ExportCancelled):
            raise
        except (OSError, ValueError, TypeError) as error:
            raise ExportError('The PNG bundle could not be saved. Previous files were kept.') from error
        finally:
            if stage is not None and not keep_recovery:
                shutil.rmtree(stage, ignore_errors=True)


def verify_png_bundle(image_path, metadata_path, *, expected_filename=None):
    metadata = json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    bundle = metadata.get('export_bundle') or {}
    if bundle.get('schema') != 'zypath.png-export.v1':
        raise ValueError('Missing PNG export identity.')
    with Image.open(image_path) as image:
        if image.info.get('zypath.export_id') != bundle.get('export_id'):
            raise ValueError('PNG and metadata belong to different exports.')
    if bundle.get('image_filename') != (expected_filename or Path(image_path).name):
        raise ValueError('PNG export filename does not match its metadata.')
    if bundle.get('image_sha256') != file_sha256(image_path):
        raise ValueError('PNG export checksum does not match its metadata.')
    return metadata
