"""Packaging resource checks; these do not claim a Windows build was executed."""
import importlib.util
from pathlib import Path
import sys

import pytest

from core.model_loader import _upernet_config_source, ModelValidationError


def test_source_and_frozen_upernet_config_locations(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    assert _upernet_config_source() == "openmmlab/upernet-swin-base"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    with pytest.raises(ModelValidationError, match="packaged UPerNet configuration is missing"):
        _upernet_config_source()
    folder = tmp_path / "models" / "upernet-config"
    folder.mkdir(parents=True)
    # Location fixture only. No model is constructed or evaluated.
    (folder / "config.json").write_text("{}", encoding="utf-8")
    assert _upernet_config_source() == str(folder)


def test_release_audit_reports_all_missing_inputs_without_creating_models(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[1] / "scripts" / "build_windows.py"
    spec = importlib.util.spec_from_file_location("build_windows_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def unavailable(*args, **kwargs):
        assert kwargs["local_files_only"] is True
        raise OSError("No cache for this fixture")

    monkeypatch.setattr("huggingface_hub.hf_hub_download", unavailable)
    missing, config = module.audit_inputs(tmp_path)
    assert "models/crc_dn21_seed42_best.pth" in missing
    assert "models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth" in missing
    assert "assets/fonts/NotoSansSC-Regular.ttf" in missing
    assert "models/dn21_folder_classification/train_crc_dn21 (1).py" in missing
    assert any("upernet-swin-base/config.json" in entry for entry in missing)
    assert config is None
    assert list(tmp_path.iterdir()) == []
