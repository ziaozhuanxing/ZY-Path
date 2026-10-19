# Second content refinement change log

## 1. 4.3.4 → 4.2.6

**Before:** Model evaluation under Functional Testing Results

**After:** Separate model evaluation subsection under System Implementation Results; required 4.1–4.6 headings retained

**Reason:** Separate model evaluation from software tests within the supervisor-prescribed framework.

## 2. Cross-references and captions

**Before:** Tiled analysis, cancellation, task-specific model defaults and responsive comparison views refine these objectives. O1 is implemented through local source execution without an application server; producing and validating a standalone executable is a further deployment objective addressed in Sections 4.3.5 and 5.2.

**After:** Tiled analysis, cancellation, task-specific model defaults and responsive comparison views refine these objectives. O1 is implemented through local source execution without an application server; producing and validating a standalone executable is a further deployment objective addressed in Sections 4.3.4 and 5.2.

**Reason:** Synchronise numbering after relocating the model section.

## 3. Cross-references and captions

**Before:** Local execution requires the selected model files and, for UPerNet reconstruction, its verified configuration in the local Hugging Face cache. Windows source execution and real-classifier validation are documented in Section 4.3.3; offline package verification is addressed separately in Section 4.3.5.

**After:** Local execution requires the selected model files and, for UPerNet reconstruction, its verified configuration in the local Hugging Face cache. Windows source execution and real-classifier validation are documented in Section 4.3.3; offline package verification is addressed separately in Section 4.3.4.

**Reason:** Synchronise numbering after relocating the model section.

## 4. Cross-references and captions

**Before:** NCT-CRC-HE-100K contains 100,000 colorectal tissue patches across nine categories, while CRC-VAL-HE-7K provides a separate labelled evaluation collection (Kather et al., 2019). This project used the former for training and internal validation and the latter for the recorded 7,180-image test. The actual split manifests and measured results are described in Sections 3.3.2 and 4.3.4.

**After:** NCT-CRC-HE-100K contains 100,000 colorectal tissue patches across nine categories, while CRC-VAL-HE-7K provides a separate labelled evaluation collection (Kather et al., 2019). This project used the former for training and internal validation and the latter for the recorded 7,180-image test. The actual split manifests and measured results are described in Sections 3.3.2 and 4.2.6.

**Reason:** Synchronise numbering after relocating the model section.

## 5. Cross-references and captions

**Before:** UPerNet reconstruction loads its configuration from the local Hugging Face cache with local_files_only=True. Preparing a redistributable application therefore requires packaging the permitted weights, cached configuration and runtime dependencies. PyInstaller is a candidate tool for this future deployment step (PyInstaller Development Team, n.d.); the current deployment evidence is assessed in Section 4.3.5.

**After:** UPerNet reconstruction loads its configuration from the local Hugging Face cache with local_files_only=True. Preparing a redistributable application therefore requires packaging the permitted weights, cached configuration and runtime dependencies. PyInstaller is a candidate tool for this future deployment step (PyInstaller Development Team, n.d.); the current deployment evidence is assessed in Section 4.3.4.

**Reason:** Synchronise numbering after relocating the model section.

## 6. Cross-references and captions

**Before:** The recorded evaluation environment used Albumentations 1.3.1 and OpenCV 4.8.1. Its transform calls A.Resize(224, 224) without overriding interpolation, using the library’s default linear resize. Pillow bilinear and OpenCV INTER_LINEAR can differ in resampling and rounding; the application preserves its legacy Pillow default and records the selected backend. Section 4.3.4 therefore attributes the reported model metrics to the recorded Albumentations evaluation pipeline.

**After:** The recorded evaluation environment used Albumentations 1.3.1 and OpenCV 4.8.1. Its transform calls A.Resize(224, 224) without overriding interpolation, using the library’s default linear resize. Pillow bilinear and OpenCV INTER_LINEAR can differ in resampling and rounding; the application preserves its legacy Pillow default and records the selected backend. Section 4.2.6 therefore attributes the reported model metrics to the recorded Albumentations evaluation pipeline.

**Reason:** Synchronise numbering after relocating the model section.

## 7. Cross-references and captions

**Before:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.3 gives the host hardware and separates its installed GPU from the actual computation device.

**After:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.5 gives the host hardware and separates its installed GPU from the actual computation device.

**Reason:** Synchronise numbering after relocating the model section.

## 8. Cross-references and captions

**Before:** Automated outcomes are identified by date, environment, command and revision. The historical Linux run used --continue-on-collection-errors and executed available cases. The latest Windows command did not use that option and stopped after a collection error, leaving no passing-test count for that invocation. Table 4.1 preserves both records without merging their counts.

**After:** Automated outcomes are identified by date, environment, command and revision. The historical Linux run used --continue-on-collection-errors and executed available cases. The latest Windows command did not use that option and stopped after a collection error, leaving no passing-test count for that invocation. Table 4.3 preserves both records without merging their counts.

**Reason:** Synchronise numbering after relocating the model section.

## 9. Cross-references and captions

**Before:** The 3552 × 3536 geometry example produces 49 crops at a 512 × 512 setting, with smaller right and bottom edges. Controlled tests verify unique source crops, RGB/raw255 preparation, class order, edge handling and area conservation. The tissue accuracy of a tiled map requires a separately defined ground-truth and scale protocol; the patch-classification results in Section 4.3.4 do not measure that map.

**After:** The 3552 × 3536 geometry example produces 49 crops at a 512 × 512 setting, with smaller right and bottom edges. Controlled tests verify unique source crops, RGB/raw255 preparation, class order, edge handling and area conservation. The tissue accuracy of a tiled map requires a separately defined ground-truth and scale protocol; the patch-classification results in Section 4.2.6 do not measure that map.

**Reason:** Synchronise numbering after relocating the model section.

## 10. Cross-references and captions

**Before:** 4.3.4 Classification training and test results

**After:** 4.2.6 Classification training and test results

**Reason:** Synchronise numbering after relocating the model section.

## 11. Cross-references and captions

**Before:** The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.11 illustrates the epoch-to-epoch variation in validation loss and accuracy.

**After:** The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

**Reason:** Synchronise numbering after relocating the model section.

## 12. Cross-references and captions

**Before:** Figure 4.11. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.

**After:** Figure 4.10. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.

**Reason:** Synchronise numbering after relocating the model section.

## 13. Cross-references and captions

**Before:** Table 4.4. Classification evaluation summary

**After:** Table 4.1. Classification evaluation summary

**Reason:** Synchronise numbering after relocating the model section.

## 14. Cross-references and captions

**Before:** Table 4.5. Class-wise classification performance on 7,180 test images

**After:** Table 4.2. Class-wise classification performance on 7,180 test images

**Reason:** Synchronise numbering after relocating the model section.

## 15. Cross-references and captions

**Before:** Figure 4.12. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.

**After:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.

**Reason:** Synchronise numbering after relocating the model section.

## 16. Cross-references and captions

**Before:** Table 4.1. Automated verification records by date and environment at revision 1f3e01e

**After:** Table 4.3. Automated verification records by date and environment at revision 1f3e01e

