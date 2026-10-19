# Windows final evidence revision — change log

Content and evidence changes retain the existing Word styles. The final section lists page-reference cache updates only.

## 1. Abstract

**Before:** ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. On 7,180 CRC-VAL-HE-7K patches, the classifier achieved 90.68% accuracy and 88.59% macro-F1 through both the recorded OpenCV/Albumentations pipeline and the application’s default Pillow Single image core, with agreement on all predicted labels. Software regressions and Windows startup records support the implemented workflow, while the Windows full-suite rerun terminated abnormally; UAT, segmentation accuracy, systematic timing and clean-machine deployment remain to be evaluated.

**After:** ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. On 7,180 CRC-VAL-HE-7K patches, the classifier achieved 90.68% accuracy and 88.59% macro-F1 through both the recorded OpenCV/Albumentations pipeline and the application’s default Pillow Single image core, with agreement on all predicted labels. The complete native Windows automated suite passed all 370 tests; UAT, segmentation accuracy, systematic performance measurement and clean-machine deployment remain to be evaluated.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 2. 3.1

**Before:** The application baseline is revision 1f3e01e. Classification methods are documented by the supervisor-provided training code, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C records complete version identifiers and the evidence sources used for each type of result.

**After:** The implementation baseline is revision 1f3e01e, supplemented by the lifecycle and responsive-layout repairs evaluated in the final Windows run. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the evaluated source state and the evidence supporting each result.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 3. 3.3.7

**Before:** [Not present]

**After:** A final lifetime guard also waits for an active worker before Qt destroys its owning widget. Model-validation signals connect to QObject-bound receivers, so destruction disconnects pending callbacks instead of allowing them to access deleted controls. Regression cases cover forced parent deletion and both successful and failed validation signals for built-in models, custom models and task-default settings.

**Reason:** Document the verified implementation and evaluated source state.

## 4. 3.4.4

**Before:** Window fitting uses the current screen's availableGeometry in logical coordinates and checks restored size/position. The implementation distinguishes normal, maximised and fullscreen states and avoids continuously forcing a size during interactive resize. Scroll areas, wrapping and suitable size policies keep child widgets from imposing an oversized application minimum.

**After:** Window fitting uses the current screen’s availableGeometry in logical coordinates and checks restored size/position. The implementation distinguishes normal, maximised and fullscreen states and avoids continuously forcing a size during interactive resize. Inner scroll areas may shrink vertically while Run, Cancel and Re-run retain usable space; their preferred content heights must not stretch the entire three-panel splitter beyond its viewport.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 5. 3.4.4

**Before:** Automated checks cover small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The Windows record dated 19 October 2026 additionally records normal, maximised and minimised states with fullscreen=false in the reported normal/maximised entries. Section 4.3.3 distinguishes those observations from the remaining native acceptance tasks.

**After:** Automated checks cover small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The final native Windows suite also passed the maximise/restore, saved-geometry, comparison/grid and compact-viewport cases. Formal end-to-end acceptance with authorised real images remains a separate activity in Appendix D.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 6. 3.6.3

**Before:** The acceptance cases include both classification modes, segmentation, cancellation, source comparison, Fit/1:1, narrow/wide transitions, maximise/restore, recorded rerun, deletion, export, calendar interaction and task-specific defaults. Development observations motivate regression cases; a formal case receives a Pass status only when its expected outcome has an execution record. The limited Windows observations currently available are reported in Section 4.3.3.

**After:** The acceptance cases include both classification modes, segmentation, cancellation, source comparison, Fit/1:1, narrow/wide transitions, maximise/restore, recorded rerun, deletion, export, calendar interaction and task-specific defaults. A formal case receives a Pass status only when its expected outcome has a completed manual execution record. Section 4.3.3 separates these records from the completed native Windows automated suite.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 7. 3.6.5

**Before:** Automated results are labelled by environment, date and invocation. Linux, 19 October executed 359 tests; the Windows rerun that afternoon also collected 359 but terminated during execution after at least two reported failures. Table 4.3 separates these outcomes from the earlier Windows collection error.

**After:** Automated results are labelled by environment, date and evaluated source state. On 19 October 2026, the final native Windows invocation completed all 370 tests with no failures, errors or skips. A preceding 131-test regression subset also passed; its count is not added to the full-suite total. Table 4.3 retains earlier invocations separately.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 8. 3.6.6

**Before:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify Linux fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**After:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses distinguish completed Windows and Linux automated checks, the recorded classifier evaluation and outstanding manual acceptance, UAT and model studies.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 9. 3.6.6 / Table 3.6

**Before:** Source: named project tests, the Linux test logs dated 17 and 19 October, classification records and Windows execution record; statuses retain their evidence scope.

**After:** Source: named project tests, the environment-labelled Linux records and the completed native Windows full-suite log/XML of 19 October 2026, together with the classifier evaluation.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 10. 3.8

**Before:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses controlled software tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**After:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation combines controlled software tests completed on native Windows, the classification training/test records and source-startup observations; UAT and formal manual acceptance follow separate protocols. Chapter 4 presents these results and their implications.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 11. 4.1

