# Segmentation result layout

Segmentation defaults to Overlay without the duplicate original-image pane above
the result. The view menu offers Overlay, Segmentation map and Original image.
Opacity applies only to Overlay. The supplied inference blend is retained at its
original opacity: 20% for the built-in overlapping UPerNet path and 40% for the
generic parser's RGBA blend. Changing opacity recomputes the blend from the
original and the actual segmentation colors, without changing predicted labels.
View and opacity changes preserve the current image coordinates and zoom.

Compare with original is off for new results. It opens an independently zoomable
original beside the selected result on wide panels, or above it on narrow panels.
The shared comparison starts with an equal split and Link views enabled. Fit
uses a common physical-pixel ratio; zoom and pan track the same source point.
The comparison splitter can be dragged and its chosen ratio is retained. Link
views can be turned off for independent navigation. See `linked-image-comparison.md`.
Selecting Original image alone does not require opening comparison.

The segmentation legend and pixel statistics remain on the same page as the
image. Wide result panes put the legend beside the viewer. Narrow panes put it
below the viewer in a bounded, themed scroll area with reflowing columns. All
classes supplied by that segmentation path remain accessible, including zero
counts in the built-in nine-class legend. Source class IDs are retained when the
generic parser supplies only present classes; counts are indexed by ID rather
than by position in that shorter legend. These are segmentation labels/colors,
not classification labels/colors. The parser's own RGBA color layer is retained
for its color-map artifact, so custom segmentation colors are not replaced by
the built-in palette.

Coverage means predicted pixels of a class divided by the full original-image
pixel count. Background, excluded and empty labels stay in the denominator.
This differs from classification tiles' estimated area coverage. Missing counts
are shown as unavailable rather than invented percentages.

Details expands a scrolling parameter description, including recorded model,
preprocessing, original dimensions and inference tile/stride/input when known.
It starts collapsed and does not force the application window to expand.
The old 600-pixel segmentation-content minimum width is removed. Main-window
geometry, native window state logic and the reusable image/grid viewer are
unchanged. Returning to single classification restores its original preview and
the user's source/result splitter allocation.

New segmentation history includes actual task/model metadata, class IDs/colors,
pixel counts, parameters, default overlay opacity and presentation. View,
opacity and comparison changes update only analysis metadata in SQLite, leaving
prediction masks and the initially saved overlay untouched. History restores the
recorded presentation. PNG exports the selected full-resolution view with a JSON
sidecar; PDF uses that view and includes the original plus model, view, pixel
statistics and analysis parameters. Comparison is a UI arrangement, not a
combined PNG. Legacy overlay-only results remain viewable; unavailable original,
map, comparison and opacity operations are disabled.

## Initial layout validation (82a919e)

`tests/test_segmentation_results_layout.py` uses synthetic pixels and recorded
segmentation fixtures, not production weights or real prediction accuracy. It
covers three panel sizes down to 360x420, Light/Dark styles, 10/15-point fonts,
scroll access to every legend entry, comparison orientation, exact rendered
pixels, zoom/coordinate preservation, sparse class IDs, history persistence,
PNG/PDF inputs, real PDF generation and task/clear transitions.

Other regression suites cover classification tiles and grids, window lifecycle,
settings, Re-run, history, deletion, database and existing exports. Old tests are
updated for the intentional change that segmentation hides the duplicate source
pane; splitter restoration is still asserted after returning to classification.

| Check | Passed | Failed | Errors |
|---|---:|---:|---:|
| Related UI, classification, segmentation, database and export regressions | 180 | 0 | 0 |
| Segmentation cases plus existing grid/screen cases at 150% Qt scale | 18 | 0 | 0 |
| Same cases at 200% Qt scale | 18 | 0 | 0 |
| Same cases on Linux Xorg/xcb | 18 | 0 | 0 |
| Complete pytest with collection errors retained | 264 | 1 | 1 |

The 11 new segmentation cases are included in these runs. The complete command
was `.venv/bin/python -m pytest -q --continue-on-collection-errors --tb=short`,
using writable temporary APPDATA/XDG/Matplotlib directories on Linux.

Linux Qt offscreen, 150%/200% Qt scale factors and Xorg/xcb are simulation and
Linux rendering checks, not Windows-native window-button or physical mixed-DPI
monitor validation. Screenshots/logs are in the cloud workspace at
`/workspace/artifacts/segmentation-results-review/`. Screenshots explicitly use
synthetic calibration pixels and no model weights.

Evidence includes `default-overlay.png`, `compare-wide.png`,
`segmentation-map.png`, `original-image.png`, `compare-small.png`, `states.json`,
`capture.py`, and `related.log`, `dpi150.log`, `dpi200.log`, `x11.log`, `full.log`.
The ordinary comparison windows are 1260x760 (horizontal) and 800x600 (vertical)
inside the Xorg display's 1280x800 available geometry; the standalone layout
regressions also exercise 360x420 panels with both font sizes.

The complete suite must retain the two existing missing-file problems: real
built-in weights (first missing `models/crc_dn21_seed42_best.pth`) and the missing
`models/dn21_folder_classification/train_crc_dn21 (1).py` collection dependency.
No replacement model/script, deleted test, skip or weakened assertion hides them.
