# Screen bounds and tile grid review — 2026-10-16

Follow-up: [window lifecycle and theme review](window-lifecycle-theme-review.md)
replaces the continuous screen-cap/event approach below after native-window
regressions were reported. The vector grid implementation remains in use.

This review covers the screen/grid repair on `codex-ready-2026-10-15`.
Inference, preprocessing, model outputs, class probabilities and area statistics
have not been changed.

## Causes and changes

The main window had a hard minimum of 1366×768. Its center tab required 500 pixels
of width and the original/result panes required 220/300 pixels of height. The
stacked result pages also contributed minimum heights, while the tiled summary
and toolbar consumed more height. These constraints could grow the top-level
window rather than make its content scroll. Saved window geometry was not being
checked against the current monitor's available work area.

The window now bounds its outer frame to the current screen's
`availableGeometry()`, including frame decorations, after startup, saved geometry
restoration, mode changes, result/history display, layout/resize, screen changes
and normal/maximized transitions. Those rectangles are already Qt logical
coordinates: no DPR conversion is applied to the work area. Saved normal geometry
and maximized state are retained. Screen work-area changes also trigger a check.

Input and export/session controls scroll independently, while Run Inference and
Re-run stay below those controls. Result details are collapsible. Results retain
readable internal dimensions and scroll on short windows; narrow windows scroll
the body horizontally. This avoids squeezing result controls to unreadable
widths. The same small-window treatment preserves the existing classification
chart and segmentation view. The full-suite check also exposed a zero-height
history table after restoring a very short window; history now scrolls internally
with space retained for the table, preserving the original visibility assertion.

Previously a one-source-pixel grid was rasterized into the large classification
image before display downsampling. Fit sampling could remove these thin lines.
The viewer now draws the grid in `QGraphicsView.drawForeground`, after the image,
mapping actual tile edges through the image's `viewportTransform()`. The line
core is 2 logical pixels with a dark contrast halo. The painter retains its DPR
mapping, so line width remains stable on high-DPI displays. Duplicate shared
edges are merged, and display pixels are never modified to draw this grid.
Source-resolution PNG exports keep their existing raster boundary behavior.

Fit uses a fresh absolute source-to-viewport transform. Manual zoom also sets an
absolute transform, rather than multiplying an existing Fit transform. Fit
recalculates on viewport resize; manual zoom preserves magnification. The former
100% label was relative to Fit. The new percentage is
`scene scale × devicePixelRatio × 100`; 1:1/100% means one source pixel per physical
display pixel. Fit is explicitly labeled with its actual percentage.

## Verification

Environment: Linux, Python 3.10.22, PyQt 5.15.11, Qt 5.15.14. Existing virtual
environment and setup workflow were reused; no dependency/configuration changes
were needed. Rendering uses Qt offscreen. These are not Windows-native screenshots
or proof of Windows window-manager behavior. Native Windows maximize/restore,
taskbar and mixed-monitor transitions still require an actual Windows session.

The lightweight fixture is **synthetic layout data**, not a prediction from the
user's unavailable image/weights. It uses a 3552×3536 canvas with 512×512 tiles:
49 boxes, STR 47/NORM 1/MUC 1, and fixed test probabilities. It creates no model
weights. Model correctness is not inferred from these screenshots or counts.

Verified source edges:

- X: 0, 512, 1024, 1536, 2048, 2560, 3072, 3552 (last column 480).
- Y: 0, 512, 1024, 1536, 2048, 2560, 3072, 3536 (last row 464).
- Six interior lines in each direction remain visibly painted at Fit and zoom
  out, with transformed sample positions checked in the rendered viewport.
- Overlay/color-map switching, boundary toggles, zoom, resize and history restore
  retain source alignment. Classes, per-tile probabilities, counts and true-crop
  area statistics remain equal to the original fixture.
- Small available logical areas: 640×480, 800×540 at nonzero origin and 480×360.
  Oversized/offscreen saved geometry, both analysis modes, result display,
  expanded details, history and restart stay within those areas. Run remains
  visible in the input panel; scrolling reaches the right-side actions.
- Real offscreen available area: 800×600. Normal/maximized and persisted maximized
  restoration are exercised. The test permits the offscreen backend's synthetic
  2-pixel maximize decoration; normal bounds are strict.
