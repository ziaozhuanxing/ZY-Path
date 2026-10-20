# ZY-Path CP2 thesis materials

## Latest: figure, table and citation review — 20 October 2026

- [Download editable Word thesis](figure-citation-review-2026-10-20/LiZiYao_24018160_CP2_Thesis_Cross_Referenced.docx)
- [Download PDF review copy — 101 pages](figure-citation-review-2026-10-20/LiZiYao_24018160_CP2_Thesis_Cross_Referenced.pdf)
- [Download complete package](figure-citation-review-2026-10-20/LiZiYao_24018160_CP2_Cross_Referenced_Package.zip)
- [Every reference and its citation locations](figure-citation-review-2026-10-20/Citation_Locations.md)
- [32-reference location summary CSV](figure-citation-review-2026-10-20/Reference_Location_Summary.csv)
- [All figure/table prose mentions and locations](figure-citation-review-2026-10-20/Figure_Table_Locations.md)
- [CP1 citation-format comparison](figure-citation-review-2026-10-20/CP1_Citation_Format_Comparison.md)
- [Before/after changes](figure-citation-review-2026-10-20/Content_Changes.md)
- [Revision summary in Chinese](figure-citation-review-2026-10-20/本轮修改说明.md)

Every one of the **20 figures and 24 tables** now has an explicit numbered mention in the relevant prose, independently of captions and contents entries. Reserved screenshots and UAT tables remain described as pending evidence. All existing illustration files and measured model results are unchanged.

The reference list follows the CP1 author–year prose citations, five reference categories, sequential [1]–[32] numbering, author/year punctuation and italicised journal/proceedings/book/resource titles. Corrected CP2 publication metadata is retained. The location files identify **32 references and 53 citation occurrences**, with section, paragraph, PDF page, printed page and the actual passage. All references have prose citations and all detected parenthetical citations are mapped.

Table C.2's source note is below the table. Both C.1 and C.2 retain their source note with the final row; the final PDF confirms this on pages **97 and 98** (printed 87 and 88). The manuscript software-test history now reports Windows invocations only. Original Linux logs remain separately archived; failures were not converted into passes. Linux development-image captions retain their actual platform labels.

The final native Windows result remains **370 passed / 0 failed / 0 errors / 0 skipped**, 15 warnings, **194.10 seconds**. No software file was changed and no new pytest run was executed in this manuscript revision. The software remains commit **7bd3552765af9d318a02bccd3e2469b95155dbe3**, with the existing tag **cp2-windows-verified-2026-10-19**. No software-branch push, force push or merge to main was made for this document update.

The original Word styles, numbering, theme and page settings are retained; the existing Emphasis character style supplies the reference-title italics. **172 page references** are checked and stable. Seven screenshot groups, 20 UAT results and two cover fields remain pending, as do the previously stated segmentation, performance and deployment evaluations. The complete package includes **77 before/after entries** and the blank evaluation instruments.

---

## Earlier drafts — use the latest links above

The following sections retain the previous deliveries and their original version descriptions. They are superseded by the current figure/citation review.

## Latest content revision — 20 October 2026

- [Download editable Word thesis](revised-thesis-2026-10-20/LiZiYao_24018160_CP2_Thesis_Revised.docx)
- [Download PDF review copy — 99 pages](revised-thesis-2026-10-20/LiZiYao_24018160_CP2_Thesis_Revised.pdf)
- [Download complete package](revised-thesis-2026-10-20/LiZiYao_24018160_CP2_Revised_Package.zip)
- [Revision summary in Chinese](revised-thesis-2026-10-20/本轮修改说明.md)
- [Before/after content changes](revised-thesis-2026-10-20/Content_Changes.md)
- [Remaining screenshot and evidence guide](revised-thesis-2026-10-20/补图与待补证据清单.md)

The tested application source is now committed as **7bd3552765af9d318a02bccd3e2469b95155dbe3**, tagged **cp2-windows-verified-2026-10-19**, on `codex-ready-2026-10-15`. The software commit and annotated tag were pushed normally. The repaired files match the 19 October Windows source record after line-ending normalisation; all 65 application/test Python files were unchanged during this revision. The commit was created after testing, and original test logs retain their original identifiers. No new pytest invocation is claimed.

