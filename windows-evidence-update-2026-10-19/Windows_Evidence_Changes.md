# Windows evidence content update

## 1. Abstract

**Before:** ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. The trained nine-class DenseNet recorded 90.68% accuracy and 88.59% macro-F1 on 7,180 CRC-VAL-HE-7K images using the OpenCV/Albumentations evaluation pipeline, while software regression tests and Windows startup logs support distinct implementation claims. The contribution is an inspectable educational/research workflow; predictive evaluation through the application’s default Pillow pathway, UAT, segmentation accuracy, systematic timing and clean-machine deployment remain separate verification tasks.

**After:** ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. On 7,180 CRC-VAL-HE-7K patches, the classifier achieved 90.68% accuracy and 88.59% macro-F1 through both the recorded OpenCV/Albumentations pipeline and the application’s default Pillow Single image core, with agreement on all predicted labels. Software regressions and Windows startup records support the implemented workflow, while the Windows full-suite rerun terminated abnormally; UAT, segmentation accuracy, systematic timing and clean-machine deployment remain to be evaluated.

**Reason:** Synchronise the narrative with the verified Windows records.

## 2. 3.3.3

**Before:** The recorded evaluation environment used Albumentations 1.3.1 and OpenCV 4.8.1. Its transform calls A.Resize(224, 224) without overriding interpolation, using the library’s default linear resize. Pillow bilinear and OpenCV INTER_LINEAR can differ in resampling and rounding; the application preserves its legacy Pillow default and records the selected backend. Section 4.2.6 therefore attributes the reported model metrics to the recorded Albumentations evaluation pipeline.

**After:** The original evaluation used Albumentations 1.3.1 and OpenCV 4.8.1, with A.Resize(224, 224) retaining its default linear interpolation. Pillow bilinear and OpenCV INTER_LINEAR can differ when resampling is necessary. A Windows rerun through the default Pillow pathway is now reported in Section 4.2.6; all 7,180 source patches were already 224 × 224, so this run validates the native-sized patch pathway rather than general equivalence when larger crops are resized.

**Reason:** Synchronise the narrative with the verified Windows records.

## 3. 3.6.5

**Before:** Automated results are labelled by environment and date. The Linux run of 19 October collected and executed 359 tests after genuine classification resources were installed; the Windows run of that date stopped during collection and requires a native rerun. Table 4.3 retains their separate outcomes.

**After:** Automated results are labelled by environment, date and invocation. Linux, 19 October executed 359 tests; the Windows rerun that afternoon also collected 359 but terminated during execution after at least two reported failures. Table 4.3 separates these outcomes from the earlier Windows collection error.

**Reason:** Synchronise the narrative with the verified Windows records.

## 4. 4.2.6 / Table 4.1

**Before:** Source: metrics.csv, test-7k/summary.json and test-7k/predictions.csv from the classification experiment; values were cross-checked by recomputing the recorded predictions.

**After:** Source: the classification experiment’s metrics.csv and test-7k outputs, together with the Windows default-Pillow evaluation of 19 October 2026. Per-image predictions from both runs reproduce the displayed aggregate results.

**Reason:** Synchronise the narrative with the verified Windows records.

## 5. 4.2.6 / Table 4.2

**Before:** Source: classification_report.csv, cross-checked against the per-image predictions; support is the number of true-class test images. Rounded displayed values may differ slightly from calculations using the full-precision CSV.

**After:** Source: class-wise reports and per-image predictions from the original evaluation and Windows default-Pillow rerun. Both runs give the same class counts and metrics; support is the number of true-class images. Displayed values are rounded.

**Reason:** Synchronise the narrative with the verified Windows records.

## 6. 4.2.6 / Figure 4.11

**Before:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.

**After:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: the classification experiment’s saved matrix; the Windows default-Pillow predictions independently reproduce every count. Rows are true labels and columns predicted labels.

**Reason:** Synchronise the narrative with the verified Windows records.

