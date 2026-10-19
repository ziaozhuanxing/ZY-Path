# ZY-Path CP2 thesis materials

## Windows layout correction and native-platform validation — 19 October 2026

- [Download the guarded one-file correction and validation tools](windows-layout-fix-2026-10-19/Windows_Window_Fix.zip)
- [Diagnostic findings and actual regression results (Chinese)](windows-layout-fix-2026-10-19/核对结论与修改说明.md)
- [Review the minimal source diff](windows-layout-fix-2026-10-19/Windows_Window_Fix/inference_panel_width.patch)

The submitted Windows diagnostics confirm a minimum-width calculation that omits existing outer padding. The correction only includes that padding in ui/inference_panel.py. Application code changes remain **uncommitted and unpushed on the software branch**; this documents-only publication distributes a checksum-guarded patch artifact and its original-file backup installer.

After correction, Linux/offscreen Qt recorded **59 related tests passed**; the unselected full suite recorded **358 passed, 1 failed, 0 collection errors**, 14 warnings, 98.51 seconds. The remaining Linux failure requires an unavailable real segmentation weight. Three installer safety checks passed. No tests, assertions, model settings or predictions were changed.

In the supplied Windows record, history double-click passed under the native windows Qt plugin and failed under offscreen. The minimum-layout test failed under both. The rerun module and full suite terminated with 0xC0000409 under offscreen at the same test, without a fatal stack. That crash is **not yet diagnosed or resolved**. The tools support explicit --qt-platform windows so the next native run retains every assertion and records the actual plugin; no passing Windows full-suite outcome is claimed.

Use the existing project Python to apply_window_width_fix.py, then run diagnose_windows_tests.py --qt-platform windows. The installer preserves LF/CRLF, backs up the original file, refuses different existing source and is idempotent. Upload the new diagnose folder; the successful 7K evaluation need not be repeated. The thesis below retains the incomplete Windows result until actual retesting.

---

## Latest Windows evidence update — 19 October 2026

- [Editable Word thesis](windows-evidence-update-2026-10-19/LiZiYao_24018160_CP2_Thesis_Windows_Evidence.docx)
- [PDF review copy — 98 pages](windows-evidence-update-2026-10-19/LiZiYao_24018160_CP2_Thesis_Windows_Evidence.pdf)
- [Complete evidence-update package](windows-evidence-update-2026-10-19/LiZiYao_24018160_CP2_Windows_Evidence_Package.zip)
- [Windows failure/crash diagnostics](windows-evidence-update-2026-10-19/Windows_Diagnostics.zip)
- [Evidence findings and next step (Chinese)](windows-evidence-update-2026-10-19/本轮证据与诊断说明.md)
- [Detailed before/after change log](windows-evidence-update-2026-10-19/Windows_Evidence_Changes.md)

The default-Pillow Single image core completed 7,180 CRC-VAL-HE-7K predictions on Windows CPU: **6,511 correct, 90.682451% accuracy, 88.587944% macro-F1**. The uploaded CSVs independently reproduce all class metrics and confusion counts. All 7,180 predicted labels agree with the original evaluation; probability vectors differ by up to 0.002732. Every source patch was already 224×224, so this does not establish resizing equivalence for larger source crops or tiled-map accuracy.

The Windows software-test rerun collected **359 items**, resolving the missing training-script collection prerequisite. It then showed at least two failures and terminated abnormally with **0xC0000409**, without a final summary or XML report. Final pass/fail totals and the specific crash cause are not available. The previous Linux full run remains a distinct **358 passed / 1 failed / 0 collection errors** record.

The diagnostics ZIP runs three independent diagnostic subsets followed by the unselected full suite, preserving immediate failure text, the last test and observed Qt platform/geometry without changing application source, assertions, model weights or default preprocessing. Two Linux process-level tool checks and 13 relevant original Linux Qt tests passed; actual Windows diagnostic execution is still needed. The 7K evaluation does not need repeating.

This is a content review draft retaining the supervisor chapter framework and existing Word styles. UAT, seven screenshot groups, cover semester/submission date, segmentation accuracy, formal timing and clean-machine packaging remain incomplete. Original model weights and supervisor source files are not redistributed. Earlier drafts remain below for comparison.

---

## Previous refinement — 19 October 2026

- [Editable Word thesis](refinement-2026-10-19/LiZiYao_24018160_CP2_Thesis_Refined.docx)
- [PDF review copy — 98 pages](refinement-2026-10-19/LiZiYao_24018160_CP2_Thesis_Refined.pdf)
- [Complete refinement package](refinement-2026-10-19/LiZiYao_24018160_CP2_Refinement_Package.zip)
- [Windows verification tools](refinement-2026-10-19/ZY_Path_Windows_Tools.zip)
- [Read first (Chinese)](refinement-2026-10-19/README_先读.md)
- [Detailed before/after change log](refinement-2026-10-19/Refinement_Changes.md)

