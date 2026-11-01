# ZY-Path

ZY-Path 1.0 is a local desktop application for histopathology image
classification, segmentation, result comparison, history and report export.
The interface uses PyQt5 and inference runs on CPU with PyTorch.

For education and exploratory research only. Not a clinical diagnosis.

## Features

- Single-image classification and explicit Tiled analysis.
- Configurable source tile dimensions, nine-class colour maps, crop inspection,
  numbered tiles and actual crop-area statistics.
- Segmentation overlays, separate class maps and pixel-coverage summaries.
- Original/result comparison with linked source coordinates, Fit, zoom and pan.
- Local SQLite history, search, date filters and recorded-parameter rerun.
- Cooperative inference cancellation and separate per-task model defaults.
- PNG export and background PDF generation with progress, cancellation,
  Unicode filenames and configurable report details.
- Resizable panels, scrolling settings, Light/Dark themes and display-scale
  handling.

## Run from source on Windows

Use 64-bit Python 3.10 on Windows 10/11. From the repository root in PowerShell:

```powershell
py -3.10 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe main.py
```

If the environment already exists, use its Python instead of recreating it.
Dependency installation requires access to the appropriate package sources.

Built-in weights are separate from this source repository. Place the genuine
files at:

```text
models/
  crc_dn21_seed42_best.pth
  UPerNet_TME_tissue-panoptils_best_model_100ep.pth
```

The built-in segmentation path also needs its locally available UPerNet
configuration. Missing resources are reported in the application; do not
substitute random weights. A compatible trusted custom model can be selected
through Browse Model or Settings > Models.

See [models and preprocessing](docs/MODELS.md) for loading constraints,
configuration requirements, dataset information and separate class palettes.

## First analysis

Select a task and validated model, upload an image, check the run summary,
then choose Run Inference.

For classification, Single image processes the complete image; Tiled analysis
uses the configured source crop dimensions. The editable starting value is
512 x 512 source pixels, while the built-in classifier's network input is
224 x 224. Physical-scale matching for an uploaded image is not verified.

The default classification resize backend remains Pillow bilinear. OpenCV
linear is an explicit alternative. Changing a backend or source tile size can
change model inputs and predictions.

The [user guide](docs/USER_GUIDE.md) covers crop inspection, comparisons,
statistics, history, cancellation, model defaults and report export.

## Tests

```powershell
& .\.venv\Scripts\python.exe -m pytest -ra --tb=short --color=no
```

Full testing needs the genuine built-in resources and the training script at
`models/dn21_folder_classification/train_crc_dn21 (1).py`.
Missing resources must be reported as failures/errors, not passing tests.
See [testing](docs/TESTING.md) for prerequisites, focused commands and recorded
results.

## Documentation

| Document | Contents |
|---|---|
| [User guide](docs/USER_GUIDE.md) | Analysis workflows and result interpretation |
| [Models](docs/MODELS.md) | Compatibility, preprocessing, scale and palettes |
| [Architecture](docs/ARCHITECTURE.md) | Components, workers, persistence and resources |
| [Testing](docs/TESTING.md) | Automated checks and validation limits |
| [Windows release](docs/WINDOWS_RELEASE.md) | Build commands and clean-machine checklist |

The Windows portable-folder build tooling is prepared. A successful native
build, fresh-machine launch and offline acceptance still require execution
and their own recorded results.

## Data and contact

History and saved results use `%APPDATA%/ZY-Path`; preferences use QSettings.
Original images and model files remain at their selected locations.
Diagnostic logs are kept in `%APPDATA%/ZY-Path/logs/zy-path.log`, including
windowed EXE runs without a console. Logs rotate automatically and may contain
local image/model paths; review them before sharing.

The bundled report font is distributed under the SIL Open Font License;
see [font attribution](assets/fonts/README.md) and its included license.

Developer: Li Zi Yao

Email: ziyao604502@gmail.com

Telephone: +601123612318
