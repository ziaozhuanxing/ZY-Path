# ZY-Path — Project Brief

> Single source of truth for AI coding assistants (GitHub Copilot, ChatGPT).
> Distilled from the Capstone Project 1 proposal ("ZY-Path: A GUI-Based AI Histopathology Image Classification Platform").
> If this file and a chat message disagree, ask the developer which one is right. Do not guess.

---

## 0. Developer context (read first)

- The developer is a software engineering student with **very little programming experience**. They act as product owner and tester; the AI writes the code.
- Always explain what you changed in **plain Simplified Chinese**, with short sentences and no unexplained jargon. Code, comments, identifiers, commit messages and docstrings stay in **English**.
- Work in **small steps**: one module or one feature per task. Never build "the whole app" in one go.
- This is an academic capstone. The developer must be able to explain every module in a viva, so favour simple, readable code over clever code.

---

## 1. What we are building

**ZY-Path** is a standalone, **offline, no-code Windows desktop app** for histopathology (H&E image) analysis. A non-programmer (pathology student, researcher) can:

1. Load a pretrained PyTorch model (`.pt` / `.pth`) from a file dialog, or use the **built-in** model.
2. Upload an image patch and run **classification** or **segmentation** on CPU.
3. See results visually: class-probability bar chart (classification) or semi-transparent colour overlay with legend (segmentation).
4. Have every run **saved automatically** to a local SQLite history, which can be searched, filtered by date, and **re-run with one click**.
5. Export results as **PNG** or a **PDF report**.
6. Ship as a single Windows `.exe` (PyInstaller) that needs no Python and no internet.

**Built-in model:** ResNet-50 fine-tuned on NCT-CRC-HE-100K (9 colorectal tissue classes). The model file is supplied by the developer and placed in `models/` (see §12, decision D6).

**Intended use:** education and exploratory research only. Never present output as a clinical diagnosis. Show this disclaimer in the About dialog and in the PDF report footer.

### Research questions the software must let us answer
- RQ1: feasible to load PyTorch models and run classification/segmentation with no coding?
- RQ2: can results be shown intuitively (confidence bars, overlays) to non-experts?
- RQ3: do history, search/filter and one-click re-run improve usability and reproducibility?

---

## 2. Scope

### In scope
- Standalone Windows desktop app, fully offline, CPU inference only
- Image upload: PNG, JPEG, TIFF, BMP (single patches, thumbnail + full view)
- Direct loading of `.pt` / `.pth` models with strict validation (§5)
- Classification (softmax + confidence) and segmentation (per-pixel class mask, overlay)
- Result visualisation inside the main window
- SQLite history, keyword search, date-range filter, one-click re-run
- PNG and PDF export
- PyInstaller single-file packaging

### Out of scope (do NOT build, do NOT suggest)
Model training, dataset creation/annotation, cloud/web/REST, multi-user features, whole-slide image (WSI) support, Grad-CAM/explainability, clinical diagnosis features, GPU support, any network access or telemetry.

---

## 3. Tech stack (pinned — do not add or upgrade without asking)

| Library | Version | Layer | Role |
|---|---|---|---|
| Python | 3.10 | all | language |
| PyQt5 | 5.15.x | Presentation | GUI, QThread, signals/slots |
| torch | 2.1.x | Inference | model loading and forward pass |
| torchvision | 0.16.x | Inference | transforms |
| Pillow | 10.x | Inference | image I/O |
| numpy | 1.26.x | Inference | array and mask handling |
| matplotlib | 3.8.x | Presentation | bar chart (FigureCanvasQTAgg), PNG export |
| sqlite3 | stdlib | Data | history database |
| fpdf2 | 2.7.x | Data | PDF reports |
| PyInstaller | 6.x | Build | packaging |
| pytest (+ pytest-qt, pytest-cov) | latest compatible | Test | testing |

Dev environment: Windows 10/11, VS Code (Python + Pylance), Git + GitHub, a **virtual environment**, and a pinned `requirements.txt`.

