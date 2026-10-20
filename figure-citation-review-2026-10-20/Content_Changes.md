# 本轮逐项修改清单

位置、修改前、修改后和原因。软件源代码及已有模型指标没有改动。

## 1. 1.1 / Figure 1.1

**修改前**
Histopathology is a reference method for diagnosing many diseases, including malignancies. In haematoxylin and eosin (H&E) images, the staining of nuclei and cytoplasmic structures provides morphological information that trained professionals interpret in context. Digital imaging makes these observations available for storage, teaching and computational analysis. A model's output, however, is an inference from image appearance and must not be equated with a verified clinical diagnosis (Litjens et al., 2017; Kather et al., 2019).

**修改后**
Histopathology is a reference method for diagnosing many diseases, including malignancies. In haematoxylin and eosin (H&E) images, the staining of nuclei and cytoplasmic structures provides morphological information that trained professionals interpret in context. Digital imaging makes these observations available for storage, teaching and computational analysis. A model's output, however, is an inference from image appearance and must not be equated with a verified clinical diagnosis (Litjens et al., 2017; Kather et al., 2019). Figure 1.1 is reserved for an authorised H&E example illustrating this tissue context.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 2. 2.2.4 / Figure 2.1

**修改前**
The model's softmax output is a normalised score over its classes. It is not automatically calibrated as the probability that an interpretation is correct (Guo et al., 2017). A high-confidence majority class across many tiles can arise from genuine image content, sampling scale, preprocessing mismatch or model/domain limitations. ZY-Path exposes per-tile probabilities and coordinates so these possibilities can be investigated rather than using a coloured map as proof of accuracy.

**修改后**
The model's softmax output is a normalised score over its classes. It is not automatically calibrated as the probability that an interpretation is correct (Guo et al., 2017). A high-confidence majority class across many tiles can arise from genuine image content, sampling scale, preprocessing mismatch or model/domain limitations. ZY-Path exposes per-tile probabilities and coordinates so these possibilities can be investigated rather than using a coloured map as proof of accuracy. Figure 2.1 distinguishes the three output meanings: whole-image classification, tile-class estimates and pixel segmentation.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 3. 3.1 / Figure 3.1

**修改前**
The implemented system has three logical layers. The presentation layer contains the main window, inference/history/action panels, settings and result viewers. The core layer loads models, prepares inputs, executes inference and parses outputs. The data layer stores records and creates export files. MainWindow coordinates transitions between these layers, including saving result artifacts before inserting a completed history record.

**修改后**
The implemented system has three logical layers. The presentation layer contains the main window, inference/history/action panels, settings and result viewers. The core layer loads models, prepares inputs, executes inference and parses outputs. The data layer stores records and creates export files. MainWindow coordinates transitions between these layers, including saving result artifacts before inserting a completed history record. Figure 3.1 shows these layers and the flow of model, image, result and history artifacts.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 4. 3.2.1 / Table 3.1

**修改前**
The requirements preserve the original model–image–inference–history workflow and add explicit spatial analysis and state-management requirements revealed during development. A requirement describes intended behaviour; its implementation and evidence status are recorded separately in Section 3.6.6.

**修改后**
The requirements preserve the original model–image–inference–history workflow and add explicit spatial analysis and state-management requirements revealed during development. A requirement describes intended behaviour; its implementation and evidence status are recorded separately in Section 3.6.6. Table 3.1 specifies each functional requirement and its observable acceptance condition.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 5. 3.2.2 / Table 3.2

**修改前**
[No prose introduction.]

**修改后**
Table 3.2 links the non-functional requirements to their verification approaches and current implementation boundaries.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 6. 3.3.4 / Table 3.3

**修改前**
This aggregate need not equal the class with the largest r_c because probability mass and hard-class coverage are different summaries. It is not a new whole-image forward pass. The history table therefore shows tile count and largest estimated coverage, leaving whole-image confidence blank; PDF metadata distinguishes “Aggregate tile label” and “Area-weighted mean probability”.

**修改后**
This aggregate need not equal the class with the largest r_c because probability mass and hard-class coverage are different summaries. It is not a new whole-image forward pass. The history table therefore shows tile count and largest estimated coverage, leaving whole-image confidence blank; PDF metadata distinguishes “Aggregate tile label” and “Area-weighted mean probability”. Table 3.3 records the classifier’s fixed class order and dedicated nine-colour display palette.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 7. 3.3.8 / Table 3.5

**修改前**
DatabaseManager uses sqlite3 connections with parameterised statements and transaction handling. The base inference_records table stores paths, task, label/confidence where applicable, result-image path and timestamp. A companion segmentation_artifacts table stores artifact paths and analysis_json; despite its legacy name, it also carries tiled-classification and single-classification parameter metadata.

