"""Select a native-resolution CRC ROI without decoding a whole slide at once."""

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys
from uuid import uuid4

from PIL import Image, PngImagePlugin
from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QLabel, QMessageBox,
    QSizePolicy, QVBoxLayout, QWidget,
)


MAX_ROI_PIXELS = 25_000_000
MAX_OVERVIEW_PIXELS = 8_000_000


@dataclass(frozen=True)
class SamplingPlan:
    slide_size: tuple[int, int]
    source_mpp: tuple[float, float]
    tile_size: tuple[int, int]
    roi_size: tuple[int, int]
    grid: int
    reference_mpp: float = 0.5
    input_size: int = 224

    @property
    def effective_input_mpp(self):
        return tuple(pixels * mpp / self.input_size
                     for pixels, mpp in zip(self.tile_size, self.source_mpp))


def make_plan(slide_size, mpp, grid=10, *, reference_mpp=0.5, input_size=224):
    if (len(slide_size) != 2 or any(type(n) is not int or n <= 0 for n in slide_size)
            or type(grid) is not int or not 1 <= grid <= 20
            or type(input_size) is not int or input_size <= 0):
        raise ValueError("Use positive slide/input dimensions and a grid from 1 to 20.")
    values = (*mpp, reference_mpp)
    if len(mpp) != 2 or any(isinstance(n, bool) or not isinstance(n, (int, float))
                            or not math.isfinite(n) or n <= 0 for n in values):
        raise ValueError("MPP must contain finite positive micrometres-per-pixel values.")
    ideal = tuple(input_size * reference_mpp / n for n in mpp)
    if any(not math.isfinite(n) or n < 0.5 for n in ideal):
        raise ValueError("The supplied sampling cannot represent this reference field.")
    tile = tuple(round(n) for n in ideal)
    roi = tuple(n * grid for n in tile)
    if roi[0] * roi[1] > MAX_ROI_PIXELS:
        raise ValueError("ROI exceeds 25 million pixels. Use a smaller --grid or check MPP.")
    if any(n > maximum for n, maximum in zip(roi, slide_size)):
        raise ValueError("The slide is smaller than the requested field. Use a smaller --grid; no padding is applied.")
    return SamplingPlan(tuple(slide_size), tuple(float(n) for n in mpp), tile, roi,
                        grid, float(reference_mpp), input_size)


def centred_box(plan, centre):
    if len(centre) != 2 or any(not math.isfinite(n) or n < 0 or n > maximum
                               for n, maximum in zip(centre, plan.slide_size)):
        raise ValueError("Choose a centre inside the slide.")
    origin = tuple(max(0, min(maximum - length, round(point - length / 2)))
                   for point, length, maximum in zip(centre, plan.roi_size, plan.slide_size))
    return (*origin, origin[0] + plan.roi_size[0], origin[1] + plan.roi_size[1])


def read_mpp(properties):
    try:
        values = tuple(float(properties[key]) for key in ('openslide.mpp-x', 'openslide.mpp-y'))
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("OpenSlide did not report both MPP values. No default MPP was assumed.") from error
    if any(not math.isfinite(n) or n <= 0 for n in values):
        raise ValueError("OpenSlide reported invalid MPP values.")
    return values


def read_overview(slide):
    """Use a bounded pyramid level; never request an unbounded level-0 image."""
    target = max(slide.dimensions[0] / 1200, slide.dimensions[1] / 900)
    preferred = slide.get_best_level_for_downsample(target)
    candidates = [i for i, size in enumerate(slide.level_dimensions)
                  if i >= preferred and size[0] * size[1] <= MAX_OVERVIEW_PIXELS]
    if not candidates:
        raise ValueError('No bounded overview pyramid level is available. Use another slide or a dedicated slide viewer.')
    level = candidates[0]
    preview = slide.read_region((0, 0), level, slide.level_dimensions[level])
    if preview.mode == 'RGBA':
        preview = Image.alpha_composite(Image.new('RGBA', preview.size, 'white'), preview)
    preview = preview.convert('RGB')
    preview.thumbnail((1200, 900), Image.Resampling.LANCZOS)
    return preview, level


