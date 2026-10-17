# Settings and history result semantics

History keeps the original persisted results and analysis parameters. The table's
`Result / summary` column distinguishes two classification workflows:

- Single-image classification keeps its label and confidence.
- Tiled analysis shows a tile count and the class with the largest estimated area,
  in a two-line summary. The Confidence column is blank (`-`); each tile's confidence
  remains available when restoring the record. Coverage uses saved crop areas and
  full-image dimensions, including partial edge crops. Tile-count fractions are
  never substituted for area fractions. Missing or inconsistent area metadata is
  shown as unavailable rather than replaced with a global label.

The existing stored tiled label/probability is the argmax of area-weighted mean
class probabilities across crops. It can differ from the class with the largest
estimated coverage. It is not a separate whole-image classification prediction.
PDF metadata now calls these values `Aggregate tile label` and
`Area-weighted mean probability`, while single-image field names remain unchanged.
Predictions, statistics, recorded models, Re-run parameters and stored history
values have not been rewritten.

## Settings sections

- **Appearance**: existing Light/Dark selection.
- **Preferences**: grouped export reminders, current/default classification mode, source
  tile width/height, resize backend, separate classification/built-in segmentation
  palettes and layout help/reset. Mode choices in Preferences immediately update
  the main panel and save the startup default. Main-panel user choices also save
  that default; history restore/Re-run only select the recorded mode without
  changing the default. The saved startup default is shown beside the control. Defaults remain Single image, 512 x 512 original-image
  tiles and Pillow bilinear. The training scale/magnification remain unconfirmed.
  Reset Classification restores only those classification preferences, preserving
  model defaults, theme, export reminders, history and current task. Reset also
  selects Single image for the next run. Mode/reset controls are locked during
  inference. Closed Settings dropdowns pass wheel gestures to page scrolling;
  explicit popup selection and keyboard arrows remain available.
- **Models**: existing independent per-task model defaults and validation.
- **Guide & Support**: quick start and a section selector, explaining the left
  inputs, central results, right actions, single/tiled classification, segmentation,
  comparison, statistics, history, export, cancellation and troubleshooting.
  `support@example.invalid` and `+1 202-555-0147` are explicitly fictional example
  contacts. The GitHub project link points to the real repository.
- **System Information**: visible, read-only runtime, library versions and saved
  configuration, with Refresh and Copy System Info. Copy uses exactly the displayed
  text and confirms locally; it never transmits information. The report excludes
  source-image/custom-model paths, username and hostname. Missing libraries are
  reported explicitly. Versions are read through package metadata without loading
  model weights or querying GPU devices.
- **About**: default version 1.0, developer, scope and technology overview. Launcher,
  About and System Information share `utils.version.APP_VERSION`.

Settings pages wrap long text and retain scrolling. Guide content uses the page's
single scroll area; section navigation jumps to the chosen heading. Navigation
items wrap without requiring a horizontal scrollbar. History retains row selection,
filters, restore, deletion and Re-run, with additional width reserved for summaries.

## UI previews

Linux/Qt previews are stored under `/tmp/zy-settings-history-review/`:
`preferences.png`, `preferences-small-large-font.png`, `guide.png`,
`system-information.png`, `about.png`, and `history-summary.png`.
The history screenshot uses explicitly simulated records, not real model output.
Windows native behavior and real-weight predictions were not verified in the cloud.

## Initial settings/history validation (2026-10-17)

- Related settings/history/classification/default-model/Re-run/export regressions:
  **123 passed, 0 failed, 0 errors**.
- New tests at 150% Qt simulated scaling: **25 passed**; at 200%: **25 passed**.
  These include 620 x 400 Settings pages with 10/15/20-point fonts, navigation,
  readable tile-summary cells, copy/display equality and scoped preference resets.
- Full pytest with `--continue-on-collection-errors`: **328 passed, 1 failed,
  1 collection error**. The failure remains the missing real built-in model weight
  `models/crc_dn21_seed42_best.pth`; the collection error remains the missing script
  `models/dn21_folder_classification/train_crc_dn21 (1).py` required by
  `tests/test_train_crc_resume.py`. No tests were skipped or production placeholder
  files created to bypass these problems.

Logs: `/tmp/zy-settings-history-related.log`, `/tmp/zy-settings-history-full.log`,
`/tmp/zy-settings-history-scale150.log`, `/tmp/zy-settings-history-scale200.log`.


## Preference interaction follow-up (2026-10-17)

The original startup-only classification dropdown was confusing during a session.
It now updates the main selector immediately and persists the startup default.
Both controls stay synchronized. Programmatic mode changes from history restore
and Re-run do not overwrite the saved default; that default is shown separately.
Explicitly choosing an already displayed mode can still save it as the default.
Mode selection and classification reset are disabled during inference.

Closed Settings dropdowns forward wheel events once to their containing scroll
area instead of changing their option, including when focused. Open popup choice
and keyboard arrows continue to work. The default backend remains Pillow bilinear;
OpenCV linear remains INTER_LINEAR, with the existing recorded parameter names.

Preferences also shows all nine built-in UPerNet segmentation labels/colours from
`SEGMENTATION_LABELS` and `SEGMENTATION_COLORS`, separately from the classification
palette. It is a read-only built-in reference; custom models' result legends remain
authoritative. No model, preprocessing, class order or colour mapping was altered.

Validation:

- Related regressions: **119 passed, 0 failed, 0 errors**.
- New input/integration tests: **13 passed** at each of 150% and 200% Qt simulated
  scaling. Tests include popup/mouse/keyboard input, scrolling without selection
  changes, history/default isolation, palettes at 10/15/20-point fonts, and actual
  tiny in-memory classifier inference switching between 9 tiles and a single image.
- Full pytest: **341 passed, 1 failed, 1 collection error**. The same missing real
  model weight and missing training script described above remain unresolved.

Linux/Qt previews: `/tmp/zy-preferences-interaction-review/mode-and-resize.png`
and `/tmp/zy-preferences-interaction-review/segmentation-palette.png`.
Windows native execution has not been tested here. Logs:
`/tmp/zy-preferences-interaction-related.log`, `/tmp/zy-preferences-interaction-full.log`,
`/tmp/zy-preferences-interaction-scale150.log`, `/tmp/zy-preferences-interaction-scale200.log`.