**修改后**
DatabaseManager uses sqlite3 connections with parameterised statements and transaction handling. The base inference_records table stores paths, task, label/confidence where applicable, result-image path and timestamp. A companion segmentation_artifacts table stores artifact paths and analysis_json; despite its legacy name, it also carries tiled-classification and single-classification parameter metadata. Table 3.5 summarises the persistent structures and the purpose of their principal fields.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 8. 3.4.1 / Figure 3.2

**修改前**
The interface keeps the CP1 three-region structure: input controls on the left, analysis/history in the centre and export/session actions on the right. Implementation changes replace fixed panel assumptions with draggable splitters, scrollable contents and bounded window restoration. The aim is to keep essential actions reachable while prioritising the analysis image.

**修改后**
The interface keeps the CP1 three-region structure: input controls on the left, analysis/history in the centre and export/session actions on the right. Implementation changes replace fixed panel assumptions with draggable splitters, scrollable contents and bounded window restoration. The aim is to keep essential actions reachable while prioritising the analysis image. Figure 3.2 presents an annotated wireframe of this arrangement and its main user actions.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 9. 3.5.1 / Figure 3.3

**修改前**
The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Model validation is included in the run workflow; tiled classification extends the classification choice when that explicit mode is selected. Restoring history and rerunning history are separate use cases because only the latter executes inference and creates a new record.

**修改后**
The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Model validation is included in the run workflow; tiled classification extends the classification choice when that explicit mode is selected. Restoring history and rerunning history are separate use cases because only the latter executes inference and creates a new record. Figure 3.3 maps the actor to the implemented use cases.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 10. 3.5.2 / Figure 3.4

**修改前**
The sequence diagram follows a successful completed run after the user selects an image, task and model. MainWindow captures parameters, starts the worker and receives progress/result signals. The worker validates and executes the pipeline; the GUI coordinator renders the result, saves artifacts and inserts a history record. Cancellation and saving failure are alternatives, not successful completed-history paths.

**修改后**
The sequence diagram follows a successful completed run after the user selects an image, task and model. MainWindow captures parameters, starts the worker and receives progress/result signals. The worker validates and executes the pipeline; the GUI coordinator renders the result, saves artifacts and inserts a history record. Cancellation and saving failure are alternatives, not successful completed-history paths. Figure 3.4 shows the interaction sequence and the alternative cancellation and persistence-failure paths.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 11. 3.5.3 / Figure 3.5

**修改前**
The class diagram shows principal runtime responsibilities rather than every widget. MainWindow coordinates panels and services; InferenceEngine depends on the loader, preprocessor, parser and task-specific spatial functions. ClassificationResult and SegmentationResult share ImageComparison and ZoomableImageView. DatabaseManager and ExportManager handle persistence/export; QSettings stores preferences separately.

**修改后**
The class diagram shows principal runtime responsibilities rather than every widget. MainWindow coordinates panels and services; InferenceEngine depends on the loader, preprocessor, parser and task-specific spatial functions. ClassificationResult and SegmentationResult share ImageComparison and ZoomableImageView. DatabaseManager and ExportManager handle persistence/export; QSettings stores preferences separately. Figure 3.5 identifies these classes and their principal dependencies.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 12. 3.5.4 / Figure 3.6

**修改前**
The activity diagram highlights the explicit mode decision, distinct preprocessing/task branches and completion/cancellation outcomes. It prevents a misleading conceptual flow in which image dimensions alone choose tiled classification or a cancellation request immediately terminates a model operation.

**修改后**
The activity diagram highlights the explicit mode decision, distinct preprocessing/task branches and completion/cancellation outcomes. It prevents a misleading conceptual flow in which image dimensions alone choose tiled classification or a cancellation request immediately terminates a model operation. Figure 3.6 traces these decisions through successful completion, cancellation and error exits.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 13. 3.6.6 / Table 3.6

**修改前**
The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses distinguish completed Windows and Linux automated checks, the recorded classifier evaluation and outstanding manual acceptance, UAT and model studies.

**修改后**
Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the completed native Windows automated checks, recorded classifier evaluation, outstanding manual acceptance, UAT and further model studies.

**原因**
Introduce the matrix explicitly and consistently scope the reported software results to Windows.

## 14. 3.6.6 / Table 3.6

**修改前**
Source: named project tests, the environment-labelled Linux records and the completed native Windows full-suite log/XML of 19 October 2026, together with the classifier evaluation.

**修改后**
Source: named project tests and the completed native Windows full-suite log/XML of 19 October 2026, together with the classifier evaluation.

**原因**
Use the target-platform records that underpin the reported verification statuses.

