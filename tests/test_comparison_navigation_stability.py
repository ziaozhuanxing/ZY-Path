"""Pointer and splitter regressions using source-coordinate Qt image views."""

import pytest
from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPixmap, QWheelEvent
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QApplication

from ui.image_comparison import ImageComparison
from ui.zoomable_image_view import ZoomableImageView


def make_comparison(qtbot, linked=True):
    comparison = ImageComparison()
    qtbot.addWidget(comparison)
    comparison.resize(1000, 650)
    comparison.show()
    image = QPixmap(1800, 1400)
    image.fill(QColor(80, 100, 120))
    comparison.set_images(image, image, {"compare": True, "link_views": linked})
    qtbot.wait(40)
    return comparison


def send_wheel(view, *, angle=0, pixel=0, horizontal=0, pos=None, phase=Qt.ScrollUpdate):
    viewport = view.graphics_view.viewport()
    pos = pos or viewport.rect().center()
    event = QWheelEvent(QPointF(pos), QPointF(viewport.mapToGlobal(pos)),
                        QPoint(0, pixel), QPoint(horizontal, angle),
                        Qt.NoButton, Qt.NoModifier, phase, False)
    QApplication.sendEvent(viewport, event)


def send_pointer(widget, event_type, pos, button, buttons, global_pos=None):
    global_pos = global_pos or widget.mapToGlobal(pos)
    event = QMouseEvent(event_type, QPointF(pos), QPointF(global_pos),
                        button, buttons, Qt.NoModifier)
    QApplication.sendEvent(widget, event)


def assert_center_close(view, expected, screen_tolerance=2):
    center = view.view_state()["center"]
    scale = view.graphics_view.transform().m11()
    assert abs(center.x() - expected.x()) * scale <= screen_tolerance
    assert abs(center.y() - expected.y()) * scale <= screen_tolerance


@pytest.mark.parametrize("linked", [True, False])
def test_manual_view_keeps_source_center_and_scale_through_splitter_moves(qtbot, linked):
    comparison = make_comparison(qtbot, linked)
    for view in (comparison.original_view, comparison.image):
        view.actual_size()
        view.graphics_view.centerOn(QPointF(800, 620))
        qtbot.wait(10)
    centers = [view.view_state()["center"] for view in (comparison.original_view, comparison.image)]
    scales = [view.zoom_percent() for view in (comparison.original_view, comparison.image)]
    for ratio in (.35, .68, .43, .61, .5):
        comparison.splitter.moveSplitter(round(comparison.splitter.width() * ratio), 1)
        qtbot.wait(15)
        for view, center, zoom in zip((comparison.original_view, comparison.image), centers, scales):
            assert_center_close(view, center)
            assert view.zoom_percent() == pytest.approx(zoom)
            assert not view.view_state()["fit"]


def test_fit_resize_is_not_published_as_user_navigation(qtbot):
    comparison = make_comparison(qtbot)
    spies = [QSignalSpy(view.view_changed) for view in (comparison.original_view, comparison.image)]
    comparison.splitter.moveSplitter(round(comparison.splitter.width() * .65), 1)
    qtbot.wait(25)
    assert [len(spy) for spy in spies] == [0, 0]
    for view in (comparison.original_view, comparison.image):
        assert view.view_state()["fit"]
        assert_center_close(view, QPointF(900, 700))
        assert view.displayed_size().width() <= view.graphics_view.viewport().width()
        assert view.displayed_size().height() <= view.graphics_view.viewport().height()
    assert comparison.image.zoom_percent() == pytest.approx(comparison.original_view.zoom_percent())


@pytest.mark.parametrize("driver_name", ["image", "original_view"])
def test_continuous_pan_follows_pointer_without_reapplying_driver_transform(qtbot, monkeypatch, driver_name):
    comparison = make_comparison(qtbot)
    driver = getattr(comparison, driver_name)
    driver.actual_size()
    qtbot.wait(15)
    start = driver.graphics_view.viewport().rect().center()
    center = driver.view_state()["center"]
    scale = driver.graphics_view.transform().m11()
    applications = []
    original_apply = driver.apply_view_state

    def record_apply(*args, **kwargs):
        applications.append(args)
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(driver, "apply_view_state", record_apply)
    viewport = driver.graphics_view.viewport()
    send_pointer(viewport, QEvent.MouseButtonPress, start, Qt.LeftButton, Qt.LeftButton)
    for delta in (QPoint(12, 8), QPoint(25, 18), QPoint(40, 25), QPoint(60, 35)):
        send_pointer(viewport, QEvent.MouseMove, start + delta, Qt.NoButton, Qt.LeftButton)
        qtbot.wait(10)
        expected = center - QPointF(delta.x() / scale, delta.y() / scale)
        assert_center_close(driver, expected)
        peer = comparison.original_view if driver is comparison.image else comparison.image
        assert_center_close(peer, driver.view_state()["center"])
    send_pointer(viewport, QEvent.MouseButtonRelease, start + delta, Qt.LeftButton, Qt.NoButton)
    qtbot.wait(10)
    assert applications == []


