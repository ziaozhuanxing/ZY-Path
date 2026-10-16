# Classification UI and inference review

This review starts from `2000ecde369897298de2b0a88d11cc438a05378f` on
`codex-ready-2026-10-15`; fetch confirmed it matched origin. This report describes the reviewed changes; consult Git history and the final
handoff for commit and push status.

## Behavior changes

- Settings is resizable/maximizable. Every content page is wrapped in a
  widget-resizable scroll area. Long text wraps; the palette uses one row per class.
  Controls retain their readable heights. All application text is English.
- Classification has an explicit Single image / Tiled analysis selector directly
  below its task radio button. The selected mode, dimensions and resize method
  are visible before running. Preferences no longer enable or implicitly choose
  tiling. Single image processes the whole image; Tiled analysis also applies to
  an image smaller than a tile (one partial crop).
- 512 x 512 remains the editable initial source tile size. The interface and saved
  metadata explicitly mark training scale/magnification as unconfirmed.
- Tiled results default to an original-resolution overlay (40% class opacity).
  Opacity, color-only view and source-coordinate tile boundaries are adjustable.
  Changes preserve zoom/pan. Legend/statistics and tile details have independent
  tabs, rather than squeezing the result image. Coverage is explicitly estimated
  from tile classes, not pixel segmentation.
- New records save explicit mode, actual model, dimensions, preprocessing,
  resize method and class/color order. History and Re-run restore the recorded
  parameters rather than today's Preferences. Older tiled records remain readable;
  older records without tiled analysis default to Single image. PNG/JSON and PDF
  exports preserve the mode and selected display presentation.

## Reported 3552 x 3536 image

512 x 512 tiles yield 7 x 7 = 49 crops. The final column is 480 pixels wide;
the final row is 464 pixels tall; the corner contains 222,720 pixels. The total
source area is 12,559,872 pixels. Crop bounds are half-open (x0,y0,x1,y1).
There is no padding, overlap, repeated whole-image preprocessing or hidden
background filtering. Partial crops are resized to 224 x 224 for the network;
statistics use their actual original-image pixel area.

Coordinate-coded synthetic tests with this exact geometry check every actual
input tensor against the corresponding PIL crop, verify 49 distinct crop codes,
and verify that each source pixel is covered exactly once. For first, center and
last crops, standalone single-image inference and tiled inference produce exactly
equal tensors, probabilities, confidence and labels for both supported resize
methods. The simulated classifier deliberately produces STR=47/NORM=1/MUC=1 to
exercise this count distribution. These synthetic labels are not evidence that
the user's actual predictions are correct.

The actual image, trained classification weights and tile-coordinate predictions
were not provided in this checkout. Their STR distribution, calibration and
biological accuracy cannot be verified here. Counts alone also cannot determine
precise area fractions: the two non-STR tiles may occupy different-size edges.
No segmentation model, segmentation label or modified classifier was used as a
classification reference.

## Resize investigation

The uploaded training source converts OpenCV BGR to RGB and uses
`A.Resize(224,224)`, `ToTensorV2()`, then float32, without normalization or division
by 255. Class order is ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM.

Published Albumentations 1.3.1 and 2.0.8 wheels were inspected in isolated temporary
source directories. Both default Resize interpolation to `cv2.INTER_LINEAR`;
2.0.8 defaults `area_for_downscale` to None. The exact historical training and
OpenCV versions remain unknown. Pillow bilinear downsizing and OpenCV linear
are not numerically interchangeable. On reproducible synthetic 512-to-224 images:

| Input | Mean absolute raw255 difference | Maximum difference |
|---|---:|---:|
| Random high-frequency texture (seed 42) | 29.8753 | 130 |
| Smooth gradient | 0.05102 | 1 |

These are synthetic examples, not measurements on the user's tissue image.
Pillow remains the explicit legacy default to preserve existing single-image
behavior. Settings offers OpenCV linear, backed by opencv-python-headless 4.11.0.86;
update dependencies from requirements.txt. Both inference modes use the same
Preprocessor with the selected backend, and record it. A 512-source-pixel crop
resized to 224 also changes sampled scale; neither changing the resize backend
nor passing consistency tests establishes that this matches the training scale.

For actual image/weight diagnosis (use the same backend as the saved run):