**Before:** This chapter reports implementation and evaluation at revision 1f3e01e. Section 4.2 presents implemented workflows and a distinct classifier evaluation; Section 4.3 reports software tests and native observations; Section 4.4 reserves the UAT results. Environment and date labels distinguish the Linux runs from the Windows execution record.

**After:** This chapter reports the implemented system and the evaluated source state identified in Appendix C. Section 4.2 presents implemented workflows and a distinct classifier evaluation; Section 4.3 reports software tests and native observations; Section 4.4 reserves the UAT results. Environment and date labels identify each completed or interrupted invocation.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 12. 4.3.1

**Before:** On Linux, 19 October 2026, the complete invocation collected 359 tests and recorded 358 passed, 1 failed and no collection errors, with 14 warnings in 104.68 seconds (exit 1). The genuine training script resolved the earlier collection prerequisite. The remaining failure is the built-in-model availability assertion because the real segmentation weight is not present in that installation.

**After:** The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source includes the lifecycle and layout repairs; Appendix C records its baseline and per-file identity.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 13. 4.3.1 / Table 4.3

**Before:** Table 4.3. Automated verification records by date and environment at revision 1f3e01e

**After:** Table 4.3. Automated verification records by environment and evaluated source state

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 14. 4.3.1 / Table 4.3

**Before:** Source: Linux test logs, 17 and 19 October 2026, and the Windows test log, 19 October 2026. Per-invocation totals are independent; related subset counts are not additive.

**After:** Source: dated pytest logs, XML summaries, exit codes and source-state records. The final Windows run began at 22:26 on 19 October 2026 (UTC+08:00); earlier invocations remain separate. Related subset counts are not additive.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 15. 4.3.1

**Before:** The Windows rerun beginning at 15:58 on 19 October collected 359 items after the genuine training script was placed at the expected path. Execution reported failure markers in the history-panel and inference-panel modules, then stopped in the rerun module with exit code 3221226505 (0xC0000409). No final pytest summary or XML report was produced, so final passing and failing totals are unavailable. The log does not contain the failing assertions or a crash stack; targeted diagnostics are required before assigning a cause.

**After:** Before the full invocation, the related Windows subset passed 131 tests in 119.90 seconds with 15 warnings and exit 0. The full command selected no modules or individual cases and used no collection-error continuation. XML confirms 370 distinct passing cases and no skips. The 15 warnings concern deprecated Matplotlib/Pyparsing, PyTorch TypedStorage and Hugging Face download interfaces.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 16. 4.3.1

**Before:** For comparison, Linux, 17 October recorded 355 passed, 1 failed and 1 collection error in 110.70 seconds using continuation after collection errors. The 19 October Linux run used the complete suite without that continuation flag. Suite durations measure test execution, not image inference.

**After:** The final Linux/offscreen invocation after the same repairs completed with 369 passed, 1 failed and no collection errors, with 14 warnings in 125.70 seconds. Its remaining failure checks availability of the real segmentation weight, which was absent from that installation. Earlier 17 and 19 October results in Table 4.3 document earlier source/resource states rather than the final Windows outcome.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 17. 4.3.1

**Before:** The availability assertion checks both built-in model paths. In the Linux installation, the segmentation weight remains missing. The Windows rerun records both files present and their checksums; file availability alone does not establish segmentation inference or accuracy. The separate default-Pillow classifier evaluation completed with exit 0 and is reported in Section 4.2.6.

**After:** The final Windows suite passed the built-in-model availability assertion and the previously affected history, rerun, worker-lifetime and responsive-layout cases. The separate default-Pillow classifier evaluation in Section 4.2.6 supplies predictive measurements; passing software tests and file-availability checks do not measure segmentation accuracy.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 18. 4.3.1

**Before:** The earlier Windows invocation ended during collection with one missing-script error, 13 warnings and exit 2 after 24.76 seconds. Restoring the unchanged training script resolved that collection prerequisite, as the subsequent 359-item collection demonstrates. The later runtime termination is a distinct unresolved issue; it does not reverse the collection repair or establish a completed test suite.

**After:** Earlier Windows invocations stopped first on the missing training-script prerequisite and later on a running-thread destruction fault. Restoring the genuine script and repairing thread lifetime, queued validation receivers and panel size policies resolved those observed failures in the final full invocation. Table 4.5 summarises the implementation causes and regression evidence.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 19. 4.3.2 / Table 4.5

**Before:** Source: implementation changes and associated Linux regression cases at revision 1f3e01e.

**After:** Source: implementation changes and their named regression cases, including the completed native Windows suite of 19 October 2026.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 20. 4.3.2

**Before:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.2.6, while Table 3.6 retains platform-specific software status. The abnormal Windows termination and its reported failures require diagnosis before a completed Windows regression result can be claimed.

**After:** The corrected cases retain their original behavioural checks; the suite additionally includes eleven lifecycle and viewport regression cases introduced during refinement. The Windows maximisation check uses the client area and Qt’s actual native frame margins, while normal/restored full-frame containment remains required. Classification performance is reported separately in Section 4.2.6.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 21. 4.3.3

**Before:** The Windows command .\.venv\Scripts\python.exe main.py recorded loading and validation of the built-in classifier around 14:23:46 on 19 October 2026. Loading completed with source=checkpoint; validation identified DenseNet, task=classification, nine classes and output shape (1, 9), and MainWindow accepted the result. A TypedStorage deprecation warning preceded successful loading. PowerShell’s NativeCommandError wrapper included an INFO message and was followed by continuing application logs, so that wrapper alone is not treated as an application crash.