## 15. 4.2.1 / Figure 4.1

**修改前**
The Windows session on 19 October 2026 launched the application from its virtual environment and recorded successful loading and validation of crc_dn21_seed42_best.pth as a nine-class DenseNet with output shape (1, 9). This establishes source-based startup and classifier integration for that session. The observed workflow and window states are detailed in Section 4.3.3.

**修改后**
The Windows session on 19 October 2026 launched the application from its virtual environment and recorded successful loading and validation of crc_dn21_seed42_best.pth as a nine-class DenseNet with output shape (1, 9). This establishes source-based startup and classifier integration for that session. The observed workflow and window states are detailed in Section 4.3.3. Figure 4.1 reserves the corresponding Windows application overview; the authorised screenshot remains to be inserted.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 16. 4.2.2 / Figure 4.3

**修改前**
[No prose introduction.]

**修改后**
Figure 4.3 reserves real-weight Windows captures of Single image and Tiled analysis; these pending captures are separate from the synthetic interface example in Figure 4.2.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 17. 4.2.3 / Figure 4.4

**修改前**
The reference notebook establishes the segmentation architecture, preprocessing, labels and probability-fusion procedure. Controlled software tests cover restored dimensions, class counts and blending behaviour. Segmentation predictive performance is treated separately: annotated-mask metrics were not available for this model, as discussed in Section 4.5.3.

**修改后**
The reference notebook establishes the segmentation architecture, preprocessing, labels and probability-fusion procedure. Controlled software tests cover restored dimensions, class counts and blending behaviour. Segmentation predictive performance is treated separately: annotated-mask metrics were not available for this model, as discussed in Section 4.5.3. Figure 4.4 reserves the real-weight Windows segmentation view and aligned source comparison; the capture is still pending.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 18. 4.2.4 / Figure 4.5

**修改前**
History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology.

**修改后**
History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 reserves the Windows history and recorded-rerun demonstration.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 19. 4.2.4 / Figure 4.6

**修改前**
Rerun tests demonstrate that the recorded model/task/mode and analysis settings take precedence over current preferences. Restoring a record does not itself create a new prediction. The export workflow uses the displayed completed record's metadata and can retain task-specific maps/JSON together with the presentation. This prevents a newly selected model from being incorrectly attached to an older visible result.

**修改后**
Rerun tests demonstrate that the recorded model/task/mode and analysis settings take precedence over current preferences. Restoring a record does not itself create a new prediction. The export workflow uses the displayed completed record's metadata and can retain task-specific maps/JSON together with the presentation. This prevents a newly selected model from being incorrectly attached to an older visible result. Figure 4.6 reserves an exported report and its companion artifacts for inspection; the real-file capture remains pending.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 20. 4.2.5 / Figure 4.7

**修改前**
Settings includes Appearance, Preferences, Models, Guide & Support, System Information and About. Model defaults are independent per task and require validation. Preferences applies the classification mode immediately while retaining a separate startup default; closed dropdowns scroll the page instead of changing selections accidentally. Guide navigation remains visible and follows the current reading section, while the system-information copy confirmation expires rather than becoming permanent content.

**修改后**
Settings includes Appearance, Preferences, Models, Guide & Support, System Information and About. Model defaults are independent per task and require validation. Preferences applies the classification mode immediately while retaining a separate startup default; closed dropdowns scroll the page instead of changing selections accidentally. Guide navigation remains visible and follows the current reading section, while the system-information copy confirmation expires rather than becoming permanent content. Figure 4.7 shows the implemented Guide & Support page and its navigation.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 21. 4.2.5 / Figure 4.9

**修改前**
Cancel inference is available during work. Tests cover cancellation at multiple checkpoints and preservation of the previous completed result. The interface waits for the current operation and worker cleanup; it does not advertise instantaneous termination. A final real-model cancellation recording remains useful because the duration of an individual model operation depends on the actual weights, workload and hardware.

**修改后**
Cancel inference is available during work. Tests cover cancellation at multiple checkpoints and preservation of the previous completed result. The interface waits for the current operation and worker cleanup; it does not advertise instantaneous termination. A final real-model cancellation recording remains useful because the duration of an individual model operation depends on the actual weights, workload and hardware. Figure 4.9 reserves the Windows demonstration of cancellation and task-specific model defaults.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 22. 4.2.6 / Tables 4.1–4.2

**修改前**
[No prose introduction.]

**修改后**
Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 23. 4.2.6 / Figure 4.11

**修改前**
[No prose introduction.]

**修改后**
Figure 4.11 shows the external-test confusion matrix, allowing the class-wise error patterns to be examined alongside the aggregate metrics.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 24. 4.3.1 / Table 4.3

