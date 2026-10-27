# Windows 508通过版本：逐项修改清单

依据27 October 2026实际日志、XML、退出码及源码/资源记录更新。此前Windows记录保留日期与版本，未编造人工验收或模型评价。

## 1. Abstract

**Before**: Deploying pathology models through separate scripts makes preprocessing, spatial sampling and previous analysis settings difficult to inspect. This project develops ZY-Path, a local PyQt5 desktop application that connects supported PyTorch CPU inference to explicit Single image and Tiled analysis controls, spatial inspection, recorded history and export, with a separate supervisor-provided segmentation integration. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native 224 × 224 CRC-VAL-HE-7K patches through the application’s default Pillow core, agreeing with every predicted label from the recorded reference pipeline. The 19 October Windows baseline passed 370 automated tests. The engineering contribution is a model-aware desktop workflow with explicit crop geometry, independent task semantics and reproducible parameter restoration. The remaining usability, native-acceptance, performance and deployment work is defined in Section 4.5.3.

**After**: Deploying pathology models through separate scripts makes preprocessing, spatial sampling and previous analysis settings difficult to inspect. This project develops ZY-Path, a local PyQt5 desktop application that connects supported PyTorch CPU inference to explicit Single image and Tiled analysis controls, spatial inspection, recorded history and export, with a separate supervisor-provided segmentation integration. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native 224 × 224 CRC-VAL-HE-7K patches through the application’s default Pillow core, agreeing with every predicted label from the recorded reference pipeline. On 27 October 2026, revision 3a935ef passed all 508 automated tests on native Windows Qt, with no failures, errors or skipped cases. The engineering contribution is a model-aware desktop workflow with explicit crop geometry, independent task semantics and reproducible parameter restoration. The remaining usability, native-acceptance, performance and deployment work is defined in Section 4.5.3.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 2. 3.1

**Before**: The current implementation is identified by revision 8c4830c. The completed Windows baseline is revision 7bd3552; its date and source version are retained when reporting the automated results. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the source versions and Windows execution records.

**After**: The implementation evaluated in this thesis is revision 3a935ef. Its complete Windows execution on 27 October 2026 passed all 508 automated cases. Classification methods are documented by the training code provided by my supervisor, my training/validation records and corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the evaluated source and the earlier Windows records.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 3. 3.2.2 / N04

**Before**: Windows baseline layout checks are recorded; final-version native Windows and assistive-technology manual acceptance remain pending.

**After**: Native Windows automated layout cases passed at revision 3a935ef. Formal real-image manual and assistive-technology acceptance remain separate evaluations.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 4. 3.3.1

**Before**: Inference uses PyTorch on CPU. OpenVINO conversion is not implemented. The genuine classification checkpoint occupies 1,726,089 bytes (1.646 MiB); Appendix E.1 records its checksum. A segmentation checkpoint size has not been supplied. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

**After**: Inference uses PyTorch on CPU. OpenVINO conversion is not implemented. The 27 October Windows resource manifest records 1,726,089 bytes (1.646 MiB) for the classification checkpoint and 489,488,187 bytes (466.812 MiB) for the segmentation checkpoint. Both files were present and unchanged through the test execution; Appendix E records their SHA-256 identities. These are stored checkpoint sizes. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

**Reason**: Use the newly supplied resource identities and original sizes; do not invent a converted-model size or segmentation accuracy.

## 5. 3.4.4

**Before**: Automated checks address small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The 19 October Windows baseline passed its maximise/restore, saved-geometry, comparison/grid and compact-viewport cases. Appendix D specifies the native real-image tasks; Section 4.3.1 defines the source versions to which the recorded results apply.

**After**: Automated checks address small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The complete Windows suite at revision 3a935ef passed its maximise/restore, saved-geometry, comparison/grid, large-font input and compact-viewport cases. These programmatic cases support layout behaviour on the recorded runtime. Appendix D defines the separate native real-image manual tasks.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 6. 3.6.1

**Before**: The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.

**After**: The 27 October Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 7. 3.6.1

**Before**: [New paragraph]

**After**: Default application settings and application-data directories are isolated per test. On Windows, the organisation/application QSettings constructor normally reads the Registry; the test fixture redirects that constructor to a per-test INI store while preserving explicit file-based settings. Separate cases verify fresh defaults and persistence between instances in the same store. This prevents a saved Tiled analysis choice or maximised window from becoming an unintended precondition of unrelated tests. Production preference storage is unchanged.

**Reason**: Describe the executed isolation fix rather than weakening the expected inference mode or window assertions.