**Reason:** Synchronise numbering after relocating the model section.

## 17. Cross-references and captions

**Before:** Table 4.2. Windows test host and actual CPU runtime on 19 October 2026

**After:** Table 4.4. Windows test host and actual CPU runtime on 19 October 2026

**Reason:** Synchronise numbering after relocating the model section.

## 18. Cross-references and captions

**Before:** Figure 4.10. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.1.

**After:** Figure 4.12. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.3.

**Reason:** Synchronise numbering after relocating the model section.

## 19. Cross-references and captions

**Before:** Table 4.3. Implementation challenges and verified resolutions

**After:** Table 4.5. Implementation challenges and verified resolutions

**Reason:** Synchronise numbering after relocating the model section.

## 20. Cross-references and captions

**Before:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.3.4, and Table 3.6 retains the environment-specific scope of the software tests. The current collection error prevents a claim that the latest Windows full suite passed.

**After:** These corrections address implementation behaviour and interpretation. Classification performance is reported separately in Section 4.2.6, and Table 3.6 retains the environment-specific scope of the software tests. The current collection error prevents a claim that the latest Windows full suite passed.

**Reason:** Synchronise numbering after relocating the model section.

## 21. Cross-references and captions

**Before:** 4.3.5 Runtime and deployment verification status

**After:** 4.3.4 Runtime and deployment verification status

**Reason:** Synchronise numbering after relocating the model section.

## 22. Cross-references and captions

**Before:** The hardware and CPU runtime are documented in Table 4.2, but no repeated stage-level measurements were recorded for loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving or export. Cold and warm runs have not been separately summarised. Appendix E.3 defines the benchmark protocol; no measured latency, mean, standard deviation or throughput is filled in here.

**After:** The hardware and CPU runtime are documented in Table 4.4, but no repeated stage-level measurements were recorded for loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving or export. Cold and warm runs have not been separately summarised. Appendix E.3 defines the benchmark protocol; no measured latency, mean, standard deviation or throughput is filled in here.

**Reason:** Synchronise numbering after relocating the model section.

## 23. Table cross-reference

**Before:** Historical fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.3.4

**After:** Historical fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.2.6

**Reason:** Synchronise the relocated section reference.

## 24. Abstract

**Before:** To make trained histopathology models accessible through a traceable graphical workflow, this project developed ZY-Path, a PyQt5 desktop application combining CPU-based PyTorch inference, Single image and Tiled analysis classification, UPerNet segmentation, linked image inspection, SQLite history, recorded rerun and PNG/PDF export. Evaluation of the custom nine-class DenseNet on 7,180 CRC-VAL-HE-7K images recorded 90.68% accuracy and 88.59% macro-F1, with consistent per-image predictions and aggregate reports; earlier Linux regression tests supplied software-level evidence, while the latest Windows pytest invocation stopped during collection and a separate Windows session recorded successful loading and structural validation of the real classifier. The contribution is a model-aware desktop integration for education and exploratory research, with user acceptance testing, segmentation accuracy, systematic performance measurement and clean-machine executable deployment remaining to be evaluated.

**After:** ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. The trained nine-class DenseNet recorded 90.68% accuracy and 88.59% macro-F1 on 7,180 CRC-VAL-HE-7K images using the OpenCV/Albumentations evaluation pipeline, while software regression tests and Windows startup logs support distinct implementation claims. The contribution is an inspectable educational/research workflow; predictive evaluation through the application’s default Pillow pathway, UAT, segmentation accuracy, systematic timing and clean-machine deployment remain separate verification tasks.

**Reason:** Attribute the numeric result specifically to its evaluated preprocessing; position segmentation as an integration with limited predictive evidence.

## 25. 1.4

**Before:** [Not present]

**After:** To support O2 and O3 with model evidence, I also trained and evaluated the classifier using the reference code provided by my supervisor. This supporting research activity supplies a documented checkpoint and patch-level evaluation; it is separate from the inference-only GUI and introduces no new neural architecture.

**Reason:** Add a supported explanation or clearly scoped method.

## 26. 2.5

**Before:** The resulting project position is a focused desktop integration for individual educational and research use. Its research value lies in connecting model compatibility, spatial interpretation and record continuity as observable requirements, building on the graphical inference precedents identified above.

**After:** The resulting project position is a focused desktop integration for individual educational and research use. Model training and patch-level evaluation support the classification component, while the application contribution connects compatibility, spatial interpretation and record continuity as observable requirements.

**Reason:** Align the stated contribution with the supporting classifier study.

## 27. 4.2.6

**Before:** The selected-epoch validation accuracy exceeds the test accuracy by approximately 8.41 percentage points. This observed gap suggests sensitivity to the evaluation collection and motivates analysis of grouping, stain/scale and domain differences; the records do not isolate a causal explanation. A high internal validation score therefore does not remove the need for the separate test collection.

**After:** The selected-epoch validation accuracy exceeds test accuracy by approximately 8.41 percentage points. Internal validation draws from the same 100,000-image pool as training, whereas the 7,180-image test is a separate collection. Class proportions also differ: ADI represents 10.41% of the 100K pool versus 18.64% of the test set, DEB 11.51% versus 4.72%, and MUS 13.54% versus 8.25%. These observed sampling differences make the two evaluations distinct, although they do not identify a single cause of the performance gap. Both validation and test scripts specify deterministic Resize, ToTensorV2 and float32 raw255; comparison with the application’s Pillow backend is a separate validation question.

**Reason:** Explain the observed gap using actual split and class-count evidence rather than an unsupported causal claim.

## 28. 4.2.6

**Before:** [Not present]

**After:** Training used the NCT-CRC-HE-100K.zip archive, identified as the standard normalised release rather than the separately named non-normalised alternative. The dataset authors’ repository documents that normalised 100K release and the availability of the alternative (Kather, n.d.). Stain normalisation of source images is distinct from numerical raw255/ImageNet tensor profiles. The test archive’s stain processing and acquisition matching were not independently characterised, so the score gap is not attributed to a proven stain mismatch.

**Reason:** Add a supported explanation or clearly scoped method.

## 29. 4.2.6

**Before:** [Not present]

**After:** Both the class-wise results and the lower macro-F1 show that a global accuracy number alone is insufficient. Patient/slide grouping, archive identity, stain characteristics and source resolution should be recorded in a follow-up evaluation. The current image-path checks establish disjoint file lists, not patient-level independence.

**Reason:** Add a supported explanation or clearly scoped method.

## 30. 3.6.5

**Before:** Automated outcomes are identified by date, environment, command and revision. The historical Linux run used --continue-on-collection-errors and executed available cases. The latest Windows command did not use that option and stopped after a collection error, leaving no passing-test count for that invocation. Table 4.3 preserves both records without merging their counts.

**After:** Automated results are labelled by environment and date. The Linux run of 19 October collected and executed 359 tests after genuine classification resources were installed; the Windows run of that date stopped during collection and requires a native rerun. Table 4.3 retains their separate outcomes.

**Reason:** Use the completed Linux rerun without replacing unexecuted Windows outcomes.