```sh
python scripts/audit_classification_tiles.py --model "<classifier.pth>" --image "<source.png>" --tile-width 512 --tile-height 512 --resize-backend pillow_bilinear --output "classification-audit.json"
```

The script compares representative real crops against standalone inference and
reports actual tensor/probability equality, crop hashes and resize differences.
It does not modify weights or train a model. `--resize-only --output <report.json>`
measures the synthetic examples without any weights.

## Layout evidence and limits

Settings captures and measurements were generated at Qt device scale factors
1, 1.25, 1.5 and 2 (100/125/150/200%). Every case retained nine palette rows and
zero horizontal overflow, with vertical scrolling. Separate tests increased
application font size at those factors in a compact 620 x 400 window, checked
readable row heights, scrolled every palette row into view and exercised maximize.
The Settings and overlay/legend/color-map screenshots use synthetic layout data.
They were visually inspected after capture. These are Linux Qt offscreen
measurements and font stress tests, not a Windows native desktop verification;
Windows window decorations/font substitution/DPI transitions need real-device
revalidation. No Windows runtime access was available in this task.

Artifacts are under `/workspace/artifacts/classification-ui-review/`, including
settings captures for all four scales, overlay, color-only map, boundaries,
legend and tile-table images, scale measurements and resize-comparison JSON.

## Modified files

- `ui/settings_dialog.py`, `ui/inference_panel.py`: scrolling/English preferences,
  explicit mode selector and pre-run parameter summary.
- `ui/classification_result.py` (new), `ui/result_panel.py`,
  `ui/zoomable_image_view.py`: overlay controls, separate detail tabs, source-pixel
  rendering and zoom-preserving display changes.
- `ui/main_window.py`, `ui/history_panel.py`, `data/export_manager.py`: persist,
  display, restore and export actual mode/parameters and the selected presentation.
- `core/classification_tiles.py`, `core/inference_engine.py`,
  `core/preprocessor.py`: explicit mode routing, tile probabilities, rendering
  and selectable, recorded resize backend.
- `main.py`, `requirements.txt`: Qt DPI initialization and OpenCV dependency.
- `scripts/audit_classification_tiles.py` (new): reproducible real-crop audit tool.
- `tests/test_classification_tiles.py`,
  `tests/test_classification_modes_display.py` (new): explicit-mode, UI, crop,
  tensor parity, edge statistics, overlay, resize and rerun regressions.
- `docs/classification-tiles.md`, this report: updated behavior and evidence.

The known full-suite missing-file issues remain documented and unhidden:
real built-in weights are missing (one failure), and
`models/dn21_folder_classification/train_crc_dn21 (1).py` is absent from the
repository's expected path (one collection error). The training attachment is
available for inspection but was not silently substituted at that legacy path.


## Executed validation

- Related UI/inference/history/export regression selection: **111 passed, 0 failed,
  0 errors**, 13 dependency deprecation warnings.
- Full `pytest -q --continue-on-collection-errors`: **217 passed, 1 failed,
  1 collection error**, 14 warnings. The failure is the existing real-weight-file
  assertion; the error is the existing missing legacy training source path.
  This is not an all-green full suite. No test was deleted, skipped or disabled.
- `uv pip check`: all 47 installed packages compatible.
- `git diff --check`: clean.
- Device-scale captures at 100/125/150/200% report zero horizontal overflow and
  nine scroll-accessible palette rows. Native Windows remains untested.

Detailed logs, JSON measurements and screenshots are retained under
`/workspace/artifacts/classification-ui-review/`. The report distinguishes synthetic
checks from checks that require the missing actual source image and weights.


## Pre-submit resize consistency check

The default remains Pillow bilinear, with the persisted backend key
`pillow_bilinear`. A golden pixel test compares the implicit default with the
original Pillow BILINEAR operation on a nonuniform image.

| UI option | Recorded backend | Actual operation |
|---|---|---|
| Pillow bilinear (legacy) | pillow_bilinear | PIL.Image.resize(..., Image.Resampling.BILINEAR) |
| OpenCV linear | opencv_linear | cv2.resize(..., interpolation=cv2.INTER_LINEAR) |

Both modes were tested with both backend choices. Assertions check history,
PNG JSON export, and Re-run after switching today's Preferences to the opposite
backend. The recorded selection remains authoritative. A separate pixel test
compares the OpenCV option against cv2.INTER_LINEAR directly.