## 8. 3.6.5

**Before**: The completed Windows baseline on 19 October 2026 passed 370 tests without failures, errors or skipped cases. Table 4.3 reports that execution with its source revision. Related subsets and earlier Windows interruptions remain separately identified in Appendix C; their counts are not added to the complete-suite total.

**After**: On 27 October 2026, revision 3a935ef completed the full native Windows Qt suite: 508 passed, 0 failed, 0 errors and 0 skipped, with 16 warnings in 268.74 seconds (exit 0). Table 4.3 presents this current-source result. Appendix C retains earlier Windows invocations with their original dates and versions; they are not added to the current total.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 9. 3.6.6 / F01 / O3

**Before**: Windows-baseline full-suite image-loading and input-error cases passed; representative real-image manual tasks pending.

**After**: Current Windows full-suite image-loading and input-error cases passed; representative real-image manual tasks pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 10. 3.6.6 / F02 / O2

**Before**: Windows baseline loader/probe and built-in-path cases passed. Probes establish structural compatibility, not predictive accuracy; see Section 4.3.1 for source scope.

**After**: Current Windows loader/probe and genuine built-in-path cases passed. Probes establish structural compatibility, not predictive accuracy.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 11. 3.6.6 / F03 / O3

**Before**: Windows-baseline software cases passed; default-Pillow patch accuracy 90.68%, macro-F1 88.59% on native 224 × 224 inputs (Section 4.2.6).

**After**: Current Windows software cases passed; default-Pillow patch accuracy 90.68%, macro-F1 88.59% on native 224 × 224 inputs (Section 4.2.6).

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 12. 3.6.6 / F04–F05 / O3–O4

**Before**: Windows-baseline crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending.

**After**: Current Windows crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 13. 3.6.6 / F06 / O3–O4

**Before**: Windows-baseline synthetic segmentation geometry/statistics and display cases passed; real-weight demonstration and ground-truth evaluation pending.

**After**: Current Windows synthetic segmentation geometry/statistics and display cases passed; real-weight demonstration and ground-truth evaluation pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 14. 3.6.6 / F07 / O4

**Before**: Windows-baseline coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed; formal real-image manual acceptance pending.

**After**: Current Windows coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed; formal real-image manual acceptance pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 15. 3.6.6 / F08 / O6

**Before**: Windows-baseline persistence and artifact cases passed with temporary test records; real-image manual workflow evidence pending.

**After**: Current Windows persistence and artifact cases passed with temporary test records; real-image manual workflow evidence pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 16. 3.6.6 / F09 / O7

**Before**: Windows-baseline query, calendar and history-interaction cases passed; user task outcomes await UAT.

**After**: Current Windows query, calendar and history-interaction cases passed; user task outcomes await UAT.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 17. 3.6.6 / F10–F11 / O7

**Before**: Windows-baseline restore and recorded-model/mode/parameter rerun cases passed; user-efficiency assessment awaits UAT.

**After**: Current Windows restore and recorded rerun cases passed, including current-preference versus saved-record isolation. User-efficiency assessment awaits UAT.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 18. 3.6.6 / F12 / O5

**Before**: Windows-baseline file/report and recorded-metadata cases passed; final real-image report screenshots pending.

**After**: Current Windows file/report, background export, image-quality and recorded-metadata cases passed; final real-image report screenshots remain to be supplied.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 19. 3.6.6 / F13 / O1

**Before**: Windows-baseline cooperative-stop, late-result and destruction/callback lifecycle cases passed; real-model manual cancellation record pending.

**After**: Current Windows cooperative-stop, late-result and destruction/callback lifecycle cases passed; real-model manual cancellation record pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 20. 3.6.6 / F14–F15 / O1–O3

**Before**: Windows-baseline defaults, validation, preferences and history-isolation cases passed.

**After**: Current Windows defaults, validation, preferences and history-isolation cases passed.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 21. 3.6.6 / F16 / O6–O7

**Before**: Windows-baseline app-owned artifact cleanup and source-preservation cases passed.

**After**: Current Windows app-owned artifact cleanup and source-preservation cases passed.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 22. 3.6.6 / N01, N04 / O1, O4

**Before**: Windows-baseline window-state, restore, small-viewport and layout cases passed; multi-monitor/assistive-technology manual acceptance pending.

**After**: Current Windows window-state, restore, small-viewport and layout cases passed; multi-monitor/assistive-technology manual acceptance pending.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 23. 3.6.6 / N02, N06 / O2, O6–O7