@pytest.mark.parametrize("angle", [15, 30, -15, -60])
def test_small_wheel_deltas_produce_proportional_zoom(qtbot, angle):
    comparison = make_comparison(qtbot)
    driver = comparison.image
    driver.actual_size()
    qtbot.wait(10)
    send_wheel(driver, angle=angle)
    qtbot.wait(10)
    assert driver.zoom_percent() == pytest.approx(100 * 1.25 ** (angle / 120))
    assert comparison.original_view.zoom_percent() == pytest.approx(driver.zoom_percent())


@pytest.mark.parametrize("horizontal,phase", [(0, Qt.ScrollBegin), (0, Qt.ScrollEnd), (120, Qt.ScrollUpdate)])
def test_zero_and_horizontal_wheel_events_do_not_zoom(qtbot, horizontal, phase):
    comparison = make_comparison(qtbot)
    before = comparison.image.view_state()
    send_wheel(comparison.image, horizontal=horizontal, phase=phase)
    qtbot.wait(10)
    after = comparison.image.view_state()
    assert after["zoom"] == pytest.approx(before["zoom"])
    assert after["fit"] == before["fit"]
    assert_center_close(comparison.image, before["center"])


def test_pixel_only_trackpad_event_zooms_and_keeps_cursor_anchor(qtbot):
    comparison = make_comparison(qtbot)
    driver = comparison.image
    driver.actual_size()
    qtbot.wait(10)
    pos = driver.graphics_view.viewport().rect().center() + QPoint(45, -30)
    anchor = driver.graphics_view.mapToScene(pos)
    send_wheel(driver, pixel=24, pos=pos)
    qtbot.wait(10)
    assert driver.zoom_percent() > 100
    mapped = driver.graphics_view.mapFromScene(anchor)
    assert abs(mapped.x() - pos.x()) <= 2
    assert abs(mapped.y() - pos.y()) <= 2
    assert_center_close(comparison.original_view, driver.view_state()["center"])


def test_dragging_splitter_previews_divider_without_resizing_images_until_release(qtbot):
    comparison = make_comparison(qtbot)
    handle = comparison.splitter.handle(1)
    start = handle.rect().center()
    initial_global = handle.mapToGlobal(start)
    before = comparison.splitter.sizes()
    view_sizes = [view.graphics_view.viewport().size() for view in (comparison.original_view, comparison.image)]
    send_pointer(handle, QEvent.MouseButtonPress, start, Qt.LeftButton, Qt.LeftButton, initial_global)
    for dx in (20, 40, 70):
        delta = QPoint(dx, 0)
        send_pointer(handle, QEvent.MouseMove, start + delta, Qt.NoButton, Qt.LeftButton, initial_global + delta)
        qtbot.wait(10)
        assert comparison.splitter.sizes() == before
        assert [view.graphics_view.viewport().size() for view in (comparison.original_view, comparison.image)] == view_sizes
    send_pointer(handle, QEvent.MouseButtonRelease, start + delta, Qt.LeftButton, Qt.NoButton, initial_global + delta)
    qtbot.wait(20)
    assert comparison.splitter.sizes() != before
    for view in (comparison.original_view, comparison.image):
        assert_center_close(view, QPointF(900, 700))


def test_standalone_zoomed_view_retains_center_on_resize(qtbot):
    view = ZoomableImageView()
    qtbot.addWidget(view)
    view.resize(600, 450)
    view.show()
    image = QPixmap(1800, 1400)
    image.fill(QColor("gray"))
    view.set_source_pixmap(image)
    qtbot.wait(20)
    view.actual_size()
    view.graphics_view.centerOn(QPointF(750, 600))
    qtbot.wait(10)
    before = view.view_state()["center"]
    for width, height in [(420, 500), (700, 400), (600, 450)]:
        view.resize(width, height)
        qtbot.wait(15)
        assert_center_close(view, before)
        assert view.zoom_percent() == pytest.approx(100)