## 7. 4.2.6

**Before:** The selected-epoch validation accuracy exceeds test accuracy by approximately 8.41 percentage points. Internal validation draws from the same 100,000-image pool as training, whereas the 7,180-image test is a separate collection. Class proportions also differ: ADI represents 10.41% of the 100K pool versus 18.64% of the test set, DEB 11.51% versus 4.72%, and MUS 13.54% versus 8.25%. These observed sampling differences make the two evaluations distinct, although they do not identify a single cause of the performance gap. Both validation and test scripts specify deterministic Resize, ToTensorV2 and float32 raw255; comparison with the application’s Pillow backend is a separate validation question.

**After:** The selected-epoch validation accuracy exceeds test accuracy by approximately 8.41 percentage points. Internal validation draws from the same 100,000-image pool as training, whereas the 7,180-image test is a separate collection. Class proportions also differ: ADI represents 10.41% of the 100K pool versus 18.64% of the test set, DEB 11.51% versus 4.72%, and MUS 13.54% versus 8.25%. These observed differences do not identify a single cause of the gap. Both validation and original test scripts use deterministic Resize, ToTensorV2 and float32 raw255; the Windows application-path rerun produces the same test labels and does not explain away that gap.

**Reason:** Synchronise the narrative with the verified Windows records.

## 8. 4.2.6

**Before:** All 7,180 prediction rows have consistent class argmax, maximum softmax score and probability sums. Recalculated accuracy, macro-F1, per-class values and confusion counts agree with the saved reports, and the selected weight hash agrees with summary.json. This is a consistency verification of recorded evaluation outputs, not a fresh inference rerun on the original test images. Appendix E records the complete checksum and preprocessing/dependency details.

**After:** Both prediction CSVs contain 7,180 unique image paths with matching true labels, valid class argmax, maximum softmax score and probability sums. Recalculation gives 6,511 correct predictions, 90.682451% accuracy and 88.587944% macro-F1 for each run. Every class-wise metric and confusion-matrix entry agrees. The deployed classifier has the same checkpoint checksum as the original evaluated model; Appendix E records the execution configurations.

**Reason:** Synchronise the narrative with the verified Windows records.

## 9. 4.2.6

**Before:** [Not present]

**After:** On 19 October 2026, I evaluated the labelled patches on Windows through the project’s ModelLoader, Preprocessor and OutputParser using the unchanged Pillow default, RGB float32 raw255, a 224 × 224 input and CPU batch size 1. All source patches were already 224 × 224. Input diagnostics against the installed OpenCV decoder and INTER_LINEAR produced zero tensor differences; the reference comparison retained all 7,180 predicted labels. Probability vectors were not identical: the maximum absolute probability difference was 0.002732. This comparison confirms native-sized patch predictions across the recorded runs, without establishing identical numerical output or resize behaviour at other source sizes.

**Reason:** Add the executed application-default evaluation with its actual scope.

## 10. 4.2.6

**Before:** The results apply to the recorded OpenCV/Albumentations raw255 pipeline. The legacy application default remains Pillow bilinear; arbitrary 512-pixel source crops and tiled coverage require their own scale and ground-truth design. Patient/slide isolation and backend equivalence are limitations discussed in Section 4.5.3.

**After:** The application-default Single image core therefore has a measured result on this labelled patch collection. Arbitrary 512-pixel source crops, tiled maps and physical-scale changes require their own ground-truth and scale design. Patient/slide independence and these generalisation limits are discussed in Section 4.5.3.

**Reason:** Synchronise the narrative with the verified Windows records.

## 11. 4.3.1

**Before:** On Windows, 19 October 2026, collection reported 356 items and one error before test execution could complete: 13 warnings, 1 error, 24.76 seconds and exit 2. No passing count was obtained for that invocation. The native rerun procedure restores the unchanged training script and records a new full result; its outcome will be reported only after execution.