**Before**: Windows-baseline missing-file/error handling and recorded-parameter cases passed; immutable provenance is not implemented.

**After**: Current Windows missing-file/error handling and recorded-parameter cases passed; immutable provenance is not implemented.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 24. 3.6.6 / N05, N07–N08 / O1

**Before**: Windows baseline: 370 passed, no failures/errors/skips. Performance and deployment follow their own protocols; current-source revalidation is specified in Section 4.3.1.

**After**: Current Windows full suite: 508 passed; no failures, errors or skips. Repeated inference-performance measurement and clean-machine deployment retain their separate protocols.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 25. 3.6.6 / F17 / O1, O6–O7

**Before**: Implemented with named clear-view, zero-selection, history-thumbnail and source-preservation cases; current-source acceptance scope is defined in Section 4.3.1.

**After**: Passed in the current Windows suite: clear view, zero-selection, synchronised history thumbnail and source/history preservation. Manual tasks and UAT are separate.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 26. 3.6.6 / Table 3.6 source

**Before**: Source: the named project tests, the 19 October Windows baseline log/XML and recorded classifier evaluation. Baseline outcomes apply only to cases executed at 7bd3552; later named cases describe the current implementation and next validation scope, not additional Windows passes. Section 4.3.1 defines the current-source execution boundary; manual tasks and UAT remain separate evaluations.

**After**: Source: the complete 27 October Windows log/XML at revision 3a935ef and the named project tests. Executable cases in this matrix were included in the 508-case invocation. Recorded classifier evaluation, source-inspection findings, manual tasks and UAT have their own evidence scope.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 27. 4.3.1

**Before**: The completed Windows invocation on 19 October 2026 passed all 370 cases at baseline source 7bd3552, with 0 failures, 0 errors and 0 skipped cases, 15 warnings and 194.10 seconds (exit 0). Table 4.3 reports this dated baseline; its result is not extended to subsequent changes in revision 8c4830c.

**After**: On 27 October 2026, revision 3a935ef completed all 508 collected tests on native Windows Qt: 508 passed, 0 failed, 0 errors and 0 skipped. The pytest summary reports 16 warnings and 268.74 seconds, with exit code 0. Table 4.3 presents this source-matched result. The recorded commit and source/resource manifests agree before and after the execution.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 28. 4.3.1

**Before**: Revision 8c4830c is the fixed target for the next Windows regression. Its scope includes numbered tiles and original-crop inspection, Square, Clear view, background PDF export and quality selection, and current-preference Run versus recorded Re-run. A version-matched Windows result is not yet available for this revision. Appendix C specifies the source and native-Qt checks; Appendix D defines the corresponding real-image manual tasks.

**After**: The completed invocation includes numbered tiles and original-crop inspection, Square, Clear view, background PDF export and quality selection, and current-preference Run versus recorded Re-run. The native Qt probe reported the windows platform. Programmatic regression completion is distinct from the real-image manual tasks in Appendix D and participant-based evaluation in Section 4.4.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 29. 4.3.1 / Table 4.3 caption

**Before**: Table 4.3. Completed Windows baseline automated execution and source version.

**After**: Table 4.3. Complete Windows automated execution for the evaluated source.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 30. 4.3.1 / Table 4.3

**Before**: Windows baseline, 19 Oct 2026

**After**: Windows, 27 Oct 2026; revision 3a935ef

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 31. 4.3.1 / Table 4.3

**Before**: 370

**After**: 508

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 32. 4.3.1 / Table 4.3

**Before**: 0

**After**: 0

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 33. 4.3.1 / Table 4.3

**Before**: 0

**After**: 0

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 34. 4.3.1 / Table 4.3

**Before**: 0 skipped; 15 warnings; 194.10 s; exit 0. Source revision 7bd3552.

**After**: 0 skipped; 16 warnings; 268.74 s; exit 0. Native Windows Qt; source and resources unchanged.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 35. 4.3.1 / Table 4.3 header

**Before**: Collection errors

**After**: Errors

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 36. 4.3.1 source

**Before**: Source: the complete Windows log/XML and exit record of 19 October 2026. Appendix C identifies its source version and preserves earlier Windows invocations separately.

**After**: Source: the complete Windows log/XML, exit record and source manifests of 27 October 2026. Earlier Windows executions are listed separately in Appendix C.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 37. 4.3.1

**Before**: The completed Windows invocation ran without test-case selection or skipped cases. Its duration measures automated testing, not inference latency. The separate 131-case Windows related subset is an independent execution and is not added to the 370-case complete-suite total.

