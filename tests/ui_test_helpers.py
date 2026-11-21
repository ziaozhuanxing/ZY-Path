"""Wait for explicitly asynchronous model selection in UI flow tests."""
def wait_for_model_idle(qtbot, panel_or_window):
    window = panel_or_window.window()
    qtbot.waitUntil(lambda: not getattr(window, "_is_model_validation_active", lambda: False)(), timeout=15000)


def wait_for_history_idle(qtbot, window):
    qtbot.waitUntil(lambda: getattr(window, '_history_worker', None) is None
                   and getattr(window, '_pending_history_load', None) is None, timeout=15000)


def wait_for_export_idle(qtbot, window):
    qtbot.waitUntil(lambda: getattr(window, '_png_export_worker', None) is None
                   and getattr(window, '_pdf_export_worker', None) is None, timeout=20000)
