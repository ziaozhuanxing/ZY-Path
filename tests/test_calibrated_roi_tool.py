"""Synthetic geometry and native-ROI extraction fixtures, not patient results."""

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image
from PyQt5.QtCore import QPoint, Qt

from scripts.extract_calibrated_roi import (
    InvalidRegionError, RegionCanvas, RegionDialog, centred_box,
    make_plan, read_mpp, read_overview, save_roi,
)


def test_measured_tcga_sampling_gives_444_pixel_tiles_and_an_exact_grid():
    plan = make_plan((40288, 31418), (.252, .252))
    assert plan.tile_size == (444, 444)
    assert plan.roi_size == (4440, 4440)
    assert plan.effective_input_mpp == pytest.approx((.4995, .4995))
    assert [plan.roi_size[i] // plan.tile_size[i] for i in (0, 1)] == [10, 10]


def test_anisotropic_sampling_uses_independent_axis_calibration():
    plan = make_plan((40000, 30000), (.252, .5))
    assert plan.tile_size == (444, 224)
    assert plan.roi_size == (4440, 2240)
    assert plan.effective_input_mpp == pytest.approx((.4995, .5))


@pytest.mark.parametrize('mpp', [(0, .5), (-1, .5), (float('nan'), .5), (float('inf'), .5),
                                  (True, .5), ('0.5', .5), (1e-320, .5), (1000, .5)])
def test_invalid_or_unrepresentable_sampling_does_not_get_a_default(mpp):
    with pytest.raises(ValueError, match='MPP|sampling'):
        make_plan((40000, 30000), mpp)


@pytest.mark.parametrize('grid', [0, 21, True, 1.5])
def test_invalid_grid_is_rejected(grid):
    with pytest.raises(ValueError):
        make_plan((40000, 30000), (.252, .252), grid)


def test_oversized_and_insufficient_fields_are_not_silently_resized_or_padded():
    with pytest.raises(ValueError, match='25 million'):
        make_plan((200000, 200000), (.01, .01))
    with pytest.raises(ValueError, match='smaller than'):
        make_plan((3000, 3000), (.252, .252))


@pytest.mark.parametrize('centre,expected', [
    ((0, 0), (0, 0, 4440, 4440)),
    ((40288, 31418), (35848, 26978, 40288, 31418)),
    ((20144, 15709), (17924, 13489, 22364, 17929)),
])
def test_selected_boxes_stay_at_level_zero_and_inside_source(centre, expected):
    assert centred_box(make_plan((40288, 31418), (.252, .252)), centre) == expected


@pytest.mark.parametrize('properties', [{}, {'openslide.mpp-x': '.252'},
    {'openslide.mpp-x': 'bad', 'openslide.mpp-y': '.252'},
    {'openslide.mpp-x': '0', 'openslide.mpp-y': '.252'}])
def test_missing_metadata_never_assumes_half_micron(properties):
    with pytest.raises(ValueError, match='MPP'):
        read_mpp(properties)


def test_native_mpp_fields_are_read_as_numbers():
    assert read_mpp({'openslide.mpp-x': '.2520', 'openslide.mpp-y': '.2520'}) == (.252, .252)


def test_overview_uses_a_bounded_low_resolution_level():
    class Pyramid:
        dimensions = (40288, 31418)
        level_dimensions = [(40288, 31418), (10072, 7854), (2518, 1963)]

        def get_best_level_for_downsample(self, value):
            return 2

        def read_region(self, origin, level, size):
            assert origin == (0, 0) and level == 2 and size == (2518, 1963)
            return Image.new('RGBA', size, (120, 80, 140, 255))

    overview, level = read_overview(Pyramid())
    assert level == 2 and overview.width <= 1200 and overview.height <= 900


def test_missing_pyramid_cannot_trigger_full_slide_decoding():
    class NoPyramid:
        dimensions = (40288, 31418)
        level_dimensions = [dimensions]

        def get_best_level_for_downsample(self, value):
            return 0

        def read_region(self, *args):
            pytest.fail('The full-resolution slide must not be decoded for its overview')

    with pytest.raises(ValueError, match='No bounded overview'):
        read_overview(NoPyramid())


class SyntheticSlide:
    properties = {'openslide.objective-power': 'synthetic'}
    level_dimensions = [(64, 48), (16, 12)]
    level_downsamples = [1., 4.]

    def __init__(self, *, transparent=False):
        self.calls = []
        self.transparent = transparent

    def read_region(self, origin, level, size):
        self.calls.append((origin, level, size))
        image = Image.new('RGBA', size)
        image.putdata([((origin[0]+x) % 256, (origin[1]+y) % 256, 77, 255)
                       for y in range(size[1]) for x in range(size[0])])
        if self.transparent:
            image.putpixel((0, 0), (0, 0, 0, 0))
        return image


def small_fixture(tmp_path):
    source = tmp_path / 'synthetic-source.svs'
    source.write_bytes(b'Synthetic source identity fixture; not an actual patient slide.')
    plan = make_plan((64, 48), (1., 1.), grid=2, reference_mpp=.5, input_size=8)
    return source, plan, centred_box(plan, (32, 24))


def test_roi_reads_only_the_selected_region_and_preserves_pixels_and_calibration(tmp_path):
    source, plan, box = small_fixture(tmp_path)
    before = source.read_bytes()
    slide = SyntheticSlide()
    png, sidecar, metadata = save_roi(slide, source, plan, box, tmp_path / 'output')
    assert slide.calls == [((28, 20), 0, (8, 8))]
    with Image.open(png) as image:
        assert image.size == (8, 8)
        assert image.getpixel((0, 0)) == (28, 20, 77)
        assert image.getpixel((7, 7)) == (35, 27, 77)
        embedded = json.loads(image.info['zypath.calibration'])
    assert embedded['source_box_px'] == [28, 20, 36, 28]
    assert embedded['pixel_size_um'] == [1., 1.]
    assert embedded['resize_applied'] is False
    assert embedded['padding_applied'] is False
    assert metadata == json.loads(sidecar.read_text())
    assert metadata['roi_png_sha256'] == hashlib.sha256(png.read_bytes()).hexdigest()
    assert source.read_bytes() == before


def test_missing_source_pixels_are_not_filled_with_fake_tissue(tmp_path):
    source, plan, box = small_fixture(tmp_path)
    with pytest.raises(InvalidRegionError, match='missing/transparent'):
        save_roi(SyntheticSlide(transparent=True), source, plan, box, tmp_path / 'output')
    assert not (tmp_path / 'output').exists()


def test_existing_output_is_not_replaced(tmp_path):
    source, plan, box = small_fixture(tmp_path)
    output = tmp_path / 'output'
    output.mkdir()
    destination = output / 'roi_native.png'
    destination.write_bytes(b'existing output')
    with pytest.raises(FileExistsError):
        save_roi(SyntheticSlide(), source, plan, box, output)
    assert destination.read_bytes() == b'existing output'


def test_metadata_write_failure_removes_partial_roi_files(tmp_path, monkeypatch):
    source, plan, box = small_fixture(tmp_path)
    original = Path.write_text

    def fail_metadata(path, *args, **kwargs):
        if path.name == 'roi_native.json.tmp':
            raise OSError('synthetic write failure')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'write_text', fail_metadata)
    with pytest.raises(OSError, match='synthetic write failure'):
        save_roi(SyntheticSlide(), source, plan, box, tmp_path / 'output')
    assert list((tmp_path / 'output').iterdir()) == []