**After**: The invocation ran without test-case selection or skipped cases. The 268.74-second value is the pytest console summary duration, not inference latency. The 16 warnings concern deprecated Matplotlib/Pyparsing, PyTorch TypedStorage and Hugging Face download interfaces. They did not prevent completion of the suite.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 38. 4.3.1 / Table 4.4

**Before**: Table 4.4. Windows test host and actual CPU runtime on 19 October 2026

**After**: Table 4.4. Windows host hardware record and verified test runtime.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 39. 4.3.1 / Table 4.4 source

**Before**: Source: Windows test/environment record dated 19 October 2026; full revision and evidence-file index in Appendix C. Installed GPU specifications are separated from the actual CPU runtime.

**After**: Source: host hardware recorded on 19 October 2026 and runtime/dependency records from the completed 27 October invocation. Physical RAM and GPU specifications were not remeasured in the later collection; the runtime probe confirms PyTorch CPU execution.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 40. 4.3.1 / Table 4.4 GUI runtime

**Before**: Startup: DPR 2.0; automation: DPR 1.0, logical DPI 168. Each geometry record uses Qt logical coordinates.

**After**: 27 Oct: native windows Qt platform confirmed. Earlier 19 Oct display/DPR measurements remain separate observations.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 41. 4.3.1 / Figure 4.12 discussion

**Before**: Figure 4.12 reproduces selected lines from the recorded 19 October Windows baseline at source 7bd3552; it is a test-log excerpt rather than an application screenshot.

**After**: Figure 4.12 reproduces selected lines from the completed 27 October Windows pytest log at revision 3a935ef; it is a test-log excerpt rather than an application screenshot.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 42. 4.3.1 / Figure 4.12 caption

**Before**: Figure 4.12. Windows baseline pytest report, 19 October 2026, source 7bd3552. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**After**: Figure 4.12. Complete Windows pytest report, 27 October 2026, revision 3a935ef. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 43. 4.3.1

**Before**: The Windows baseline passed its built-in-model availability assertion and the history, rerun, worker-lifetime and layout cases in that source version. The separate classifier evaluation in Section 4.2.6 supplies predictive measurements. A file-availability check or a passing fixture does not measure segmentation accuracy.

**After**: The current Windows suite passed its genuine built-in-model availability assertion and the history, rerun, worker-lifetime and layout cases. Its resource manifest includes both production checkpoints. The separate classifier evaluation in Section 4.2.6 supplies predictive measurements; file availability and synthetic fixtures do not measure segmentation accuracy.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 44. 4.3.1

**Before**: Earlier Windows runs were interrupted by a missing training-script prerequisite and a worker-thread destruction fault. Restoring the genuine script and correcting worker lifetime, queued validation callbacks and panel size policies resolved the observed regression cases in the completed baseline suite. Table 4.5 summarises the implementation corrections; Appendix C retains the earlier run outcomes.

**After**: Earlier Windows iterations exposed missing training prerequisites, thread-lifetime faults, settings leakage and platform-dependent layout/path assumptions. Corrections addressed these causes while preserving production preference persistence and the behavioural assertions. The completed 508-case invocation includes the corrected cases. Table 4.5 summarises the resolutions; Appendix C preserves the earlier Windows outcomes.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 45. 4.3.2 / Table 4.5 source

**Before**: Source: implementation changes and their named regression cases, including the completed native Windows suite of 19 October 2026.

**After**: Source: implementation changes and named regression cases in the complete Windows suite of 27 October 2026, with earlier records identified in Appendix C.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 46. 4.3.2 / Table 4.5

**Before**: Named preference-lifetime cases assert actual crop boxes, current preference values and recorded geometry; final-version Windows acceptance remains pending.

**After**: Current Windows preference-lifetime cases passed with actual crop boxes, current values and recorded rerun geometry.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 47. 4.3.2 / Table 4.5

**Before**: Named PDF encoding, data-preservation, layout and worker-lifecycle cases assert the implementation contract; current Windows acceptance and user report re-export remain pending.

**After**: Current Windows PDF encoding, complete-path, data-preservation, layout and worker-lifecycle cases passed; online preview and real-image captures require their own observations.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 48. 4.3.2 / Table 4.5

**Before**: Named navigation, Fit and grid regression cases address coordinate stability; current native Windows manual acceptance remains pending.

**After**: Current Windows navigation and Fit/grid cases passed; formal real-image manual acceptance remains separate.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 49. 4.3.2 / Table 4.5

