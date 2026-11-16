"""Read borrowed Qt event data before native or re-entrant handlers run."""

import pytest
from PyQt5.QtCore import QEvent, QPointF, Qt, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMainWindow

from ui.main_window import MainWindow


class BorrowedStateEvent:
    """Model native event data at the callback boundary.

    PyQt does not permit constructing QWindowStateChangeEvent directly. The
    patched base handler below consumes this double without passing it to C++.
    The existing maximize/restore regression separately exercises real events.
    """

    def __init__(self, previous):
        self.previous = previous
        self.expired = False

    def type(self):
        assert not self.expired, "event type read after native dispatch"
        return QEvent.WindowStateChange

    def oldState(self):
        assert not self.expired, "old state read after native/re-entrant dispatch"
        return self.previous


@pytest.mark.parametrize("expiry", ["base", "logging"])
@pytest.mark.parametrize("previous", [Qt.WindowMaximized, Qt.WindowMinimized, Qt.WindowFullScreen])
def test_restore_snapshots_event_before_native_or_logging_dispatch(
    qtbot, monkeypatch, tmp_path, expiry, previous
):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    window = MainWindow(db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    event = BorrowedStateEvent(previous)
    delegated, logged, queued, deadlines = [], [], [], []
    native_change = QMainWindow.changeEvent

    def delegate(self, received):
        if received is event:
            delegated.append(received)
            if expiry == "base":
                received.expired = True
        else:
            native_change(self, received)

    def log(reason):
        logged.append(reason)
        if expiry == "logging":
            event.expired = True

    monkeypatch.setattr(QMainWindow, "changeEvent", delegate)
    monkeypatch.setattr(window, "_log_window_geometry", log)
    monkeypatch.setattr(window, "_queue_normal_geometry", lambda: queued.append(True))
    monkeypatch.setattr(QTimer, "singleShot", lambda delay, callback: deadlines.append((delay, callback)))

    window.changeEvent(event)

    assert delegated == [event]
    assert logged == ["state-change"]
    assert queued == [True]
    assert deadlines == [(80, window._schedule_screen_fit)]
    assert not window.isMaximized()
    assert not window.isFullScreen()


def test_entering_maximized_state_stops_geometry_recording_without_restore(
    qtbot, monkeypatch, tmp_path
):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    window = MainWindow(db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    event = BorrowedStateEvent(Qt.WindowNoState)
    delegated, deadlines = [], []
    native_change = QMainWindow.changeEvent

    def delegate(self, received):
        if received is event:
            delegated.append(received)
            received.expired = True
        else:
            native_change(self, received)

    monkeypatch.setattr(QMainWindow, "changeEvent", delegate)
    monkeypatch.setattr(window, "windowState", lambda: Qt.WindowMaximized)
    monkeypatch.setattr(window, "_log_window_geometry", lambda reason: None)
    monkeypatch.setattr(QTimer, "singleShot", lambda delay, callback: deadlines.append((delay, callback)))
    window._normal_geometry_timer.start()

    window.changeEvent(event)

    assert delegated == [event]
    assert not window._normal_geometry_timer.isActive()
    assert deadlines == []


def test_mouse_event_is_forwarded_without_window_state_handling(qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr(MainWindow, "_load_builtin_model", lambda self: None)
    window = MainWindow(db_path=tmp_path / "history.db", builtin_model_path=tmp_path / "missing.pth")
    qtbot.addWidget(window)
    event = QMouseEvent(QEvent.MouseMove, QPointF(4, 5), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
    delegated, logged = [], []
    native_change = QMainWindow.changeEvent

    def delegate(self, received):
        if received is event:
            delegated.append(received)
        else:
            native_change(self, received)

    monkeypatch.setattr(QMainWindow, "changeEvent", delegate)
    monkeypatch.setattr(window, "_log_window_geometry", logged.append)

    window.changeEvent(event)

    assert delegated == [event]
    assert logged == []
