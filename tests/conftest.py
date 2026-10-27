"""Keep application preferences out of the user's native settings store."""
import pytest
from PyQt5.QtCore import QSettings


@pytest.fixture(autouse=True)
def isolated_application_settings(tmp_path, monkeypatch):
    """Each test gets fresh defaults, also on Windows (whose default is Registry)."""
    monkeypatch.setenv("APPDATA", str(tmp_path / "application-data"))
    # The organization/application overload explicitly uses NativeFormat;
    # setDefaultFormat alone only affects the no-argument constructor.
    original_init = QSettings.__init__

    def sandboxed_init(self, *args, **kwargs):
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], str):
            args = (QSettings.IniFormat, QSettings.UserScope, *args)
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(QSettings, "__init__", sandboxed_init)
    original_format = QSettings.defaultFormat()
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path / "user-settings"))
    QSettings.setPath(QSettings.IniFormat, QSettings.SystemScope, str(tmp_path / "system-settings"))
    QSettings.setDefaultFormat(QSettings.IniFormat)
    try:
        yield
    finally:
        QSettings.setDefaultFormat(original_format)
