# Windows regression corrections

Compared application revisions: `8c4830c1281e4a85248c9a2ea9d0adae64bd4525` → `3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5`.

The saved patches are generated directly by `git diff --no-ext-diff --binary` between these commits. They contain no edits beyond the committed changes. `Windows_Regression_Fix.diff` covers all seven changed files; `Tests_Before_After.diff` covers the three test files.

## Causes in the immediately preceding Windows execution

| Cause | Failed cases | Correction |
|---|---:|---|
| Saved application preferences leaking into fixtures | 7 | Temporary application-data directory and settings stores for each test |
| Saved maximised state affecting default-window expectations | 3 | Same isolation fixture; retain production window-state implementation |
| Large-font input layout | 4 | Upload priority, scrollbar allowance and aligned tile controls |
| Short action-panel body | 1 | Shrinkable panel height and compact pinned action spacing |
| Line breaks in extracted PDF paths | 1 | Remove only carriage-return/line-feed formatting before requiring the complete path |
| Portable build-resource identifiers | 1 | Emit portable forward-slash identifiers |
| **Total** | **17** | |

Three teardown errors accompanied failing settings-related cases; they are not three additional unique test identities. Missing training-script collection and thread-lifecycle crash records belong to earlier executions, rather than to these 17 failures.

## Test isolation and production behaviour

The fixture resides in `tests/conftest.py`. Pytest applies it for each case and restores its constructor patch afterward. Default organisation/application QSettings instances are redirected to the test's temporary INI store. Explicit file-based settings remain file-based. A fresh store prevents saved real-user modes and window states from becoming hidden test preconditions. It does not force a desired inference result or modify how a normal launch stores preferences in the Windows Registry.

Two new tests verify both fresh defaults and persistence between instances within one test store. Isolation between tests and persistence within one store are distinct requirements. These checks do not by themselves replace a dedicated Registry-backend integration test.

## Assertions and test counts

No test was deleted, disabled, marked to skip or changed to accept an incorrect predicted result. The PDF assertion still requires the complete model path, including its characters, order and separators; it permits only CR/LF introduced by PDF text layout. A separate Windows-style path parameter was added. The two isolation tests and this new path parameter explain the increase from 505 distinct test identities to 508. The earlier JUnit aggregate had 508 reports because three teardown errors were additional reports for already failing cases.

The committed correction changes four production modules and three test files. Production changes concern input/action layout and build-audit path representation. Model weights, preprocessing, class labels, inference outputs and grid coordinate transforms are unchanged in this diff.

## Completed verification

The uploaded native Windows evidence for 27 October 2026 records 508 distinct cases, 508 passed, zero failures/errors/skips, 16 warnings and exit 0 at revision `3a935ef`. Source/resource identities were unchanged during execution. The pytest summary duration is 268.74 seconds, not an inference benchmark. No further execution is claimed in this editorial revision.
