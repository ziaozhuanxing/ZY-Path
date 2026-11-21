# Architecture

## Components

ZY-Path is a Python 3.10 desktop application. PyQt5 owns the interface and Qt
worker lifecycles; PyTorch performs inference; SQLite stores local history.

| Location | Responsibility |
|---|---|
| main.py | Application startup, high-DPI attributes and saved theme |
| ui/main_window.py | Connects input, result, history, model validation and export workflows |
| ui/inference_panel.py | Model/image selection, explicit classification mode and run summary |
| ui/classification_result.py | Tile view, class summaries, crop inspection and detailed tables |
| ui/segmentation_result.py | Segmentation views and pixel statistics |
| ui/zoomable_image_view.py | Full-resolution image navigation and vector annotations |
| ui/image_comparison.py | Responsive source/result comparison and linked coordinates |
| ui/settings_dialog.py | Preferences, guide, runtime information and About |
| ui/model_settings.py | Task-specific model-default validation and persistence |
| core/inference_engine.py | Background inference and validation workers |
| core/model_loader.py | Supported model loading, metadata and output validation |
| core/preprocessor.py | Profile-specific tensors and selectable classification resize backend |
| core/model_profile.py | Weight-bound declarative model input contracts |
| core/image_budget.py | Header-first raster working-memory preflight and thumbnail limit |
| ui/image_load_worker.py | Background image verification/decoding and latest-selection handling |
| data/artifact_integrity.py | Saved output checksums, verification and legacy detection |
| core/image_calibration.py | Explicit MPP metadata, image checksums and decoder-axis calibration |
| core/spatial_sampling.py | Model tissue-field to source-pixel geometry |
| core/profiled_inference.py | Configured classification and segmentation adapters |
| ui/input_configuration.py | Model profile editing and per-image MPP entry |
| core/classification_tiles.py | Classification crops, optional border coverage and unique-pixel area statistics |
| core/large_image_segmentation.py | Built-in overlapping UPerNet inference |
| core/output_parser.py | Classification probabilities and segmentation outputs |
| data/database_manager.py | Parameterized SQLite operations and artifact metadata |
| data/export_manager.py | PNG export and safe PDF destination replacement |
| data/pdf_report.py | Report layout, statistics and Unicode text |
| ui/pdf_export_worker.py | Background source verification, presentation rendering and PDF generation |
| ui/png_export_worker.py | Background verification, presentation rendering and PNG pair export |
| ui/history_load_worker.py | Latest-selection history checks and image decoding |
| ui/result_rendering.py | Widget-free rendering of immutable presentation snapshots |
| data/png_bundle.py | Staged PNG/JSON pairs, shared export identity and rollback |
| utils/paths.py | Source/frozen resources and per-user data paths |

The UI coordinates core and data operations. Core and data modules do not depend
on application widgets. Model work, history restoration and exports use workers; Qt signals
deliver status/results to main-thread receivers.

## Inference flow

The input panel supplies the actual selected model, image, task and mode.
ModelLoader returns the model and its available class/preprocessing metadata.
Validation checks the output task before inference is enabled.

Explicit input profiles provide the validation tensor boundary and class order.
Image calibration is independent. Opt-in physical matching derives source crops
from the model field and calibrated MPP. The UPerNet reference adapter retains
its supplied numerical path without an assumed physical scale. Legacy records
retain their original pipeline. New records bind calibration/profile snapshots
to input checksums; changed inputs require a new run. See [input contracts](INPUT_PROFILES.md).

Single-image classification preprocesses the whole source and parses its output.
Tiled classification loops over recorded half-open crop boxes, applies the same
chosen preprocessing to each crop, and assembles the colour map and statistics.
The built-in UPerNet state-dictionary path runs overlapping tile fusion; generic
supported segmentation models use their own forward/parser path.

Only accepted completed results are displayed and saved. Cancellation requests
are checked between safe operations; workers are not forcefully terminated.
Window closing waits for active work to finish cleanup before saving geometry.
QObject-bound callbacks and retained worker ownership protect against callbacks
to deleted widgets and premature QThread destruction.

## Result and presentation data

Prediction data includes the actual model path, task, timestamp, labels,
probabilities or mask artifacts, and available analysis parameters.
Classification analysis retains crop boxes, tile order, counts, actual pixel
areas, class colours and resize backend.

View mode, opacity, comparison, grid and numbering are presentation settings.
Changing these does not recompute predictions. Tile inspection is transient and
does not become an export annotation or a changed result statistic.
The image and foreground annotations share source coordinates. Foreground line
widths are measured in logical display pixels; display zoom accounts for device
pixel ratio.

