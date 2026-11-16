# Project status and evidence inventory

Reviewed on 12 November 2026. This page distinguishes implemented software,
measured model performance and deployment work still requiring execution.

## Source and branch status

The old default `main` pointed to `b73219e218f788e941f4be29a5b32fb46658a431`.
The application development snapshot is
`b4ba6346300b51aab8e6056d9cc0c1e25324bd55`, 41 commits ahead with no main-only
commits. Its application features are documented in [Architecture](ARCHITECTURE.md).
This portfolio revision changes documentation, public demonstration captures,
evaluation records and test-evidence tooling; it does not change inference or
training logic. The development snapshot is not designated a clinically validated
or clean-machine-accepted release.

Promotion to `main` must preserve ancestry and use a normal fast-forward push.
Do not rewrite history, force-push, delete older test outcomes or merge the
separate thesis branch into the application portfolio.

## Evidence boundaries

| Area | Available evidence | Remaining limit |
|---|---|---|
| Classification training | Author-run Sunway HPC/Slurm experiments; checkpoint/script hashes; external prediction records | Original HPC Git HEAD was not recorded; source identity is by script hash. |
| Classification evaluation | Verified aggregate arithmetic, per-class reports and confusion matrices for 7,180 external CRC patches | No fresh external-image inference in this repository update; no universal/clinical accuracy claim. |
| DenseNet169 | Official ImageNet weights and GPU preflight; fine-tuning in progress | No independent test score yet. |
| Segmentation | Supervisor-provided UPerNet and notebook; implemented integration | No author-training claim, independent Dice/IoU or verified training physical field. |
| Software demonstration | Four actual CPU classification/comparison/history captures with source/model identities | Offscreen Linux UI capture, not Windows acceptance; montage is explicitly artificial. |
| Native Windows regression | Dated, commit-specific records, including the later geometry-test failure | Current source needs a new native Windows collection. |
| Current Linux regression | 719 passed / 1 failed at `f96a6f7`; full log/XML retained | Genuine UPerNet file absent; not all-pass or native Windows evidence. |
| Windows release | Build script, input audit and acceptance checklist | Portable build, clean-machine/offline acceptance and formal release not established. |
| Licensing | Dependency/font inventory and source/model provenance | No root reuse licence or blanket external-model redistribution permission. |

Use [the collector](../scripts/collect_windows_evidence.py) on the development
Windows machine with genuine resources. It records exact commit, versions,
native Qt probe, unfiltered pytest log/XML, counts and unchanged source/resource
identities. See [Testing](TESTING.md) and [Windows release](WINDOWS_RELEASE.md).
Clean-machine acceptance must retain PASS / FAIL / NOT RUN outcomes from actual
execution. A public segmentation screenshot still needs a genuine, appropriately
attributed and shareable example; no substitute result is shown.

## Suggested repository About fields

Description:

> PyQt5/PyTorch histopathology research workbench with author-trained CRC classification, supervisor-provided UPerNet integration, tiled analysis, comparison, history and reports.

Topics:

`pytorch`, `pyqt5`, `computer-vision`, `medical-imaging`, `histopathology`,
`image-classification`, `image-segmentation`, `desktop-application`.

These are suggested metadata, not a statement that remote settings have already
been changed. No product/version badge should imply an accepted Windows 1.0
release. The home page should identify the problem, personal contribution,
supervisor-provided model, technology stack, evidence and limitations directly.