**Before**: [New evidence row]

**After**: Default settings affected unrelated tests | The organisation/application QSettings overload read saved native preferences, including Tiled mode and maximised state | Per-test INI settings and temporary application data; preserve ordinary preference persistence | Current Windows settings-sandbox, inference, history and window cases passed

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 50. 4.3.2 / Table 4.5

**Before**: [New evidence row]

**After**: Large-font controls and short action panel | Status text, scrollbar extent and implicit minimum-height hints consumed the available space | Upload before verbose status; reserve scrollbar width; aligned stacked tile inputs; compact pinned actions | Current Windows large-font, input-alignment and compact-body cases passed

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 51. 4.3.2 / Table 4.5

**Before**: [New evidence row]

**After**: Platform-dependent path representation | Windows audit messages used backslashes; PDF extraction added visual line breaks to long paths | Portable audit identifiers; retain exact path assertions after removing CR/LF layout characters; add a Windows path case | Current Windows build-input and complete segmentation-report path cases passed

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 52. 4.3.3

**Before**: The Windows baseline automated checks cover maximise/restore, saved geometry, comparison/grid alignment and compact action panels for that earlier source. Subsequent navigation, metadata wrapping, task-specific progress, model-source and tile-preference refinements require a new native Windows execution and formal manual records on the selected final version, as specified in Appendix D.

**After**: The 27 October native Windows suite passed programmatic maximise/restore, saved-geometry, comparison/grid, compact-panel, navigation, metadata wrapping, task-progress, model-source and tile-preference cases. Formal real-image manual acceptance in Appendix D remains distinct from these automated inputs and assertions.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 53. 4.3.3

**Before**: The source-startup session reported devicePixelRatio=2.0 and availableGeometry=[0, 0, 1280, 758] in Qt logical coordinates, with normal, maximised and minimised state entries. The automated Windows application reported DPR 1.0, logical DPI 168 and availableGeometry=[0, 0, 2560, 1516]. Each record is interpreted within its own Qt application; these logical values are not substituted for a measured physical monitor resolution.

**After**: The 19 October source-startup session reported devicePixelRatio=2.0 and availableGeometry=[0, 0, 1280, 758] in Qt logical coordinates, with normal, maximised and minimised state entries. The separate 19 October automated Windows application reported DPR 1.0, logical DPI 168 and availableGeometry=[0, 0, 2560, 1516]. Each record is interpreted within its own Qt application; these logical values are not substituted for a measured physical monitor resolution.

**Reason**: Retain the original dates of the earlier display measurements; do not attribute them to the new probe.

## 54. 4.5.1 / O1

**Before**: Local PyTorch CPU workflow implemented. Windows baseline startup and 370-test execution are recorded; Section 4.3.1 defines source scope and Section 4.5.3 the deployment limit.

**After**: Local PyTorch CPU workflow implemented; the source-matched Windows suite passed 508 cases. Clean-machine/offline delivery remains outside the completed verification.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 55. 4.5.1 / O2

**Before**: Supported loader and task-default checks implemented. Real classifier loading recorded on Windows; structural probes do not establish unrestricted semantic compatibility.

**After**: Current Windows loader, task-default and genuine built-in-path cases passed. Structural compatibility is distinguished from model-specific predictive performance.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 56. 4.5.1 / O4

**Before**: Numbered-tile inspection, original-crop detail, coordinate/grid and linked navigation are implemented with named regression cases. Execution scope is defined in Section 4.3.1; user evaluation follows Section 4.4.

**After**: Current Windows numbered-tile, original-crop, coordinate/grid and linked-navigation cases passed. User interpretation and real-image manual tasks remain separate evaluations.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 57. 4.5.1 / O5

**Before**: Background atomic/cancellable PDF and two image-quality modes are implemented with named file/encoding/metadata cases. Synthetic size observations are separate from native acceptance; real-image export capture remains pending.

**After**: Current Windows background atomic/cancellable PDF, image-quality, file/encoding and recorded-metadata cases passed. Synthetic report-size observations remain distinct from real-image captures.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 58. 4.5.1 / O6

**Before**: SQLite/artifact persistence is recorded in the Windows baseline; clear-view history/source preservation is implemented. Per-run immutable file identities, backup and recovery are not implemented.

**After**: Current Windows persistence, clear-view and history/source-preservation cases passed. Immutable per-run file identities, backup and recovery remain further work.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 59. 4.5.1 / O7