**After:** Windows source execution recorded successful loading and validation of the built-in classifier at approximately 14:23 on 19 October 2026. Loading completed from the checkpoint; validation identified DenseNet, classification, nine classes and output shape (1, 9), and the main window accepted the model. The later default-Pillow evaluation completed 7,180 real-patch predictions (Section 4.2.6).

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 22. 4.3.3

**Before:** The recorded Qt platform is windows, with devicePixelRatio=2.0 and availableGeometry=[0, 0, 1280, 758] in logical coordinates. A normal-window entry gives geometry=[641, 26, 638, 731], frame=[640, 0, 640, 758] and minimum=[320, 240]. The state record includes normal (maximized=false, fullscreen=false), subsequent maximisation (maximized=true, fullscreen=false) and a later minimised entry. These are observed state transitions; no physical monitor resolution is derived from the logical geometry.

**After:** The source-startup session reported devicePixelRatio=2.0 and availableGeometry=[0, 0, 1280, 758] in Qt logical coordinates, with normal, maximised and minimised state entries. The automated Windows application reported DPR 1.0, logical DPI 168 and availableGeometry=[0, 0, 2560, 1516]. Each record is interpreted within its own Qt application; these logical values are not substituted for a measured physical monitor resolution.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 23. 4.3.3

**Before:** The startup session establishes classifier validation and the stated window observations. A separate command-line evaluation subsequently completed 7,180 real-image predictions through the application’s classification core (Section 4.2.6); it does not supply a GUI task-acceptance record. Restore after maximisation, edge dragging, restart geometry restoration, clipping checks, tiled/segmentation operations and normal exit remain acceptance cases in Appendix D.

**After:** Native Windows automated checks now cover maximise/restore, saved-geometry recovery, repeated narrow/wide comparison, grid alignment and short viewports with accessible Run/Re-run actions. These completed checks resolve the earlier engineering regressions. Appendix D still reserves formal manual outcomes for authorised real-image workflows, real-model cancellation, screenshot verification and the intended display configurations.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 24. 4.4.5

**Before:** Development observations and the Windows startup/state record are discussed in Section 4.3.3. UAT responses will be analysed under the participant and task protocol in Appendix B rather than pooled with those engineering observations.

**After:** The engineering observations, startup record and completed Windows regressions are discussed in Section 4.3. UAT responses will be analysed under the participant and task protocol in Appendix B rather than pooled with software tests.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 25. 4.5.1 / Table 4.9

**Before:** Source: author’s synthesis of the implementation, recorded tests, classifier evaluation and partial Windows runtime evidence.

**After:** Source: the implementation, completed Windows software tests, classifier evaluation and source-startup records; manual acceptance and UAT retain separate statuses.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 26. 4.5.1

**Before:** The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. The Windows CPU evaluation now adds a measured default-path classifier result, while the software-test termination identifies an unresolved regression-validation issue.

**After:** The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. The Windows patch evaluation supplies a measured default-path classifier result, and the 370-test native Windows run verifies the implemented software contracts under the documented test conditions.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 27. 4.5.1

**Before:** H1 has supporting implementation tests, real-classifier loading and patch-level prediction evidence. Linux restoration and rerun checks support the technical component of H3, while the Windows regression termination remains unresolved. H2 and user-efficiency claims await UAT; native task acceptance and real segmentation evaluation limit the system-level conclusions.

**After:** H1 has supporting implementation tests, real-classifier loading and patch-level prediction evidence. Passing native Windows restoration and recorded-rerun checks support the technical component of H3. H2 and user-efficiency claims await UAT; the predictive and system-level limits are consolidated in Section 4.5.3.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 28. 4.5.3

**Before:** Native and user acceptance are incomplete. Windows logs support source startup, classifier validation, patch inference and the observed window states; the full-suite rerun terminated abnormally and needs diagnosis. Restore, resizing, complete control visibility and end-to-end GUI tasks need formal records. UAT, assistive-technology testing and coverage measurement remain uncompleted activities. Section 4.3.1 retains the distinct software outcomes.

**After:** The complete 370-test native Windows suite provides automated regression evidence for the evaluated source state. Formal manual task acceptance and UAT remain incomplete, including authorised real-image screenshots, representative display configurations and real-model workflow observations. Assistive-technology testing and coverage measurement have not been completed. These activities address usability and deployment conditions beyond the controlled software cases.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 29. 4.5.4

**Before:** The immediate priorities are to diagnose the Windows failures and process termination, obtain a completed full-suite result, and complete native acceptance and UAT. The default application patch evaluation is complete; further model work should examine patient/slide grouping, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**After:** The immediate priorities are to complete formal real-image Windows acceptance, collect UAT responses and retain the passing regression suite as the baseline for further changes. The default application patch evaluation is complete; further model work should examine patient/slide grouping, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 30. 4.6

**Before:** ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches, matching the original evaluation labels. Linux, 19 October completed with 358 passed, 1 failed and no collection errors. The Windows rerun resolved collection but terminated during execution; UAT and the remaining validation tasks retain their separate status.