The main results table now presents the final native Windows result: **370 passed, 0 failed, 0 errors, 0 skipped**, 15 warnings, **194.10 seconds**, exit 0. All six dated execution records, including earlier interrupted runs and the Linux missing-segmentation-weight failure, remain in Appendix C. The preceding 131-test subset is not added to the full-suite count.

The dataset discussion distinguishes the external CRC-VAL-HE-7K cohort of 50 patients, documented as having no patient overlap with NCT-CRC-HE-100K, from the project's patch-level internal training/validation split. The author supplied official Zenodo excerpts and citation metadata checked on 20 October: published 7 April 2018, v0.1, DOI 10.5281/zenodo.1214456; both datasets have nominal 224×224 patches at 0.5 μm/pixel. Standard 100K stain normalisation is distinguished from NONORM and from numerical input scaling. The validation–test gap is not assigned a proven single cause. Default-Pillow external-patch results remain **90.68% accuracy / 88.59% macro-F1**.

The revision contains 35 before/after content entries, retains the supervisor chapter framework and original Word styles, and has 167 checked page-reference fields. Seven screenshot groups, 20 UAT entries and two cover fields remain pending. Segmentation accuracy, systematic performance measurement and clean-machine packaging retain their actual evidence limits. This is a content review copy; a separate formatting revision can follow content approval.

Only thesis materials are published on this documents branch. The software branch remains separate; no force push or merge to main was made.

---

## Earlier drafts — superseded by the links above

The following sections retain earlier delivery descriptions and their original version references. Use the current links above for the latest thesis and source identity.

## Latest thesis: completed Windows full-suite evidence — 19 October 2026

- [Download editable Word thesis](windows-verified-thesis-2026-10-19/LiZiYao_24018160_CP2_Thesis_Windows_Verified.docx)
- [Download PDF review copy — 101 pages](windows-verified-thesis-2026-10-19/LiZiYao_24018160_CP2_Thesis_Windows_Verified.pdf)
- [Download complete current package](windows-verified-thesis-2026-10-19/LiZiYao_24018160_CP2_Windows_Verified_Package.zip)
- [Revision summary (Chinese)](windows-verified-thesis-2026-10-19/本轮论文修改说明.md)
- [Chapter-by-chapter before/after changes](windows-verified-thesis-2026-10-19/Windows_Final_Changes.md)
- [Remaining screenshot/evidence guide](windows-verified-thesis-2026-10-19/补图与待补证据清单.md)

**The Windows regression investigation is complete. No further patch or repeated test run is needed for this thesis update.** The actual native Windows full suite reports **370 passed / 0 failed / 0 errors / 0 skipped**, 15 warnings, **194.10 seconds**, exit 0. The preceding 131-test subset also passed and is recorded independently. All 13 recorded source hashes match the reviewed baseline-plus-repairs state. The Linux full suite remains a separate **369 passed / 1 failed / 0 collection errors** record because that installation lacks the real segmentation weight.

The thesis now synchronises the abstract, methodology/traceability, Chapter 4 software outcomes and objective assessment, limitations, Chapter 5 and appendices. Earlier collection/runtime failures remain dated comparison records rather than unresolved current results. Figure 4.12 reproduces selected lines from the genuine final Windows log, with omissions marked; it is not a fabricated GUI screenshot. Classification metrics remain **90.68% accuracy / 88.59% macro-F1 on 7,180 native 224×224 patches** through the unchanged default Pillow pathway.

This is a content revision retaining the supervisor chapter framework, original Word styles/numbering/theme and 32-reference list. All 166 existing page-reference fields match the final PDF. Seven screenshot groups, 20 UAT placeholders and the two cover fields remain reserved. Formal manual acceptance, segmentation accuracy, stage-level performance and clean-machine packaging retain their actual evidence limits. UAT and manual-acceptance templates are included. The 6.7MB complete package contains no obsolete diagnostic/installation launcher.

**Software files, HEAD and working-tree state were unchanged during this manuscript revision. No software-branch commit/push or main merge was made.** The passing Windows result describes revision 1f3e01e plus the recorded repairs, not an invented new clean commit. Only thesis materials are published on this independent documents branch.

---

## Earlier working drafts and diagnostic deliveries — superseded

The sections below are retained as dated records. Use the latest thesis links above; earlier diagnostic next steps are superseded by the completed 370-test Windows run.

## Compact body viewport follow-up — 19 October 2026

