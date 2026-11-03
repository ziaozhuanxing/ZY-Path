# Windows startup-restore correction — 3 November 2026

## Actual uploaded Windows result

Source fbe152a5e4bbe14ad6dcc682468ad571d2efd33c completed its full 585-case native Windows execution: **584 passed, 1 failed, 0 errors, 0 skipped**, 16 warnings, pytest console 281.36 seconds, XML 281.257 seconds, exit 1. The failed identity is `tests/test_window_lifecycle_and_theme.py::test_explicit_normal_rectangle_recovers_native_maximized_geometry`. It timed out waiting for 520 × 360 after restoring a maximized startup window; the original failure output did not record the actual resulting rectangle.

The independent Qt probe reports the Windows platform, Python 3.10.22, PyTorch 2.1.2+cpu, CUDA unavailable, 24 PyTorch threads, pytest 9.1.1, PyQt5 5.15.11 and Qt 5.15.2. Before/after HEAD and clean status agree. All 94 recorded source hashes match that commit (4 exact, 90 with Windows CRLF conversion). Both real weights and the genuine training script are present with the same hashes before/after. No model-resource failure occurred in this Windows run. All 37 new model/persistence/date/workload regressions passed.

## Fix

Software commit **63ce699411b3ad1350864286b7b28902cd7d136c** changes only `ui/main_window.py`, the existing lifecycle test's failure diagnostics, and four new startup regressions. For a maximized startup with a valid explicit `window/normalGeometry`, the application applies that rectangle directly instead of replaying the binary geometry blob first. Legacy binary restoration remains available when the explicit rectangle is absent or invalid.

A deterministic late-native-geometry fixture reproduces the same lost-normal-size contract on the previous implementation: it fails before the fix. After the fix it passes, as do the three absent/invalid-rectangle legacy cases. This is a regression model of the restore-order hazard, not an observation of the Windows machine's unrecorded actual rectangle. The original native test still requires 520 × 360 in 1500 milliseconds and the same persisted size; no assertion or timeout was relaxed. If it fails again, its diagnostics now include the actual rectangle, frame, Qt normal rectangle, cached rectangle, state, screen bounds, minimum size and DPR.

Development validation ran separately on Linux/offscreen: the complete 589-case run recorded 588 passed and the unchanged real-resource failure for the absent segmentation checkpoint. The restored-window test and all four new cases passed. One initial focused offscreen invocation also exposed a transient comparison-layout assertion after a fixed 40 ms wait; the isolated invocation and the unfiltered complete run passed that test unchanged. All logs are retained in the engineering workspace. These results are not substituted for native Windows acceptance or inserted as passing Windows results in the thesis.

## One Windows verification command

The accompanying collector accepts `--check-startup-first`. It first runs the original native window-restore case and the four new regressions, retaining a separate command, log, XML and INFO geometry trace. A failed precheck stops there and explicitly reports that the full suite was not invoked. A successful precheck proceeds to the **complete, unfiltered pytest suite** with separate full-suite log/XML. Precheck cases are not added to the complete-suite count. Source/resource identities and native Qt are checked as before. No test, settings assertion, model or application file is replaced by the collector.

The thesis must retain the fbe152a failure in its dated Windows history. The manuscript's current version/result text will be consolidated only after the corrected source's actual native execution is supplied; the preceding 548-pass d9fb8e5 baseline is not relabelled.