**After:** ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches. The final native Windows full suite completed with 370 passed, 0 failed, 0 errors and 0 skipped; the Linux installation retained one real-segmentation-file availability failure. UAT and the model, performance and deployment limitations remain as specified in Section 4.5.3.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 31. 5.1

**Before:** The Windows application-default Pillow evaluation produced 6,511 correct predictions from 7,180 native-sized test patches, or 90.68% accuracy and 88.59% macro-F1. It matches the original OpenCV/Albumentations evaluation on every predicted label, while probabilities show small numerical differences. This establishes the classifier’s measured Single image core result on the defined collection; software regression and GUI acceptance are separate, with the Windows test termination still unresolved.

**After:** The Windows application-default Pillow evaluation produced 6,511 correct predictions from 7,180 native-sized test patches, or 90.68% accuracy and 88.59% macro-F1. It matches the original OpenCV/Albumentations evaluation on every predicted label, while probabilities show small numerical differences. Separately, all 370 native Windows software tests passed without errors or skips, supporting the implemented loading, inspection, persistence, rerun, cancellation and export contracts. Formal manual acceptance and predictive generalisation retain the limits in Section 4.5.3.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 32. 5.2

**Before:** Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Resolving the Windows regression termination and completing a full invocation are immediate engineering checks, separate from those model studies.

**After:** Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Formal real-image Windows acceptance should complement the completed automated suite, which provides the regression baseline for subsequent development.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 33. 5.4

**Before:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the controlled software tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**After:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. The measured classifier result and the completed 370-test native Windows suite complement source-startup observations. UAT, formal manual acceptance, segmentation evaluation and verified packaging are the next steps toward stronger usability, generalisation and deployment claims.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 34. Appendix A.3

**Before:** Before submission, resolve the Windows regression termination and complete a full test invocation, authorised GUI screenshots, UAT and cover fields. The default-Pillow patch result is now available; subsequent conclusions should retain its dataset and native-size scope. Final formatting and clean-machine packaging claims follow their corresponding review and execution evidence.

**After:** Before submission, complete authorised GUI screenshots, formal manual acceptance, UAT and the remaining cover fields. Retain the completed 370-test Windows result and the default-Pillow patch evaluation with their actual source and dataset scope. Final formatting and clean-machine packaging claims follow their corresponding review and execution evidence.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 35. Appendix C.1

**Before:** Source baseline: revision 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Software results are identified by platform and date: Linux/offscreen Qt on 17 and 19 October 2026 and Windows on 19 October 2026. Table C.1 indexes the implementation, experiment and execution evidence.

**After:** Source baseline: revision 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56, supplemented by the lifecycle and responsive-layout repairs evaluated on 19 October 2026. The passing Windows source state includes changes in nine production modules and four test modules. The evidence package preserves the tracked difference, the thirteen per-file checksums and the reviewed source supplement, including the new worker-lifetime test file; no new software commit is implied. Table C.1 identifies each execution record.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 36. Appendix C.2

**Before:** The evidence archive separates completed invocations, collection failures and abnormal runtime termination. I deployed the selected classification checkpoint under the application filename; its checksum is recorded in Appendix E. The Windows default-Pillow run independently completes inference on the labelled test patches and reproduces the original metrics and predicted labels. The interrupted Windows pytest run remains incomplete despite the resolved collection prerequisite.

**After:** The evidence archive separates the final completed invocations from earlier collection errors, runtime termination and diagnostic subsets. Windows completed 370 tests with no failures, errors or skips; its preceding 131-test subset is not added to that total. Linux completed 369 passing tests and one missing-segmentation-file availability failure. The default-Pillow patch evaluation remains the source of classification metrics, independently of these software-test counts.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 37. Appendix D.1

**Before:** For each acceptance case record date, tester, revision, Windows/Python/dependency versions, hardware, Qt display metrics, model/input identity, expected outcome, actual outcome and evidence file. The 19 October record provides partial W01 startup evidence and partial W02 window-state evidence; restoration and the full action sequences remain unverified. The remaining cases in Table D.1 have no completed acceptance outcome in this record. Their criteria must not be converted into Pass entries from Linux fixture results.

**After:** For each manual acceptance case record date, tester, source state, Windows/Python/dependency versions, hardware, Qt display metrics, model/input identity, expected outcome, actual outcome and evidence file. The source-startup log gives partial manual observations, while the completed Windows suite supplies automated coverage for several corresponding behaviours. Table D.1 remains a manual acceptance checklist: its outcomes require the specified real-image task records and must not be filled from automated test totals alone.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 38. 3.6.6 / Table 3.6

**Before:** Fixture-verified; final representative real files pending

**After:** Windows full-suite image-loading and input-error cases passed; representative real-image manual tasks pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 39. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: structural checks pass; built-in availability fails for missing segmentation weight. Windows classifier validation recorded.

**After:** Windows loader/probe and built-in-path cases passed; real-classifier validation recorded. Arbitrary-model semantic compatibility is outside this check.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 40. 3.6.6 / Table 3.6

**Before:** Linux fixture checks; Windows default-Pillow patch accuracy 90.68%, macro-F1 88.59%; native 224 × 224 input scope in Section 4.2.6

**After:** Windows software cases passed; default-Pillow patch accuracy 90.68%, macro-F1 88.59% on native 224 × 224 inputs (Section 4.2.6).

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 41. 3.6.6 / Table 3.6