**After:** The Windows rerun beginning at 15:58 on 19 October collected 359 items after the genuine training script was placed at the expected path. Execution reported failure markers in the history-panel and inference-panel modules, then stopped in the rerun module with exit code 3221226505 (0xC0000409). No final pytest summary or XML report was produced, so final passing and failing totals are unavailable. The log does not contain the failing assertions or a crash stack; targeted diagnostics are required before assigning a cause.

**Reason:** Synchronise the narrative with the verified Windows records.

## 12. 4.3.1

**Before:** The availability test checks both real built-in model files. In the Linux rerun, the supplied classifier is present but the segmentation weight remains unavailable, so that assertion still fails. The Windows startup log establishes classifier loading separately; it does not establish the outcome of a test interrupted before execution.

**After:** The availability assertion checks both built-in model paths. In the Linux installation, the segmentation weight remains missing. The Windows rerun records both files present and their checksums; file availability alone does not establish segmentation inference or accuracy. The separate default-Pillow classifier evaluation completed with exit 0 and is reported in Section 4.2.6.

**Reason:** Synchronise the narrative with the verified Windows records.

## 13. 4.3.1

**Before:** The Windows collection error concerned the expected classification training-script path. The resume checks read that script and extract normalize_model_settings and validate_resume_config; placing the genuine file at the expected location lets all three resume checks pass in Linux. The Windows wrapper verifies the script checksum and preserves any different existing file before running the unchanged full suite.

**After:** The earlier Windows invocation ended during collection with one missing-script error, 13 warnings and exit 2 after 24.76 seconds. Restoring the unchanged training script resolved that collection prerequisite, as the subsequent 359-item collection demonstrates. The later runtime termination is a distinct unresolved issue; it does not reverse the collection repair or establish a completed test suite.

**Reason:** Synchronise the narrative with the verified Windows records.

## 14. 4.3.2

**Before:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.2.6, and Table 3.6 retains the environment-specific scope of the software tests. The current collection error prevents a claim that the latest Windows full suite passed.

**After:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.2.6, while Table 3.6 retains platform-specific software status. The abnormal Windows termination and its reported failures require diagnosis before a completed Windows regression result can be claimed.

**Reason:** Synchronise the narrative with the verified Windows records.

## 15. 4.3.3

**Before:** This session establishes startup, real-classifier structural validation and the stated window-state observations. It contains no completed image inference or formal all-feature acceptance record. Restore after maximisation, edge dragging, restart geometry restoration, clipping checks and normal exit remain acceptance cases in Appendix D.

**After:** The startup session establishes classifier validation and the stated window observations. A separate command-line evaluation subsequently completed 7,180 real-image predictions through the application’s classification core (Section 4.2.6); it does not supply a GUI task-acceptance record. Restore after maximisation, edge dragging, restart geometry restoration, clipping checks, tiled/segmentation operations and normal exit remain acceptance cases in Appendix D.

**Reason:** Synchronise the narrative with the verified Windows records.

## 16. 4.4.4

**Before:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the Linux suite duration of 110.70 seconds on 17 October is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**After:** Test-suite durations and the diagnostic evaluation-loop duration are excluded from inference latency claims. The Windows evaluation includes input comparison and CSV writing, and no repeated stage-level benchmark has been recorded. Runtime observations in UAT will be reported separately from the protocol in Appendix E.3.

**Reason:** Synchronise the narrative with the verified Windows records.

## 17. 4.5.1

**Before:** The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. Classification evaluation supplies additional model evidence, while the latest Windows record supplies startup and state evidence under a CPU-only runtime.

**After:** The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. The Windows CPU evaluation now adds a measured default-path classifier result, while the software-test termination identifies an unresolved regression-validation issue.

**Reason:** Synchronise the narrative with the verified Windows records.

## 18. 4.5.1

**Before:** H1 is supported by the controlled implementation tests and real-classifier loading on Windows. The Linux restoration and rerun checks support the technical component of H3. H2 and user-efficiency claims await UAT, while native acceptance and real segmentation availability limit the present system-level conclusions.

