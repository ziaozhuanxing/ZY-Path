# Linked original/result comparison

`ui/image_comparison.py` is shared by segmentation and classification tiles.
Single-image classification retains its existing source image and probability
chart. New image comparisons default off; Link views defaults on. Legacy history
without the new keys uses those defaults.

The first comparison starts with equal pane sizes. The Qt splitter previously
chose unequal initial sizes, after which each view fitted independently; that
made the result smaller than the original. The new component explicitly applies
50:50 after layout settles. User dragging updates the original-pane fraction;
resize, orientation changes, closing/reopening comparison and history restore
retain it. Wide comparison areas use left/right panes; narrow ones use top/bottom.

Linked Fit takes the smaller of the two viewports' fitted physical-pixel ratios,
so both images are complete and equally magnified even with unequal panes.
Zoom In/Out, wheel zoom, actual size, double-click Fit and pan can originate in
either view. Absolute zoom and source-image center are applied to the peer with
feedback suppressed. An explicit navigation action is published before a
following resize can reuse old state. Resizing in Fit refits both; resizing a
zoomed view preserves the shared magnification and center.

The reusable image view exposes navigation state/signals rather than copying
its zoom/pan implementation into both result pages. Scene padding permits
unequal viewports to center the same point at image edges, where independent Qt
scrollbar clamping would otherwise make their coordinates differ. The 100%
meaning remains one source pixel per physical display pixel, accounting for Qt
device pixel ratio. Source images, masks, model preprocessing and inference
parameters are not resized or changed by this comparison logic.

Turning Link views off restores independent navigation; turning it on uses the
current result view. Mismatched source dimensions disable linking. Comparison
controls reflow, and narrow labels have explanatory tooltips. In especially
short panels, a borderless themed scroll area keeps image controls accessible;
its internal minimum does not enlarge the main window. Short result pages use a
compact scrolling statistics row while comparison is open. Primary view controls
remain visible on both wide and narrow layouts.

Classification's cosmetic grid is still drawn after the image using the same
source-to-viewport transform, now on both compared images. It is not rasterized
into the preview. Recorded tile boxes also drive hover inspection on both views.
The 3552x3536 fixture has 49 tiles with a 480-pixel final column and 464-pixel final
row. Grid, view, zoom and comparison changes leave its probabilities, classes and
area statistics unchanged. Segmentation continues to use its own colors and
full-image pixel coverage, not the classification palette or estimated tile area.

Both result types record `compare`, `link_views` and `split_ratio` alongside their
existing view/opacity/grid presentation parameters. UI changes update SQLite
analysis metadata without modifying prediction artifacts. History restores those
parameters; classification mode, task and actual model information are retained.
PNG still exports the selected full-resolution result view with JSON metadata,
and PDF still reports the original and selected result. Comparison is a UI
arrangement, not a concatenated export or a new inference task.

A regression run also exposed a Qt display-table paint lifetime problem. Python
garbage collection could delete an unreachable top-level widget during the
delegate's virtual paint callback, invalidating its native table/painter. The
delegate now retains the top-level owner for that callback. A deterministic test
forces collection during style initialization, fails without retention, and
checks that the owner is collectable after painting; production code does not
disable garbage collection or replace table styling.

## Validation and evidence

`tests/test_linked_image_comparison.py` covers equal default splits, common Fit,
manual proportions and resize/reopen, both image types, bidirectional buttons,
wheel and real mouse drag events, edge coordinates, linked/unlinked navigation,
Fit immediately followed by resize, grid pixels, hover, historical parameters,
PNG pixels/model metadata and short panels with larger fonts and expanded tables.
`tests/test_result_panel.py` includes the deterministic table-paint lifetime test.
Existing exact presentation assertions are extended for the recorded new keys;
existing image size, chart, theme, read-only table and grid assertions remain.

| Final check | Passed | Failed | Errors |
|---|---:|---:|---:|
| Focused comparison/layout/grid plus paint-lifetime cases | 37 | 0 | 0 |
| Related window, classification, segmentation, history and export regressions | 191 | 0 | 0 |
| Focused cases at 150% Qt scale | 37 | 0 | 0 |
| Focused cases at 200% Qt scale | 37 | 0 | 0 |
| Focused cases on Linux Xorg/xcb | 37 | 0 | 0 |
| Complete pytest, retaining collection errors | 275 | 1 | 1 |

The complete command was `.venv/bin/python -m pytest -q
--continue-on-collection-errors --tb=short`, with writable temporary APPDATA,
XDG and Matplotlib directories. Final logs use `*-verified.log`. Earlier debug
runs in this directory include the paint crash; those incomplete runs are not
reported as passing. The lifetime regression also demonstrated an assertion
failure before its fix, without needing a native crash to verify the defect.

Evidence is under `/workspace/artifacts/linked-comparison-review/`. Screenshots
and `capture.py` use synthetic calibration textures and existing recorded result
fixtures without production weights. `states.json` records frames, actual image
magnifications, displayed image sizes, splitter sizes, presentation and grid lines.
The paired Fit captures have 384/384 pane sizes. Segmentation displays both images
at 63.0% (379x253 displayed pixels), and classification displays both at about
8.088% (288x287). Zoom captures also retain identical image sizes/magnification.
Screenshots include `segmentation-fit.png`, `segmentation-zoom.png`,
`classification-fit.png`, `classification-zoom.png`, `classification-small.png`
and `classification-small-details.png`.
This is Linux Qt offscreen/Xorg rendering and scale-factor validation, not
Windows-native buttons, display drivers or physical mixed-DPI monitor validation.
Real model prediction accuracy cannot be assessed without the production weights.

The complete suite continues to report missing real built-in model weights and
the missing `models/dn21_folder_classification/train_crc_dn21 (1).py` collection
dependency. No test is skipped or removed and no substitute model or script hides
those known missing-file problems.