**Before**: Search, filtering, zero-selection, restore and recorded rerun are implemented. New-run preferences and saved-record parameters have separate lifetimes; user efficiency remains unmeasured.

**After**: Current Windows search, filtering, zero-selection, restore and recorded-rerun cases passed, including preference/record isolation. User efficiency remains unmeasured.

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 60. 4.5.1

**Before**: The implementation makes task/mode, source crop versus network input, resize backend and coverage semantics visible. Current refinements strengthen numbered inspection, navigation, export and the separation of new-run preferences from recorded rerun settings. The patch evaluation supplies a measured classifier result; the completed Windows baseline supplies version-specific software verification.

**After**: The implementation makes task/mode, source crop versus network input, resize backend and coverage semantics visible. Current refinements strengthen numbered inspection, navigation, export and the separation of new-run preferences from recorded rerun settings. The patch evaluation supplies a measured classifier result; the completed 508-case Windows execution supplies verification for the evaluated source.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 61. 4.5.3

**Before**: The completed 370-test native Windows suite supports the earlier baseline. Later controls and workflows require final-version native Windows manual acceptance. UAT, authorised current screenshots and representative display/assistive-technology acceptance remain incomplete.

**After**: The 508-case Windows suite verifies the evaluated software revision under the recorded runtime. Formal real-image manual acceptance, authorised current screenshots, participant UAT and representative assistive-technology assessment remain incomplete. These concern user experience and acceptance rather than an outstanding automated regression result.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 62. 4.5.4

**Before**: The immediate priorities are to resolve genuine resources on the chosen acceptance installation, run the current complete Windows suite, complete authorised real-image manual tasks and execute the frozen UAT protocol. The documented patch evaluation remains the classifier result; larger-crop and tiled predictive work requires its own authorised ground-truth design. No new biological generalisation result is introduced by the current software refinements.

**After**: Following completion of the current-source Windows regression, the immediate priorities are authorised real-image manual acceptance and execution of the UAT protocol. The documented patch evaluation remains the classifier result; larger-crop and tiled predictive work requires its own authorised ground-truth design. The software regression does not add a new biological generalisation result.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 63. 4.6

**Before**: ZY-Path implements model-aware inference, spatial inspection and record continuity, with current refinements to numbered tiles, preferences, reset operations and background report export. The default-Pillow Single image core achieves 90.68% accuracy and 88.59% macro-F1 on the documented native-sized patch test. The Windows baseline passed 370 cases. The remaining user, manual, performance and deployment evidence is specified in Section 4.5.3.

**After**: ZY-Path implements model-aware inference, spatial inspection and record continuity, with current refinements to numbered tiles, preferences, reset operations and background report export. The default-Pillow Single image core achieves 90.68% accuracy and 88.59% macro-F1 on the documented native-sized patch test. Revision 3a935ef passed all 508 cases in the complete 27 October Windows execution. The remaining user, manual, performance and deployment evidence is specified in Section 4.5.3.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 64. 5.1

**Before**: The Windows default-Pillow evaluation produced 6,511 correct labels from 7,180 native-sized test patches: 90.68% accuracy and 88.59% macro-F1. Every predicted label agrees with the recorded reference pipeline, with small probability differences. Software verification remains separate: the earlier native Windows baseline passed 370 cases with no failures, errors or skipped cases. Final-version native acceptance, UAT and broader predictive claims retain the limits in Section 4.5.3.

**After**: The Windows default-Pillow evaluation produced 6,511 correct labels from 7,180 native-sized test patches: 90.68% accuracy and 88.59% macro-F1. Every predicted label agrees with the recorded reference pipeline, with small probability differences. Software verification remains separate: revision 3a935ef passed all 508 automated cases on Windows, with no failures, errors or skipped cases. Real-image manual acceptance, UAT, performance/deployment measurements and broader predictive claims retain the limits in Section 4.5.3.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 65. 5.2

**Before**: Further evaluation should examine patient- or slide-grouped internal validation, additional authorised cohorts and larger-crop/tiled predictive behaviour under documented source geometry. The immediate engineering follow-up is current-version Windows regression and manual acceptance, followed by the predefined timing/memory protocol. Passing subsets must not replace the full-suite result, and unavailable resources must remain reported rather than substituted.

**After**: Further evaluation should examine patient- or slide-grouped internal validation, additional authorised cohorts and larger-crop/tiled predictive behaviour under documented source geometry. The immediate engineering follow-up is real-image manual acceptance and UAT, followed by the predefined timing/memory protocol. Passing subsets must not replace the full-suite result, and unavailable resources must remain reported rather than substituted.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 66. Appendix A.2