**After:** H1 has supporting implementation tests, real-classifier loading and patch-level prediction evidence. Linux restoration and rerun checks support the technical component of H3, while the Windows regression termination remains unresolved. H2 and user-efficiency claims await UAT; native task acceptance and real segmentation evaluation limit the system-level conclusions.

**Reason:** Synchronise the narrative with the verified Windows records.

## 19. 4.5.3

**Before:** Classification performance is specific to its data and preprocessing. The 90.68% accuracy and 88.59% macro-F1 describe the recorded OpenCV/Albumentations patch evaluation. The application defaults to Pillow bilinear, and its source crops may differ in field of view; evaluation through that exact pathway is still required. Stratified patch-level splitting and disjoint file paths do not establish patient/slide independence or exclude content duplicates. Calibration and tiled-map ground truth were not evaluated.

**After:** Classification performance is specific to its data and preprocessing. The 90.68% accuracy and 88.59% macro-F1 are reproduced by the original evaluation and the application-default Single image core on native 224 × 224 test patches. That agreement does not establish performance after resizing arbitrary source crops or under different physical scales. Stratified patch-level splitting and disjoint file paths do not establish patient/slide independence or exclude content duplicates. Calibration and tiled-map ground truth were not evaluated.

**Reason:** Synchronise the narrative with the verified Windows records.

## 20. 4.5.3

**Before:** Native and user acceptance are incomplete. Windows logs support source startup, classifier validation and the observed window states, while restore, resizing, complete control visibility and end-to-end tasks need formal records. UAT, assistive-technology testing and coverage measurement remain uncompleted evaluation activities. The environment-specific software outcomes are reported in Section 4.3.1.

**After:** Native and user acceptance are incomplete. Windows logs support source startup, classifier validation, patch inference and the observed window states; the full-suite rerun terminated abnormally and needs diagnosis. Restore, resizing, complete control visibility and end-to-end GUI tasks need formal records. UAT, assistive-technology testing and coverage measurement remain uncompleted activities. Section 4.3.1 retains the distinct software outcomes.

**Reason:** Synchronise the narrative with the verified Windows records.

## 21. 4.5.4

**Before:** The immediate priorities are to execute the prepared Windows full-suite rerun, evaluate the default application classifier on the available test images, and complete native acceptance and UAT. Further model work should establish archive identity, patient/slide grouping and source scale; segmentation evaluation requires authorised aligned masks.

**After:** The immediate priorities are to diagnose the Windows failures and process termination, obtain a completed full-suite result, and complete native acceptance and UAT. The default application patch evaluation is complete; further model work should examine patient/slide grouping, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**Reason:** Synchronise the narrative with the verified Windows records.

## 22. 4.6

**Before:** ZY-Path implements model-aware inference, spatial inspection and record continuity. The recorded OpenCV/Albumentations classifier evaluation gives 90.68% accuracy and 88.59% macro-F1; these are not yet a measurement of the default application pathway. Linux, 19 October completed with 358 passed, 1 failed and no collection errors. Windows startup is documented, while the Windows full-suite rerun, UAT and the remaining validation tasks retain their separate status.

**After:** ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches, matching the original evaluation labels. Linux, 19 October completed with 358 passed, 1 failed and no collection errors. The Windows rerun resolved collection but terminated during execution; UAT and the remaining validation tasks retain their separate status.

**Reason:** Synchronise the narrative with the verified Windows records.

## 23. 5.1

**Before:** Using the recorded OpenCV/Albumentations pipeline, the classifier produced 6,511 correct predictions from 7,180 images, or 90.68% accuracy and 88.59% macro-F1. This supports the trained model under that evaluation configuration; accuracy through the application’s default Pillow pathway remains to be measured. Software tests and Windows startup observations address implementation behaviour separately, as reported in Chapter 4.