**修改前**
The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source content is recorded in revision 7bd3552, as identified in Appendix C.

**修改后**
The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source content is recorded in revision 7bd3552, as identified in Appendix C. Table 4.3 summarises this completed target-platform invocation.

**原因**
Introduce the numbered figure/table in the relevant prose, without upgrading a reserved screenshot or pending UAT result to completed evidence.

## 25. 4.3.1 / Figure 4.12

**修改前**
[No prose introduction.]

**修改后**
Figure 4.12 reproduces selected lines from the genuine final Windows pytest report; it is a test-log excerpt rather than an application screenshot.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 26. 4.4.1 / Table 4.6

**修改前**
[No prose introduction.]

**修改后**
Table 4.6 reserves the participant profile; its entries will be completed only after actual UAT recruitment and consent.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 27. 4.4.2 / Table 4.7

**修改前**
[No prose introduction.]

**修改后**
Table 4.7 defines the reporting fields for valid SUS responses and task outcomes; the numerical results remain pending.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 28. 4.4.3 / Table 4.8

**修改前**
[No prose introduction.]

**修改后**
Table 4.8 reserves the feature-use and rating results, distinguishing features actually used from those not attempted.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 29. 4.5.1 / Table 4.9

**修改前**
[No prose introduction.]

**修改后**
Table 4.9 maps each research objective to the implemented outcome and the evidence available for assessing its achievement.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 30. Appendix A.1 / Tables A.1–A.3

**修改前**
Tables A.1 and A.2 retain the CP1 planning baseline as a stored record. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

**修改后**
Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

**原因**
Mention each planning table explicitly without changing the distinction between planned and achieved work.

## 31. Appendix B.3 / Table B.1

**修改前**
[No prose introduction.]

**修改后**
Table B.1 specifies the UAT tasks, participant instructions and observable success criteria to be used during the planned study.

**原因**
Introduce the numbered figure/table explicitly in its own section.

## 32. 3.6.5

**修改前**
Three evidence streams are kept separate. Automated development/integration tests establish repeatable technical behaviour under controlled fixtures. Manual Windows testing establishes behaviour on the intended operating system, display configurations and real files. UAT evaluates observed task performance and user perceptions. Independent model evaluation is a fourth, distinct activity needed for predictive claims; no amount of GUI testing replaces it.

**修改后**
Four evidence streams are kept separate. Automated development/integration tests establish repeatable technical behaviour under controlled fixtures. Manual Windows testing establishes behaviour on the intended operating system, display configurations and real files. UAT evaluates observed task performance and user perceptions. Independent model evaluation supports predictive claims; no amount of GUI testing replaces it.

**原因**
Correct the enumeration to match the four distinct evaluation activities already described.

## 33. 4.6

**修改前**
ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches. The final native Windows full suite completed with 370 passed, 0 failed, 0 errors and 0 skipped; the Linux installation retained one real-segmentation-file availability failure. UAT and the model, performance and deployment limitations remain as specified in Section 4.5.3.

**修改后**
ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches. The final native Windows full suite completed with 370 passed, 0 failed, 0 errors and 0 skipped. UAT and the model, performance and deployment limitations remain as specified in Section 4.5.3.

**原因**
Keep the chapter summary focused on the completed target-platform verification rather than an installation-specific Linux prerequisite failure.

## 34. Appendix C.2

**修改前**
Table C.2 distinguishes completed runs from collection errors and runtime termination. The final Windows run completed 370 tests with no failures, errors or skips. A preceding 131-test regression subset passed in 119.90 seconds with 15 warnings; its count is not added to the full-suite total. The final Linux/offscreen run completed with 369 passed, 1 failed and no collection errors in 125.70 seconds, with 14 warnings: the real segmentation weight was unavailable in that installation. Classifier performance is reported separately in Section 4.2.6.

**修改后**
Table C.2 distinguishes the completed native Windows run from earlier Windows collection and runtime interruptions. The final invocation completed 370 tests with no failures, errors or skips. A preceding 131-test regression subset passed in 119.90 seconds with 15 warnings; its count is not added to the full-suite total. Classifier performance is reported separately in Section 4.2.6.

**原因**
Limit the manuscript execution history to Windows, preserving all original platform logs separately in the accompanying materials.

## 35. Appendix C.2 / Table C.2

**修改前**
Table C.2. Automated test execution history

**修改后**
Table C.2. Windows automated test execution history

**原因**
Make the target-platform scope explicit in the caption.

## 36. Appendix C.2 / Table C.2

**修改前**
Linux, 19 Oct; final full run | 369 | 1 | 0 | 370 collected; 14 warnings; 125.70 s; exit 1. Real segmentation weight unavailable.