## 31. 4.1

**Before:** This chapter reports implementation and evaluation at application revision 1f3e01e. It combines the historical Linux/offscreen-Qt tests of 17 October 2026, the Windows test and launch record of 19 October 2026, and the classification training/evaluation outputs. Development captures identify their environment; figures derived from synthetic fixtures are distinguished from real-model results.

**After:** This chapter reports implementation and evaluation at revision 1f3e01e. Section 4.2 presents implemented workflows and a distinct classifier evaluation; Section 4.3 reports software tests and native observations; Section 4.4 reserves the UAT results. Environment and date labels distinguish the Linux runs from the Windows execution record.

**Reason:** Make the evidence structure explicit and reduce repeated chronology wording.

## 32. 4.3.1

**Before:** The latest Windows invocation on 19 October 2026 collected 356 items and encountered one collection error in tests/test_train_crc_resume.py. Execution stopped during collection: the summary reported 13 warnings and 1 error in 24.76 seconds, with exit code 2. No passing or executed-failure count was obtained for this invocation. The command did not include --continue-on-collection-errors.

**After:** On Linux, 19 October 2026, the complete invocation collected 359 tests and recorded 358 passed, 1 failed and no collection errors, with 14 warnings in 104.68 seconds (exit 1). The genuine training script resolved the earlier collection prerequisite. The remaining failure is the built-in-model availability assertion because the real segmentation weight is not present in that installation.

**Reason:** Report the actual completed rerun; retain the real remaining failure.

## 33. 4.3.1

**Before:** The Windows command was .\.venv\Scripts\python.exe -m pytest -ra --tb=long --color=no --junitxml=<evidence-directory>\pytest.xml, executed in the project virtual environment. Appendix C records the project/evidence paths and the temporal limits of the saved revision and worktree observations.

**After:** On Windows, 19 October 2026, collection reported 356 items and one error before test execution could complete: 13 warnings, 1 error, 24.76 seconds and exit 2. No passing count was obtained for that invocation. The native rerun procedure restores the unchanged training script and records a new full result; its outcome will be reported only after execution.

**Reason:** Keep the Windows result accurate and describe the actionable repair rather than distant future work.

## 34. 4.3.1

**Before:** The earlier Linux/offscreen-Qt full run dated 17 October used pytest -q --continue-on-collection-errors --tb=short and recorded 355 passed, 1 failed, 14 warnings and 1 collection error in 110.70 seconds. Related regression and simulated-DPI runs are subsets, not additional passes. Both 110.70 and 24.76 seconds measure pytest invocations, not image inference.

**After:** For comparison, Linux, 17 October recorded 355 passed, 1 failed and 1 collection error in 110.70 seconds using continuation after collection errors. The 19 October Linux run used the complete suite without that continuation flag. Suite durations measure test execution, not image inference.

**Reason:** Give compact environment/date context without repeating historical throughout the prose.

## 35. 4.3.1

**Before:** The historical failed case was test_default_builtin_paths_keep_real_classification_and_segmentation_models in tests/test_main_window_inference.py, which first reported the absent classification weight in that Linux installation. This failure belongs to the historical run. The later Windows collection interruption provides no observation of that case’s outcome, while the separate application log records successful loading of the real classifier.

**After:** The availability test checks both real built-in model files. In the Linux rerun, the supplied classifier is present but the segmentation weight remains unavailable, so that assertion still fails. The Windows startup log establishes classifier loading separately; it does not establish the outcome of a test interrupted before execution.

**Reason:** Update the failure cause and preserve the separation of Windows startup and test outcomes.

## 36. 4.3.1

**Before:** The current collection error is FileNotFoundError for models/dn21_folder_classification/train_crc_dn21 (1).py. During collection, tests/test_train_crc_resume.py reads that path and extracts normalize_model_settings and validate_resume_config through AST. The actual training script is available in the research materials, but its absence at the repository’s expected path remains a test prerequisite to reconcile. The 13 warnings concern Matplotlib use of Pyparsing parseString, resetCache and enablePackrat deprecated interfaces.

**After:** The Windows collection error concerned the expected classification training-script path. The resume checks read that script and extract normalize_model_settings and validate_resume_config; placing the genuine file at the expected location lets all three resume checks pass in Linux. The Windows wrapper verifies the script checksum and preserves any different existing file before running the unchanged full suite.

**Reason:** Treat the narrow collection repair as completed in Linux and ready to run on Windows.

## 37. 4.3.1 / Table 4.3

**Before:** Source: saved Linux logs dated 17 October 2026 and the Windows test record dated 19 October 2026. Historical subset counts overlap.

**After:** Source: Linux test logs, 17 and 19 October 2026, and the Windows test log, 19 October 2026. Per-invocation totals are independent; related subset counts are not additive.

**Reason:** Include the newly executed Linux run in the table source.

## 38. 4.5.3

**Before:** The Windows application record establishes startup and classifier validation, followed by normal, maximised and minimised states. It does not establish completed inference for either task, maximise-to-restore behaviour, manual resizing, all-control visibility or normal exit. Native acceptance, assistive-technology checks and UAT remain to be completed. No coverage percentage was produced by the recorded test commands.

**After:** The available Windows record establishes startup, real-classifier validation and normal/maximised/minimised states. Completed image inference, restoration sequences and full interaction acceptance require their own execution evidence. UAT and accessibility evaluation are also separate from these startup observations.

**Reason:** Move operational details out of the limitations and avoid a blanket assertion about all possible application runs.

## 39. 4.5.3

**Before:** The application integrates trained models and provides no GUI training or annotation workflow. I trained and evaluated the classifier separately; the segmentation model and reference notebook were provided by my supervisor. Segmentation training data, optimisation settings and Dice/IoU results were not available. The checkpoint filename is therefore used as an identifier rather than evidence of its dataset or completed training epochs.

**After:** Classification performance is specific to its data and preprocessing. The 90.68% accuracy and 88.59% macro-F1 describe the recorded OpenCV/Albumentations patch evaluation. The application defaults to Pillow bilinear, and its source crops may differ in field of view; evaluation through that exact pathway is still required. Stratified patch-level splitting and disjoint file paths do not establish patient/slide independence or exclude content duplicates. Calibration and tiled-map ground truth were not evaluated.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 40. 4.5.3

**Before:** Large raster-image tiling is implemented, extending the original proposal, but native WSI pyramid reading, memory-bounded streaming and physical-scale extraction remain outside scope. Full-size source arrays, maps and restored masks consume memory. Source tile dimensions are editable, and the 512 × 512 classification starting value has no established physical-scale equivalence to the training images; non-square edge crops are resized anisotropically to the network input.

**After:** Large raster tiling is implemented, but native WSI pyramid reading, physical-scale extraction and memory-bounded streaming remain outside scope. Full-resolution arrays and restored masks consume memory. The editable 512 × 512 classification starting value has unconfirmed training-scale equivalence, and rectangular edge crops are resized to the fixed network input.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 41. 4.5.3