**Before**: Current revision 8c4830c; completed Windows baseline 7bd3552 recorded separately

**After**: Evaluated revision 3a935ef; complete 27 Oct Windows log/XML and source/resource identity records

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 67. Appendix A.2

**Before**: Implemented; final native capture pending

**After**: Implemented; current Windows automated cases passed; final real-image capture remains pending

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 68. Appendix A.2

**Before**: Revision 7bd3552

**After**: Evaluated revision 3a935ef; earlier source history retained in Appendix C

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 69. Appendix A.2

**Before**: Committed source matching the completed Windows regression; version identified in Appendix C.

**After**: Current complete Windows regression passed

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 70. Appendix A.2

**Before**: Versioned task/material protocol and Windows baseline are recorded; actual UAT responses and current-source manual sheets have not been supplied

**After**: Task/material protocol and complete current Windows regression recorded; no actual UAT responses or completed real-image manual sheets supplied

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 71. Appendix A.2

**Before**: Baseline automated record available; current-source acceptance follows the frozen Windows protocol

**After**: Automated Windows verification complete; formal manual acceptance and UAT pending

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 72. Appendix A.2

**Before**: Windows baseline log/XML/exit code; 370 distinct passing cases; source identity recorded

**After**: Complete log/XML/exit code at revision 3a935ef; 508 distinct passing cases

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 73. Appendix A.2

**Before**: Completed on 19 Oct 2026; 0 failures, errors or skips

**After**: Completed on 27 Oct 2026; 0 failures, errors or skipped cases

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 74. Appendix A.2

**Before**: Revision 8c4830c; current export, navigation and preference implementation with named regression cases

**After**: Revision 3a935ef; current export, navigation, preferences and settings-isolation cases

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 75. Appendix A.2

**Before**: Implemented; current-version native Windows execution and manual acceptance remain pending

**After**: Implemented and included in the completed Windows regression; real-image manual acceptance remains separate

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 76. Appendix A.3

**Before**: Before submission, select and record the final software source, collect its native Windows result, complete authorised screenshots/manual tasks and the frozen UAT protocol, and supply semester/submission date. Preserve the earlier Windows baseline and classifier evaluation with their real scope. Execute the performance or deployment protocols only when those claims are to be made; otherwise retain their explicit incomplete status.

**After**: The evaluated software source and complete Windows regression are recorded. Before submission, complete authorised screenshots, real-image manual tasks and the UAT protocol, and supply semester/submission date. Preserve the earlier Windows and classifier-evaluation records with their original scope. Execute the performance or deployment protocols when those claims are to be made; otherwise retain their explicit incomplete status.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 77. Appendix C.1

**Before**: The current application source is commit 8c4830c1281e4a85248c9a2ea9d0adae64bd4525. The completed Windows baseline is 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19, recorded after the 19 October Windows run. Original Windows logs retain their original identifiers. Table C.1 identifies the supporting materials and Table C.2 separates the actual Windows executions.

**After**: The evaluated application source is commit 3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5. Its complete native Windows Qt execution on 27 October 2026 passed all 508 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 78. Appendix C.1

**Before**: The next Windows invocation is tied to the full current-source hash above. Before testing, verify HEAD and an unchanged tracked/untracked source state, close the application and retain the genuine model resources and training-script prerequisite. The evidence collector checks the expected commit and clean source, explicitly requests the native Windows Qt platform, records the full pytest command/log/XML/exit status, and compares source hashes before and after execution. The run is version-matched only when its native-platform probe and source checks succeed. The procedure does not substitute a resource, select a test subset or assign a passing total to an interrupted run. It is a prepared procedure, not an executed Windows result.

**After**: The invocation used the project’s Python environment, an expected-commit check, a clean-source check and an explicitly requested native Windows Qt platform. The command was python -m pytest -ra --tb=long --color=no --junitxml=[EVIDENCE]/pytest.xml, executed through the project virtual environment. The log, XML and exit status were retained. The console summary reports 268.74 seconds; XML reports 268.009 seconds and the outer collector 271.218 seconds. They are separate instrumentation intervals, all concerning software testing rather than model inference. Model identities and original checkpoint sizes are recorded in Appendix E.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 79. Appendix C.1 / Table C.1

**Before**: [New evidence row]