- [Download two-file incremental repair and native Windows verification](windows-compact-body-fix-2026-10-19/Windows_Compact_Body_Fix.zip)
- [Findings and exact scope (Chinese)](windows-compact-body-fix-2026-10-19/本轮核对与增量修复说明.md)
- [Review the incremental changes](windows-compact-body-fix-2026-10-19/incremental_review.patch)
- [Redacted native Windows verification evidence](windows-compact-body-fix-2026-10-19/Windows_Verification_Evidence_Redacted.zip)

The 22:12 native Windows invocation reports **124 passed / 1 failed / 0 errors / 0 skipped**, 15 warnings, **81.73 seconds**. The runner stopped after this related subset; **no full suite ran**. The previous callback, classification/segmentation result and maximization cases passed. The recorded source hashes and state match the second repair before and after the run.

The remaining snapshot shows a **120px body viewport** but a **203px three-panel splitter**: the right panel's inner scroll-area minimum-size hint stretches the whole splitter, placing Run below the visible window. The incremental production change is one vertical size-policy setting in ui/action_panel.py. Two added cases reproduce this with 16px/30px scrollbars and a 150px body; both fail before the change and pass after it. They retain the original window assertions and additionally check that both Run and Re-run fit fully in the body viewport and inner content remains scrollable.

Final Linux checks: **131 related tests passed**, **56 high-DPI layout tests passed**, and the complete suite reports **369 passed / 1 failed / 0 collection errors**, 14 warnings, **125.70 seconds**. The only failure still requires the real segmentation weight missing from that Linux installation. Four incremental-installer checks passed separately. No model, preprocessing, default Pillow resize, prediction/statistic, grid-transform or window-state behavior changed.

Close ZY-Path before installing. This package verifies the previously installed second repair and updates only ui/action_panel.py and tests/test_screen_fit_and_tile_grid.py, backs up original bytes, preserves line endings and refuses unknown edits. Run verification with the project Python; it runs 131 related tests and then the unfiltered full suite (370 cases) only if they pass. Upload the new verify-fix folder. **Windows results after this incremental repair remain pending.** No software-branch commit/push or main merge was made. The thesis must not yet claim a completed Windows full suite, and the successful 7K Pillow evaluation need not be repeated.

---

## Native Windows verification findings and second repair — 19 October 2026

- [Download guarded update and verification tools](windows-validation-fix2-2026-10-19/Windows_Validation_Fix2.zip)
- [Actual findings, changes and verification limits (Chinese)](windows-validation-fix2-2026-10-19/本轮核对与修复说明.md)
- [Review all source and regression changes](windows-validation-fix2-2026-10-19/reviewed_changes.patch)
- [Redacted native Windows input evidence](windows-validation-fix2-2026-10-19/Windows_Verification_Evidence_Redacted.zip)

The 19:25 native Windows run completed its **related subset: 114 passed / 5 failed / 0 errors / 0 skipped**, 15 warnings, **110.92 seconds**, exit 1. The runner therefore did **not** execute the full suite. Before/after revision, source hashes and tracked differences match. The prior worker-destruction and history-coordinate regressions pass on Windows; a queued validation lambda still accessed an already deleted checkbox, and three small-window layout cases failed. The remaining assertion imposed an offscreen 2px frame assumption on native Windows maximization.

The follow-up routes validation through QObject-bound receivers, adds six lifecycle regression cases, keeps Tile details accessible at the top, sizes segmentation legend viewports from actual card heights and protects the Run/Cancel area while preserving readable panel width. The Windows maximization test checks client containment and actual Qt native frame margins; normal/restored full-frame containment and other platforms' assertions remain. No native window-state workaround, arbitrary tolerance increase or skipped test was introduced.

Final Linux checks: **125 related tests passed**, **50 high-DPI layout tests passed**, and the complete suite reports **367 passed / 1 failed / 0 collection errors**, 14 warnings, **122.99 seconds**. The one failure still requires the real segmentation weight missing from the Linux installation. Six new callback cases failed on an isolated copy with the old lambda connections and passed after repair. The intermediate development failure and fixture correction logs are retained. Five installer-protection checks passed; these are separate from application counts.

Close ZY-Path, run apply_regression_fix.py, then verify_windows_fix.py with the existing project Python. The guarded installer accepts the prior reviewed patch, backs up original bytes and refuses unknown source edits. Verification runs 125 related tests followed by the unfiltered full suite only if they succeed. Read-only snapshots capture the Qt platform once and widget/frame geometry after failures; no line/event tracing runs. Upload the resulting verify-fix evidence folder. **Windows post-update results remain pending.** The successful 7K Pillow evaluation need not be repeated. No software-branch commit/push or main merge was made; the thesis must not claim a successful Windows full suite yet.