**Before:** Crop, mode and actual-area statistics fixture-verified

**After:** Windows crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 42. 3.6.6 / Table 3.6

**Before:** Synthetic segmentation verified; real-weight/ground-truth study pending

**After:** Windows synthetic segmentation geometry/statistics and display cases passed; real-weight demonstration and ground-truth evaluation pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 43. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: coordinate/grid checks; native startup/state observations only; complete Windows case pending

**After:** Windows coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed; formal real-image manual acceptance pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 44. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: persistence checks pass; Windows end-to-end persistence acceptance pending.

**After:** Windows persistence and artifact cases passed with temporary test records; real-image manual workflow evidence pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 45. 3.6.6 / Table 3.6

**Before:** Linux query/calendar checks; Windows history module reported a failure before process termination; assertion detail pending

**After:** Windows query, calendar and history-interaction cases passed; user task outcomes await UAT.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 46. 3.6.6 / Table 3.6

**Before:** Linux recorded-parameter checks; Windows invocation terminated in the rerun module; diagnosis pending

**After:** Windows restore and recorded-model/mode/parameter rerun cases passed; user-efficiency assessment awaits UAT.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 47. 3.6.6 / Table 3.6

**Before:** File/report semantics verified; final Windows report screenshots pending

**After:** Windows file/report and recorded-metadata cases passed; final real-image report screenshots pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 48. 3.6.6 / Table 3.6

**Before:** Safe checkpoint and late-result handling fixture-verified

**After:** Windows cooperative-stop, late-result and destruction/callback lifecycle cases passed; real-model manual cancellation record pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 49. 3.6.6 / Table 3.6

**Before:** Defaults, validation and history isolation fixture-verified

**After:** Windows defaults, validation, preferences and history-isolation cases passed.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 50. 3.6.6 / Table 3.6

**Before:** App-owned cleanup and source preservation fixture-verified

**After:** Windows app-owned artifact cleanup and source-preservation cases passed.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 51. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: Qt fixtures; normal/maximised/minimised Windows states recorded; restore/docking/accessibility pending

**After:** Windows window-state, restore, small-viewport and layout cases passed; multi-monitor/assistive-technology manual acceptance pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 52. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**After:** Windows missing-file/error handling and recorded-parameter cases passed; immutable provenance is not implemented.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 53. 3.6.6 / Table 3.6

**Before:** Local execution established by design; security audit not performed

**After:** Local execution established by design and recorded source startup; security audit not performed.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 54. 3.6.6 / Table 3.6

**Before:** Regression evidence available; benchmark, clean package and coverage pending

**After:** Windows full suite: 370 passed, 0 failed/errors/skipped; repeated benchmark, clean package and coverage measurement pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 55. 3.6.6 / Table 3.6

**Before:** test_cancellation_and_model_defaults.py

**After:** test_cancellation_and_model_defaults.py; test_worker_lifetime.py

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 56. 3.7 / Table 3.7

**Before:** Complete UAT, native rerun and segmentation evaluation; retain each executed result with its environment and date

**After:** Complete UAT, formal real-image Windows acceptance and segmentation evaluation; retain each executed result with its environment and source state.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 57. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** Windows, 19 Oct; final full run

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 58. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 370

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 59. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 0

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 60. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 0

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 61. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 0 skipped; native Qt; 15 warnings; 194.10 s; exit 0. Baseline plus reviewed repairs.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 62. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** Linux, 19 Oct; final full run

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 63. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 369

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 64. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 1

**Reason:** Add the executed result using the existing table styling.

## 65. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 0

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 66. 4.3.1 / Table 4.3

**Before:** [Not present: added row cell]

**After:** 370 collected; 14 warnings; 125.70 s; exit 1. Real segmentation weight unavailable.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 67. 4.3.1 / Table 4.3

**Before:** Linux, 19 Oct 2026

**After:** Linux, 19 Oct; before repairs

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 68. 4.3.1 / Table 4.3

**Before:** Windows, 19 Oct 2026; rerun

**After:** Windows, 19 Oct; 15:58 run

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 69. 4.3.1 / Table 4.4

**Before:** Recorded DPR 2.0; screen geometry reported in logical coordinates

**After:** Startup: DPR 2.0; automation: DPR 1.0, logical DPI 168. Each geometry record uses Qt logical coordinates.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 70. 4.3.2 / Table 4.5

**Before:** Linux loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**After:** Windows default-Pillow patch accuracy 90.68%, macro-F1 88.59%; agreement measured on native 224 × 224 images.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 71. 4.3.2 / Table 4.5

**Before:** Logical screen bounds, scroll areas and height-for-width handling

**After:** Logical screen bounds, inner scrolling, measured legend/card sizes and pinned action space.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 72. 4.3.2 / Table 4.5