**After**: E22 | 27 Oct 2026 complete Windows log/XML, exit status, runtime probe and source/resource manifests | Revision 3a935ef: 508 passed; 0 failed/errors/skipped; 16 warnings; pytest summary 268.74 s; exit 0.

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 80. Appendix C.1 / Table C.1

**Before**: [New evidence row]

**After**: E23 | 27 Oct 2026 preceding Windows execution at source 8c4830c | 505 distinct cases: 488 passed, 17 failed and 3 teardown errors; exit 1. Retained as the preceding source outcome, not added to the current total.

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 81. Appendix C.2

**Before**: Table C.2 separates the completed Windows baseline from earlier Windows interruptions. The baseline has 370 passes; the 131-case related subset is an independent record and is not added to the complete-suite total. No later source version is assigned that earlier outcome.

**After**: Table C.2 reports the completed current Windows execution separately from earlier Windows invocations. The preceding 8c4830c run had 505 distinct test identities, with 17 failures and 3 teardown errors attached to failing cases; its JUnit aggregate included 508 reports. The current 3a935ef invocation has 508 distinct cases, all passing. The older 131-case subset is an independent record and is not added to either complete-suite total.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 82. Appendix C.2 / Table C.2 header

**Before**: Collection errors

**After**: Errors

**Reason**: Align the recorded result and remaining evaluation boundary with the current Windows evidence.

## 83. Appendix C.2 / Table C.2

**Before**: [New evidence row]

**After**: Windows, 27 Oct 2026; source 8c4830c | 488 | 17 | 3 | 505 distinct cases; teardown errors overlap failed cases. 16 warnings; 389.62 s; exit 1.

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 84. Appendix C.2 / Table C.2

**Before**: [New evidence row]

**After**: Windows, 27 Oct 2026; evaluated source 3a935ef | 508 | 0 | 0 | 508 distinct cases; 0 skipped; 16 warnings; 268.74 s; native Qt; exit 0.

**Reason**: Record actual dated evidence separately; do not add subset counts to the full-suite total.

## 85. Appendix C.2 source

**Before**: Source: Windows log/XML and exit records of 19 October 2026. Incomplete invocations retain their recorded status.

**After**: Source: Windows log/XML and exit records of 19 and 27 October 2026. Interrupted invocations retain their recorded status; source versions and test stages are not conflated.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 86. Appendix D.1

**Before**: For each manual acceptance case record date, tester, final source state, Windows/Python/dependency versions, hardware, actual Qt platform/display metrics, model/input identity, expected outcome, actual outcome and evidence file. The earlier source-startup record and baseline suite do not automatically accept current changes. Table D.1 remains a manual checklist: a Pass requires the specified observed native task record and is not inferred from an older Windows total.

**After**: For each manual acceptance case record date, tester, evaluated source state, Windows/Python/dependency versions, hardware, actual Qt platform/display metrics, model/input identity, expected outcome, actual outcome and evidence file. Table D.1 remains a real-image manual checklist. The completed automated suite is supporting evidence, not a prefilled Pass for human-observed tasks.

**Reason**: Update the source-matched Windows evidence using the completed 27 October log/XML and exit status.

## 87. Appendix E.2

**Before**: [New paragraph]

**After**: The 27 October Windows manifest identifies UPerNet_TME_tissue-panoptils_best_model_100ep.pth as 489,488,187 bytes (466.812 MiB), with SHA-256 b4d8956856800fc44b274244713494f63e2791cd31a1b07b1d5223870b408486. The file was present and unchanged before and after the completed regression. This resource identity does not supply missing segmentation training provenance or predictive IoU/Dice measurements.

**Reason**: Add the newly provided real-file identity without inventing training or prediction-quality evidence.

## 88. 4.3.2 / Table 4.5

**Before**: Native fatal message identified cause; two worker-destruction regressions and 19 October Windows baseline suite passed.

**After**: Native fatal message identified the original cause; worker-destruction regressions also passed in the current 508-case Windows suite.

**Reason**: Use the current passing invocation as the primary verification rather than the older baseline.

## 89. Appendix C.1 heading

**Before**: C.1 Source baseline

**After**: C.1 Evaluated source and evidence

**Reason**: Name the evaluated source directly; older baselines remain dated rows in the evidence history.

## 90. 4.3.1 / Figure 4.12 image

**Before**: Selected 19 October log excerpt showing the earlier 370-pass source.

**After**: Selected unaltered 27 October log lines: 508 collected, 508 passed, 16 warnings, 268.74s; author heading identifies revision 3a935ef.

**Reason**: Match the result illustration to the actual current-source evidence while marking omitted output.