**After:** The Windows application-default Pillow evaluation produced 6,511 correct predictions from 7,180 native-sized test patches, or 90.68% accuracy and 88.59% macro-F1. It matches the original OpenCV/Albumentations evaluation on every predicted label, while probabilities show small numerical differences. This establishes the classifier’s measured Single image core result on the defined collection; software regression and GUI acceptance are separate, with the Windows test termination still unresolved.

**Reason:** Synchronise the narrative with the verified Windows records.

## 24. 5.2

**Before:** Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, preprocessing equivalence and segmentation against authorised masks. Immediate completion checks are specified in Section 4.3.1 and Appendix E.

**After:** Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Resolving the Windows regression termination and completing a full invocation are immediate engineering checks, separate from those model studies.

**Reason:** Synchronise the narrative with the verified Windows records.

## 25. Appendix A

**Before:** Before submission, complete the prepared Windows rerun and default-Pillow evaluation, authorised application screenshots, UAT and cover fields. Update the model/application evidence separately, then refresh the conclusions and document fields from the actual results. Final formatting and any clean-machine packaging claims follow their corresponding review and execution evidence.

**After:** Before submission, resolve the Windows regression termination and complete a full test invocation, authorised GUI screenshots, UAT and cover fields. The default-Pillow patch result is now available; subsequent conclusions should retain its dataset and native-size scope. Final formatting and clean-machine packaging claims follow their corresponding review and execution evidence.

**Reason:** Synchronise the narrative with the verified Windows records.

## 26. Appendix C.2

**Before:** The evidence archive distinguishes executed tests from collection errors and separates software fixtures from real-model predictions. I deployed the selected classification checkpoint under the application filename; its checksum is recorded in Appendix E. The original evaluation CSVs reproduce the reported aggregate metrics, while a fresh application-pipeline run is a distinct evaluation. Windows logs establish only the actions they record.

**After:** The evidence archive separates completed invocations, collection failures and abnormal runtime termination. I deployed the selected classification checkpoint under the application filename; its checksum is recorded in Appendix E. The Windows default-Pillow run independently completes inference on the labelled test patches and reproduces the original metrics and predicted labels. The interrupted Windows pytest run remains incomplete despite the resolved collection prerequisite.

**Reason:** Synchronise the narrative with the verified Windows records.

## 27. Appendix E.1

**Before:** The recorded test preprocessing was OpenCV RGB decoding followed by Albumentations 1.3.1 Resize(224, 224), ToTensorV2 and float32 raw255, with OpenCV 4.8.1. The environment record lists Python 3.10.22, PyTorch 2.1.2+cu121, torchvision 0.16.2+cu121 and scikit-learn 1.3.2. Accuracy, macro-F1, class metrics and confusion counts were recomputed from the prediction CSV and agree with the report. Future evaluations should document patient/slide grouping, content-duplicate checks, physical scale and backend equivalence, and define separate ground truth for Tiled analysis.

**After:** The original test used OpenCV RGB decoding followed by Albumentations 1.3.1 Resize(224, 224), ToTensorV2 and float32 raw255, with OpenCV 4.8.1. Its environment lists Python 3.10.22, PyTorch 2.1.2+cu121, torchvision 0.16.2+cu121 and scikit-learn 1.3.2. The Windows rerun used the application’s default Pillow pathway on CPU: Python 3.10.22, PyTorch 2.1.2+cpu, Pillow 10.4.0, NumPy 1.26.4 and OpenCV 4.11.0 for the input diagnostic. Both use the same nine-class order and checkpoint.

**Reason:** Synchronise the narrative with the verified Windows records.

## 28. Appendix E.1

**Before:** [Not present]

**After:** The Windows summary records Single image, pillow_bilinear, RGB float32 raw255, input size 224 × 224 and 7,180 native 224 × 224 source images. Per-image CSVs independently reproduce 6,511 correct labels, the class-wise report and the confusion counts. All reference labels agree; the largest absolute probability difference is 0.002731651. This run does not exercise resizing of larger crops. Future studies should document patient/slide grouping, duplicate checks and physical scale, and define separate ground truth for Tiled analysis.

