# Windows portable release and acceptance

Status: build tooling prepared; a completed Windows build and clean-machine
acceptance must be recorded separately. Automated Qt tests on Linux do not
verify native Windows controls or a packaged executable.

## Build on the development Windows machine

Use Windows 10/11, 64-bit Python 3.10 and a committed, clean source revision.
Keep the genuine models at:

- `models/crc_dn21_seed42_best.pth`
- `models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth`

Full tests additionally require the genuine training script at
`models/dn21_folder_classification/train_crc_dn21 (1).py`. The verified
`openmmlab/upernet-swin-base/config.json` must already be in the local Hugging Face
cache from segmentation setup. No model or config is downloaded by the build.
The complete existing config is bundled unchanged; the frozen application
reads that config without requiring a separate per-user Hugging Face cache.

```powershell
cd E:\ZY-PATH
& .\.venv\Scripts\python.exe -m pip install -r requirements-windows-build.txt
& .\.venv\Scripts\python.exe scripts\build_windows.py --check-only
& .\.venv\Scripts\python.exe scripts\build_windows.py
```

The build stops on missing inputs or any failure/error in the full pytest run.
It saves the exact source revision, dependency versions, model/config hashes,
pytest log and XML under `build/windows-inputs`. That folder is release evidence,
not runtime data. Keep it with the release.

The output is a portable **folder**, `dist/ZY-Path`, containing `ZY-Path.exe`
and `_internal`. Distribute the entire folder, not the EXE alone. Do not put a
new build over an old build; retain earlier release/evidence folders separately.
This tooling does not produce an installer or establish acceptance by itself.

## Install and launch on a clean Windows machine

1. Copy/extract the complete release to a writable folder.
2. Use a fresh Windows user profile with no Python, project source, model cache
   or development virtual environment. Record Windows build, CPU, RAM and
   display scale. Disconnect networking before the offline checks.
3. Run `ZY-Path.exe`. The bundled runtime should start without Python installed.
   The application uses per-user `%APPDATA%/ZY-Path` for history/results and
   QSettings for preferences. Resources in the release folder are not history.
4. Keep screenshots, exported files, exact error messages and the bundled
   `_internal/build-manifest.json`. Record actual outcomes below.

## Acceptance record

Use PASS / FAIL / NOT RUN; do not fill PASS without execution.
Test date, tester, source revision and release archive SHA-256: **pending**.

| Check | Expected behaviour | Actual outcome / evidence |
|---|---|---|
| Fresh offline startup | Opens without Python or a Hugging Face cache | NOT RUN |
| Normal/maximize/restore/minimize | Native Windows states and repeated resizing work | NOT RUN |
| 100%, 150%, 200% display scale | Controls accessible; no clipped critical buttons | NOT RUN |
| Small/split-screen window | Panel scrolling and original comparison adapt in both directions | NOT RUN |
| Unicode source path | A Chinese-named image loads and exports legible PDF text | NOT RUN |
| Single image | Genuine classification model runs; one result is recorded | NOT RUN |
| Tiled analysis | Configured width/height, planned count and actual edge crops agree | NOT RUN |
| Tile inspection | Image click and tile row identify the same original crop; dragging pans | NOT RUN |
| Segmentation offline | Genuine model loads with bundled config and produces a result | NOT RUN |
| Cancel inference | Waits safely for operation; no partial history result | NOT RUN |
| Linked comparison | Image/grid/number/highlight remain aligned through Fit/zoom/resize | NOT RUN |
| Recorded rerun | History reuses its recorded model/task/mode/parameters | NOT RUN |
| Task defaults | Trusted compatible custom defaults persist; restore built-in works | NOT RUN |
| PNG/PDF | Saved images, labels, colours and statistics match the selected record | NOT RUN |
| PDF cancellation/failure | Existing destination survives; no incomplete file remains | NOT RUN |
| Export during long report | Progress updates; Cancel and window close clean up safely | NOT RUN |
| Offline PDF | Bundled Chinese font works; Open PDF/Open folder use Windows defaults | NOT RUN |
| Restart | History/preferences persist in the same Windows profile | NOT RUN |
| Update | Close old app, extract new folder separately; history remains accessible | NOT RUN |

## Updating

Close the application, preserve the previous release and back up
`%APPDATA%/ZY-Path` before changing versions. Extract the new complete release
into a separate directory and run it using the same Windows account.
Do not overwrite individual production modules or copy only the new EXE.
Recheck startup, history restore and one export. A release manifest identifies
what was built; the acceptance record identifies what was actually tested.
