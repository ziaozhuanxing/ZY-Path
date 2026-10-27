# 本轮编辑修改清单

对应本轮逐项审阅。保留较早Windows结果的源版本，不赋予当前源码新的通过结论。

## 1. 4.3.1 / Table 4.3

**Before**: Table 4.3. Completed Windows automated execution with its source version. Source: the recorded Windows log, XML result and exit status.

**After**: Table 4.3. Completed Windows baseline automated execution and source version.

**Reason**: Remove duplicate source text from the caption; retain the separate Source paragraph immediately below the table.

## 2. Appendix C.2 / Table C.2

**Before**: Windows, 19 Oct; final full run

**After**: Windows baseline, 19 Oct 2026; source 7bd3552

**Reason**: Replace the ambiguous final-run label with the actual baseline and source version.

## 3. 4.3.1 / Figure 4.12 discussion

**Before**: Figure 4.12 reproduces selected lines from the genuine final Windows pytest report; it is a test-log excerpt rather than an application screenshot.

**After**: Figure 4.12 reproduces selected lines from the recorded 19 October Windows baseline at source 7bd3552; it is a test-log excerpt rather than an application screenshot.

**Reason**: Use baseline consistently without changing the original log or excerpt image.

## 4. 4.3.1 / Figure 4.12 caption

**Before**: Figure 4.12. Completed Windows pytest report, 19 October 2026. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**After**: Figure 4.12. Windows baseline pytest report, 19 October 2026, source 7bd3552. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**Reason**: Identify the old source version explicitly and remove final-version ambiguity.

## 5. 4.2.5 → 3.3.4

**Before**: 4.2.5, between the Settings discussion and Figure 4.7: The preference-lifetime regression defines a record at 8 × 7 source pixels, changes preferences to 16 × 12, restores or reruns the old record and starts a new run. For a 31 × 23 synthetic raster, its assertions require four real rectangles, including smaller right/bottom edges, while recorded rerun must retain its original geometry and backend. These small dimensions define deterministic test inputs and do not recommend a biological tile scale.

**After**: Immediately after the Run/Re-run parameter-lifetime paragraph in 3.3.4: The preference-lifetime regression defines a record at 8 × 7 source pixels, changes preferences to 16 × 12, restores or reruns the old record and starts a new run. For a 31 × 23 synthetic raster, its assertions require four real rectangles, including smaller right/bottom edges, while recorded rerun must retain its original geometry and backend. These small dimensions define deterministic test inputs and do not recommend a biological tile scale.

**Reason**: Place the synthetic geometry/parameter example with its implemented inference semantics; keep the Settings text and Guide & Support figure together.

## 6. 3.3.1

**Before**: The application loads and runs PyTorch models on CPU; no OpenVINO conversion or runtime is implemented. The genuine classification checkpoint occupies 1,726,089 bytes (1.646 MiB). Its checksum is recorded in Appendix E.1. A segmentation file-size measurement has not been supplied, and there is no converted-model size to report. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

**After**: Inference uses PyTorch on CPU. OpenVINO conversion is not implemented. The genuine classification checkpoint occupies 1,726,089 bytes (1.646 MiB); Appendix E.1 records its checksum. A segmentation checkpoint size has not been supplied. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

**Reason**: The supervisor previously raised OpenVINO conversion. Retain one concise factual runtime statement and the measured original checkpoint size; do not claim conversion.

## 7. 4.3.4

**Before**: The demonstrated delivery route is source execution. The current repository contains a Windows PyInstaller specification, build script, genuine-resource preflight, bundled-configuration support and release-manifest generation. No corresponding completed build log, distributable artifact or clean-machine/offline acceptance was supplied. Tooling implementation is therefore reported separately from unverified deployment. No OpenVINO runtime or converted model is present.

**After**: The demonstrated delivery route is source execution. The current repository contains a Windows PyInstaller specification, build script, genuine-resource preflight, bundled-configuration support and release-manifest generation. No corresponding completed build log, distributable artifact or clean-machine/offline acceptance was supplied. Tooling implementation is therefore reported separately from unverified deployment.

**Reason**: Remove the repeated OpenVINO disclaimer; the runtime is specified once in 3.3.1.

## 8. 4.5.3

**Before**: Runtime and deployment require further measurement. The recorded Windows execution uses PyTorch CPU, not its installed RTX 4060 GPU or an OpenVINO runtime. A fixed cold/warm benchmark protocol is prepared, but repeated timing and memory results remain unavailable. Windows build tooling is implemented; an actual version-matched package, clean-machine acceptance and offline execution are unverified. The demonstrated delivery remains source execution.

**After**: Runtime and deployment require further measurement. The recorded Windows execution uses PyTorch CPU; the installed RTX 4060 GPU was not used. A fixed cold/warm benchmark protocol is prepared, but repeated timing and memory results remain unavailable. Windows build tooling is implemented; an actual version-matched package, clean-machine acceptance and offline execution are unverified. The demonstrated delivery remains source execution.