**Before:** Linux small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**After:** Windows small-screen/font, maximise/restore and compact-viewport cases passed; formal manual task evidence pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 73. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Worker destroyed during model loading

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 74. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Forced parent deletion bypassed deferred close while a QThread was still running

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 75. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Wait for worker completion before destroying child threads; retain asynchronous normal close

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 76. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Native fatal message identified cause; two worker-destruction regressions and final Windows suite passed.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 77. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Validation callback accessed deleted controls

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 78. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Queued lambda outlived its owning window or settings page

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 79. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Use QObject-bound receivers disconnected with their owner

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 80. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Six successful/error callback lifecycle cases passed for built-in, custom and task-default validation.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 81. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Run/Re-run clipped in short viewports

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 82. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Right-side inner scroll-area height hint enlarged the full three-panel splitter

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 83. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** Allow vertical shrinking of scrolling content; retain pinned action space

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 84. 4.3.2 / Table 4.5

**Before:** [Not present: added row cell]

**After:** 16/30px-scrollbar compact-body regressions and the original 480 × 360 Windows case passed.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 85. 4.5.1 / Table 4.9

**Before:** Local source startup and real-classifier validation recorded on Windows; clean offline package not verified

**After:** Windows source startup and complete 370-test suite passed; clean offline executable remains unverified.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 86. 4.5.1 / Table 4.9

**Before:** Windows real-classifier loading/validation recorded; Linux structural checks pass with one missing-segmentation-file availability failure.

**After:** Windows real-classifier loading/validation and automated loader/path cases passed; semantic safety of arbitrary models is not established.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 87. 4.5.1 / Table 4.9

**Before:** Linux, 19 Oct: Qt fixtures and partial native state observations; formal interaction acceptance and UAT pending

**After:** Native Windows chart, legend, coordinate/grid and comparison regressions passed; formal real-image inspection tasks and UAT pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 88. 4.5.1 / Table 4.9

**Before:** Linux, 19 Oct: temporary-artifact/report tests pass; current Windows export demonstration pending

**After:** Native Windows temporary-artifact/report cases passed; real-image export demonstration pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 89. 4.5.1 / Table 4.9

**Before:** Linux, 19 Oct: controlled persistence checks; immutable provenance and backup not implemented

**After:** Native Windows persistence/artifact regressions passed; immutable per-run identities and backup not implemented.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 90. 4.5.1 / Table 4.9

**Before:** Linux recorded-parameter checks; Windows history failure and runtime termination unresolved; efficiency awaits UAT

**After:** Native Windows search, calendar, restore and recorded-parameter rerun cases passed; efficiency awaits UAT.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 91. Appendix A / Table A.3

**Before:** Project ui/, core/ and data/ modules with Linux regression tests

**After:** Project modules and completed 370-test native Windows run

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 92. Appendix A / Table A.3

**Before:** Current documented baseline

**After:** Baseline plus lifecycle/layout repairs; evaluated source identified in Appendix C

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 93. Appendix A / Table A.3

**Before:** Partial Windows startup/state record; no UAT responses or complete native acceptance record

**After:** Windows automated regressions complete; source startup recorded; no UAT responses or completed manual task sheets

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 94. Appendix A / Table A.3

**Before:** Partial native evidence; formal acceptance and UAT pending

**After:** Automated Windows verification complete; formal manual acceptance and UAT pending

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 95. Appendix A / Table A.3

**Before:** [Not present: added row cell]

**After:** Native Windows full-suite regression

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 96. Appendix A / Table A.3

**Before:** [Not present: added row cell]

**After:** Final log/XML/exit code; 370 distinct passing cases; source identity recorded

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 97. Appendix A / Table A.3

**Before:** [Not present: added row cell]

**After:** Completed on 19 Oct 2026; 0 failures, errors or skips

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 98. Appendix C / Table C.1

**Before:** 17 and 19 Oct Linux logs; 19 Oct Windows collection and runtime records

**After:** Dated Linux and Windows collection, runtime, subset and complete-suite records

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 99. Appendix C / Table C.1

**Before:** 359 items collected; at least two failure markers and abnormal termination; final totals unavailable

**After:** Earlier 359-item invocation stopped with no final totals; failure paths subsequently repaired and exercised in the final suite

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 100. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** E18

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 101. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** 19 Oct, 22:24 Windows related log/XML, exit code and Qt snapshot

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 102. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** 131 passed; native windows platform; independent subset, not added to the full-suite total

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 103. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** E19

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 104. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** 19 Oct, 22:26 Windows full log/XML, exit code, Qt snapshot and source hashes

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 105. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** 370 passed; 0 failed/errors/skipped; 15 warnings; 194.10s; evaluated baseline plus repairs

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 106. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** E20

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 107. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** Final 19 Oct Linux full log/XML and source supplement

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 108. Appendix C / Table C.1

**Before:** [Not present: added row cell]

**After:** 369 passed, 1 missing-real-segmentation-file failure, 0 collection errors; no skipped tests

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 109. 5.3

**Before:** The fourth contribution is an auditable evaluation package connecting requirements, named software tests, the classification training/test outputs and platform-specific execution records. It includes per-class metrics and a confusion matrix, explicit unresolved test prerequisites, and prepared UAT instruments. The work contributes an engineering integration and its documented evaluation rather than a new neural architecture.

**After:** The fourth contribution is an evaluation package linking requirements, named software tests, the classification training/test outputs and platform-specific execution records. It includes class-wise metrics, a confusion matrix, the completed native Windows suite and prepared UAT instruments. The work contributes an engineering integration and its documented evaluation rather than a new neural architecture.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 110. 3.2.2 / Table 3.2