---

## Confirmed Qt worker crash and reviewed Windows repair — 19 October 2026

- [Download guarded repair and native Windows verification](windows-regression-fix-2026-10-19/Windows_Regression_Fix.zip)
- [Findings and actual regression results (Chinese)](windows-regression-fix-2026-10-19/本轮修复与验证说明.md)
- [Complete review patch, including three added regression cases](windows-regression-fix-2026-10-19/reviewed_changes.patch)
- [Redacted Windows diagnostic evidence](windows-regression-fix-2026-10-19/Windows_Trace_Evidence_Redacted.zip)

The 19:03 trace captured the fatal Qt message **QThread: Destroyed while thread is still running**. The process terminates while waiting for model validation in the next test window, before its missing-model re-run action. The original single case passes; the rerun sequence still has no final totals. The history sequence reports **96 passed / 1 failed**, with the same mouse coordinate moving from row 1 to blank space during deferred row resizing.

The repair protects active worker lifetime during forced parent deletion and calculates history row heights before interaction. It also includes the previous reviewed panel width and short-page scrolling repairs. All original tests/assertions remain; three regression cases are added. Each new regression failed before the corresponding repair and passed afterward. Linux checks: **119 related tests passed**; **24 high-font-DPI tests passed**; the entire suite recorded **361 passed / 1 failed / 0 collection errors**, 14 warnings, **104.36 seconds**. The one failure requires the real segmentation weight absent from that Linux installation. These are not Windows post-repair results.

Close ZY-Path before applying the installer. It checks every source file before writing, preserves existing recognized width corrections and line endings, backs up original bytes, refuses unrecognized edits, and supports safe repeat execution. Then run verify_windows_fix.py with the project Python. It runs related tests first and the unfiltered full suite only after those pass, without tracing plugins or assertion changes. Upload the generated verify-fix evidence folder. **No software branch commit/push or main merge was made.** The thesis must retain the incomplete Windows full-suite status until this verification actually completes; the successful 7K Pillow evaluation need not be repeated.

---

## Native Windows follow-up and precise crash tracing — 19 October 2026

- [Download scoped Windows crash tracer](windows-crash-trace-2026-10-19/Windows_Crash_Trace.zip)
- [Verified native findings and regression notes (Chinese)](windows-crash-trace-2026-10-19/本轮核对与后续说明.md)
- [Preview of additional result-layout correction — not automatically applied](windows-crash-trace-2026-10-19/pending_result_layout_preview.patch)

The 18:36 native Windows record confirms the padding correction: the minimum-layout case passed with panel width **264 = layout requirement 264**. The rerun module and full suite **still terminate with 0xC0000409 under the native windows plugin**, so offscreen is not a sufficient explanation. History double-click passes alone but fails in the full sequence. The second visible full-sequence failure is now large-font comparison navigation clipping, not the repaired width assertion. The full Windows invocation remains incomplete with no final counts.

A separate result-layout correction was reproduced and tested on Linux at font DPI 168. Final checks: **10 large-font comparison tests passed**, **56 related tests passed**, and the full suite recorded **358 passed / 1 failed / 0 collection errors**, 14 warnings, 105.49 seconds. The sole full-suite failure requires the unavailable real segmentation weight in that Linux installation. The intermediate failed development check is retained. These additional layout changes remain uncommitted and are **not applied by the tracer**.

The new tracer observes the exact missing-custom-model case alone, the original rerun sequence, and the original pre-history sequence. It records source lines, native calls, table mouse coordinates/indices, Qt fatal messages and matching Windows Application Error events. It does not run the full suite, install dependencies, apply patches, change model output, modify tests or suppress assertions. Three process-level tracer checks passed, including preservation of a deliberate Qt-fatal fixture message and stack; two original Linux cases also passed under observation. Tracing can change timing and is diagnostic evidence, not final acceptance or a performance benchmark.

Close ZY-Path and run trace_windows_crash.py with the existing project virtual-environment Python. Upload its crash-trace evidence folder. Keep the current Windows baseline plus the earlier width correction for this step; the 7K evaluation need not be repeated. The software branch has not been committed or pushed. The thesis retains its incomplete Windows regression status until genuine final results are available.

---

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