**修改后**
[Retained in the original Linux records in the supplementary archive; excluded from the Windows-scoped manuscript table.]

**原因**
Use a consistent platform scope without recoding a failed run as a pass or deleting any test.

## 37. Appendix C.2 / Table C.2

**修改前**
Linux, 19 Oct; before repairs | 358 | 1 | 0 | 359 collected; 14 warnings; 104.68 s; exit 1. Real segmentation weight unavailable.

**修改后**
[Retained in the original Linux records in the supplementary archive; excluded from the Windows-scoped manuscript table.]

**原因**
Use a consistent platform scope without recoding a failed run as a pass or deleting any test.

## 38. Appendix C.2 / Table C.2

**修改前**
Linux, 17 Oct 2026 | 355 | 1 | 1 | Continuation after collection errors; 14 warnings; 110.70 s.

**修改后**
[Retained in the original Linux records in the supplementary archive; excluded from the Windows-scoped manuscript table.]

**原因**
Use a consistent platform scope without recoding a failed run as a pass or deleting any test.

## 39. Appendix C.1 / Table C.1

**修改前**
E20 | 19 Oct 2026 Linux full-suite log, XML result and environment record | 369 passed, 1 missing-real-segmentation-file failure, 0 collection errors; no skipped tests

**修改后**
[Linux execution record retained in the archive, outside the manuscript’s Windows verification scope.]

**原因**
Keep the evidence index aligned with the reported Windows software verification.

## 40. Appendix C.1 / Table C.1

**修改前**
Dated Linux and Windows collection, runtime, subset and complete-suite records

**修改后**
Dated Windows collection, runtime, subset and complete-suite records

**原因**
Align the evidence index with the declared test-platform scope.

## 41. Appendix C.1 / Table C.1 header

**修改前**
Evidence

**修改后**
ID

**原因**
Use a short identifier heading that fits the narrow evidence-code column without splitting a word across lines.

## 42. Appendix C.2 / Table C.2 source

**修改前**
Source: dated pytest logs, XML results and exit codes for 17 and 19 October 2026. “Not final” and “Not run” identify incomplete invocations; they are not passing-test totals.

**修改后**
Source: Windows pytest logs, XML results and exit codes of 19 October 2026. “Not final” and “Not run” identify incomplete invocations rather than passing-test totals.

**原因**
Use the actual Windows execution date and clarify the interrupted-run labels.

## 43. Appendix C / Table C.1 source placement

**修改前**
C.1 source could be orphaned; C.2 source appeared between caption and table.

**修改后**
Source paragraph immediately follows its table; the final table row stays with the source paragraph.

**原因**
Keep the source with its table without forcing a multi-page table onto one page.

## 44. Appendix C / Table C.2 source placement

**修改前**
C.1 source could be orphaned; C.2 source appeared between caption and table.

**修改后**
Source paragraph immediately follows its table; the final table row stays with the source paragraph.

**原因**
Keep the source with its table without forcing a multi-page table onto one page.

## 45. References / I. Peer-Reviewed Journal Articles

**修改前**
Bangor, A., Kortum, P. and Miller, J. (2009) ‘Determining what individual SUS scores mean: Adding an adjective rating scale’, Journal of Usability Studies, 4(3), pp. 114–123.

**修改后**
[1] Bangor, A., Kortum, P., & Miller, J. (2009). Determining what individual SUS scores mean: Adding an adjective rating scale. Journal of Usability Studies, 4(3), 114–123.

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 46. References / I. Peer-Reviewed Journal Articles

**修改前**
Bankhead, P. et al. (2017) ‘QuPath: Open source software for digital pathology image analysis’, Scientific Reports, 7, article 16878. https://doi.org/10.1038/s41598-017-17204-5

**修改后**
[2] Bankhead, P., et al. (2017). QuPath: Open source software for digital pathology image analysis. Scientific Reports, 7, article 16878. https://doi.org/10.1038/s41598-017-17204-5

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 47. References / I. Peer-Reviewed Journal Articles

**修改前**
Dolezal, J.M., Kochanny, S., Dyer, E., Ramesh, S., Srisuwananukorn, A., Sacco, M., Howard, F.M., Li, A., Mohan, P. and Pearson, A.T. (2024) ‘Slideflow: Deep learning for digital histopathology with real-time whole-slide visualization’, BMC Bioinformatics, 25, article 134. https://doi.org/10.1186/s12859-024-05758-x

**修改后**
[3] Dolezal, J. M., Kochanny, S., Dyer, E., Ramesh, S., Srisuwananukorn, A., Sacco, M., Howard, F. M., Li, A., Mohan, P., & Pearson, A. T. (2024). Slideflow: Deep learning for digital histopathology with real-time whole-slide visualization. BMC Bioinformatics, 25, article 134. https://doi.org/10.1186/s12859-024-05758-x

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 48. References / I. Peer-Reviewed Journal Articles