**Before:** The classifier evaluation uses a stratified patch-level training/validation split and a separately named CRC-VAL-HE-7K test collection. Relative filenames are disjoint, but the available manifests do not establish patient- or slide-level isolation or rule out image-content duplicates. The 90.68% accuracy and 88.59% macro-F1 describe the recorded Albumentations test pipeline. The application’s legacy Pillow backend and arbitrary larger source crops may present different inputs; calibration, tiled-analysis ground truth and clinical generalisation were not evaluated.

**After:** Segmentation is a supervisor-provided model integration with a documented inference procedure. I did not train it, and its training dataset and Dice/IoU report were not obtained. Controlled tests establish software geometry and statistics rather than segmentation accuracy; a real-weight demonstration and aligned ground-truth evaluation remain necessary.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 42. 4.5.3

**Before:** Software verification is incomplete across environments. The historical Linux run preserves its 355 passes, one failed availability check and one collection error; the latest Windows invocation stopped during collection with one error and no pass count. The later clean-worktree check is a post-test observation, and no corresponding post-check HEAD output was provided. Passing fixtures and observed window states cannot fill those missing execution records.

**After:** Native and user acceptance are incomplete. Windows logs support source startup, classifier validation and the observed window states, while restore, resizing, complete control visibility and end-to-end tasks need formal records. UAT, assistive-technology testing and coverage measurement remain uncompleted evaluation activities. The environment-specific software outcomes are reported in Section 4.3.1.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 43. 4.5.3

**Before:** The available Windows record establishes startup, real-classifier validation and normal/maximised/minimised states. Completed image inference, restoration sequences and full interaction acceptance require their own execution evidence. UAT and accessibility evaluation are also separate from these startup observations.

**After:** Runtime and deployment require further measurement. The documented Windows execution is CPU-based; its installed RTX 4060 was not used. Repeated cold/warm stage timings, memory measurements, PyInstaller build records, clean-machine acceptance and offline dependency checks are unavailable, so the current delivery level is source execution.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 44. 4.5.3

**Before:** Performance and deployment also remain unverified. Although the Windows hardware is documented, no repeated stage-level benchmark separates loading, preprocessing, forward inference, fusion/statistics, GUI display, saving and export. The installed RTX 4060 was not used by PyTorch 2.1.2+cpu. There are no PyInstaller build records, matched packaged artifacts, clean-machine acceptance records or offline deployment checks, so source execution is the present delivery level.

**After:** Model compatibility and provenance are constrained. Structural checks cannot guarantee semantic labels, calibrated confidence or safety of arbitrary serialised modules. Records reference mutable paths and do not provide immutable per-run identities, automatic backups, multi-user access control or an atomic transaction over external artifacts. These limits restrict the system to trusted-model educational and exploratory research use.

**Reason:** Consolidate substantive limitations into six paragraphs; remove repeated audit bookkeeping.

## 45. 4.5.3

**Before:** Structural model checks establish supported tensor and metadata conventions, not semantic label accuracy, calibrated confidence or file safety. Full pickled modules can require their original Python classes and execute code during deserialisation. Use is restricted to trusted model sources; the application is an educational/research integration without clinical validation or a model-security sandbox.Structural model checks establish supported tensor and metadata conventions, not semantic label accuracy, calibrated confidence or file safety. Full pickled modules can require their original Python classes and execute code during deserialisation. Use is restricted to trusted model sources; the application is an educational/research integration without clinical validation or a model-security sandbox.Structural model checks establish supported tensor and metadata conventions, not semantic label accuracy, calibrated confidence or file safety. Full pickled modules can require their original Python classes and execute code during deserialisation. Use is restricted to trusted model sources; the application is an educational/research integration without clinical validation or a model-security sandbox.

**After:** [Consolidated into the six thematic limitation paragraphs]

**Reason:** Remove duplicate limitation/audit detail, not evidence or tests.

## 46. 4.5.3

**Before:** History references mutable filesystem paths and does not provide immutable per-run file identities, automatic backup, multi-user access control or an atomic transaction covering all external artifacts. It supports local workflow continuity rather than a certified clinical audit trail. These are specific persistence and collaboration limits of the implemented design.History references mutable filesystem paths and does not provide immutable per-run file identities, automatic backup, multi-user access control or an atomic transaction covering all external artifacts. It supports local workflow continuity rather than a certified clinical audit trail. These are specific persistence and collaboration limits of the implemented design.History references mutable filesystem paths and does not provide immutable per-run file identities, automatic backup, multi-user access control or an atomic transaction covering all external artifacts. It supports local workflow continuity rather than a certified clinical audit trail. These are specific persistence and collaboration limits of the implemented design.

**After:** [Consolidated into the six thematic limitation paragraphs]

**Reason:** Remove duplicate limitation/audit detail, not evidence or tests.

## 47. 4.5.3

**Before:** The archived evidence includes the Windows pytest text/XML outputs, exit-code file, saved commit, environment records and application log, alongside the classification experiment files. The post-test clean-worktree observation is documented separately because no git-status.txt or accompanying post-check HEAD output was saved. Appendix C distinguishes those direct artifacts from the later observation.The archived evidence includes the Windows pytest text/XML outputs, exit-code file, saved commit, environment records and application log, alongside the classification experiment files. The post-test clean-worktree observation is documented separately because no git-status.txt or accompanying post-check HEAD output was saved. Appendix C distinguishes those direct artifacts from the later observation.The archived evidence includes the Windows pytest text/XML outputs, exit-code file, saved commit, environment records and application log, alongside the classification experiment files. The post-test clean-worktree observation is documented separately because no git-status.txt or accompanying post-check HEAD output was saved. Appendix C distinguishes those direct artifacts from the later observation.

**After:** [Consolidated into the six thematic limitation paragraphs]

**Reason:** Remove duplicate limitation/audit detail, not evidence or tests.

## 48. 4.5.4

**Before:** The immediate priorities are to reconcile the expected training-script path and rerun the full suite, complete the Windows acceptance cases and UAT, and establish patient/slide grouping and source scale for further model evaluation. Segmentation evaluation requires authorised aligned masks and confirmed label provenance. These tasks address identified uncertainty before adding new features.

**After:** The immediate priorities are to execute the prepared Windows full-suite rerun, evaluate the default application classifier on the available test images, and complete native acceptance and UAT. Further model work should establish archive identity, patient/slide grouping and source scale; segmentation evaluation requires authorised aligned masks.

**Reason:** Move the ready-to-run repairs out of long-term speculative work.

## 49. 4.6

**Before:** ZY-Path implements local model-aware inference, spatial inspection and record continuity. The classifier’s recorded 7,180-image evaluation gives 90.68% accuracy and 88.59% macro-F1. Historical Linux tests and the latest Windows invocation retain separate outcomes: the latter stopped during collection with one error and no pass count. Windows startup and real-classifier validation were recorded; formal UAT, remaining native acceptance, performance benchmarking and clean-machine packaging are further evaluation activities.

**After:** ZY-Path implements model-aware inference, spatial inspection and record continuity. The recorded OpenCV/Albumentations classifier evaluation gives 90.68% accuracy and 88.59% macro-F1; these are not yet a measurement of the default application pathway. Linux, 19 October completed with 358 passed, 1 failed and no collection errors. Windows startup is documented, while the Windows full-suite rerun, UAT and the remaining validation tasks retain their separate status.

