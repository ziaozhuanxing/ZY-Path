# Inference cancellation and model defaults

During inference, the pinned Run button is replaced by **Cancel inference**.
Inputs remain locked. Cancellation waits for the current model operation (load,
validation, forward pass or tile) to finish; it does not terminate the thread.
**Cancelling…** remains visible until cleanup completes. Cancelled results do not
create history rows or result files. The previous completed result stays available
for viewing and export, including when cancelling a history Re-run.

Closing the main window during inference requests cancellation and waits without
blocking the interface. Model validation also finishes before the window closes.

In **Settings > Models**, Classification and Segmentation each have their own
local default path. Choose a trusted supported `.pt` or `.pth` model, then select
**Validate and use as default**. Validation runs in the background and must detect
the matching output task before the preference is saved. Model files can contain
executable code. No weights are copied or overwritten.

Saved defaults apply at startup and when selecting the corresponding task. Manual
model selection remains available for the current session. A missing saved file
blocks inference and asks the user to reselect it or restore the built-in default;
it never silently falls back. **Restore built-in default** resets only that task's
model preference. Built-in weights must still be installed at their existing paths.
Tile settings, theme and history are preserved.

History Re-run uses the record's model path, task, classification mode and analysis
parameters, regardless of current defaults. Large recorded models validate in the
background before Re-run continues. Model preference controls are unavailable while
inference or model validation is active.

This change does not alter preprocessing, resize methods, model outputs, labels,
colors, segmentation pixel statistics, grid transforms or linked comparison logic.
Linux Qt tests use tiny temporary test models; real production weights and Windows
native execution require separate validation on the user's machine.

## Cloud validation (2026-10-17)

Final related regressions: **127 passed, 0 failed, 0 errors**, including 28 new
lightweight cases for cancellation, defaults and recorded-model Re-run. These
also cover original grid, linked image comparison, result layouts and window
lifecycle behavior.

Final full pytest (`--continue-on-collection-errors`): **303 passed, 1 failed,
1 collection error**. The two existing missing-file problems remain:

- Missing real built-in weight `models/crc_dn21_seed42_best.pth` fails
  `test_default_builtin_paths_keep_real_classification_and_segmentation_models`.
- Missing `models/dn21_folder_classification/train_crc_dn21 (1).py` prevents
  collecting `tests/test_train_crc_resume.py`.

The small-window test for the Models scroll area and pinned Cancel control passed
at both `QT_SCALE_FACTOR=1.5` and `2` (one test per scale).

An additional 150% offscreen run of window/theme/grid tests plus that new test
reported **20 passed, 8 failed**. All eight failing cases can also be reproduced
against unchanged commit `206b51f`: the baseline suite had 20 passes and 7 failures,
and the remaining timed resize case failed when run separately. The virtual screen
is only 533 x 400 logical pixels, below hard-coded test resize expectations. Six
rendering assertions sample physical QImage pixels using logical widget positions
without a DPR conversion. No application geometry, theme, grid or those existing
tests were changed to bypass these failures. This additional run is not a claim
that every high-DPI regression passes, or that Windows native controls were tested.

Linux/Qt UI previews (no real model running):

- `/tmp/zy-cancel-defaults-review/cancel-controls.png`
- `/tmp/zy-cancel-defaults-review/models-settings.png`

Logs: `/tmp/feature-verified-related.log`, `/tmp/feature-complete.log`,
`/tmp/feature-scale150.log`, `/tmp/feature-scale150-baseline.log`,
`/tmp/feature-scale150-baseline-resize.log`, `/tmp/feature-scale200.log`.