---

## 4. Architecture

Strict **three-layer** architecture. Dependencies point downward only.

```
Presentation (ui/)  ──►  Inference (core/)
        │
        └──────────────►  Data (data/)
```

| Layer | Package | Classes | Responsibility |
|---|---|---|---|
| Presentation | `ui/` | MainWindow, InferencePanel, HistoryPanel, ResultPanel | user interaction, image display, results, history table |
| Inference | `core/` | InferenceEngine, ModelLoader, Preprocessor, OutputParser | load/validate model, preprocess, forward pass, parse output |
| Data | `data/` | DatabaseManager, ExportManager | SQLite CRUD, PNG/PDF export |

**Rules**
- `ui/` must **never** import `sqlite3` or `torch` directly. It calls `core/` and `data/` classes.
- `core/` and `data/` must not import widgets from `ui/`. (`InferenceEngine` is the only `core/` class allowed to import PyQt5, because it is a `QThread`.)
- Inference **always runs in a background `QThread`** so the GUI never freezes. Results come back via signals (Observer pattern).
- `MainWindow` is the mediator: it connects `InferenceEngine.result_ready` to a slot that shows the result and calls `DatabaseManager.insert_record()`.

### Suggested project layout
(Confirm against Figure 3.4 in the proposal; adjust this file if the figure differs.)

```
ZY-Path/
├─ main.py                  # entry point
├─ requirements.txt
├─ README.md
├─ PROJECT_BRIEF.md
├─ .github/copilot-instructions.md
├─ ui/
│  ├─ __init__.py
│  ├─ main_window.py
│  ├─ inference_panel.py
│  ├─ history_panel.py
│  ├─ result_panel.py
│  └─ theme.py              # colours, fonts, stylesheet constants
├─ core/
│  ├─ __init__.py
│  ├─ model_loader.py
│  ├─ preprocessor.py
│  ├─ output_parser.py
│  └─ inference_engine.py
├─ data/                    # Python package (code), NOT user data
│  ├─ __init__.py
│  ├─ database_manager.py
│  └─ export_manager.py
├─ models/                  # built-in model file lives here
├─ assets/                  # logo, icons, class_labels_nct_crc.json
├─ tests/
└─ utils/
   └─ paths.py              # resource_path(), app_data_dir()
```

---

## 5. Model constraints and validation (`core/model_loader.py`)

`ModelLoader` checks every model **before** any real inference. Failures raise a descriptive exception, and the GUI shows a plain-language dialog (no stack traces).

| Constraint | Rule | How |
|---|---|---|
| File format & size | extension `.pt` or `.pth`; size ≤ 500 MB | check extension + `os.path.getsize()` **before** loading |
| Input shape | accepts `(1, 3, H, W)`, H and W in [32, 2048] | probe forward pass with a `(1, 3, 224, 224)` dummy tensor; catch `RuntimeError` |
| Output shape | classification: `(1, C)`; segmentation: `(1, C, H, W)`; both are **logits** | after probe: `output.ndim == 2` → classification, `== 4` → segmentation; anything else is rejected |
| Loadable alone | must load without extra architecture definitions | `torch.load(path, map_location="cpu")`, then `model.eval()` |

- The detected task type (classification / segmentation) and number of classes are reported to the UI, e.g. status label: `Custom Model: Valid, Segmentation (8 classes)`.
- Error messages must tell the user what was wrong and what was expected, e.g. "This model outputs 3 dimensions; ZY-Path expects (1, C) or (1, C, H, W)."

**API**
- `ModelLoader.load(path) -> torch.nn.Module` (CPU, eval mode)
- `ModelLoader.validate(model) -> ValidationResult` (fields: `task_type`, `num_classes`, `output_shape`)

---

## 6. Preprocessing (`core/preprocessor.py`)

Same pipeline for built-in and custom models:

