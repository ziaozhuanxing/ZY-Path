"""Render immutable presentation snapshots without reading GUI widgets."""
from copy import deepcopy
from PIL import Image
from PyQt5.QtGui import QImage, QPainter, QTransform
from core.classification_tiles import render_classification_map
from core.large_image_segmentation import make_overlay
from ui.tile_annotations import draw_tile_numbers, snapshot_number_style


def presentation_snapshot(page, kind, *, copy_metadata=True):
    """GUI thread only. Result-page PIL images are immutable owned sources.

    Keep references so replacing/clearing the page cannot free or change a
    worker's inputs. Copy only metadata; image compression/copies run on worker.
    """
    snapshot = {'kind': kind, 'presentation': deepcopy(page.presentation()),
                'original': page.original}
    if kind == 'classification':
        snapshot.update(color_map=page.color_map, analysis=deepcopy(page.analysis) if copy_metadata else page.analysis)
        if snapshot['presentation']['tile_numbers']:
            size = max(12, min(160, min(page.analysis['tile_size']) // 5))
            snapshot['number_style'] = snapshot_number_style(page.font(), size)
    else:
        snapshot.update(color_map=page.color_mask, overlay=page.overlay,
                        initial_opacity=page._initial_opacity)
    return snapshot


def render_snapshot(snapshot, *, include_boundaries=True, include_numbers=True):
    p = snapshot['presentation']
    original, colors = snapshot['original'], snapshot['color_map']
    if snapshot['kind'] == 'segmentation':
        if p['view'] == 'original' and original is not None:
            return original.copy()
        if p['view'] == 'segmentation_map' and colors is not None:
            return colors.copy()
        if original is None or colors is None or round(p['opacity'] * 100) == round(snapshot['initial_opacity'] * 100):
            return snapshot['overlay'].copy()
        return make_overlay(original, colors, p['opacity'])
    analysis = snapshot['analysis']
    image = render_classification_map(original, colors, analysis,
        0 if p['view'] == 'original' else p['opacity'], p['view'] == 'color_map',
        p['boundaries'] and include_boundaries)
    if p['tile_numbers'] and include_numbers:
        qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format_RGB888).copy()
        qimage.setDotsPerMeterX(3780)
        qimage.setDotsPerMeterY(3780)
        painter = QPainter(qimage)
        try:
            size = max(12, min(160, min(analysis['tile_size']) // 5))
            draw_tile_numbers(painter, [tile.get('area_box', tile['box']) for tile in analysis['tiles']], QTransform(), size,
                style=snapshot['number_style'])
        finally:
            painter.end()
        image = Image.frombytes('RGB', image.size, qimage.bits().asstring(qimage.byteCount()), 'raw', 'RGB', qimage.bytesPerLine())
    return image