**Reason:** Add the executed application-default evaluation with its actual scope.

## 29. 4.2.6 / Table 4.1

**Before:** Recomputed from predictions.csv

**After:** Both runs: independently recomputed from their prediction CSVs

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 30. 4.2.6 / Table 4.1

**Before:** 6,511 / 7,180

**After:** Original and default-Pillow runs: 6,511 / 7,180

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 31. 4.2.6 / Table 4.1

**Before:** Unweighted mean of nine class F1 values

**After:** Both runs; unweighted mean of nine class F1 values

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 32. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** Default application input

**Reason:** Add the newly executed record using the existing table styling.

## 33. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** 7,180 native 224 × 224 RGB patches

**Reason:** Add the newly executed record using the existing table styling.

## 34. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** Pillow; float32 raw255; CPU batch 1

**Reason:** Add the newly executed record using the existing table styling.

## 35. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** Prediction agreement

**Reason:** Add the newly executed record using the existing table styling.

## 36. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** 7,180 / 7,180 reference labels

**Reason:** Add the newly executed record using the existing table styling.

## 37. 4.2.6 / Table 4.1

**Before:** [Not present: new table row cell]

**After:** Max probability difference: 0.002732

**Reason:** Add the newly executed record using the existing table styling.

## 38. 4.3.1 / Table 4.3

**Before:** [Not present: new table row cell]

**After:** Windows, 19 Oct 2026; rerun

**Reason:** Record the new invocation without inventing final totals.

## 39. 4.3.1 / Table 4.3

**Before:** [Not present: new table row cell]

**After:** Not final

**Reason:** Record the new invocation without inventing final totals.

## 40. 4.3.1 / Table 4.3

**Before:** [Not present: new table row cell]

**After:** At least 2

**Reason:** Record the new invocation without inventing final totals.

## 41. 4.3.1 / Table 4.3

**Before:** [Not present: new table row cell]

**After:** 0 reported

**Reason:** Record the new invocation without inventing final totals.

## 42. 4.3.1 / Table 4.3

**Before:** [Not present: new table row cell]

**After:** 359 collected; runtime termination; exit 0xC0000409. No final summary.

**Reason:** Record the new invocation without inventing final totals.

## 43. 4.3.1 / Table 4.3

**Before:** Windows, 19 Oct 2026

**After:** Windows, 19 Oct 2026; first run

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 44. 4.3.1 / Table 4.3

**Before:** Not obtained

**After:** Not run

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 45. 4.3.1 / Table 4.3

**Before:** Not obtained

**After:** Not run

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 46. 4.3.1 / Table 4.3

**Before:** 356 collected; interrupted collection; 13 warnings; 24.76 s; exit 2. Native rerun required.

**After:** 356 collected; collection interrupted; 13 warnings; 24.76 s; exit 2.

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 47. 4.3.1 / Table 4.4

**Before:** Native win32 pytest/application environment

**After:** Windows Python/Qt environment; native acceptance assessed separately

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 48. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.2.6

**After:** Linux fixture checks; Windows default-Pillow patch accuracy 90.68%, macro-F1 88.59%; native 224 × 224 input scope in Section 4.2.6

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 49. 3.6.6 / Table 3.6

**Before:** Query semantics and English calendar verified

**After:** Linux query/calendar checks; Windows history module reported a failure before process termination; assertion detail pending

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 50. 3.6.6 / Table 3.6

**Before:** Recorded task/model/parameters fixture-verified

**After:** Linux recorded-parameter checks; Windows invocation terminated in the rerun module; diagnosis pending

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 51. 4.5.1 / Table 4.9

**Before:** Classifier benchmark: 90.68% accuracy / 88.59% macro-F1 with OpenCV/Albumentations. Default-Pillow, segmentation and tiled predictive evaluation pending.