**Reason:** Synchronise the summary without overstating application accuracy or native testing.

## 50. 5.1

**Before:** The classification evaluation recorded 6,511 correct predictions from 7,180 images, corresponding to 90.68% accuracy and 88.59% macro-F1. Historical Linux tests provide controlled software evidence. On 19 October 2026, Windows pytest stopped during collection with one error and no obtained pass count, while a separate application session successfully loaded and validated the real nine-class classifier. These outcomes support distinct parts of the implementation and its evaluation, as detailed in Chapter 4.

**After:** Using the recorded OpenCV/Albumentations pipeline, the classifier produced 6,511 correct predictions from 7,180 images, or 90.68% accuracy and 88.59% macro-F1. This supports the trained model under that evaluation configuration; accuracy through the application’s default Pillow pathway remains to be measured. Software tests and Windows startup observations address implementation behaviour separately, as reported in Chapter 4.

**Reason:** State the model result’s preprocessing scope explicitly in the conclusion.

## 51. 5.2

**Before:** The first priority is completing verification: restore the genuine training script at the intended repository location, record a new full-suite result, finish Windows acceptance and evaluate segmentation with authorised ground truth if it becomes available. Further classifier studies should document patient/slide separation, source scale, calibration and application backend effects. Test assertions and error reporting should be preserved throughout.

**After:** Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, preprocessing equivalence and segmentation against authorised masks. Immediate completion checks are specified in Section 4.3.1 and Appendix E.

**Reason:** Keep the simple collection repair out of the long-term development contribution.

## 52. 4.5.1

**Before:** H1 is supported at the controlled implementation level and by successful real-classifier loading on Windows. Historical restoration and rerun tests support the technical component of H3. H2 and user-efficiency claims await UAT; the interrupted latest test run and remaining deployment checks qualify the level of system acceptance.

**After:** H1 is supported by the controlled implementation tests and real-classifier loading on Windows. The Linux restoration and rerun checks support the technical component of H3. H2 and user-efficiency claims await UAT, while native acceptance and real segmentation availability limit the present system-level conclusions.

**Reason:** Avoid describing the completed Linux run as interrupted and identify the remaining evidence precisely.

## 53. Appendix C.1

**Before:** Repository: ziaozhuanxing/ZY-Path. Application branch: codex-ready-2026-10-15. Recorded test revision: 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Windows project: E:\ZY-PATH. Windows evidence directory: E:\ZY-PATH-evidence\20261019-142119. A later git status --porcelain=v1 --untracked-files=all produced no output, establishing a clean worktree at that later check. git-status.txt was not created during testing; no post-check git rev-parse HEAD output was provided, so the later HEAD is not represented as independently reverified.

**After:** Source baseline: revision 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Software results are identified by platform and date: Linux/offscreen Qt on 17 and 19 October 2026 and Windows on 19 October 2026. Table C.1 indexes the implementation, experiment and execution evidence.

**Reason:** Remove personal paths, branch names and repeated worktree bookkeeping while retaining the scientific revision identifier.

## 54. Appendix C.2

**Before:** The archived Linux logs preserve the 17 October outcomes. The Windows originals include pytest-full.log, pytest.xml, pytest-exit-code.txt, commit.txt, windows-app.log, dependencies.txt, hardware.txt, python-version.txt, runtime-device.txt and test-date.txt. The text log and XML agree on one collection error, and the exit file records 2; JUnit tests=1 represents the collection-error entry, not one passed test or 356 executed tests. The XML duration is 24.755 seconds and the console rounds it to 24.76. Classification records support recomputed CSV consistency and checkpoint identity; the author confirms that the deployed file was renamed from that checkpoint. Model inference was not rerun as part of this consistency verification.

**After:** The evidence archive distinguishes executed tests from collection errors and separates software fixtures from real-model predictions. I deployed the selected classification checkpoint under the application filename; its checksum is recorded in Appendix E. The original evaluation CSVs reproduce the reported aggregate metrics, while a fresh application-pipeline run is a distinct evaluation. Windows logs establish only the actions they record.

**Reason:** Replace third-person author confirms and low-level XML bookkeeping with concise provenance interpretation.

## 55. Appendix A.3

**Before:** Before submission, confirm the cover fields, complete authorised Windows screenshots and UAT, reconcile the missing test prerequisite and record a new full-suite result. Retain the classification evaluation and add any supported segmentation evidence. Update conclusions only from actual findings, then refresh document fields and apply the agreed final formatting. Verify a clean-machine package before claiming executable distribution.

**After:** Before submission, complete the prepared Windows rerun and default-Pillow evaluation, authorised application screenshots, UAT and cover fields. Update the model/application evidence separately, then refresh the conclusions and document fields from the actual results. Final formatting and any clean-machine packaging claims follow their corresponding review and execution evidence.

**Reason:** Update the immediate completion sequence after the genuine training-resource placement.

## 56. 4.3.1 / Table 4.3

**Before:** 19 Oct 2026: Windows full invocation; revision 1f3e01e

**After:** Linux, 19 Oct 2026

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 57. 4.3.1 / Table 4.3

**Before:** Not obtained

**After:** 358

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 58. 4.3.1 / Table 4.3

**Before:** Not obtained

**After:** 1

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 59. 4.3.1 / Table 4.3

**Before:** 1

**After:** 0

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 60. 4.3.1 / Table 4.3

**Before:** 356 items collected; stopped during collection; 13 warnings; 24.76 s; exit 2

**After:** 359 collected; 14 warnings; 104.68 s; exit 1. Real segmentation weight unavailable.

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 61. 4.3.1 / Table 4.3

**Before:** 17 Oct 2026: Linux/offscreen Qt; full run with --continue-on-collection-errors

**After:** Windows, 19 Oct 2026

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 62. 4.3.1 / Table 4.3

**Before:** 355

**After:** Not obtained

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 63. 4.3.1 / Table 4.3

**Before:** 1

**After:** Not obtained

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 64. 4.3.1 / Table 4.3

**Before:** Historical record; 14 warnings; 110.70 s; missing-file issues

**After:** 356 collected; interrupted collection; 13 warnings; 24.76 s; exit 2. Native rerun required.

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 65. 4.3.1 / Table 4.3

**Before:** 17 Oct 2026: related result-control/history/comparison/grid/layout cases

**After:** Linux, 17 Oct 2026

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 66. 4.3.1 / Table 4.3

**Before:** 83

**After:** 355

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 67. 4.3.1 / Table 4.3

**Before:** 0

**After:** 1

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 68. 4.3.1 / Table 4.3

**Before:** 0

**After:** 1

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 69. 4.3.1 / Table 4.3

**Before:** Historical controlled regression subset

**After:** Earlier complete invocation with continuation; 14 warnings; 110.70 s.

**Reason:** Use concise environment/date labels and actual independent outcomes.

## 70. 4.3.1 / Table 4.3

