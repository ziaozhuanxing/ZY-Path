"""Wait for explicitly asynchronous model selection in UI flow tests."""
def wait_for_model_idle(qtbot, panel_or_window):
    window = panel_or_window.window()
    qtbot.waitUntil(lambda: not getattr(window, "_is_model_validation_active", lambda: False)(), timeout=15000)