## Local storage

DatabaseManager uses these tables:

- inference_records: source/model paths, task, result summary, result-image path
  and UTC timestamp.
- segmentation_artifacts: optional label/colour/overlay paths and analysis_json
  keyed by record ID. Despite its historical name, this table stores both
  segmentation and tiled-classification analysis metadata.

The default database is %APPDATA%/ZY-Path/zy_path_history.db. Result files live
under %APPDATA%/ZY-Path/results. UI preferences and model-default paths use
QSettings. Source images and user model files remain at their chosen locations.
Timestamps are stored in UTC and displayed/filtered in local time.

History restoration reads recorded analysis, including its task/model and
presentation. Re-run selects the recorded inputs and parameters rather than
reinterpreting a record using current preferences. SQL values are parameterized.
Deletion is limited to selected records and owned result artifacts.

Normal InferenceEngine runs call a non-widget result preparation step on the
worker before emitting result_ready. It verifies source identity, renders and
writes artifacts, records their manifest, and commits history through a fresh
SQLite connection. Cancellation before the commit rolls back newly owned files;
a completed commit wins over late cancellation. The GUI then publishes that
prepared result without decoding the same image again. All real model files are
loaded through ModelValidationThread. ImageLoadWorker emits a bounded thumbnail
and the original decoded identity; sampling never uses thumbnail dimensions.

The optional classification `cover` run policy retains complete source fields
and aligns the last crop to each image edge. `box` records the model input crop;
`area_box` is a disjoint ownership rectangle bounded by overlapping centres.
Counts, probability aggregation and colour maps use `area_box`. Model input
profiles retain their original edge policy; the explicit per-image choice is
saved in spatial_context for exact recorded reruns.

New analysis rows contain artifact_manifest with SHA-256/size/path entries for
outputs. Its metadata-sidecar digest is retained in the database only to avoid a
self-hashing cycle. Presentation changes update the database without rewriting
prediction artifacts or their recorded hashes. Legacy rows are explicitly
unverified; incompatible or changed new artifacts are rejected.

## Export and resources

PNG uses the current full-resolution result presentation. PDF takes an
independent snapshot of metadata, result pixels and the available colour map.
Widget state is captured on the GUI thread; report layout, compression, model
checksum calculation and file generation run in PdfExportWorker.

PDF generation writes a temporary file in the destination directory and replaces
the destination only after success. Failure or cooperative cancellation removes
the temporary output. The worker finishes before its owning window closes.

resource_path resolves assets/models relative to the source tree or the frozen
bundle's _MEIPASS root. User history/results never need to be written beside the
executable. The report font and SIL license are bundled resources.

Windows packaging uses a portable folder, not a single-file executable.
The build includes genuine weights and the locally cached UPerNet configuration.
Frozen model loading uses that bundled configuration; source execution retains
the existing local-cache lookup. See [Windows release](WINDOWS_RELEASE.md) for
the build gate and unexecuted clean-machine acceptance checks.


## History and export worker boundaries

HistoryLoadWorker reads the SQLite row on its own connection, verifies source
and artifact hashes, and decodes images before publishing a prepared payload.
MainWindow assigns a generation to each request and ignores obsolete completion.
Clear/delete/new input/inference completion invalidate pending history requests.
Image hashes check cancellation between chunks. Widgets and QPixmap creation
remain on the GUI thread; publication consumes prepared PIL images and a verified
source identity instead of reopening files or hashing them on the GUI thread.

PNG/PDF actions snapshot widget selections and immutable page-image references.
Metadata is copied; result-page PIL sources are not mutated by display changes.
Workers validate input artifacts, render through result_rendering and compress
outputs. Numbered exports snapshot ten digit outlines and scalar font metrics
on the GUI thread; workers draw these paths without using Qt's thread-local font
caches. No widget access occurs in worker renderers. Owned worker lifetimes and
close/cancel handling wait for cleanup without forcefully terminating threads.

PNG output staging includes image, JSON, backups and a recovery journal in the
destination filesystem. The JSON contains an image SHA-256 and a shared export
ID embedded in the PNG. Both complete staged files exist before replacement.
Normal replacement errors roll back earlier replacements; rollback failures keep
recovery copies. This is recoverable paired persistence, not a claim that two
filesystem paths can be replaced atomically against process/power loss. Cancel
is checked before commit; a completed commit wins over late cancellation.
