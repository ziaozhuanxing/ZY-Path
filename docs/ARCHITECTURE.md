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
| core/classification_tiles.py | Non-overlapping classification crops and area-weighted statistics |
| core/large_image_segmentation.py | Built-in overlapping UPerNet inference |
| core/output_parser.py | Classification probabilities and segmentation outputs |
| data/database_manager.py | Parameterized SQLite operations and artifact metadata |
| data/export_manager.py | PNG export and safe PDF destination replacement |
| data/pdf_report.py | Report layout, statistics and Unicode text |
| ui/pdf_export_worker.py | Background PDF generation with cooperative cancellation |
| utils/paths.py | Source/frozen resources and per-user data paths |

The UI coordinates core and data operations. Core and data modules do not depend
on application widgets. Model work and PDF generation use workers; Qt signals
deliver status/results to main-thread receivers.

## Inference flow

The input panel supplies the actual selected model, image, task and mode.
ModelLoader returns the model and its available class/preprocessing metadata.
Validation checks the output task before inference is enabled.

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
