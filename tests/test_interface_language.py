"""Verify saved UI languages, translated explanations and independent help."""

import csv
from string import Formatter

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialogButtonBox, QLabel

from ui.inference_panel import InferencePanel
from ui.input_help import InputHelpDialog, scale_readiness
from ui.language import LANGUAGES, LANGUAGE_KEY, apply_interface_language, interface_language
from ui.settings_dialog import SettingsDialog
from utils.paths import resource_path


@pytest.mark.parametrize(("code", "settings_title", "run_title", "cancel"), [
    ("en", "Settings", "Run Inference", "Cancel"),
    ("zh", "设置", "运行推理", "取消"),
    ("ja", "設定", "推論を実行", "キャンセル"),
])
def test_saved_language_applies_when_opening_new_widgets(qapp, qtbot, tmp_path, code, settings_title, run_title, cancel):
    path = str(tmp_path / "test.ini")
    settings = QSettings(path, QSettings.IniFormat)
    dialog = SettingsDialog(settings)
    qtbot.addWidget(dialog)
    assert [dialog.language_combo.itemData(i) for i in range(dialog.language_combo.count())] == [key for key, _ in LANGUAGES]
    dialog.language_combo.setCurrentIndex(dialog.language_combo.findData(code))
    restarted_settings = QSettings(path, QSettings.IniFormat)
    assert interface_language(restarted_settings) == code
    assert dialog.windowTitle() == "Settings"
    apply_interface_language(qapp, restarted_settings)
    try:
        restarted = SettingsDialog(restarted_settings)
        qtbot.addWidget(restarted)
        assert restarted.windowTitle() == settings_title
        assert restarted.language_combo.currentData() == code
        panel = InferencePanel()
        qtbot.addWidget(panel)
        assert panel.run_button.text() == run_title
        assert restarted.language_combo.count() == 3
        if code in ("zh", "ja"):
            notes = [label.text() for label in restarted.findChildren(QLabel)]
            assert any(("分享时建议选用标准画质" if code == "zh" else "共有時は標準を推奨します") in text for text in notes)
            assert ("快速开始" if code == "zh" else "はじめに") in restarted.guide_view.browser.toPlainText()
        help_dialog = InputHelpDialog("scale", panel, readiness=scale_readiness(None, None, has_image=False))
        qtbot.addWidget(help_dialog)
        assert help_dialog.language.currentData() == code
        help_dialog.language.setCurrentIndex(help_dialog.language.findData("zh"))
        assert "边缘处理" in help_dialog.browser.toPlainText()
        assert "请先上传图像" in help_dialog.browser.toPlainText()
        help_dialog.language.setCurrentIndex(help_dialog.language.findData("en"))
        assert "Edge handling" in help_dialog.browser.toPlainText()
        help_dialog.language.setCurrentIndex(help_dialog.language.findData("ja"))
        assert "画像端の処理" in help_dialog.browser.toPlainText()
        assert "先に画像を読み込んでください" in help_dialog.browser.toPlainText()
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel, panel)
        assert buttons.button(QDialogButtonBox.Cancel).text() == cancel
    finally:
        settings.setValue(LANGUAGE_KEY, "en")
        apply_interface_language(qapp, settings)


@pytest.mark.parametrize("code", ["es", "hi", "ar"])
def test_removed_languages_fall_back_to_english(tmp_path, code):
    settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)
    settings.setValue(LANGUAGE_KEY, code)
    assert interface_language(settings) == "en"


def test_catalog_translations_keep_template_fields():
    def fields(text):
        return {(name, spec) for _, name, spec, _ in Formatter().parse(text) if name is not None}

    with resource_path("assets/interface_languages.tsv").open(encoding="utf-8", newline="") as catalog:
        seen = set()
        for entry in csv.DictReader(catalog, delimiter="\t"):
            assert entry["en"] not in seen
            seen.add(entry["en"])
            for code, _ in LANGUAGES:
                assert entry[code]
                assert fields(entry[code]) == fields(entry["en"])