| Step | Parameter |
|---|---|
| Convert | image to RGB |
| Resize | 224 × 224 (default; configurable for custom models) |
| ToTensor | scale [0,255] → [0.0,1.0] |
| Normalize | mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]` |
| Unsqueeze | `(3,H,W)` → `(1,3,H,W)` |

`Preprocessor.transform(pil_image) -> torch.Tensor` of shape `(1, 3, H, W)`.

---

## 7. Output parsing (`core/output_parser.py`)

Two static methods.

**`parse_classification(output_tensor, class_labels) -> dict`**
- softmax over dim 1 → probabilities; argmax → predicted index
- returns: `label` (str), `class_index` (int), `confidence` (float 0.0–1.0), `probabilities` (list of float, same order as `class_labels`)
- UI shows confidence as a percentage, e.g. `94.7 %`.

**`parse_segmentation(output_tensor, original_size, class_colors) -> dict`**
- argmax over dim 1 → `(1, H, W)` integer mask
- resize mask to `original_size` with **nearest-neighbour** interpolation (keeps hard class borders)
- colour each class index with an RGBA colour → overlay (`PIL.Image`, RGBA)
- returns: `mask` (numpy int array), `overlay` (PIL RGBA), `classes_present` (list of ints)
- Overlay is composited on the original image at **40 % opacity**, with a colour legend.

---

## 8. Inference engine (`core/inference_engine.py`)

`InferenceEngine(QThread)` runs the whole pipeline in `run()`:

`ModelLoader.load()` → `validate()` → `Preprocessor.transform()` → `torch.no_grad()` forward pass → `OutputParser.parse_*()`

- Constructor inputs: `model_path`, `image_path`, `task_type`, optional `class_labels`.
- Signals: `result_ready(dict)` and `error_occurred(str)`.
- The result dict must contain everything needed to display and to save a history record (task type, label, confidence, probabilities or overlay, model name, image path, timestamp).
- Built-in model is loaded on app start-up (status label: `Built-in Model: Ready`).

---

## 9. Database (`data/database_manager.py`)

File: `zy_path_history.db`, stored in the **user data folder** (see §12, D8), never next to the `.exe`.

Single table **`inference_records`**:

| Column | Type | Null | Description |
|---|---|---|---|
| id | INTEGER PRIMARY KEY | no | auto-increment |
| image_path | TEXT | no | absolute path of input image |
| model_path | TEXT | no | absolute path of model used (or a built-in marker) |
| task_type | TEXT | no | `'classification'` or `'segmentation'` |
| result_label | TEXT | yes | predicted label (classification only) |
| confidence | REAL | yes | 0.0–1.0 (classification only) |
| result_image_path | TEXT | yes | path of saved result PNG |
| timestamp | TEXT | no | ISO-8601, **UTC** |

**API**
- `insert_record(...) -> int`
- `get_all_records() -> list[dict]` (newest first)
- `get_record_by_id(record_id) -> dict | None`
- `search(keyword, start=None, end=None) -> list[dict]`: `LIKE` on `image_path` and `model_path`, optional `timestamp BETWEEN start AND end`

**Rules:** schema created on first launch; **all SQL parameterised** (no string-built SQL); every DB call wrapped in try/except with friendly errors; empty results return `[]`, never crash.

---

## 10. Export (`data/export_manager.py`)

- `export_png(...)`: saves the result figure/overlay at a user-chosen path, Matplotlib `savefig(dpi=150)`.
- `export_pdf(...)`: A4 report using fpdf2 containing: (1) header with logo and title; (2) original image full width; (3) result (label + confidence bar chart, or overlay + legend); (4) metadata table (model name, task type, timestamp, file path); (5) footer with page numbers and the educational-use disclaimer. Font: Helvetica.

---

## 11. GUI design

**Window:** minimum 1366 × 768. Three persistent regions in a `QSplitter` layout.

| Region | Width | Contents |
|---|---|---|
| Left (InferencePanel) | 280 px fixed | "Use Built-in Model" checkbox, Browse Model button, model status label, Upload Image button + thumbnail, task radios (Classification default / Segmentation), **Run Inference** button (spinner while running) |
| Middle | flexible, min 500 px | Tabs: **Inference** (image viewer `QLabel`+`QPixmap`, result area with label, confidence, Matplotlib bar chart or overlay + legend) and **History** (search box, two `QDateEdit`, Search / Clear Filter, `QTableWidget`) |
| Right | 240 px fixed | Export PNG, Export PDF, session metadata (model name, image filename, timestamp), **Re-run** button |

History table columns: `ID, Timestamp, Image Filename, Model Name, Task, Result/Label, Confidence`.
Flow in the left panel is top-to-bottom: select model → upload image → choose task → run.

**Style (Table 3.5):**

| Element | Value |
|---|---|
| Primary | `#2C5282` navy (header bar, primary buttons, active tab) |
| Accent | `#3182CE` (hover, selected row, progress bar) |
| Success | `#38A169` |
| Error | `#E53E3E` |
| Background | `#F7FAFC` |
| Body text | `#1A202C` |
| UI font | Segoe UI 10 pt |
| Mono font | Consolas 9 pt (file paths, confidence numbers) |