**After:** Default-Pillow Single image core: 90.68% accuracy / 88.59% macro-F1 on 7,180 native 224 × 224 patches. Segmentation and tiled predictive evaluation pending.

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 52. 4.5.1 / Table 4.9

**Before:** Linux, 19 Oct: recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**After:** Linux recorded-parameter checks; Windows history failure and runtime termination unresolved; efficiency awaits UAT

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 53. Appendix A / Table A.1

**Before:** Recorded accuracy 90.68%, macro-F1 88.59%; grouping/backend limits documented

**After:** Default-Pillow patch evaluation completed; 90.68% accuracy / 88.59% macro-F1; generalisation limits retained

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 54. Appendix C / Table C.1

**Before:** 17 Oct 2026 Linux full/related/scale logs; 19 Oct Windows execution record

**After:** 17 and 19 Oct Linux logs; 19 Oct Windows collection and runtime records

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 55. Appendix C / Table C.1

**Before:** Current collection interruption, exit 2, recorded revision and CPU test environment; originals cross-checked

**After:** First Windows invocation: collection error, exit 2; resolved by restoring the original training script

**Reason:** Update the evidence status without altering test assertions or outcomes.

## 56. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** E16

**Reason:** Add the newly executed record using the existing table styling.

## 57. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** 19 Oct Windows rerun: live progress, exit code and model-availability records

**Reason:** Add the newly executed record using the existing table styling.

## 58. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** 359 items collected; at least two failure markers and abnormal termination; final totals unavailable

**Reason:** Add the newly executed record using the existing table styling.

## 59. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** E17

**Reason:** Add the newly executed record using the existing table styling.

## 60. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** 19 Oct default-Pillow predictions, class report, matrix, summary and environment

**Reason:** Add the newly executed record using the existing table styling.

## 61. Appendix C / Table C.1

**Before:** [Not present: new table row cell]

**After:** 7,180 completed patch predictions, model identity, actual preprocessing, reference label agreement and probability differences

**Reason:** Add the newly executed record using the existing table styling.

## 62. Existing page-reference cache: head_68

**Before:** 43

**After:** 44

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 63. Existing page-reference cache: head_78

**Before:** 55

**After:** 56

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 64. Existing page-reference cache: head_79

**Before:** 55

**After:** 56

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 65. Existing page-reference cache: head_81

**Before:** 59

**After:** 60

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 66. Existing page-reference cache: head_82

**Before:** 60

**After:** 61

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 67. Existing page-reference cache: head_83

**Before:** 60

**After:** 61

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 68. Existing page-reference cache: head_84

**Before:** 61

**After:** 62

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 69. Existing page-reference cache: head_86

**Before:** 62

**After:** 63

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 70. Existing page-reference cache: head_88

**Before:** 63

**After:** 64

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 71. Existing page-reference cache: head_89

**Before:** 63

**After:** 64

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 72. Existing page-reference cache: head_90

**Before:** 64

**After:** 65

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 73. Existing page-reference cache: head_91

**Before:** 65

**After:** 66

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 74. Existing page-reference cache: head_92

**Before:** 66

**After:** 67

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 75. Existing page-reference cache: head_117

**Before:** 86

**After:** 87

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 76. Existing page-reference cache: head_120

**Before:** 87

**After:** 88

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 77. Existing page-reference cache: cap_Figure_4_10

**Before:** 57

**After:** 58

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 78. Existing page-reference cache: new_Table_4_2__Windows_test_host_and_actua

**Before:** 56

**After:** 57

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 79. Existing page-reference cache: cap_Table_4_3

**Before:** 60

**After:** 61

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 80. Existing page-reference cache: cap_Table_4_4

**Before:** 61

**After:** 62

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.

## 81. Existing page-reference cache: cap_Table_4_6

**Before:** 63

**After:** 64

**Reason:** Refresh the existing field after evidence updates; retain styles and field instructions.
