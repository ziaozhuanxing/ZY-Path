# Classification result layout

Tiled analysis keeps the result image and a compact nine-class summary on the
same page. Each entry shows the model's class color, label, tile count and
estimated coverage. Entries follow the recorded class order, including classes
with zero tiles. Coverage uses the existing real-crop area ratios; it is not a
pixel segmentation measurement or a percentage of tile counts.

`Tile details` expands a drawer below the viewer. Its splitter can be dragged;
both the Tiles table and the optional Class details (RGB) table leave the image
and compact summary visible. Both tables remain read-only, support keyboard
scrolling, and clear current/selected state as before. The drawer starts closed
for new results and history loads.

The duplicate original-image pane is hidden only for tiled results. The viewer
offers Overlay, Class color map and Original image. Opacity affects Overlay;
tile boundaries and source-coordinate hover inspection work in every view.
Single-image classification and stored-image fallback restore their existing
original-image preview. Segmentation now has its own optional original-image
comparison (see `segmentation-results-layout.md`).

The summary reflows into one, two or three columns. A bounded vertical scroll
area makes all nine entries accessible on small panels without forcing the main
window to grow. Short panels use a compact summary row when the drawer is open.
They put the redundant parameter headline in `Parameters`, which still exposes
the actual tile dimensions, network input, preprocessing, resize method and
unconfirmed training-scale note. Drawer sizing includes the styled headers,
one data row and horizontal scrollbar. The splitter inherits the current theme
at startup instead of a hard-coded Light style.

Hover inspection maps the viewport point through `QGraphicsView.mapToScene()`
and searches recorded crop boxes with half-open bounds. It does not infer a
class from display colors or assume that the network input is the source crop
size. A row/column index avoids scanning every tile on pointer movement. The
tooltip shows the recorded class, confidence, source box and crop dimensions.
Leaving, panning, zooming and clearing the result dismiss stale tooltips.

Inference, preprocessing, model classes/colors, probabilities and area
statistics are unchanged. Existing history and export presentation metadata also
supports `view: original`; classification mode and model information remain
attached to PNG/PDF output. The vector grid and true-pixel zoom implementation
in `ZoomableImageView` is unchanged.

## Validation and evidence

`tests/test_classification_results_layout.py` uses synthetic results without
production weights. Its eight cases cover small panels down to 360x420, actual
Light/Dark application styles, larger fonts, every class's visibility via
scrolling, table/summary/image coexistence, actual crop edge mapping, Fit/zoom/
pan/view changes, history, PNG/PDF presentation inputs and task transitions.
Existing theme/table tests retain their focus, selection, keyboard and color
assertions; navigation is updated for the new drawer instead of an image tab.

| Check | Passed | Failed | Errors |
|---|---:|---:|---:|
| Related UI/classification/history/export regressions | 143 | 0 | 0 |
| New layout/hover cases on Linux Xorg/xcb | 8 | 0 | 0 |
| New layout cases plus grid tests at 150%, and at 200%, each | 15 | 0 | 0 |
| Complete pytest, retaining collection errors | 253 | 1 | 1 |

The related test list is the list in `window-lifecycle-theme-review.md` plus
`tests/test_classification_results_layout.py`.

Final logs and screenshots are under
`/workspace/artifacts/classification-results-review/` in this cloud workspace:

- `normal-overlay.png`, `expanded-tiles.png`, `small-window.png`.
- `class-color-map.png`, `original-image.png`, `tile-tooltip.png`.
- `capture.py`, `states.json`, `ui-events.log` reproduce/record the preview.
- `related-verified.log`, `x11-verified.log`, `dpi150-verified.log`,
  `dpi200-verified.log`, `full-verified.log` record test execution.

The screenshots use a synthetic calibration texture and the existing 49-tile
fixture (47 STR, one NORM, one MUC). They demonstrate layout and coordinate
mapping, not real model accuracy. The last crop is 480x464 pixels at
`(3072, 3072, 3552, 3536)`.

Validation uses Linux Qt offscreen and Xorg/xcb. These are not Windows-native
window-button, display-driver or physical mixed-DPI monitor validation. On Linux
the test commands use a writable `APPDATA`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`
and `MPLCONFIGDIR`; no user data is reset.

The complete suite is run with
`.venv/bin/python -m pytest -q --continue-on-collection-errors`. Its known missing
files remain the real built-in model weights and
`models/dn21_folder_classification/train_crc_dn21 (1).py`. No replacement weights
or scripts are created and no tests are removed or skipped to hide these issues.