**Before:** [["Run / environment", "Passed", "Failed", "Collection errors", "Interpretation"], ["19 Oct 2026: Windows full invocation; revision 1f3e01e", "Not obtained", "Not obtained", "1", "356 items collected; stopped during collection; 13 warnings; 24.76 s; exit 2"], ["17 Oct 2026: Linux/offscreen Qt; full run with --continue-on-collection-errors", "355", "1", "1", "Historical record; 14 warnings; 110.70 s; missing-file issues"], ["17 Oct 2026: related result-control/history/comparison/grid/layout cases", "83", "0", "0", "Historical controlled regression subset"], ["17 Oct 2026: Qt scale factor 1.5", "7", "0", "0", "Historical simulated 150% scale; not native acceptance"], ["17 Oct 2026: Qt scale factor 2", "7", "0", "0", "Historical simulated 200% scale; not native acceptance"]]

**After:** [["Run / environment", "Passed", "Failed", "Collection errors", "Interpretation"], ["Linux, 19 Oct 2026", "358", "1", "0", "359 collected; 14 warnings; 104.68 s; exit 1. Real segmentation weight unavailable."], ["Windows, 19 Oct 2026", "Not obtained", "Not obtained", "1", "356 collected; interrupted collection; 13 warnings; 24.76 s; exit 2. Native rerun required."], ["Linux, 17 Oct 2026", "355", "1", "1", "Earlier complete invocation with continuation; 14 warnings; 110.70 s."]]

**Reason:** Retain primary comparable runs; subset logs remain archived and are not added to pass counts.

## 71. 4.3.1 / Table 4.4

**Before:** Collection used 2³⁰ bytes although its field was named RAM_GB

**After:** Physical system memory

**Reason:** Keep the GiB specification but remove the logging-field implementation note.

## 72. Requirements / objective tables

**Before:** Historical structural fixtures verified; Windows real-classifier load/validation recorded; latest availability test not executed

**After:** Linux, 19 Oct: structural fixtures verified; Windows real-classifier load/validation recorded; latest availability test not executed

**Reason:** Label executable evidence by environment and date.

## 73. Requirements / objective tables

**Before:** Historical fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.2.6

**After:** Linux, 19 Oct: fixture verification; recorded CRC-VAL-HE-7K accuracy 90.68%, macro-F1 88.59%; backend scope in Section 4.2.6

**Reason:** Label executable evidence by environment and date.

## 74. Requirements / objective tables

**Before:** Historical Qt fixtures; normal/maximised/minimised Windows states recorded; restore/docking/accessibility pending

**After:** Linux, 19 Oct: Qt fixtures; normal/maximised/minimised Windows states recorded; restore/docking/accessibility pending

**Reason:** Label executable evidence by environment and date.

## 75. Requirements / objective tables

**Before:** Historical fixture checks pass; latest full Windows invocation interrupted; immutable provenance not implemented

**After:** Historical fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**Reason:** Label executable evidence by environment and date.

## 76. Requirements / objective tables

**Before:** Historical Qt fixtures and partial native state observations; formal interaction acceptance and UAT pending

**After:** Linux, 19 Oct: Qt fixtures and partial native state observations; formal interaction acceptance and UAT pending

**Reason:** Label executable evidence by environment and date.

## 77. Requirements / objective tables

**Before:** Historical temporary-artifact/report tests pass; current Windows export demonstration pending

**After:** Linux, 19 Oct: temporary-artifact/report tests pass; current Windows export demonstration pending

**Reason:** Label executable evidence by environment and date.

## 78. Requirements / objective tables

**Before:** Historical controlled persistence checks; immutable provenance and backup not implemented

**After:** Linux, 19 Oct: controlled persistence checks; immutable provenance and backup not implemented

**Reason:** Label executable evidence by environment and date.

## 79. Terminology throughout

**Before:** No-code interaction is implemented through explicit task controls and interpretable defaults. The mode, source dimensions and resize backend are visible before execution, and a historical record preserves the settings actually used. Separating model adapters, presentation and persistence also localises responsibility for changes, consistent with modular software design principles (Gamma et al., 1994).

**After:** No-code interaction is implemented through explicit task controls and interpretable defaults. The mode, source dimensions and resize backend are visible before execution, and a stored record preserves the settings actually used. Separating model adapters, presentation and persistence also localises responsibility for changes, consistent with modular software design principles (Gamma et al., 1994).

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 80. Terminology throughout

**Before:** The Models settings page maintains independent classification and segmentation defaults. A candidate default is validated for the intended task before it is saved, and “restore built-in” resets that task's model preference. A missing custom default is reported as unavailable rather than silently falling back. Historical rerun still uses its recorded model path. Defaults are convenience preferences, not a migration of historical analyses to new weights.

**After:** The Models settings page maintains independent classification and segmentation defaults. A candidate default is validated for the intended task before it is saved, and “restore built-in” resets that task's model preference. A missing custom default is reported as unavailable rather than silently falling back. Recorded rerun still uses its recorded model path. Defaults are convenience preferences, not a migration of earlier analyses to new weights.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 81. Terminology throughout

**Before:** Fallback is intentionally constrained. Missing weights, missing cached UPerNet configuration and incompatible checkpoints produce explicit errors. An unsupported architecture is not replaced by a random network. A missing historical model is not replaced with the current default. The software can remain available for other operations after an error, but “graceful handling” does not mean silently obtaining a prediction from a different model.

**After:** Fallback is intentionally constrained. Missing weights, missing cached UPerNet configuration and incompatible checkpoints produce explicit errors. An unsupported architecture is not replaced by a random network. A missing recorded model is not replaced with the current default. The software can remain available for other operations after an error, but “graceful handling” does not mean silently obtaining a prediction from a different model.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 82. Terminology throughout

**Before:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify historical fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**After:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify earlier fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 83. Terminology throughout

**Before:** Source: named project tests, the historical Linux test logs, classification records and Windows execution record; statuses retain their evidence scope.

**After:** Source: named project tests, the earlier Linux test logs, classification records and Windows execution record; statuses retain their evidence scope.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 84. Terminology throughout

**Before:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses historical controlled tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**After:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses earlier controlled tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 85. Terminology throughout

**Before:** Figure 4.12. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.3.

**After:** Figure 4.12. Earlier pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.3.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 86. Terminology throughout

**Before:** Source: implementation changes and associated historical regression cases at revision 1f3e01e.

**After:** Source: implementation changes and associated earlier regression cases at revision 1f3e01e.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 87. Terminology throughout

**Before:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the historical Linux suite duration of 110.70 seconds is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**After:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the earlier Linux suite duration of 110.70 seconds is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 88. Terminology throughout

**Before:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the historical controlled tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**After:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the earlier controlled tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 89. Terminology throughout

**Before:** Tables A.1 and A.2 retain the CP1 planning baseline as a historical record. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

**After:** Tables A.1 and A.2 retain the CP1 planning baseline as a stored record. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 90. Terminology throughout

**Before:** Source: CP1 proposal planning baseline, retained as historical planned activities.

**After:** Source: CP1 proposal planning baseline, retained as earlier planned activities.

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 91. Terminology throughout