**Before:** Partial native state observations recorded; complete device/accessibility acceptance pending

**After:** Native Windows automated layout/window-state checks passed; complete device/accessibility manual acceptance pending.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 111. 3.7 / Table 3.7

**Before:** Confirm source scale, deployed-backend input equivalence and dataset grouping; retain supplied checkpoint checksum

**After:** Confirm physical scale, resampling beyond native-sized patches and dataset grouping; retain the selected checkpoint checksum.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 112. 4.3.1 / Figure 4.12

**Before:** Figure 4.12. Pytest log excerpt (Linux, 17 October 2026). Source: saved Linux/offscreen-Qt log; current Linux and Windows outcomes are reported in Table 4.3.

**After:** Figure 4.12. Completed Windows pytest report, 19 October 2026. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**Reason:** Synchronise the manuscript with the completed native Windows regression and its evidence scope.

## 113. 4.3.1 / Figure 4.12 content

**Before:** Reproduced 17 October Linux report with 355 passed / 1 failed / 1 collection error.

**After:** Selected genuine Windows full-suite lines: collected 370 items; 370 passed, 15 warnings in 194.10s. Omissions are explicitly marked.

**Reason:** Show the completed Windows outcome in the main results figure, retaining earlier records in the table and appendix; do not invent a GUI screenshot.

## 114. Contents / figure-table list label

**Before:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.

**After:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: the classification experiment’s saved matrix; the Windows default-Pillow predictions independently reproduce every count. Rows are true labels and columns predicted labels.

**Reason:** Synchronise visible entry with its existing linked heading/caption, preserving the field and style.

## 115. Contents / figure-table list label

**Before:** Figure 4.12. Pytest log excerpt (Linux, 17 October 2026). Source: saved Linux/offscreen-Qt log; current Linux and Windows outcomes are reported in Table 4.3.

**After:** Figure 4.12. Completed Windows pytest report, 19 October 2026. Source: the recorded full-suite log; selected text is reproduced with omissions marked.

**Reason:** Synchronise visible entry with its existing linked heading/caption, preserving the field and style.

## 116. Contents / figure-table list label

**Before:** Table 4.3. Automated verification records by date and environment at revision 1f3e01e

**After:** Table 4.3. Automated verification records by environment and evaluated source state

**Reason:** Synchronise visible entry with its existing linked heading/caption, preserving the field and style.

## 117. Contents / figure-table list page cache: head_67

**Before:** 41

**After:** 42

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 118. Contents / figure-table list page cache: head_70

**Before:** 46

**After:** 47

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 119. Contents / figure-table list page cache: head_71

**Before:** 46

**After:** 47

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 120. Contents / figure-table list page cache: head_72

**Before:** 46

**After:** 47

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 121. Contents / figure-table list page cache: head_73

**Before:** 46

**After:** 47

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 122. Contents / figure-table list page cache: head_74

**Before:** 47

**After:** 48

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 123. Contents / figure-table list page cache: head_75

**Before:** 48

**After:** 49

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 124. Contents / figure-table list page cache: head_76

**Before:** 48

**After:** 49

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 125. Contents / figure-table list page cache: head_77

**Before:** 49

**After:** 50

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 126. Contents / figure-table list page cache: new_4_3_4_Classification_training_and_test

**Before:** 51

**After:** 52

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 127. Contents / figure-table list page cache: head_78

**Before:** 56

**After:** 57

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 128. Contents / figure-table list page cache: head_79

**Before:** 56

**After:** 57

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 129. Contents / figure-table list page cache: head_80

**Before:** 58

**After:** 59

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 130. Contents / figure-table list page cache: head_81

**Before:** 60

**After:** 61

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 131. Contents / figure-table list page cache: new_4_3_5_Runtime_and_deployment_verificat

**Before:** 60

**After:** 62

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 132. Contents / figure-table list page cache: head_82

**Before:** 61

**After:** 62

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 133. Contents / figure-table list page cache: head_83

**Before:** 61

**After:** 62

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 134. Contents / figure-table list page cache: head_84

**Before:** 62

**After:** 63

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 135. Contents / figure-table list page cache: head_85

**Before:** 62

**After:** 64

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 136. Contents / figure-table list page cache: head_86

**Before:** 63

**After:** 64

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 137. Contents / figure-table list page cache: head_87

**Before:** 63

**After:** 65

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 138. Contents / figure-table list page cache: head_88

**Before:** 64

**After:** 65

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 139. Contents / figure-table list page cache: head_89

**Before:** 64

**After:** 65

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 140. Contents / figure-table list page cache: head_90

**Before:** 65

**After:** 67

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 141. Contents / figure-table list page cache: head_91

**Before:** 66

**After:** 67

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 142. Contents / figure-table list page cache: head_92

**Before:** 67

**After:** 68

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 143. Contents / figure-table list page cache: head_93

**Before:** 67

**After:** 69

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 144. Contents / figure-table list page cache: head_94

**Before:** 68

**After:** 70

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 145. Contents / figure-table list page cache: head_95

**Before:** 68

**After:** 70

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 146. Contents / figure-table list page cache: head_96

**Before:** 69

**After:** 71

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 147. Contents / figure-table list page cache: head_97

**Before:** 69