**Reason**: State the actual compute environment without repeating the alternative-runtime disclaimer.

## 9. 4.3.1

**Before**: [New paragraph]

**After**: Revision 8c4830c is the fixed target for the next Windows regression. Its scope includes numbered tiles and original-crop inspection, Square, Clear view, background PDF export and quality selection, and current-preference Run versus recorded Re-run. A version-matched Windows result is not yet available for this revision. Appendix C specifies the source and native-Qt checks; Appendix D defines the corresponding real-image manual tasks.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 10. Appendix C.1

**Before**: [New paragraph]

**After**: The next Windows invocation is tied to the full current-source hash above. Before testing, verify HEAD and an unchanged tracked/untracked source state, close the application and retain the genuine model resources and training-script prerequisite. The evidence collector checks the expected commit and clean source, explicitly requests the native Windows Qt platform, records the full pytest command/log/XML/exit status, and compares source hashes before and after execution. The run is version-matched only when its native-platform probe and source checks succeed. The procedure does not substitute a resource, select a test subset or assign a passing total to an interrupted run. It is a prepared procedure, not an executed Windows result.

**Reason**: Provide a reproducible frozen-source protocol while preserving the actual status of the next Windows execution.

## 11. Abstract

**Before**: Deploying pathology models through separate scripts makes preprocessing, spatial sampling and previous analysis settings difficult to inspect. This project develops ZY-Path, a local PyQt5 desktop application that connects supported PyTorch CPU inference to explicit Single image and Tiled analysis controls, spatial inspection, recorded history and export, with a separate supervisor-provided segmentation integration. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native 224 × 224 CRC-VAL-HE-7K patches through the application’s default Pillow core, agreeing with every predicted label from the recorded reference pipeline. The 19 October Windows baseline passed 370 automated tests. The engineering contribution is a model-aware desktop workflow with explicit crop geometry, independent task semantics and reproducible parameter restoration. UAT, final-version manual Windows acceptance, systematic performance measurements and clean-machine deployment remain incomplete.

**After**: Deploying pathology models through separate scripts makes preprocessing, spatial sampling and previous analysis settings difficult to inspect. This project develops ZY-Path, a local PyQt5 desktop application that connects supported PyTorch CPU inference to explicit Single image and Tiled analysis controls, spatial inspection, recorded history and export, with a separate supervisor-provided segmentation integration. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native 224 × 224 CRC-VAL-HE-7K patches through the application’s default Pillow core, agreeing with every predicted label from the recorded reference pipeline. The 19 October Windows baseline passed 370 automated tests. The engineering contribution is a model-aware desktop workflow with explicit crop geometry, independent task semantics and reproducible parameter restoration. The remaining usability, native-acceptance, performance and deployment work is defined in Section 4.5.3.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 12. 4.2.1

**Before**: Current-version additions comprise numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run now reads current preferences independently of restored or rerun records. These implemented additions are separate from the earlier Windows baseline and require final-version native acceptance.

**After**: Current-version additions comprise numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run now reads current preferences independently of restored or rerun records. Their execution-evidence scope is defined in Section 4.3.1.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 13. 3.4.4

**Before**: Automated checks address small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The 19 October Windows baseline passed its maximise/restore, saved-geometry, comparison/grid and compact-viewport cases. Subsequent navigation and parameter-lifetime refinements require final-version native Windows manual acceptance with authorised real images in Appendix D.

**After**: Automated checks address small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The 19 October Windows baseline passed its maximise/restore, saved-geometry, comparison/grid and compact-viewport cases. Appendix D specifies the native real-image tasks; Section 4.3.1 defines the source versions to which the recorded results apply.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 14. 3.6.6 / Table 3.6 source

**Before**: Source: the named project tests, the 19 October Windows baseline log/XML and recorded classifier evaluation. Later implementation changes retain separate acceptance status; subset counts are reported separately.

**After**: Source: the named project tests, the 19 October Windows baseline log/XML and recorded classifier evaluation. Baseline outcomes apply only to cases executed at 7bd3552; later named cases describe the current implementation and next validation scope, not additional Windows passes. Section 4.3.1 defines the current-source execution boundary; manual tasks and UAT remain separate evaluations.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 15. 3.6.6 / F02

**Before**: Windows baseline loader/probe and built-in-path cases passed. Supported model-loading and task-default checks are implemented. Probe checks do not validate semantic accuracy; current-version native acceptance remains pending.

**After**: Windows baseline loader/probe and built-in-path cases passed. Probes establish structural compatibility, not predictive accuracy; see Section 4.3.1 for source scope.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 16. 3.6.6 / N05, N07–N08

**Before**: Windows baseline: 370 passed, no failures/errors/skips. Repeated performance measurement and clean-machine deployment remain incomplete. Later changes require current-version Windows execution.

