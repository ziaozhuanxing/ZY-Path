# Copilot Instructions — ZY-Path

ZY-Path is an offline Windows desktop app (Python 3.10, PyQt5, PyTorch, SQLite) for histopathology image classification/segmentation. **Read `PROJECT_BRIEF.md` in the repo root before doing any task.** It defines the architecture, classes, database, GUI and build order. Follow it exactly.

## Who you are working with
- The developer is **not an experienced programmer**. Explain every change in **simple Simplified Chinese**, short sentences, no unexplained jargon.
- Code, comments, docstrings, identifiers and commit messages are in **English**.
- This is a university capstone: keep code simple and readable so the developer can explain it in a viva.

## How to work
1. **One task at a time.** Do only what the current request asks. No bonus features, no "while I'm here" refactors.
2. **Only touch the files the request names.** If another file must change, say so and ask first.
3. **Do not add dependencies**, change pinned versions, or switch libraries. The stack is fixed in `PROJECT_BRIEF.md` §3.
4. **Do not invent APIs.** If you are not sure a function, parameter or library behaviour exists, say so instead of guessing.
5. **If the brief is unclear or conflicts with the request, stop and ask** a single clear question before writing code.
6. Never edit `PROJECT_BRIEF.md` or this file unless explicitly asked.
7. Never delete or weaken tests, validation checks, or error handling to make something pass.

## Architecture rules (never break)
- Three layers: `ui/` (presentation) → `core/` (inference) and `data/` (database/export). Dependencies point downward only.
- `ui/` must **not** import `sqlite3` or `torch`. `core/` and `data/` must **not** import from `ui/`. (`InferenceEngine` is the only `core/` class that may import PyQt5, because it is a `QThread`.)
- Inference **always** runs in a background `QThread`; never block the GUI thread. Send results back with signals (`result_ready`, `error_occurred`).
- Use the names, class layout, DB schema and design decisions (D1–D11) from `PROJECT_BRIEF.md`.
- **No network access, no telemetry, no cloud calls.** The app is fully offline.

## Code standards
- Python 3.10, type hints on function signatures, short docstrings on classes and public methods.
- Use `pathlib.Path`, not string path concatenation. No hard-coded absolute paths.
- Bundled files (model, logo, JSON) go through `utils.paths.resource_path()`. User data (history DB, results, logs) goes in `%APPDATA%\ZY-Path\` via `utils.paths.app_data_dir()`. Never write next to the `.exe`.
- All SQL must be **parameterised** (`?` placeholders). Never build SQL with f-strings or `+`.
- No bare `except:`. Catch specific exceptions, log details with `logging`, and show the user a **plain-language** dialog (no stack traces, no raw exception text).
- Use `print` only in throwaway scripts, never in app code.
- Avoid dynamic imports and runtime-generated code (they break PyInstaller packaging).
- Keep functions short and single-purpose. Prefer clear names over comments that restate the code.

## Testing
- Every new module in `core/` or `data/` comes with **pytest** tests in `tests/`, written in the same task.
- Tests must be offline, fast, and use tiny synthetic tensors/models and temporary directories. Do not download datasets or models in tests.
- Run the tests and report the result before saying a task is done. If you cannot run them, say so.

## What to send back after every task
Reply in simple Chinese with these parts:
1. **改了什么**: files created or changed, one line each.
2. **怎么运行**: the exact command(s) to run the code and the tests.
3. **怎么手动验证**: what the developer should click or see to confirm it works.
4. **没做的 / 需要注意**: anything incomplete, assumed, or risky.
5. **建议的 Git 提交信息** (English, one line).

## Always avoid
- Large rewrites, renaming files or classes without being asked.
- Features listed as out of scope: model training, dataset tools, cloud/web, multi-user, whole-slide images, Grad-CAM, GPU, clinical-diagnosis claims.
- Presenting results as medical diagnoses. The app is for education and research only; keep the disclaimer in the About dialog and PDF footer.