class RegionCanvas(QWidget):
    region_changed = pyqtSignal(object)

    def __init__(self, thumbnail, plan, parent=None):
        super().__init__(parent)
        self.plan, self.box = plan, None
        rgb = thumbnail.convert('RGB')
        qimage = QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimage.copy())
        self.setMinimumSize(320, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.CrossCursor)

    def image_rect(self):
        available = self.contentsRect().adjusted(8, 8, -8, -8)
        scale = min(available.width() / self.pixmap.width(), available.height() / self.pixmap.height())
        if scale <= 0:
            return QRectF()
        width, height = self.pixmap.width() * scale, self.pixmap.height() * scale
        return QRectF(available.center().x() - width / 2, available.center().y() - height / 2, width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#263445'))
        rectangle = self.image_rect()
        painter.drawPixmap(rectangle, self.pixmap, QRectF(self.pixmap.rect()))
        if self.box is not None:
            x0, y0, x1, y1 = self.box
            width, height = self.plan.slide_size
            box = QRectF(rectangle.left() + x0 / width * rectangle.width(),
                         rectangle.top() + y0 / height * rectangle.height(),
                         (x1 - x0) / width * rectangle.width(), (y1 - y0) / height * rectangle.height())
            painter.setPen(QPen(QColor('black'), 4))
            painter.drawRect(box)
            painter.setPen(QPen(QColor('#ffdf00'), 2))
            painter.drawRect(box)

    def mousePressEvent(self, event):
        rectangle = self.image_rect()
        if event.button() != Qt.LeftButton or rectangle.isEmpty() or not rectangle.contains(QPointF(event.pos())):
            event.ignore()
            return
        centre = ((event.x() - rectangle.left()) / rectangle.width() * self.plan.slide_size[0],
                  (event.y() - rectangle.top()) / rectangle.height() * self.plan.slide_size[1])
        self.box = centred_box(self.plan, centre)
        self.region_changed.emit(self.box)
        self.update()
        event.accept()


class RegionDialog(QDialog):
    def __init__(self, thumbnail, plan):
        super().__init__()
        self.setWindowTitle('Select a CRC tissue region')
        layout = QVBoxLayout(self)
        message = QLabel('Click a coloured tissue area to centre the yellow box, then choose Save native ROI.')
        message.setWordWrap(True)
        layout.addWidget(message)
        summary = QLabel(f'Source MPP: {plan.source_mpp[0]:g} x {plan.source_mpp[1]:g} micrometres/pixel\n'
                         f'Native region: {plan.roi_size[0]} x {plan.roi_size[1]} pixels; '
                         f'tiles: {plan.tile_size[0]} x {plan.tile_size[1]}, grid: {plan.grid} x {plan.grid}.')
        summary.setWordWrap(True)
        summary.setMinimumWidth(0)
        layout.addWidget(summary)
        self.canvas = RegionCanvas(thumbnail, plan, self)
        layout.addWidget(self.canvas, 1)
        self.selection = QLabel('No region selected.')
        self.selection.setWordWrap(True)
        layout.addWidget(self.selection)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.save_button = buttons.button(QDialogButtonBox.Save)
        self.save_button.setText('Save native ROI')
        self.save_button.setEnabled(False)
        self.canvas.region_changed.connect(self._selected)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1000, screen.width() - 60), min(760, screen.height() - 60))

    def _selected(self, box):
        self.selection.setText(f'Selected source box (level 0): {box}')
        self.save_button.setEnabled(True)


class InvalidRegionError(ValueError):
    """An ROI includes missing source pixels rather than real scanned data."""