**Before:** Historical Qt coordinate/grid checks; native startup/state observations only; complete Windows case pending

**After:** Earlier Qt coordinate/grid checks; native startup/state observations only; complete Windows case pending

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 92. Terminology throughout

**Before:** Historical temporary persistence tests; historical availability failure; latest Windows invocation blocked at collection

**After:** Earlier temporary persistence tests; earlier availability failure; latest Windows invocation blocked at collection

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 93. Terminology throughout

**Before:** Historical fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**After:** Earlier fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 94. Terminology throughout

**Before:** Historical loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**After:** Earlier loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 95. Terminology throughout

**Before:** Historical small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**After:** Earlier small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 96. Terminology throughout

**Before:** Historical recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**After:** Earlier recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 97. Terminology throughout

**Before:** Project ui/, core/ and data/ modules with historical regression tests

**After:** Project ui/, core/ and data/ modules with earlier regression tests

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 98. Terminology throughout

**Before:** Historical outcomes; current collection interruption; command/environment context

**After:** Earlier outcomes; current collection interruption; command/environment context

**Reason:** Reduce repetitive historical and use stored/proposal/environment terminology where appropriate.

## 99. Terminology throughout

**Before:** The Models settings page maintains independent classification and segmentation defaults. A candidate default is validated for the intended task before it is saved, and “restore built-in” resets that task's model preference. A missing custom default is reported as unavailable rather than silently falling back. Recorded rerun still uses its recorded model path. Defaults are convenience preferences, not a migration of earlier analyses to new weights.

**After:** The Models settings page maintains independent classification and segmentation defaults. A candidate default is validated for the intended task before it is saved, and “restore built-in” resets that task's model preference. A missing custom default is reported as unavailable rather than silently falling back. Recorded rerun uses the saved model path. Defaults are convenience preferences, not a migration of earlier analyses to new weights.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 100. Terminology throughout

**Before:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify earlier fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**After:** The traceability matrix connects objectives and requirements to source modules and named tests. Its statuses identify Linux fixture verification, the recorded classifier evaluation, partial Windows runtime evidence and outstanding acceptance activities. A verification claim retains its environment and execution record.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 101. Terminology throughout

**Before:** Source: named project tests, the earlier Linux test logs, classification records and Windows execution record; statuses retain their evidence scope.

**After:** Source: named project tests, the Linux test logs dated 17 and 19 October, classification records and Windows execution record; statuses retain their evidence scope.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 102. Terminology throughout

**Before:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses earlier controlled tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**After:** The methodology combines independent task contracts, source-aware classification geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation uses controlled software tests, the classification training/test records and a partial Windows runtime record, with UAT and further acceptance activities defined separately. Chapter 4 presents these evidence streams and their implications.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 103. Terminology throughout

**Before:** Source: implementation changes and associated earlier regression cases at revision 1f3e01e.

**After:** Source: implementation changes and associated Linux regression cases at revision 1f3e01e.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 104. Terminology throughout

**Before:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the earlier Linux suite duration of 110.70 seconds is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**After:** Neither the interrupted Windows pytest duration of 24.76 seconds nor the Linux suite duration of 110.70 seconds on 17 October is an inference latency measure. Runtime observations in UAT will be reported separately from the repeatable technical benchmark defined in Appendix E.3.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 105. Terminology throughout

**Before:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the earlier controlled tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**After:** ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. Classification evaluation and partial Windows runtime observations complement the controlled software tests. Completing UAT, remaining native acceptance, segmentation evaluation and verified packaging will support the next level of claims about usability, generalisation and deployment readiness.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 106. Terminology throughout

**Before:** Source: CP1 proposal planning baseline, retained as earlier planned activities.

**After:** Source: CP1 proposal planning baseline, retained as proposal-stage planned activities.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 107. Terminology throughout

**Before:** Earlier Qt coordinate/grid checks; native startup/state observations only; complete Windows case pending

**After:** Linux, 19 Oct: coordinate/grid checks; native startup/state observations only; complete Windows case pending

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 108. Terminology throughout

**Before:** Earlier fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**After:** Linux, 19 Oct: fixture checks pass; Windows full invocation interrupted; immutable provenance not implemented

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 109. Terminology throughout

**Before:** Earlier complete invocation with continuation; 14 warnings; 110.70 s.

**After:** Continuation after collection errors; 14 warnings; 110.70 s.

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 110. Terminology throughout

**Before:** Earlier loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**After:** Linux loader/preprocessor fixtures; recorded classifier accuracy 90.68%; application backend effects remain to evaluate

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 111. Terminology throughout

**Before:** Earlier small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**After:** Linux small-screen/font checks; Windows normal/maximised/minimised state entries; restore/clipping cases not established

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 112. Terminology throughout

**Before:** Earlier recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**After:** Linux, 19 Oct: recorded-parameter semantics verified; user-efficiency benefit awaits UAT

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 113. Terminology throughout

**Before:** Project ui/, core/ and data/ modules with earlier regression tests

**After:** Project ui/, core/ and data/ modules with Linux regression tests

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 114. Terminology throughout

**Before:** Earlier outcomes; current collection interruption; command/environment context

**After:** Environment/date-specific outcomes, commands and prerequisite states

**Reason:** Prefer direct concepts and environment/date labels to repeated chronology qualifiers.

## 115. 3.6.6 / Table 3.6

**Before:** Linux, 19 Oct: structural fixtures verified; Windows real-classifier load/validation recorded; latest availability test not executed

**After:** Linux, 19 Oct: structural checks pass; built-in availability fails for missing segmentation weight. Windows classifier validation recorded.

**Reason:** Distinguish the completed Linux test from Windows startup and the actual remaining availability failure.

## 116. 3.6.6 / Table 3.6

**Before:** Earlier temporary persistence tests; earlier availability failure; latest Windows invocation blocked at collection

**After:** Linux, 19 Oct: persistence checks pass; Windows end-to-end persistence acceptance pending.

**Reason:** Report the current persistence checks without conflating them with the model-availability assertion.

## 117. 4.5.1 / Table 4.9

**Before:** Supported contracts implemented; real classifier loaded and validated on Windows; complete latest suite blocked at collection

**After:** Windows real-classifier loading/validation recorded; Linux structural checks pass with one missing-segmentation-file availability failure.

**Reason:** Replace the unqualified latest-suite interruption with platform-specific results.

## 118. 4.5.1 / Table 4.9

**Before:** Classifier test accuracy 90.68% and macro-F1 88.59% in the recorded pipeline; segmentation and tiled predictive evaluation pending

**After:** Classifier benchmark: 90.68% accuracy / 88.59% macro-F1 with OpenCV/Albumentations. Default-Pillow, segmentation and tiled predictive evaluation pending.

**Reason:** Prevent interpreting the recorded benchmark as measured default-application accuracy.

## 119. 5.3

**Before:** The first contribution is an implemented local workflow connecting compatible PyTorch inference to a graphical desktop interface and persistent per-analysis records. It demonstrates the feasibility of integrating these components without a running application server, while preserving explicit deployment prerequisites.