**修改前**
Kaczmarzyk, J.R., O’Callaghan, A., Inglis, F., Gat, S., Kurc, T., Gupta, R., Bremer, E., Bankhead, P. and Saltz, J.H. (2024) ‘Open and reusable deep learning for pathology with WSInfer and QuPath’, npj Precision Oncology, 8, article 9. https://doi.org/10.1038/s41698-024-00499-9

**修改后**
[4] Kaczmarzyk, J. R., O’Callaghan, A., Inglis, F., Gat, S., Kurc, T., Gupta, R., Bremer, E., Bankhead, P., & Saltz, J. H. (2024). Open and reusable deep learning for pathology with WSInfer and QuPath. npj Precision Oncology, 8, article 9. https://doi.org/10.1038/s41698-024-00499-9

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 49. References / I. Peer-Reviewed Journal Articles

**修改前**
Kather, J.N. et al. (2019) ‘Predicting survival from colorectal cancer histology slides using deep learning: A retrospective multicenter study’, PLOS Medicine, 16(1), e1002730. https://doi.org/10.1371/journal.pmed.1002730

**修改后**
[5] Kather, J. N., et al. (2019). Predicting survival from colorectal cancer histology slides using deep learning: A retrospective multicenter study. PLOS Medicine, 16(1), e1002730. https://doi.org/10.1371/journal.pmed.1002730

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 50. References / I. Peer-Reviewed Journal Articles

**修改前**
Litjens, G. et al. (2017) ‘A survey on deep learning in medical image analysis’, Medical Image Analysis, 42, pp. 60–88. https://doi.org/10.1016/j.media.2017.07.005

**修改后**
[6] Litjens, G., et al. (2017). A survey on deep learning in medical image analysis. Medical Image Analysis, 42, 60–88. https://doi.org/10.1016/j.media.2017.07.005

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 51. References / I. Peer-Reviewed Journal Articles

**修改前**
Marée, R. et al. (2016) ‘Collaborative analysis of multi-gigapixel imaging data using Cytomine’, Bioinformatics, 32(9), pp. 1395–1401. https://doi.org/10.1093/bioinformatics/btw013

**修改后**
[7] Marée, R., et al. (2016). Collaborative analysis of multi-gigapixel imaging data using Cytomine. Bioinformatics, 32(9), 1395–1401. https://doi.org/10.1093/bioinformatics/btw013

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 52. References / I. Peer-Reviewed Journal Articles

**修改前**
Yen, P.-Y. and Bakken, S. (2012) ‘Review of health information technology usability study methodologies’, Journal of the American Medical Informatics Association, 19(3), pp. 413–422. https://doi.org/10.1136/amiajnl-2010-000020

**修改后**
[8] Yen, P.-Y., & Bakken, S. (2012). Review of health information technology usability study methodologies. Journal of the American Medical Informatics Association, 19(3), 413–422. https://doi.org/10.1136/amiajnl-2010-000020

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 53. References / II. Peer-Reviewed Conference Papers

**修改前**
Guo, C., Pleiss, G., Sun, Y. and Weinberger, K.Q. (2017) ‘On calibration of modern neural networks’, Proceedings of the 34th International Conference on Machine Learning, Proceedings of Machine Learning Research, 70, pp. 1321–1330. https://proceedings.mlr.press/v70/guo17a.html

**修改后**
[9] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In Proceedings of the 34th International Conference on Machine Learning, Proceedings of Machine Learning Research, 70 (pp. 1321–1330). https://proceedings.mlr.press/v70/guo17a.html

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 54. References / II. Peer-Reviewed Conference Papers

**修改前**
He, K., Zhang, X., Ren, S. and Sun, J. (2016) ‘Deep residual learning for image recognition’, Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pp. 770–778. https://doi.org/10.1109/CVPR.2016.90

**修改后**
[10] He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (pp. 770–778). https://doi.org/10.1109/CVPR.2016.90

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 55. References / II. Peer-Reviewed Conference Papers

**修改前**
Huang, G., Liu, Z., van der Maaten, L. and Weinberger, K.Q. (2017) ‘Densely connected convolutional networks’, Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pp. 2261–2269. https://arxiv.org/abs/1608.06993

**修改后**
[11] Huang, G., Liu, Z., van der Maaten, L., & Weinberger, K. Q. (2017). Densely connected convolutional networks. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (pp. 2261–2269). https://arxiv.org/abs/1608.06993

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 56. References / II. Peer-Reviewed Conference Papers