def save_roi(slide, source_path, plan, box, output_dir, *, reader_versions=None):
    source_path, output_dir = Path(source_path), Path(output_dir)
    x0, y0, x1, y1 = box
    if (any(type(n) is not int for n in box) or x0 < 0 or y0 < 0
            or (x1 - x0, y1 - y0) != plan.roi_size
            or x1 > plan.slide_size[0] or y1 > plan.slide_size[1]):
        raise ValueError("Invalid source box; no padded or resized ROI is written.")
    before = source_path.stat()
    region = slide.read_region((x0, y0), 0, plan.roi_size)
    if region.size != plan.roi_size:
        raise ValueError("The reader returned an unexpected ROI size.")
    if 'A' in region.getbands() and region.getchannel('A').getextrema() != (255, 255):
        raise InvalidRegionError('This region contains missing/transparent slide pixels. Choose a region inside the scanned tissue.')
    image = region.convert('RGB')
    after = source_path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("The source slide changed while reading. No ROI was saved.")
    calibration = {'schema': 'zypath.roi-calibration.v1', 'image_role': 'native_resolution_roi',
                   'source_slide': source_path.name, 'source_bytes': before.st_size,
                   'source_level': 0, 'source_size_px': list(plan.slide_size),
                   'source_box_px': list(box), 'pixel_size_um': list(plan.source_mpp),
                   'calibration_source': 'OpenSlide openslide.mpp-x and openslide.mpp-y',
                   'roi_size_px': list(plan.roi_size), 'resize_applied': False, 'padding_applied': False,
                   'colour_transform_applied': False, 'selection': 'manual; not a ground-truth annotation',
                   'reference_dataset': 'NCT-CRC-HE-100K', 'reference_mpp': plan.reference_mpp,
                   'network_input_px': [plan.input_size] * 2,
                   'recommended_tile_px': list(plan.tile_size), 'grid': [plan.grid] * 2,
                   'effective_network_mpp': list(plan.effective_input_mpp),
                   'source_coarser_than_reference': [n > plan.reference_mpp for n in plan.source_mpp],
                   'model_inference_performed': False}
    metadata = dict(calibration, reader_versions=reader_versions or {},
                    tool_version='1.0',
                    tool_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    source_objective_power=slide.properties.get('openslide.objective-power'),
                    source_level_dimensions=[list(size) for size in slide.level_dimensions],
                    source_level_downsamples=list(slide.level_downsamples),
                    icc_profile_preserved=bool(image.info.get('icc_profile')))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination, details = output_dir / 'roi_native.png', output_dir / 'roi_native.png.calibration.json'
    temporary, temporary_details = output_dir / 'roi_native.png.tmp', output_dir / 'roi_native.json.tmp'
    if any(path.exists() for path in (destination, details, temporary, temporary_details)):
        raise FileExistsError('An ROI already exists in this output directory. Use a new run directory.')
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text('zypath.calibration', json.dumps(calibration))
    committed = False
    try:
        image.save(temporary, format='PNG', pnginfo=png_info)
        digest = hashlib.sha256()
        with temporary.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        metadata['roi_png_sha256'] = digest.hexdigest()
        temporary_details.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        temporary.replace(destination)
        committed = True
        temporary_details.replace(details)
    except Exception:
        temporary.unlink(missing_ok=True)
        temporary_details.unlink(missing_ok=True)
        if committed:
            destination.unlink(missing_ok=True)
        raise
    return destination, details, metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slide', required=True, type=Path)
    parser.add_argument('--packages', type=Path, help='Independent OpenSlide dependency directory')
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--grid', type=int, default=10)
    parser.add_argument('--expect-mpp', type=float, help='Check both reported axes against an expected MPP')
    parser.add_argument('--thumbnail-only', action='store_true')
    parser.add_argument('--centre-x', type=float)
    parser.add_argument('--centre-y', type=float)
    args = parser.parse_args(argv)
    if (args.centre_x is None) != (args.centre_y is None):
        parser.error('Provide both centre coordinates, or neither for interactive selection.')
    if not args.slide.is_file():
        parser.error('The slide file does not exist.')
    if args.packages:
        sys.path.insert(0, str(args.packages.resolve()))
    try:
        import openslide
    except (ImportError, OSError) as error:
        parser.error(f'OpenSlide could not load: {error}. Install the optional dependencies in the independent tool directory.')
    try:
        with openslide.OpenSlide(str(args.slide)) as slide:
            mpp = read_mpp(slide.properties)
            if args.expect_mpp is not None and (not math.isfinite(args.expect_mpp) or args.expect_mpp <= 0
                    or any(not math.isclose(n, args.expect_mpp, rel_tol=1e-5) for n in mpp)):
                raise ValueError(f'The slide reports MPP {mpp}, which differs from --expect-mpp. No override was applied.')
            plan = make_plan(slide.dimensions, mpp, args.grid)
            run_dir = args.output_root / (datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid4().hex[:8])
            run_dir.mkdir(parents=True, exist_ok=False)
            thumbnail, overview_level = read_overview(slide)
            preview_info = PngImagePlugin.PngInfo()
            preview_info.add_text('zypath.image_role', 'overview_display_only_not_for_inference')
            preview_info.add_text('zypath.overview_level', str(overview_level))
            thumbnail.save(run_dir / 'overview_display_only.png', pnginfo=preview_info)
            print(f'MPP: {mpp}; source tiles: {plan.tile_size}; native ROI: {plan.roi_size}', flush=True)
            if args.thumbnail_only:
                print('Overview saved:', run_dir / 'overview_display_only.png')
                return 0
            app = dialog = None
            if args.centre_x is None:
                app = QApplication.instance()
                if app is None:
                    app = QApplication([sys.argv[0]])
                    app.setQuitOnLastWindowClosed(False)
                dialog = RegionDialog(thumbnail, plan)
            while True:
                if dialog is not None:
                    if dialog.exec_() != QDialog.Accepted:
                        print('Cancelled. No ROI was written. Overview directory:', run_dir)
                        return 0
                    box = dialog.canvas.box
                    if box is None:
                        continue
                else:
                    box = centred_box(plan, (args.centre_x, args.centre_y))
                print('Reading the selected level-0 region; the whole slide is not decoded.', flush=True)
                try:
                    destination, details, metadata = save_roi(slide, args.slide, plan, box, run_dir,
                        reader_versions={'openslide-python': openslide.__version__,
                                         'openslide-library': openslide.__library_version__})
                    break
                except InvalidRegionError as error:
                    if dialog is None:
                        raise
                    QMessageBox.warning(dialog, 'Choose another region', str(error))
            print('ROI saved:', destination)
            print('Calibration saved:', details)
            print(f'Use Tiled analysis, {plan.tile_size[0]} x {plan.tile_size[1]} source pixels, OpenCV linear.')
            print(f'Expected grid: {plan.grid} x {plan.grid}; network input: {plan.input_size} x {plan.input_size}.')
            print('No model prediction or accuracy evaluation was performed.')
            return 0
    except (ValueError, OSError, openslide.OpenSlideError) as error:
        print(f'ROI extraction failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