This content review draft retains the supervisor's chapter framework and existing Word styles. Classifier training and evaluation are separated from software testing in Section 4.2.6; limitations are consolidated into six paragraphs. The standard NCT-CRC-HE-100K.zip training archive is confirmed. The recorded 90.68% accuracy and 88.59% macro-F1 belong to the OpenCV/Albumentations evaluation, not an already measured application-default Pillow run.

**Executed software tests:** Linux/offscreen Qt, 19 October: **358 passed, 1 failed, 0 collection errors**, 14 warnings, 104.68 seconds, exit 1. Genuine classification resources resolved the training-script collection prerequisite. The remaining failure requires the unavailable real segmentation weight. The initial read-only-APPDATA attempt is retained separately. Seven lightweight standalone-tool checks passed; these are separate from the application suite.

**Windows:** the 19 October supplied invocation remains interrupted during collection, with 1 error and no obtained passing count. Native retest and default-Pillow 7,180-image evaluation tools are ready but have not been executed here. Their actual Windows results must be returned before those claims are updated. Application defaults, source code and tests are unchanged.

UAT, seven screenshot groups and cover semester/submission date remain reserved. Segmentation predictive evaluation, repeated runtime measurements and clean-machine/offline packaging validation remain unverified. No model weights or complete supervisor source files are redistributed. The original and previous drafts below remain available for comparison.

Download a file using **Download raw file**, or select **Code → Download ZIP** on this documents-only branch. For the two Windows checks, download the small tools ZIP and read its Chinese instructions.

---

## Previous content review revision — 19 October 2026

- [Editable Word content revision](content-revision-2026-10-19/LiZiYao_24018160_CP2_Thesis_Content_Revision.docx)
- [PDF content review copy](content-revision-2026-10-19/LiZiYao_24018160_CP2_Thesis_Content_Revision.pdf)
- [Complete revised package](content-revision-2026-10-19/LiZiYao_24018160_CP2_Content_Revision_Package.zip)
- [Read first (Chinese)](content-revision-2026-10-19/README_本轮先读.md)
- [Detailed before/after change log](content-revision-2026-10-19/Content_Changes.md)

The revised PDF has 98 pages. This is a content review draft using the existing document styles; final formatting follows content approval. It incorporates genuine classification training/evaluation materials and the 19 October Windows logs. The latest Windows pytest invocation stopped during collection with 1 error, 13 warnings, exit code 2 and no obtained pass count; the historical Linux results are retained separately. No new application pytest run was performed during document editing.

UAT, seven screenshot groups and cover semester/submission date remain reserved. Segmentation accuracy, repeated runtime measurements and clean-machine/offline package validation are explicitly unverified. Windows sharing logs redact only the local username and hostname, with both original and sharing checksums recorded. No model weights or supervisor source code are redistributed in the revised package.

To download everything, select **Code → Download ZIP**, or open the complete revised package and choose **Download raw file**. The application branch remains unchanged; this documents-only branch is not a software update.

## Original 17 October draft (retained for comparison)


This independent documents-only branch contains the CP2 thesis and evaluation materials. It does not change the application branch or `main`.

## Downloads

- [Editable Word thesis](LiZiYao_24018160_CP2_Thesis.docx)
- [PDF review copy](LiZiYao_24018160_CP2_Thesis.pdf)
- [Complete package: thesis, questionnaire, scoring workbook, diagrams, evidence and revision notes](LiZiYao_24018160_CP2_Package.zip)
- [SHA-256 checksums](SHA256SUMS.txt)

Open a file and use **Download raw file**, or choose **Code → Download ZIP** on this branch to download everything. No Python or Git installation is required to read these documents.

## Document status

These are review drafts based on application commit `1f3e01e7866d1b1f78103d817214f7dbb1cc5a56`. The thesis is 89 pages. Actual UAT responses and independent model evaluation results have not yet been supplied; the package includes blank evaluation materials and clearly marked pending evidence. Cover date/semester and the listed screenshots also require confirmation or completion.

The recorded application test result is **355 passed, 1 failed, 1 collection error**. The two known missing-file issues are preserved: unavailable real model weights and the missing `models/dn21_folder_classification/train_crc_dn21 (1).py` training script. This document publication does not constitute a new test run.

## 中文说明

本分支仅用于下载论文资料，不是软件更新分支。点击上方完整资料包链接后，选择 Download raw file；也可以在此分支页面选择 Code → Download ZIP。解压完整资料包后，请先阅读 `README_先读我.md`、修订说明及补图与待补证据清单。UAT 和独立模型评估尚无实际结果，未编造实验数据。