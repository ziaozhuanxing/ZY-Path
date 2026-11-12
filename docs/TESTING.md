# Testing and validation

## Full suite

Software tests establish implementation behaviour, not model accuracy. This
repository does not claim that its current source has passed native Windows
regression or packaged-release acceptance without a matching execution record.

Run from the repository root with the project Python environment:

```powershell
& .\.venv\Scripts\python.exe -m pytest -ra --tb=long --color=no --junitxml=pytest-results.xml
```

This runs the unfiltered suite. A collection error, failed assertion or abnormal
process exit must remain part of the reported outcome. Unit and Qt integration
tests use synthetic fixtures where appropriate; those fixtures are not model
evaluation results.

Real-resource prerequisites include:

- models/crc_dn21_seed42_best.pth
- models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth
- models/dn21_folder_classification/train_crc_dn21 (1).py

The genuine training script is read during collection of
tests/test_train_crc_resume.py to extract and exercise its resume helpers.
A missing script can stop collection before tests execute. Restore the genuine
resource rather than substituting a stub or changing an assertion.

## Focused checks

The following selection covers tile inspection, run summaries, background
export, metadata, image navigation and window lifecycle:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q tests/test_tile_inspection_and_run_summary.py tests/test_background_pdf_export.py tests/test_classification_tiles.py tests/test_classification_results_layout.py tests/test_segmentation_results_layout.py tests/test_linked_image_comparison.py tests/test_screen_fit_and_tile_grid.py tests/test_window_lifecycle_and_theme.py tests/test_main_window_export.py tests/test_pdf_report_layout.py tests/test_worker_lifetime.py
```

Tests also cover model loading/preprocessing, output parsing, database operations,
history and recorded rerun, cancellation, task defaults, preference controls,
themes, Unicode report text, actual crop-area statistics, high-DPI transforms,
English calendars and packaging input checks.

## Linux Qt execution

For a headless Linux development environment, set a writable application/cache
location and use the Qt offscreen plugin:

```bash
APPDATA=/tmp/zy-path-tests QT_QPA_PLATFORM=offscreen MPLCONFIGDIR=/tmp/zy-path-mpl .venv/bin/python -m pytest -ra --tb=short --color=no
```

For native Windows acceptance, run the application with the Windows platform
plugin. Linux offscreen/X11 checks or simulated scaling do not establish that
Windows title-bar buttons, display drivers or mixed-DPI monitors work correctly.
The [Windows checklist](WINDOWS_RELEASE.md#acceptance-record) separates these
manual checks from automated tests.

## Archived native Windows records

The supplied Windows evidence ZIPs contain exact source identities, native Qt
probes, dependency output and unfiltered pytest logs/XML. Source and model
resources were unchanged during these runs. Public, path-minimised summaries
are in [windows-archived-summary.json](verification/windows-archived-summary.json).

| Date | Exact source revision | Passed | Failed | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| 2 November 2026 | `d9fb8e5e4ef43214ed140a0b3c81d18dd4fc7592` | 548 | 0 | 0 | 0 |
| 3 November 2026 | `fbe152a5e4bbe14ad6dcc682468ad571d2efd33c` | 584 | 1 | 0 | 0 |

Both used Python 3.10.22, PyTorch 2.1.2, PyQt5 5.15.11, pytest 9.1.1 and the
native `windows` Qt platform. The later failure was
`test_explicit_normal_rectangle_recovers_native_maximized_geometry`: a 1,500 ms
wait timed out. Commit `63ce699` subsequently changed normal-rectangle restoration,
but that change is not represented as a passing native rerun. Additional input
profile/calibration work followed. Neither archived result is relabelled as a
test of the current application revision.

For the current Windows source, with genuine resources installed and a clean
checkout, use:

```powershell
& .\.venv\Scripts\python.exe scripts\collect_windows_evidence.py
```

The collector records HEAD, versions, exact pytest command, native Qt probe,
source/resource checksums, actual counts, full log and XML in a ZIP outside
the checkout. It neither filters tests nor uploads anything. An optional
`--expected-commit <full-SHA>` stops collection on a different revision.
Keep failures, collection errors and process exits; review private paths
before sharing. This is a source regression run, separate from the packaged
[clean-machine acceptance](WINDOWS_RELEASE.md).

## Current Linux execution

On 12 November 2026, the complete unfiltered 720-case suite ran at
`f96a6f79a7bfce7cdc1d8a101c5a0be779c1d7be`, using Python 3.10.22,
PyTorch 2.1.2+cpu, PyQt5 5.15.11, pytest 9.1.1 and Qt offscreen:
**719 passed, 1 failed, 0 errors, 0 skipped** (149.39 seconds wall time).

The failure is
`test_default_builtin_paths_keep_real_classification_and_segmentation_models`:
the genuine built-in UPerNet file is absent in that environment. It was not
replaced by a stub, skipped or relabelled as passing. This portfolio change
leaves application inference and all existing tests byte-identical to `b4ba634`.
The evidence publication following `f96a6f7` changes documentation/records only.

See the [exact summary](verification/linux-20261112/summary.json),
[full log](verification/linux-20261112/pytest-full.log) and
[JUnit XML](verification/linux-20261112/pytest.xml). The record identifies the
execution commit; a later documentation-only commit is not claimed as a new
test execution. No current native Windows or packaged acceptance is inferred.

## Historical Linux software baseline

On 23 October 2026, revision 9793ba80ed1c5a71ada1e47fdb9f2ebf49a09398
was tested with Python 3.10.22, pytest 9.1.1, PyQt5 5.15.11 and the Linux
offscreen Qt plugin.

| Invocation | Passed | Failed | Errors | Skipped | Duration |
|---|---:|---:|---:|---:|---:|
| Related 142-case selection | 142 | 0 | 0 | 0 | 75.03 s |
| Full 422-case suite | 421 | 1 | 0 | 0 | 126.63 s |
| Full suite after documentation/tool cleanup, same application and tests | 421 | 1 | 0 | 0 | 141.10 s |

The full-suite failure checks the actual built-in segmentation file:
models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth was absent in that
installation. The classification resource and genuine training script were
present, so that run had no training-script collection error. It was not an
all-pass result. The elapsed pytest time is not inference performance.

The cleanup recheck used Python's no-bytecode option and pytest's disabled
cache provider so generated cache files could be removed without recreating
them. All 422 cases were still collected and executed. Application source,
tests and assertions were byte-identical to the software baseline.

Earlier execution notes and test outcomes remain recoverable from their source
revisions. Results from different dates, platforms or source states should not
be combined into a single passing count.

## Model and deployment evaluation

Automated layout, crop/tensor consistency and synthetic-model tests do not
measure predictive accuracy. Classification evaluation requires genuine weights,
a defined dataset and the actual selected preprocessing pipeline. Segmentation
accuracy additionally requires suitable reference masks and an evaluation
protocol.

Systematic timing, UAT and clean-machine packaging acceptance are separate
activities. Record hardware, runtime versions, image dimensions, task/mode,
parameters, source revision and actual outcomes for each. An unexecuted check
remains unexecuted.

The Windows build script gates packaging on resources and a successful complete
pytest invocation. See [Windows release](WINDOWS_RELEASE.md) for commands and
release evidence requirements.