**修改前**
Liu, Z., Lin, Y., Cao, Y., Hu, H., Wei, Y., Zhang, Z., Lin, S. and Guo, B. (2021) ‘Swin Transformer: Hierarchical vision transformer using shifted windows’, Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 10012–10022. https://arxiv.org/abs/2103.14030

**修改后**
[12] Liu, Z., Lin, Y., Cao, Y., Hu, H., Wei, Y., Zhang, Z., Lin, S., & Guo, B. (2021). Swin Transformer: Hierarchical vision transformer using shifted windows. In Proceedings of the IEEE/CVF International Conference on Computer Vision (pp. 10012–10022). https://arxiv.org/abs/2103.14030

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 57. References / II. Peer-Reviewed Conference Papers

**修改前**
Nielsen, J. (1994) ‘Enhancing the explanatory power of usability heuristics’, Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, pp. 152–158. https://doi.org/10.1145/191666.191729

**修改后**
[13] Nielsen, J. (1994). Enhancing the explanatory power of usability heuristics. In Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (pp. 152–158). https://doi.org/10.1145/191666.191729

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 58. References / II. Peer-Reviewed Conference Papers

**修改前**
Paszke, A. et al. (2019) ‘PyTorch: An imperative style, high-performance deep learning library’, Advances in Neural Information Processing Systems, 32. https://proceedings.neurips.cc/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html

**修改后**
[14] Paszke, A., et al. (2019). PyTorch: An imperative style, high-performance deep learning library. In Advances in Neural Information Processing Systems, 32. https://proceedings.neurips.cc/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 59. References / II. Peer-Reviewed Conference Papers

**修改前**
Ronneberger, O., Fischer, P. and Brox, T. (2015) ‘U-Net: Convolutional networks for biomedical image segmentation’, in Medical Image Computing and Computer-Assisted Intervention – MICCAI 2015, pp. 234–241. https://doi.org/10.1007/978-3-319-24574-4_28

**修改后**
[15] Ronneberger, O., Fischer, P., & Brox, T. (2015). U-Net: Convolutional networks for biomedical image segmentation. In Medical Image Computing and Computer-Assisted Intervention – MICCAI 2015 (pp. 234–241). https://doi.org/10.1007/978-3-319-24574-4_28

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 60. References / II. Peer-Reviewed Conference Papers

**修改前**
Tan, M. and Le, Q.V. (2019) ‘EfficientNet: Rethinking model scaling for convolutional neural networks’, Proceedings of the 36th International Conference on Machine Learning, Proceedings of Machine Learning Research, 97, pp. 6105–6114. https://proceedings.mlr.press/v97/tan19a.html

**修改后**
[16] Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. In Proceedings of the 36th International Conference on Machine Learning, Proceedings of Machine Learning Research, 97 (pp. 6105–6114). https://proceedings.mlr.press/v97/tan19a.html

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 61. References / II. Peer-Reviewed Conference Papers

**修改前**
Xiao, T., Liu, Y., Zhou, B., Jiang, Y. and Sun, J. (2018) ‘Unified perceptual parsing for scene understanding’, Proceedings of the European Conference on Computer Vision, pp. 418–434. https://arxiv.org/abs/1807.10221

**修改后**
[17] Xiao, T., Liu, Y., Zhou, B., Jiang, Y., & Sun, J. (2018). Unified perceptual parsing for scene understanding. In Proceedings of the European Conference on Computer Vision (pp. 418–434). https://arxiv.org/abs/1807.10221

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 62. References / III. Books and Book Chapters

**修改前**
Brooke, J. (1996) ‘SUS: A “quick and dirty” usability scale’, in Jordan, P.W., Thomas, B., Weerdmeester, B.A. and McClelland, I.L. (eds.) Usability Evaluation in Industry. London: Taylor & Francis, pp. 189–194.

**修改后**
[18] Brooke, J. (1996). SUS: A “quick and dirty” usability scale. In P. W. Jordan, B. Thomas, B. A. Weerdmeester, & I. L. McClelland (Eds.), Usability Evaluation in Industry (pp. 189–194). Taylor & Francis.

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 63. References / III. Books and Book Chapters

**修改前**
Gamma, E., Helm, R., Johnson, R. and Vlissides, J. (1994) Design Patterns: Elements of Reusable Object-Oriented Software. Reading, MA: Addison-Wesley.

**修改后**
[19] Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Reading, MA: Addison-Wesley.

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 64. References / III. Books and Book Chapters

**修改前**
Kreibich, J.A. (2010) Using SQLite. Sebastopol, CA: O’Reilly Media.

**修改后**
[20] Kreibich, J. A. (2010). Using SQLite. Sebastopol, CA: O’Reilly Media.

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 65. References / IV. Magazine and Technical Articles