def test_overview_letterboxing_does_not_select_a_region(qtbot):
    plan = make_plan((10000, 5000), (.5, .5))
    canvas = RegionCanvas(Image.new('RGB', (200, 100)), plan)
    qtbot.addWidget(canvas)
    canvas.resize(600, 600)
    canvas.show()
    qtbot.waitExposed(canvas)
    qtbot.mouseClick(canvas, Qt.LeftButton, pos=QPoint(300, 20))
    assert canvas.box is None
    rectangle = canvas.image_rect()
    qtbot.mouseClick(canvas, Qt.LeftButton, pos=rectangle.center().toPoint())
    assert canvas.box == centred_box(plan, (5000, 2500))


def test_resizing_overview_does_not_change_saved_source_coordinates(qtbot):
    plan = make_plan((10000, 5000), (.5, .5))
    canvas = RegionCanvas(Image.new('RGB', (200, 100)), plan)
    qtbot.addWidget(canvas)
    canvas.show()
    qtbot.waitExposed(canvas)
    qtbot.mouseClick(canvas, Qt.LeftButton, pos=canvas.image_rect().center().toPoint())
    box = canvas.box
    canvas.resize(900, 500)
    qtbot.wait(20)
    assert canvas.box == box


def test_save_requires_an_explicit_selection(qtbot):
    plan = make_plan((40288, 31418), (.252, .252))
    dialog = RegionDialog(Image.new('RGB', (800, 624)), plan)
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    assert not dialog.save_button.isEnabled()
    qtbot.mouseClick(dialog.canvas, Qt.LeftButton, pos=dialog.canvas.image_rect().center().toPoint())
    assert dialog.save_button.isEnabled()
    assert dialog.canvas.box is not None
