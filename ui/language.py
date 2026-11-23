"""Persist the interface locale and translate source strings at display time."""

import csv
from functools import lru_cache

from PyQt5.QtCore import QCoreApplication, QTranslator

from utils.paths import resource_path


LANGUAGE_KEY = "appearance/language"
LANGUAGES = (
    ("en", "English"),
    ("zh", "简体中文"),
    ("ja", "日本語"),
)


def interface_language(settings):
    code = settings.value(LANGUAGE_KEY, "en", type=str)
    return code if code in dict(LANGUAGES) else "en"


def tr(source):
    return QCoreApplication.translate("ZYPath", source)


@lru_cache(maxsize=len(LANGUAGES))
def _messages(code):
    with resource_path("assets/interface_languages.tsv").open(encoding="utf-8", newline="") as catalog:
        return {row["en"]: row[code] for row in csv.DictReader(catalog, delimiter="\t")}


def translate_for(code, source):
    """Translate help text using its own selected language."""
    return source if code == "en" else _messages(code).get(source, source)


class InterfaceTranslator(QTranslator):
    def __init__(self, code, parent):
        super().__init__(parent)
        self.messages = _messages(code)

    def isEmpty(self):
        return not self.messages

    def translate(self, context, sourceText, disambiguation=None, n=-1):
        if context == "ZYPath":
            return self.messages.get(sourceText) or None
        if context in ("QPlatformTheme", "QDialogButtonBox", "QMessageBox"):
            # Qt uses ampersands to mark standard-button mnemonics.
            return self.messages.get(sourceText.replace("&", "")) or None
        return None


def apply_interface_language(app, settings):
    code = interface_language(settings)
    previous = getattr(app, "_zy_translator", None)
    if previous is not None:
        app.removeTranslator(previous)
        previous.deleteLater()
    app._zy_translator = None
    if code != "en":
        translator = InterfaceTranslator(code, app)
        app.installTranslator(translator)
        app._zy_translator = translator
    app.setProperty("zyLanguage", code)