**After:** The first contribution is a local classification workflow connecting supported PyTorch inference to a graphical interface and persistent analysis records. A separately integrated segmentation pathway broadens inspection options, with its evidence and evaluation limits explicitly distinguished from the trained classifier.

**Reason:** Clarify the main contribution without overstating real segmentation validation.

## 120. 3.6.1 / 3.7

**Before:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.5 gives the host hardware and separates its installed GPU from the actual computation device.

**After:** The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.

**Reason:** Correct the host-table cross-reference and separate verification work from evidence retention.

## 121. 3.6.1 / 3.7

**Before:** Complete UAT, remaining native cases and segmentation evaluation; preserve the current collection failure

**After:** Complete UAT, native rerun and segmentation evaluation; retain each executed result with its environment and date

**Reason:** Correct the host-table cross-reference and separate verification work from evidence retention.

## 122. References

**Before:** [Not present]

**After:** Kather, J.N. (n.d.) deep-stroma-histology: Code and dataset guidance for histological tissue classification. Project repository. https://github.com/jnkather/deep-stroma-histology

**Reason:** Add a supported explanation or clearly scoped method.

## 123. 4.3.1

**Before:** Figure 4.12. Earlier pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.3.

**After:** Figure 4.12. Pytest log excerpt (Linux, 17 October 2026). Source: saved Linux/offscreen-Qt log; current Linux and Windows outcomes are reported in Table 4.3.

**Reason:** Use an explicit date/environment instead of Historical and preserve the log’s original scope.

## 124. Contents / caption indexes

**Before:** 4.3.4 Classification training and test results	55

**After:** 4.2.6 Classification training and test results	55

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 125. Contents / caption indexes

**Before:** 4.3.5 Runtime and deployment verification status	59

**After:** 4.3.4 Runtime and deployment verification status	59

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 126. Contents / caption indexes

**Before:** Figure 4.10. Historical pytest outcome excerpt for 17 October 2026. Source: saved Linux/offscreen-Qt log; the current Windows invocation is reported separately in Table 4.1.	53

**After:** Figure 4.12. Pytest log excerpt (Linux, 17 October 2026). Source: saved Linux/offscreen-Qt log; current Linux and Windows outcomes are reported in Table 4.3.	53

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 127. Contents / caption indexes

**Before:** Figure 4.11. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.	56

**After:** Figure 4.10. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.	56

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 128. Contents / caption indexes

**Before:** Figure 4.12. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.	58

**After:** Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: saved test-7k/confusion_matrix.png from the classification evaluation; its count matrix agrees with predictions.csv. Rows are true labels and columns predicted labels.	58

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 129. Contents / caption indexes

**Before:** Table 4.1. Automated verification records by date and environment at revision 1f3e01e	51

**After:** Table 4.3. Automated verification records by date and environment at revision 1f3e01e	51

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 130. Contents / caption indexes

**Before:** Table 4.2. Windows test host and actual CPU runtime on 19 October 2026	52

**After:** Table 4.4. Windows test host and actual CPU runtime on 19 October 2026	52

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 131. Contents / caption indexes

**Before:** Table 4.3. Implementation challenges and verified resolutions	54

**After:** Table 4.5. Implementation challenges and verified resolutions	54

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 132. Contents / caption indexes

**Before:** Table 4.4. Classification evaluation summary	56

**After:** Table 4.1. Classification evaluation summary	56

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 133. Contents / caption indexes

**Before:** Table 4.5. Class-wise classification performance on 7,180 test images	57

**After:** Table 4.2. Class-wise classification performance on 7,180 test images	57

**Reason:** Match visible labels to relocated headings and renumbered captions.

## 134. Contents / List of Figures / List of Tables: head_12

**Before:** 6

**After:** 7

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 135. Contents / List of Figures / List of Tables: head_67

**Before:** 42

**After:** 41

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 136. Contents / List of Figures / List of Tables: head_68

**Before:** 44

**After:** 43

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 137. Contents / List of Figures / List of Tables: new_4_3_4_Classification_training_and_test

**Before:** 55

**After:** 51

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 138. Contents / List of Figures / List of Tables: head_78

**Before:** 51

**After:** 55

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 139. Contents / List of Figures / List of Tables: head_79

**Before:** 51

**After:** 55

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 140. Contents / List of Figures / List of Tables: head_80

**Before:** 54

**After:** 58

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 141. Contents / List of Figures / List of Tables: head_81

**Before:** 55

**After:** 59

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 142. Contents / List of Figures / List of Tables: new_4_3_5_Runtime_and_deployment_verificat

**Before:** 59

**After:** 60

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 143. Contents / List of Figures / List of Tables: head_82

**Before:** 59

**After:** 60

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 144. Contents / List of Figures / List of Tables: head_84

**Before:** 60

**After:** 61

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 145. Contents / List of Figures / List of Tables: head_85

**Before:** 61

**After:** 62

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 146. Contents / List of Figures / List of Tables: head_87

**Before:** 62

**After:** 63

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 147. Contents / List of Figures / List of Tables: head_91

**Before:** 64

**After:** 65

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 148. Contents / List of Figures / List of Tables: head_105

**Before:** 81

**After:** 80

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 149. Contents / List of Figures / List of Tables: head_106

**Before:** 81

**After:** 80

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 150. Contents / List of Figures / List of Tables: head_109

**Before:** 83

**After:** 82

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 151. Contents / List of Figures / List of Tables: head_115

**Before:** 86

**After:** 85

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 152. Contents / List of Figures / List of Tables: head_116

**Before:** 86

**After:** 85

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 153. Contents / List of Figures / List of Tables: head_117

**Before:** 87

**After:** 86

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 154. Contents / List of Figures / List of Tables: head_120

**Before:** 88

**After:** 87

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 155. Contents / List of Figures / List of Tables: new_Figure_4_11__Classification_training_a

**Before:** 56

**After:** 52

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 156. Contents / List of Figures / List of Tables: new_Figure_4_12__Nine_class_confusion_matr

**Before:** 58

**After:** 54

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 157. Contents / List of Figures / List of Tables: cap_Figure_4_10

**Before:** 53

**After:** 57

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 158. Contents / List of Figures / List of Tables: new_Table_4_4__Classification_evaluation_s

**Before:** 56

**After:** 52

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 159. Contents / List of Figures / List of Tables: new_Table_4_5__Class_wise_classification_p

**Before:** 57

**After:** 53

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 160. Contents / List of Figures / List of Tables: cap_Table_4_1

**Before:** 51

**After:** 56

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 161. Contents / List of Figures / List of Tables: new_Table_4_2__Windows_test_host_and_actua

**Before:** 52

**After:** 56

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 162. Contents / List of Figures / List of Tables: cap_Table_4_2

**Before:** 54

**After:** 58

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 163. Contents / List of Figures / List of Tables: cap_Table_4_4

**Before:** 60

**After:** 61

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.

## 164. Contents / List of Figures / List of Tables: cap_Table_4_5

**Before:** 61

**After:** 62

**Reason:** Refresh the existing cached page reference from the rendered PDF after the section move; retain field instructions and styles.