**After**: Windows baseline: 370 passed, no failures/errors/skips. Performance and deployment follow their own protocols; current-source revalidation is specified in Section 4.3.1.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 17. 3.6.6 / F17

**Before**: Clear-view, zero-selection, history-thumbnail and source-preservation behaviour is implemented with named regression cases; final-version native acceptance remains pending.

**After**: Implemented with named clear-view, zero-selection, history-thumbnail and source-preservation cases; current-source acceptance scope is defined in Section 4.3.1.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 18. 4.5.1 / O1

**Before**: Local PyTorch CPU workflow implemented. Windows baseline startup and 370-test suite recorded. Current-version native acceptance and clean-machine offline delivery remain unverified.

**After**: Local PyTorch CPU workflow implemented. Windows baseline startup and 370-test execution are recorded; Section 4.3.1 defines source scope and Section 4.5.3 the deployment limit.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 19. 4.5.1 / O4

**Before**: Numbered-tile inspection, original-crop detail, coordinate/grid and linked navigation are implemented with named regression cases. Final-version native real-image tasks and UAT remain pending.

**After**: Numbered-tile inspection, original-crop detail, coordinate/grid and linked navigation are implemented with named regression cases. Execution scope is defined in Section 4.3.1; user evaluation follows Section 4.4.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 20. 5.4

**Before**: ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis, numbered inspection and stronger state/export management. The measured classifier result and dated Windows automated record support different aspects of the work. Current-version Windows manual acceptance, UAT, systematic runtime/memory measurements and clean-machine deployment remain unfinished and must be completed or retained as explicit limits.

**After**: ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis, numbered inspection and stronger state/export management. The measured classifier result and dated Windows automated record support different aspects of the work. The source scope and remaining evaluations are defined in Sections 4.3.1 and 4.5.3.

**Reason**: Keep the actual Windows baseline outcome separate from the fixed source targeted by the next execution; consolidate the boundary in Section 4.3.1 instead of repeating it throughout the results.

## 21. 4.3.1

**Before**: Earlier Windows runs were interrupted by a missing training-script prerequisite and a worker-thread destruction fault. Restoring the genuine script and correcting worker lifetime, queued validation callbacks and panel size policies resolved the observed regression cases in the final suite. Table 4.5 summarises the implementation corrections; Appendix C retains the earlier run outcomes.

**After**: Earlier Windows runs were interrupted by a missing training-script prerequisite and a worker-thread destruction fault. Restoring the genuine script and correcting worker lifetime, queued validation callbacks and panel size policies resolved the observed regression cases in the completed baseline suite. Table 4.5 summarises the implementation corrections; Appendix C retains the earlier run outcomes.

**Reason**: Use baseline consistently for the old executed source.

## 22. 4.3.2 / Table 4.5

**Before**: Table 4.5. Implementation challenges and verified resolutions

**After**: Table 4.5. Implementation challenges, corrections and supporting evidence.

**Reason**: Distinguish implemented later fixes from source-specific executed Windows evidence.

## 23. 4.3.2 / Table 4.5

**Before**: Native fatal message identified cause; two worker-destruction regressions and final Windows suite passed.

**After**: Native fatal message identified cause; two worker-destruction regressions and 19 October Windows baseline suite passed.

**Reason**: Scope the available Windows evidence to the completed baseline.

## 24. Appendix A.2 / Table A.3

**Before**: Versioned task/material protocol prepared; Windows baseline recorded; no actual UAT responses or completed final-version manual sheets

**After**: Versioned task/material protocol and Windows baseline are recorded; actual UAT responses and current-source manual sheets have not been supplied

**Reason**: Scope the available Windows evidence to the completed baseline.

## 25. Appendix A.2 / Table A.3

**Before**: Automated Windows verification complete; formal manual acceptance and UAT pending

**After**: Baseline automated record available; current-source acceptance follows the frozen Windows protocol

**Reason**: Scope the available Windows evidence to the completed baseline.

## 26. Appendix A.2 / Table A.3

**Before**: Final log/XML/exit code; 370 distinct passing cases; source identity recorded

**After**: Windows baseline log/XML/exit code; 370 distinct passing cases; source identity recorded

**Reason**: Scope the available Windows evidence to the completed baseline.

## 27. All 53 author–year citations / hyperlink styles

**Before**: Blue underlined Hyperlink character style; visited-state styling unspecified.

**After**: Black text without underline for normal and followed hyperlinks; all original citation texts and link destinations remain clickable.

**Reason**: Use unobtrusive academic citation typography while retaining source access; change character styles rather than inline font overrides.

## 28. Windows validation protocol / collector

**Before**: No required source hash, clean-state gate or explicitly requested native Windows Qt platform.

**After**: Optional exact-commit, clean-source and native-Windows guards; source/resource manifests before and after the unchanged full pytest command. No actual Windows run is implied.

**Reason**: Tie the planned complete execution to the declared source and platform without replacing or skipping tests.