**修改前**
Hunter, J.D. (2007) ‘Matplotlib: A 2D graphics environment’, Computing in Science & Engineering, 9(3), pp. 90–95. https://doi.org/10.1109/MCSE.2007.55

**修改后**
[21] Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. https://doi.org/10.1109/MCSE.2007.55

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 66. References / V. Standards, Documentation, and Online Resources

**修改前**
Aiforia (n.d.) Aiforia Create. Product information. https://www.aiforia.com/aiforia-create

**修改后**
[22] Aiforia. (n.d.). Aiforia Create. Product information. https://www.aiforia.com/aiforia-create

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 67. References / V. Standards, Documentation, and Online Resources

**修改前**
fpdf2 Contributors (n.d.) fpdf2: Simple PDF generation for Python. Project documentation. https://github.com/py-pdf/fpdf2

**修改后**
[23] fpdf2 Contributors. (n.d.). fpdf2: Simple PDF generation for Python. Project documentation. https://github.com/py-pdf/fpdf2

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 68. References / V. Standards, Documentation, and Online Resources

**修改前**
Kather, J.N., Halama, N. and Marx, A. (2018). 100,000 histological images of human colorectal cancer and healthy tissue (v0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.1214456

**修改后**
[24] Kather, J. N., Halama, N., & Marx, A. (2018). 100,000 histological images of human colorectal cancer and healthy tissue (v0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.1214456

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 69. References / V. Standards, Documentation, and Online Resources

**修改前**
NumPy Developers (n.d.) NumPy user guide. https://numpy.org/doc/stable/user/

**修改后**
[25] NumPy Developers. (n.d.). NumPy user guide. https://numpy.org/doc/stable/user/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 70. References / V. Standards, Documentation, and Online Resources

**修改前**
Pillow Contributors (n.d.) Pillow documentation: Image processing and resampling. https://pillow.readthedocs.io/en/stable/

**修改后**
[26] Pillow Contributors. (n.d.). Pillow documentation: Image processing and resampling. https://pillow.readthedocs.io/en/stable/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 71. References / V. Standards, Documentation, and Online Resources

**修改前**
PyInstaller Development Team (n.d.) PyInstaller documentation. https://pyinstaller.org/en/stable/

**修改后**
[27] PyInstaller Development Team. (n.d.). PyInstaller documentation. https://pyinstaller.org/en/stable/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 72. References / V. Standards, Documentation, and Online Resources

**修改前**
PyTorch Contributors (n.d.) torch.load; inference_mode; serialization semantics. PyTorch documentation. https://pytorch.org/docs/stable/

**修改后**
[28] PyTorch Contributors. (n.d.). torch.load; inference_mode; serialization semantics. PyTorch documentation. https://pytorch.org/docs/stable/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 73. References / V. Standards, Documentation, and Online Resources

**修改前**
Riverbank Computing (n.d.) PyQt5 reference guide. https://www.riverbankcomputing.com/static/Docs/PyQt5/

**修改后**
[29] Riverbank Computing. (n.d.). PyQt5 reference guide. https://www.riverbankcomputing.com/static/Docs/PyQt5/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 74. References / V. Standards, Documentation, and Online Resources

**修改前**
SQLite (n.d.) Zero-configuration. SQLite documentation. https://sqlite.org/zeroconf.html

**修改后**
[30] SQLite. (n.d.). Zero-configuration. SQLite documentation. https://sqlite.org/zeroconf.html

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 75. References / V. Standards, Documentation, and Online Resources

**修改前**
The Qt Company (n.d.) Qt 5 documentation: QThread, QScreen, QGraphicsView and high-DPI support. https://doc.qt.io/qt-5/

**修改后**
[31] The Qt Company. (n.d.). Qt 5 documentation: QThread, QScreen, QGraphicsView and high-DPI support. https://doc.qt.io/qt-5/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 76. References / V. Standards, Documentation, and Online Resources

**修改前**
W3C (2023) Web Content Accessibility Guidelines (WCAG) 2.2. W3C Recommendation, 5 October 2023. https://www.w3.org/TR/WCAG22/

**修改后**
[32] W3C. (2023). Web Content Accessibility Guidelines (WCAG) 2.2. W3C Recommendation, 5 October 2023. https://www.w3.org/TR/WCAG22/

**原因**
Match CP1’s grouped numbered reference list, author-initial spacing, year punctuation and final-author ampersand; retain the corrected CP2 source metadata.

## 77. References / category headings and Table of Contents

**修改前**
One unnumbered, ungrouped reference list.

**修改后**
CP1’s five category headings with sequential [1]–[32] entries and linked contents entries.

**原因**
Use the same reference-list organisation as CP1 without reinstating unrelated or inaccurate references.