**Accessibility:** tooltips on every control; never use colour alone (add icons: warning triangle, green check); body-text contrast ≥ 4.5:1 (WCAG 2.2 AA); progressive disclosure (advanced options hidden by default).

---

## 12. Design decisions (resolve ambiguities in the proposal)

These were inconsistent or unspecified in the proposal. Treat them as decided unless the developer says otherwise.

| ID | Decision |
|---|---|
| D1 | Table name is **`inference_records`** (the proposal also once wrote `inferred_records`; ignore that). |
| D2 | Method names are **`parse_classification`** / **`parse_segmentation`** (the proposal also abbreviated them `parse_cls` / `parse_seg`). |
| D3 | **Double-click a History row** → show that stored result in the Inference tab (UC3, no re-run). **Re-run button** (right panel, enabled when a history row is selected) → fill the InferencePanel with the record's image, model and task (UC4); the user then presses Run Inference. A re-run creates a **new** record; the original is kept. |
| D4 | If the selected task does not match the model's detected output type, show a friendly error ("This model produces classification output; please select Classification.") instead of running. |
| D5 | **Model file loading.** `torch.load` on a pickled full model works only if its Python class is importable. Proposed approach (to confirm with the supervisor): try `torch.jit.load` first (TorchScript files need no class definition), fall back to `torch.load(map_location="cpu")`. `torch.load` runs pickle code, so show a one-line warning in the UI: "Only load model files from sources you trust." |
| D6 | Built-in model path: `models/resnet50_nct_crc.pt` (rename if the real file differs). Its class-label order **must match training order**; store labels in `assets/class_labels_nct_crc.json` and have the developer confirm the order. Custom models default to labels `Class 0 … Class C-1` with an optional "name your classes" dialog. |
| D7 | Resizing is a plain resize to 224×224 (Table 3.3). No square-padding. |
| D8 | User data (history DB, saved result images, logs) lives in `%APPDATA%\ZY-Path\`, created on first run. Never write beside the `.exe` or inside the PyInstaller temp folder. |
| D9 | All bundled files (model, logo, JSON) are accessed through `utils.paths.resource_path()`, which handles both normal runs and PyInstaller (`sys._MEIPASS`). Never hard-code absolute paths. |
| D10 | Export buttons and the Re-run button live in the right column; implement that column inside `ResultPanel` so the project keeps the nine classes from the class diagram. |
| D11 | Timestamps are stored in UTC and displayed in local time. |

---

## 13. Use cases (acceptance scenarios)

**UC1 — Classify with built-in model.** Launch → status `Built-in Model: Ready` → Upload Image (filter PNG/JPEG/TIFF/BMP) → thumbnail shown → Classification selected by default → Run Inference (background thread, spinner) → bold label, `xx.x %` confidence, bar chart of 9 class probabilities → record saved, History updated → Export PDF works.

**UC2 — Segment with custom model.** Untick built-in → Browse Model (`.pt`/`.pth`) → validation runs → status `Custom Model: Valid, Segmentation (N classes)` → upload image → choose Segmentation → Run → overlay at 40 % opacity + legend (optional class-name dialog) → record saved → Export PNG works.

**UC3 — Search history.** History tab lists all records newest first → type keyword, Search → matching rows only → double-click a row → stored result and metadata shown, no re-run → Export PNG works.

**UC4 — Re-run.** Select a history row → Re-run → InferencePanel filled with image, model, task → Run Inference → new result shown, **new record** added, label and confidence **identical** to the original (deterministic reproducibility). If the original image or model file no longer exists, show a clear message.

---

## 14. Testing and acceptance targets

- **pytest** unit tests for ModelLoader (valid and invalid models), Preprocessor (several sizes/formats), OutputParser (classification and segmentation), DatabaseManager (CRUD, empty results, odd search strings), ExportManager (PNG and PDF).
- Integration tests: InferenceEngine end-to-end including error paths; signal/slot wiring (pytest-qt).
- Coverage target: **≥ 80 %** on `core/` and `data/`.
- Built-in ResNet-50: **> 94 %** accuracy on an NCT-CRC-HE-100K test subset.
- At least **3 custom PyTorch architectures** tested for compatibility.
- Usability study later: 8–10 participants, Nielsen's heuristics, SUS (benchmark 68), think-aloud interviews.
- Tests use small synthetic tensors or tiny models; they must run offline and quickly.

---

## 15. Build order and "done when"

Do the milestones **in order**. Do not start the next until the current one is verified and committed.

| # | Milestone | Done when |
|---|---|---|
| M0 | Environment | Python 3.10 venv, VS Code, Git/GitHub repo, `requirements.txt`; `python main.py` opens an empty window; `pytest` runs |
| M1 | Command-line proof | A throwaway script loads the built-in model, preprocesses one image, prints label + confidence. **Confirms the model file and label order actually work** |
| M2 | Inference core | `ModelLoader`, `Preprocessor`, `OutputParser` with passing pytest tests |
| M3 | Data layer | `DatabaseManager` and `ExportManager` with tests; PNG and PDF files open correctly |
| M4 | Early packaging test | A minimal PyInstaller `.exe` (even a bare window) runs on a machine/VM without Python. Repeat after M5, M6, M7 |
| M5 | GUI shell | MainWindow with three regions; all panels visible and clickable (no real logic yet) |
| M6 | Wire it up | `InferenceEngine` (QThread) connected to the GUI; UC1 works end to end |
| M7 | History and export | History tab, search/filter, double-click, Re-run, PNG/PDF buttons; UC2–UC4 work |
| M8 | Polish | Colour palette, tooltips, icons, error dialogs, About dialog with disclaimer |
| M9 | Final test and package | Full pytest suite and coverage report; accuracy test; final `.exe` verified on a clean Windows VM |

---

## 16. Known risks (from the proposal) to keep in mind

R1 model compatibility failures · R2 PyInstaller packaging failure (PyTorch + PyQt5 hidden imports, DLLs, large size, slow start) · R3 library incompatibilities · R4 CPU performance · R6 SQLite corruption · R7 library version drift (pin versions) · R8 low SUS score.

---

## 17. Glossary (plain language)

- **Inference** — using a trained model to make a prediction on a new image.
- **Classification** — the model gives one label for the whole image (e.g. "tumour").
- **Segmentation** — the model gives a label for every pixel (a coloured map).
- **Logits** — raw model scores before softmax turns them into probabilities.
- **Overlay** — a semi-transparent coloured mask drawn over the original image.
- **QThread / signal / slot** — Qt's way of running work in the background and sending results back to the window.
- **PyInstaller** — tool that bundles the app and Python into one `.exe`.