**After:** 71

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 148. Contents / figure-table list page cache: head_98

**Before:** 70

**After:** 72

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 149. Contents / figure-table list page cache: head_99

**Before:** 71

**After:** 73

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 150. Contents / figure-table list page cache: head_100

**Before:** 74

**After:** 76

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 151. Contents / figure-table list page cache: head_101

**Before:** 74

**After:** 76

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 152. Contents / figure-table list page cache: head_102

**Before:** 74

**After:** 76

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 153. Contents / figure-table list page cache: head_103

**Before:** 79

**After:** 81

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 154. Contents / figure-table list page cache: head_104

**Before:** 80

**After:** 82

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 155. Contents / figure-table list page cache: head_105

**Before:** 80

**After:** 83

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 156. Contents / figure-table list page cache: head_106

**Before:** 80

**After:** 83

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 157. Contents / figure-table list page cache: head_107

**Before:** 81

**After:** 83

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 158. Contents / figure-table list page cache: head_108

**Before:** 81

**After:** 83

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 159. Contents / figure-table list page cache: head_109

**Before:** 82

**After:** 85

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 160. Contents / figure-table list page cache: head_110

**Before:** 83

**After:** 85

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 161. Contents / figure-table list page cache: head_111

**Before:** 83

**After:** 85

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 162. Contents / figure-table list page cache: head_112

**Before:** 84

**After:** 86

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 163. Contents / figure-table list page cache: head_113

**Before:** 84

**After:** 86

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 164. Contents / figure-table list page cache: head_114

**Before:** 85

**After:** 88

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 165. Contents / figure-table list page cache: head_115

**Before:** 85

**After:** 88

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 166. Contents / figure-table list page cache: head_116

**Before:** 85

**After:** 88

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 167. Contents / figure-table list page cache: head_117

**Before:** 87

**After:** 89

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 168. Contents / figure-table list page cache: head_118

**Before:** 87

**After:** 89

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 169. Contents / figure-table list page cache: head_119

**Before:** 87

**After:** 89

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 170. Contents / figure-table list page cache: head_120

**Before:** 88

**After:** 90

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 171. Contents / figure-table list page cache: head_121

**Before:** 88

**After:** 90

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 172. Contents / figure-table list page cache: cap_Figure_4_1

**Before:** 46

**After:** 47

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 173. Contents / figure-table list page cache: cap_Figure_4_2

**Before:** 47

**After:** 48

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 174. Contents / figure-table list page cache: cap_Figure_4_3

**Before:** 48

**After:** 49

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 175. Contents / figure-table list page cache: cap_Figure_4_4

**Before:** 48

**After:** 49

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 176. Contents / figure-table list page cache: cap_Figure_4_5

**Before:** 49

**After:** 50

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 177. Contents / figure-table list page cache: cap_Figure_4_6

**Before:** 49

**After:** 50

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 178. Contents / figure-table list page cache: cap_Figure_4_7

**Before:** 50

**After:** 51

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 179. Contents / figure-table list page cache: cap_Figure_4_8

**Before:** 50

**After:** 51

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 180. Contents / figure-table list page cache: cap_Figure_4_9

**Before:** 51

**After:** 52

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 181. Contents / figure-table list page cache: new_Figure_4_11__Classification_training_a

**Before:** 52

**After:** 53

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 182. Contents / figure-table list page cache: new_Figure_4_12__Nine_class_confusion_matr

**Before:** 54

**After:** 55

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 183. Contents / figure-table list page cache: cap_Figure_4_10

**Before:** 58

**After:** 59

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 184. Contents / figure-table list page cache: new_Table_4_4__Classification_evaluation_s

**Before:** 52

**After:** 53

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 185. Contents / figure-table list page cache: new_Table_4_5__Class_wise_classification_p

**Before:** 53

**After:** 54

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 186. Contents / figure-table list page cache: cap_Table_4_1

**Before:** 56

**After:** 57

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 187. Contents / figure-table list page cache: new_Table_4_2__Windows_test_host_and_actua

**Before:** 57

**After:** 58

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 188. Contents / figure-table list page cache: cap_Table_4_2

**Before:** 58

**After:** 59

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 189. Contents / figure-table list page cache: cap_Table_4_3

**Before:** 61

**After:** 62

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 190. Contents / figure-table list page cache: cap_Table_4_4

**Before:** 62

**After:** 63

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 191. Contents / figure-table list page cache: cap_Table_4_5

**Before:** 62

**After:** 64

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 192. Contents / figure-table list page cache: cap_Table_4_6

**Before:** 64

**After:** 65

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 193. Contents / figure-table list page cache: cap_Table_A_1

**Before:** 74

**After:** 76

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 194. Contents / figure-table list page cache: cap_Table_A_2

**Before:** 76

**After:** 78

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 195. Contents / figure-table list page cache: cap_Table_A_3

**Before:** 79

**After:** 81

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 196. Contents / figure-table list page cache: cap_Table_B_1

**Before:** 81

**After:** 83

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 197. Contents / figure-table list page cache: cap_Table_C_1

**Before:** 84

**After:** 86

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.

## 198. Contents / figure-table list page cache: cap_Table_D_1

**Before:** 86

**After:** 88

**Reason:** Refresh the existing page field from the final PDF; retain field instructions, styles and numbering.