- `QT_ENABLE_HIGHDPI_SCALING=1` with `QT_SCALE_FACTOR=1.25`, `1.5`, `2`: 7 passed
  each, 0 failed, 0 errors. A separate screen query confirms DPR 2 with a
  400×300 logical available area at 200% (800×600 physical).

Related tests: **114 passed, 0 failed, 0 errors**. Command, after activating the
existing environment's Qt/cache/app-data paths:

```bash
.venv/bin/python -m pytest -q \
  tests/test_screen_fit_and_tile_grid.py tests/test_result_panel.py \
  tests/test_classification_modes_display.py tests/test_classification_tiles.py \
  tests/test_settings_dialog.py tests/test_ui_shell.py \
  tests/test_inference_panel.py tests/test_action_panel.py \
  tests/test_history_panel.py tests/test_main_window_rerun.py \
  tests/test_main_window_export.py tests/test_main_window_delete.py
```

Full command: `.venv/bin/python -m pytest -q --continue-on-collection-errors`.
Final result: **224 passed, 1 failed, 1 collection error**, 14 warnings.
The remaining failure is
`test_default_builtin_paths_keep_real_classification_and_segmentation_models`:
the real built-in classification checkpoint `models/crc_dn21_seed42_best.pth`
is absent (the real segmentation checkpoint is also not installed). The
collection error is `tests/test_train_crc_resume.py`, which reads the absent
`models/dn21_folder_classification/train_crc_dn21 (1).py`. These are the two
previously known missing-file problems, not successful checks. No tests were
removed, skipped or given weaker prediction assertions to conceal them.

`git diff --check` passes. The repair was reviewed against base commit
`26a6a5e2bfbab86a9030b8eaf40e3d4031a286ee` on `codex-ready-2026-10-15`.

## Screenshots and measurements

Artifacts are under `/workspace/artifacts/screen-grid-review/`. They are captured
at actual small window sizes, not by enlarging the available rendering canvas.
All three zoom screenshots show the same synthetic result with boundaries on:

| File | Actual ratio | Outer frame |
|---|---:|---|
| `fit.png` | Fit (2.5%), precise 2.54525% | 800×600 |
| `zoom-in.png` | 3.2%, precise 3.18156% | 800×600 |
| `zoom-out.png` | 2%, precise 2.03620% | 800×600 |

`*-grid.png` files are unscaled viewport captures. The Fit capture clearly shows
7×7. A zoomed-in image can naturally extend beyond the viewport; its visible
grid follows the same transform rather than fitting independently.

`window-640x480-{single_image,tiled_analysis}.png` and
`window-480x360-{single_image,tiled_analysis}.png` show both modes in bounded
windows, with Run visible. The corresponding `*-result-scrolled.png` files show
access to the result through horizontal/vertical scrolling. Measurements are in
`capture-report.json`; reproducible capture code is `capture.py`. Test output is
in `related-tests.log`, `dpi-{125,150,200}.log` and `full-tests.log`.
The publication check repeats these tests, with output retained as
`precommit-related-tests.log`, `precommit-dpi-{1.25,1.5,2}.log` and
`precommit-full-tests.log`.

## Modified files

- `ui/main_window.py`, new `ui/window_geometry.py`: logical work-area bounds,
  screen/state events, geometry persistence and scrollable body.
- `ui/inference_panel.py`, `ui/action_panel.py`: scrolling controls, pinned actions.
- `ui/result_panel.py`, `ui/history_panel.py`: readable scrollable small panes.
- `ui/classification_result.py`: collapsible details, responsive toolbar,
  separate vector grid display.
- `ui/zoomable_image_view.py`: foreground grid, absolute Fit/zoom, actual percentage.
- New `tests/test_screen_fit_and_tile_grid.py`: geometry, coordinates, rendered
  grid pixels, zoom, history and prediction/statistics invariants.
- `tests/test_result_panel.py`, `tests/test_settings_dialog.py`,
  `tests/test_ui_shell.py`: updated Fit/screen-aware layout expectations; chart
  readability, panel containment and splitter drag assertions remain.
- `docs/classification-tiles.md`, this report: behavior and verification evidence.
