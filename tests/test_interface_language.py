"""Verify saved UI language choices and the independent bilingual help."""

import csv
from string import Formatter

import pytest
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QDialogButtonBox

from ui.inference_panel import InferencePanel
from ui.input_help import InputHelpDialog
from ui.language import LANGUAGES, LANGUAGE_KEY, apply_interface_language, interface_language
from ui.settings_dialog import SettingsDialog
from utils.paths import resource_path


@pytest.mark.parametrize(("code", "settings_title", "run_title", "cancel"), [
    ("en", "Settings", "Run Inference", "Cancel"),
    ("zh", "设置", "运行推理", "取消"),
    ("es", "Ajustes", "Ejecutar inferencia", "Cancelar"),
    ("hi", "सेटिंग्स", "अनुमान चलाएँ", "रद्द करें"),
    ("ar", "الإعدادات", "تشغيل الاستدلال", "إلغاء"),
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
        assert qapp.layoutDirection() == (Qt.RightToLeft if code == "ar" else Qt.LeftToRight)
        help_dialog = InputHelpDialog("scale", panel)
        qtbot.addWidget(help_dialog)
        help_dialog.language.setCurrentIndex(help_dialog.language.findData("zh"))
        assert "边缘处理" in help_dialog.browser.toPlainText()
        help_dialog.language.setCurrentIndex(help_dialog.language.findData("en"))
        assert "Edge handling" in help_dialog.browser.toPlainText()
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel, panel)
        assert buttons.button(QDialogButtonBox.Cancel).text() == cancel
    finally:
        settings.setValue(LANGUAGE_KEY, "en")
        apply_interface_language(qapp, settings)


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
