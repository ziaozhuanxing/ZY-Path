# 本轮正文与局部布局修改清单

按章节记录修改前、修改后及原因。未补写第2、3项所需的新证据或结论；原参考文献格式、已有模型结果及待补证据保留。

## 1. Abstract

**修改前**：ZY-Path is a local PyQt5 desktop application for model-aware histopathology classification, combining Single image and Tiled analysis modes, spatial inspection, SQLite history, recorded rerun and export, with a separate supervisor-provided segmentation integration. On 7,180 CRC-VAL-HE-7K patches, the classifier achieved 90.68% accuracy and 88.59% macro-F1 through both the recorded OpenCV/Albumentations pipeline and the application’s default Pillow Single image core, with agreement on all predicted labels. The complete native Windows automated suite passed all 370 tests; UAT, segmentation accuracy, systematic performance measurement and clean-machine deployment remain to be evaluated.

**修改后**：Deploying pathology models through separate scripts makes preprocessing, spatial sampling and previous analysis settings difficult to inspect. This project develops ZY-Path, a local PyQt5 desktop application that connects supported PyTorch CPU inference to explicit Single image and Tiled analysis controls, spatial inspection, recorded history and export, with a separate supervisor-provided segmentation integration. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native 224 × 224 CRC-VAL-HE-7K patches through the application’s default Pillow core, agreeing with every predicted label from the recorded reference pipeline. The 19 October Windows baseline passed 370 automated tests; the current-source Linux/offscreen-Qt run passed 504 tests with one genuine segmentation-weight availability failure and no errors. The engineering contribution is a model-aware desktop workflow with explicit crop geometry, independent task semantics and reproducible parameter restoration. UAT, final-version manual Windows acceptance, systematic performance measurements and clean-machine deployment remain incomplete.

**原因**：Add the problem, purpose and engineering contribution required by the rubric; retain scoped measured results and actual remaining evidence.

## 2. 3.1

**修改前**：The implementation is identified by revision 7bd3552. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the software version and the source content evaluated in the final Windows run.

**修改后**：The current implementation is identified by revision 8c4830c. The earlier Windows baseline is revision 7bd3552; the completed Windows and current-source Linux invocations are reported separately. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the source versions and supporting execution records.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 3. 1.5

**修改前**：Local execution requires the selected model files and, for UPerNet reconstruction, its verified configuration in the local Hugging Face cache. Windows source execution and real-classifier validation are documented in Section 4.3.3; offline package verification is addressed separately in Section 4.3.4.

**修改后**：Local source execution requires the selected model files and the verified UPerNet configuration in the local Hugging Face cache. Frozen-build support instead packages that configuration with the application. Windows source execution and real-classifier validation are documented in Section 4.3.3; building and validating a clean-machine offline distribution remain separate activities in Section 4.3.4.

**原因**：Describe the implemented source/frozen resource paths without claiming a tested deployment.

## 4. 2.6

**修改前**：UPerNet reconstruction loads its configuration from the local Hugging Face cache with local_files_only=True. Preparing a redistributable application therefore requires packaging the permitted weights, cached configuration and runtime dependencies. PyInstaller is a candidate tool for this future deployment step (PyInstaller Development Team, n.d.); the current deployment evidence is assessed in Section 4.3.4.

**修改后**：Source-based UPerNet reconstruction loads its configuration from the local Hugging Face cache with local_files_only=True. The Windows build script and PyInstaller specification now describe how to collect the permitted weights, verified configuration, report font and runtime dependencies (PyInstaller Development Team, n.d.). Frozen execution reads the bundled configuration. These implemented build preparations are distinct from an actual version-matched build and clean-machine offline acceptance, whose status is assessed in Section 4.3.4.

**原因**：Update the implemented packaging preparation while preserving the verified citation and deployment limits.

## 5. 1.2

**修改前**：The original research questions remain relevant to this implemented scope:

**修改后**：The research questions guide the implemented scope and its evaluation:

**原因**：Use direct academic wording rather than describing the revision process.

## 6. 2.3.2

**修改前**：Slideflow supports deep-learning development for digital histopathology, with slide processing, model training and real-time whole-slide visualisation (Dolezal et al., 2024). Its official repository explicitly describes Slideflow Studio, model-development functionality, stain-processing tools and visualisation. These documented capabilities correct the proposal's implication that Slideflow is only a command-line framework.

**修改后**：Slideflow supports deep-learning development for digital histopathology, with slide processing, model training and real-time whole-slide visualisation (Dolezal et al., 2024). Its official repository explicitly describes Slideflow Studio, model-development functionality, stain-processing tools and visualisation.

**原因**：State the documented platform capabilities without recounting manuscript correction.

## 7. 3.2.1 / F05

**修改前**：Nine-class legend, per-tile label/confidence and actual-area estimates agree with stored tiles

**修改后**：Nine-class legend, numbered tiles, linked image/table selection, original-crop preview, per-tile confidence and actual-area estimates agree with stored tiles

**原因**：Include the implemented tile inspection workflow.

## 8. 3.2.1 / F07

**修改前**：Overlay/map/original, opacity, comparison, linked navigation and appropriate grid remain aligned

**修改后**：Overlay/map/original, opacity, linked navigation and vector grid remain aligned during zoom, panning and divider resizing

**原因**：Include navigation and divider regressions.

## 9. 3.2.1 / F12

**修改前**：PNG/PDF contain the selected presentation and available recorded metadata

**修改后**：PNG/PDF retain recorded identity/statistics; PDF quality is selectable, background export can be cancelled and an existing destination is replaced only after successful completion

**原因**：Include PDF quality and safe background export.

## 10. 3.2.1 / F15

**修改前**：Mode/default selection, source tile dimensions and resize method persist with clear scope

**修改后**：Mode, tile dimensions and resize method persist; ordinary Run uses current preferences and Re-run uses the selected record snapshot

**原因**：Make preference lifetime an observable acceptance condition.

## 11. 3.2.1 / F17

**修改前**：[New table row]

**修改后**：F17 | Clear the workspace and history selection | Clear view removes transient input/result/session state while retaining saved history/files/settings; Clear Selection leaves no selected history row

**原因**：Document the completed clear-view and zero-selection operations.

## 12. 3.2.2 / N04

**修改前**：Native Windows automated layout/window-state checks passed; complete device/accessibility manual acceptance pending.

**修改后**：Windows baseline and current Linux/offscreen checks cover layout behaviour; final-version native Windows and assistive-technology manual acceptance remain pending.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 13. 3.2.2 / N05

**修改前**：Planned fixed-workload benchmark with CPU/RAM/image/tile details

**修改后**：Fixed-workload CPU timings with predefined repetitions, separate cold/warm cases, file sizes and process memory

**原因**：Make the measurement procedure operational without inventing results.

## 14. 3.2.2 / N07

**修改前**：Real classifier loads on Windows; complete offline package and clean-machine deployment unverified

**修改后**：Build script/specification and local-resource checks implemented; actual packaged artifact, clean-machine and offline acceptance unverified

**原因**：Separate build preparation from deployment verification.

## 15. 3.2.2

**修改前**：[New explanatory paragraph]

**修改后**：The final acceptance record must state its tested logical window sizes and display scales, whether essential controls remain reachable, and any failure to resize or restore. Performance observations will use the predefined workload and timing boundaries in Appendix E.3. Thresholds requiring user or institutional agreement remain protocol decisions rather than retrospectively selected pass criteria.

**原因**：Clarify how qualitative non-functional requirements will be accepted.

## 16. 3.3.1

**修改前**：[New explanatory paragraph]

**修改后**：The application loads and runs PyTorch models on CPU; no OpenVINO conversion or runtime is implemented. The genuine classification checkpoint occupies 1,726,089 bytes (1.646 MiB). Its checksum is recorded in Appendix E.1. A segmentation file-size measurement has not been supplied, and there is no converted-model size to report. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

**原因**：Resolve the CPU/conversion and original-model-size questions using actual code and file measurement.

## 17. 3.3.2

**修改前**：[New explanatory paragraph]

**修改后**：The augmentation order and parameters are reproducible from the training script: Resize(224, 224); VerticalFlip(p=0.5); HorizontalFlip(p=0.5); HueSaturationValue(hue_shift_limit=(-25, 0), sat_shift_limit=0, val_shift_limit=0, p=1); Rotate(p=1, border_mode=cv2.BORDER_CONSTANT, value=0); RandomSizedCrop((224, 224), 224, 224); and ToTensorV2 followed by float conversion. Arguments not explicitly set use the defaults of the recorded Albumentations 1.3.1 environment. Because the crop height range is fixed at 224 after resizing to 224 × 224, this crop operation does not provide evidence of training with different source fields of view.

**原因**：Specify the actual operations and avoid implying unsupported multi-scale augmentation.

## 18. 3.3.2

**修改前**：[New explanatory paragraph]

**修改后**：Class weights are calculated as w_c = 1 − n_c / Σ_j n_j from the training counts; they are not inverse-frequency weights. Cross-entropy uses a summed reduction, with epoch reporting normalised by the accumulated class-weight denominator. The script seeds Python, NumPy, PyTorch and the data-loader generator with 42, seeds workers from their PyTorch worker seed, disables cuDNN benchmarking and requests deterministic cuDNN behaviour. Continuation restores the model, optimizer and scheduler states. The reported results describe this recorded run; no multi-seed training-variation study was conducted.

**原因**：Document weighting, seeding and continuation precisely without claiming replicated training.

## 19. 3.3.4

**修改前**：Source crop dimensions determine the field of view before resampling to 224 × 224. The dataset’s nominal source-patch dimensions and resolution are documented in Section 4.2.6. The interface retains 512 × 512 as an editable starting value; its physical-scale equivalence to the training data is unverified for an arbitrary uploaded image. The evaluation consequences are discussed in Section 4.5.3.

**修改后**：Source crop dimensions determine the field of view before resampling to 224 × 224. At the source dataset’s nominal 0.5 μm/pixel, a 224-pixel edge spans 112 μm. If a new raster’s resolution r is known in μm/pixel, a candidate crop edge covering that field is approximately 112/r pixels; this is a physical-scale calculation, not evidence of optimal predictive performance. The interface retains 512 × 512 as an editable starting value. Values such as 256 and 300 are exploratory source-crop candidates, while the network input remains 224 × 224. A controlled comparison should keep the crop centre, source image, model, backend and display dimensions fixed. No outcomes from those new-size trials are supplied here.

**原因**：Make source geometry and the physical-scale calculation explicit without claiming unperformed trials.

## 20. 3.3.4

**修改前**：[New explanatory paragraph]

**修改后**：Ordinary Run Inference snapshots the current preference width, height and resize backend at launch. Restoring a history result does not replace those new-run defaults. Re-run alone supplies the recorded parameter snapshot, and the input summary returns to current preferences when it finishes. A change made while inference is active applies to the next run. The 11-case preference-lifetime regression verifies actual crop boxes, recorded geometry, same-value re-entry, mode/image changes, clear view and parameter isolation.

**原因**：Document the current fix and the distinct semantics of new runs and recorded reruns.

## 21. 3.3.8

**修改前**：[New explanatory paragraph]

**修改后**：Clear view removes the current input, visible result and session metadata and clears history selection. It does not delete saved analyses or source files. Clear Selection, Esc in the history table and a click on empty table space can leave no row selected. Restoring history also synchronises the left-side original-image thumbnail; the completed record retains its own identity independently of subsequent model selections.

**原因**：Include the implemented reset/selection and history-image behaviour.

## 22. 3.3.9

**修改前**：[New explanatory paragraph]

**修改后**：PdfExportWorker snapshots the selected result, metadata, map and export options before background generation. Progress and cooperative cancellation keep the GUI responsive; the destination is atomically replaced only after a complete report is written. Standard PDF quality is the default: report display copies are sized for up to 300 DPI, large photographs and overlays use high-quality JPEG, and class maps use nearest-neighbour resizing with lossless encoding. Original resolution retains full image pixels with lossless encoding. Text, numerical tables, predictions, saved masks and source files are unchanged. The report distinguishes original image dimensions from display-copy quality and an export-time file checksum from an identity actually recorded at inference.

**原因**：Describe the current export architecture and image-quality/provenance boundaries.

## 23. 3.3.9

**修改前**：[New explanatory paragraph]

**修改后**：The inference panel’s built-in/custom selector is a session choice. Selecting the built-in model clears the visible local-model filename while remembering that local choice for a later explicit return in the same session. This does not change either task’s saved startup default or relabel the completed result’s Session metadata. Interrupted custom validation is resumed when required rather than leaving a stale loading state.

**原因**：Explain runtime source selection versus persistent defaults.

## 24. 3.4.2

**修改前**：[New explanatory paragraph]

**修改后**：Tile boundaries and optional one-based tile numbers are drawn in source coordinates. Selecting a tile in an image or its detail row locates the same numbered crop and displays its original pixels, rectangle, label and confidence. The Square action copies the current width to the height once; dimensions remain independently editable. Numeric preference controls route wheel input to page scrolling. The expandable resize guide explains the available backends without changing the model or network input size.

**原因**：Include the completed tile inspection and explicit preference controls.

## 25. 3.4.2

**修改前**：[New explanatory paragraph]

**修改后**：Linked panning updates the peer view without repeatedly recentering the actively dragged pane. Resizing retains the intended source-coordinate centre, and divider dragging uses a rubber-band preview before the panes resize on release. Fractional wheel deltas produce proportional zoom while zero or horizontal-only deltas do not trigger an unintended zoom. These operations affect presentation and leave analysis values unchanged.

**原因**：Document the navigation stability changes and their semantic limit.

## 26. 3.4.4

**修改前**：Windows baseline and current-source checks previously had no version distinction.

**修改后**：Automated checks cover small logical screens, repeated narrow/wide transitions and Qt scale-factor simulation. The 19 October Windows baseline passed its maximise/restore, saved-geometry, comparison/grid and compact-viewport cases. Current-source navigation and parameter-lifetime regressions passed on Linux/offscreen Qt, including a separate 2× scale-factor run. They do not replace final-version native Windows manual acceptance with authorised real images in Appendix D.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 27. 3.5.1

**修改前**：The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Model validation is included in the run workflow; tiled classification extends the classification choice when that explicit mode is selected. Restoring history and rerunning history are separate use cases because only the latter executes inference and creates a new record. Figure 3.3 maps the actor to the implemented use cases.

**修改后**：The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Selecting a model includes compatibility validation. Tiled analysis is an explicit classification variant. Restore saved result and Re-run recorded analysis are separate use cases because only rerun performs inference and creates a new record; Search/filter locates records without executing either operation. Figure 3.3 maps these actions and their scope.

**原因**：Remove the diagram/prose contradiction and clarify optional use cases.

## 28. 3.5.2

**修改前**：The sequence diagram follows a successful completed run after the user selects an image, task and model. MainWindow captures parameters, starts the worker and receives progress/result signals. The worker validates and executes the pipeline; the GUI coordinator renders the result, saves artifacts and inserts a history record. Cancellation and saving failure are alternatives, not successful completed-history paths. Figure 3.4 shows the interaction sequence and the alternative cancellation and persistence-failure paths.

**修改后**：The sequence diagram follows a run after image, task and model selection. MainWindow snapshots the current preferences for ordinary Run or the selected record for Re-run, then starts the worker. Signals deliver progress and a completed result. The coordinator saves completed artifacts and inserts a record only after successful persistence. Figure 3.4 uses guarded alternative fragments for cancellation, pipeline error and persistence failure; these exits are distinct from completed history.

**原因**：Use explicit alternative fragments and current parameter-source semantics.

## 29. 3.5.3

**修改前**：The class diagram shows principal runtime responsibilities rather than every widget. MainWindow coordinates panels and services; InferenceEngine depends on the loader, preprocessor, parser and task-specific spatial functions. ClassificationResult and SegmentationResult share ImageComparison and ZoomableImageView. DatabaseManager and ExportManager handle persistence/export; QSettings stores preferences separately. Figure 3.5 identifies these classes and their principal dependencies.

**修改后**：The class diagram shows selected runtime responsibilities rather than every widget. MainWindow coordinates input, history, inference, persistence and export. InferenceEngine depends on model loading, preprocessing and output parsing. PdfExportWorker delegates report generation to ExportManager. Spatial result pages use ImageComparison and ZoomableImageView. Figure 3.5 distinguishes coordination dependencies and worker inheritance for the current implementation.

**原因**：Update the selected class responsibilities to include asynchronous export.

## 30. 3.5.4

**修改前**：The activity diagram highlights the explicit mode decision, distinct preprocessing/task branches and completion/cancellation outcomes. It prevents a misleading conceptual flow in which image dimensions alone choose tiled classification or a cancellation request immediately terminates a model operation. Figure 3.6 traces these decisions through successful completion, cancellation and error exits.

**修改后**：The activity diagram distinguishes current-preference Run from recorded-parameter Re-run before selecting the task/mode pathway. Classification crops and segmentation processing regions retain independent geometry. Cancellation is checked at safe points before/after model work and between processing regions. Figure 3.6 labels the decisions and success/error exits; a request does not forcibly interrupt a running forward operation.

**原因**：Represent current parameter ownership and guarded activity branches.

## 31. 3.6.1

**修改前**：[New explanatory paragraph]

**修改后**：The current-source Linux invocation uses Python 3.10.22, pytest 9.1.1, PyQt5 5.15.11, Qt runtime 5.15.19 and Qt compiled 5.15.14 with the offscreen Qt platform. It completed 505 cases: 504 passed and one production segmentation-file availability assertion failed. The current-source 126-case related run and separate 14-case 2×-DPI run passed; these subsets are not added to the full-suite count. Existing source hashes connect that executed content to revision 8c4830c.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 32. 3.6.4

**修改前**：The planned pilot retains the CP1 target of approximately 8–10 participants, subject to recruitment, consent and institutional requirements. Participants should include intended educational/research users with varied programming and pathology experience. Recruitment is purposive/convenience sampling rather than a representative clinical sample; results should be reported accordingly.

**修改后**：The planned pilot targets approximately 8–10 intended educational/research users, subject to recruitment, consent and institutional requirements. Purposive/convenience recruitment should include varied programming and pathology experience. Protocol revision 1.0 in Appendix B fixes material identifiers, task geometry, assistance categories and stop rules before the first participant; selecting and authorising the actual material pack remains a prerequisite. This is a formative usability study, not a representative clinical sample.

**原因**：Turn the generic UAT template into a versioned operational protocol without implying recruitment occurred.

## 33. 3.6.4

**修改前**：Participants receive the same orientation and authorised sample files, then attempt a fixed task sequence: load/classify an image; select tiled analysis and inspect a tile; explain tile coverage versus confidence; compare aligned source/result regions; inspect segmentation; locate and restore history; rerun after changing current defaults; export; cancel; and configure/restore a task-specific model default. Assisted completion is recorded separately from independent completion. Cancellation is judged against the intended safe-stop outcome, not the speed of killing a thread.

**修改后**：Participants receive the same five-minute orientation and the approved material pack, then attempt the ten tasks in Table B.1. P01 is an authorised native 224 × 224 classification patch; P02 is an authorised 1024 × 768 raster crop prepared consistently from its source; S01 is a saved real-model segmentation record. R01 is a prepared P02 classification record using 256 × 256 source tiles and Pillow bilinear. Those dimensions standardise the interaction task and are not a validated training-scale recommendation. T07 explicitly contrasts Re-run of R01 with ordinary Run after changing current dimensions to 512 × 512. Actual filenames, checksums, permissions and the tested commit must be entered in the supplied material register before testing.

**原因**：Predefine a repeatable task pack and distinguish intended protocol values from uncollected evidence.

## 34. 3.6.5

**修改前**：Automated results are labelled by environment, date and software version. On 19 October 2026, the final native Windows invocation completed all 370 tests with no failures, errors or skips. Table 4.3 presents this completed result; Appendix C retains the preceding regression subset and earlier execution history.

**修改后**：Automated results are labelled by environment, date and source version. The 19 October Windows baseline completed 370 tests without failures/errors/skips. The current-source 26 October Linux/offscreen-Qt invocation completed 505 cases with 504 passed, one genuine segmentation-weight availability failure and no errors/skips. Table 4.3 presents both complete invocations separately; related subsets and original interruptions remain in Appendix C.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 35. 3.6.6 / F01 / O3

**修改前**：Windows full-suite image-loading and input-error cases passed; representative real-image manual tasks pending.

**修改后**：Windows-baseline full-suite image-loading and input-error cases passed; representative real-image manual tasks pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 36. 3.6.6 / F02 / O2

**修改前**：Windows loader/probe and built-in-path cases passed; real-classifier validation recorded. Arbitrary-model semantic compatibility is outside this check.

**修改后**：Windows baseline loader/probe and built-in paths passed. Current Linux loader cases passed, but the separate genuine segmentation-weight availability assertion failed because that resource is absent. Probe checks do not validate semantic accuracy.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 37. 3.6.6 / F03 / O3

**修改前**：Windows software cases passed; default-Pillow patch accuracy 90.68%, macro-F1 88.59% on native 224 × 224 inputs (Section 4.2.6).

**修改后**：Windows-baseline software cases passed; default-Pillow patch accuracy 90.68%, macro-F1 88.59% on native 224 × 224 inputs (Section 4.2.6). Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 38. 3.6.6 / F04–F05 / O3–O4

**修改前**：Windows crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending.

**修改后**：Windows-baseline crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 39. 3.6.6 / F06 / O3–O4

**修改前**：Windows synthetic segmentation geometry/statistics and display cases passed; real-weight demonstration and ground-truth evaluation pending.

**修改后**：Windows-baseline synthetic segmentation geometry/statistics and display cases passed; real-weight demonstration and ground-truth evaluation pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 40. 3.6.6 / F07 / O4

**修改前**：Windows coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed; formal real-image manual acceptance pending.

**修改后**：Windows-baseline coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed; formal real-image manual acceptance pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 41. 3.6.6 / F08 / O6

**修改前**：Windows persistence and artifact cases passed with temporary test records; real-image manual workflow evidence pending.

**修改后**：Windows-baseline persistence and artifact cases passed with temporary test records; real-image manual workflow evidence pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 42. 3.6.6 / F09 / O7

**修改前**：Windows query, calendar and history-interaction cases passed; user task outcomes await UAT.

**修改后**：Windows-baseline query, calendar and history-interaction cases passed; user task outcomes await UAT. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 43. 3.6.6 / F10–F11 / O7

**修改前**：Windows restore and recorded-model/mode/parameter rerun cases passed; user-efficiency assessment awaits UAT.

**修改后**：Windows-baseline restore and recorded-model/mode/parameter rerun cases passed; user-efficiency assessment awaits UAT. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 44. 3.6.6 / F12 / O5

**修改前**：Windows file/report and recorded-metadata cases passed; final real-image report screenshots pending.

**修改后**：Windows-baseline file/report and recorded-metadata cases passed; final real-image report screenshots pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 45. 3.6.6 / F13 / O1

**修改前**：Windows cooperative-stop, late-result and destruction/callback lifecycle cases passed; real-model manual cancellation record pending.

**修改后**：Windows-baseline cooperative-stop, late-result and destruction/callback lifecycle cases passed; real-model manual cancellation record pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 46. 3.6.6 / F14–F15 / O1–O3

**修改前**：Windows defaults, validation, preferences and history-isolation cases passed.

**修改后**：Windows-baseline defaults, validation, preferences and history-isolation cases passed. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 47. 3.6.6 / F16 / O6–O7

**修改前**：Windows app-owned artifact cleanup and source-preservation cases passed.

**修改后**：Windows-baseline app-owned artifact cleanup and source-preservation cases passed. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 48. 3.6.6 / N01, N04 / O1, O4

**修改前**：Windows window-state, restore, small-viewport and layout cases passed; multi-monitor/assistive-technology manual acceptance pending.

**修改后**：Windows-baseline window-state, restore, small-viewport and layout cases passed; multi-monitor/assistive-technology manual acceptance pending. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 49. 3.6.6 / N02, N06 / O2, O6–O7

**修改前**：Windows missing-file/error handling and recorded-parameter cases passed; immutable provenance is not implemented.

**修改后**：Windows-baseline missing-file/error handling and recorded-parameter cases passed; immutable provenance is not implemented. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 50. 3.6.6 / N03 / O1

**修改前**：Local execution established by design and recorded source startup; security audit not performed.

**修改后**：Local execution established by design and recorded source startup; security audit not performed. Relevant current-source fixture cases also passed on Linux/offscreen Qt; see Section 4.3.1 for the full-suite resource failure.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 51. 3.6.6 / N05, N07–N08 / O1

**修改前**：Windows full suite: 370 passed, 0 failed/errors/skipped; repeated benchmark, clean package and coverage measurement pending.

**修改后**：Windows baseline: 370 passed. Current Linux: 504 passed, 1 file-availability failure, 0 errors/skips. Repeated performance measurement, coverage percentage and clean-machine deployment remain incomplete.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 52. 3.6.6 / F17

**修改前**：[New table row]

**修改后**：F17 / O1, O6–O7 | MainWindow; InferencePanel; HistoryPanel | test_clear_view_and_history_sync.py | Current Linux clear-view, zero-selection, history-thumbnail and source-preservation cases passed; final-version native acceptance remains pending.

**原因**：Add traceability for workspace reset and history selection.

## 53. 3.6.6 / Table 3.6 source

**修改前**：Source: named project tests and the completed native Windows full-suite log/XML of 19 October 2026, together with the classifier evaluation.

**修改后**：Source: the named project tests, the 19 October Windows baseline log/XML, the 26 October current-source Linux log/XML and recorded classifier evaluation. Subset counts are reported separately.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 54. 4.2.1

**修改前**：[New explanatory paragraph]

**修改后**：Current-version additions comprise numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run now reads current preferences independently of restored or rerun records. The corresponding current-source regressions are Linux/offscreen-Qt evidence; the earlier Windows session does not establish their native acceptance.

**原因**：Account for the implemented features added after the earlier thesis baseline.

## 55. 4.2.2

**修改前**：Figure 4.2 is a current Qt result-view capture using a deterministic synthetic fixture. It demonstrates the grid, paired views and statistics placement. The fixture deliberately contains 49 tiles with 47 STR, one NORM and one MUC assignments. These assignments are prescribed test data, not model predictions on the coloured source pattern and not evidence of classifier accuracy.

**修改后**：Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Current-version real-image inspection remains reserved in Figure 4.3, including tile numbers and original-crop detail.

**原因**：Keep the genuine fixture screenshot while avoiding a false claim that it is the final current UI.

## 56. 4.2.2

**修改前**：[New explanatory paragraph]

**修改后**：In the current viewer, optional tile numbers identify the same one-based entry in the image, detail table and original-crop preview. The input summary displays the current Run dimensions and planned grid. Restoring an older result preserves its recorded geometry in the result panel while leaving current new-run preferences intact.

**原因**：Describe the current inspection and parameter-lifetime behaviour.

## 57. 4.2.4

**修改前**：[New explanatory paragraph]

**修改后**：The current export implementation adds a background worker, cancellation and atomic replacement of completed PDF files. Standard and Original resolution settings distinguish sharing copies from full-pixel inspection. A controlled 2100 × 1500 synthetic texture/label fixture produced a classification report of 652,957 bytes in Standard versus 18,668,531 bytes at Original resolution, and a segmentation report of 652,071 versus 18,747,945 bytes. These measurements describe synthetic export fixtures, not model accuracy, a native Windows benchmark or a guaranteed Google Drive preview limit.

**原因**：Use existing measured export-size evidence with explicit fixture and platform limits.

## 58. 4.2.5

**修改前**：[New explanatory paragraph]

**修改后**：The current preference-lifetime regression first creates a result at 8 × 7 source pixels, changes preferences to 16 × 12, restores or reruns the old record and starts a new run. On a 31 × 23 synthetic raster, the new result contains the expected four real rectangles, including smaller right/bottom edges, while the recorded rerun retains its original geometry and backend. All 11 focused cases passed. The small dimensions are deterministic test inputs and do not recommend a biological tile scale.

**原因**：Present a concrete before/after validation example without treating fixture predictions as model evidence.

## 59. 4.2.6 / Table 4.1

**修改前**：[New table row]

**修改后**：Original checkpoint size | 1,726,089 bytes (1.646 MiB) | Measured genuine classification checkpoint; no model conversion performed

**原因**：Report the original weight size without inventing an OpenVINO after-conversion size.

## 60. 4.3.1

**修改前**：The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source content is recorded in revision 7bd3552, as identified in Appendix C. Table 4.3 summarises this completed target-platform invocation.

**修改后**：The completed Windows invocation on 19 October 2026 passed all 370 cases at baseline source 7bd3552, with 0 failures/errors/skips, 15 warnings and 194.10 seconds (exit 0). The current-source 26 October Linux/offscreen-Qt invocation completed 505 cases: 504 passed, 1 failed, 0 errors and 0 skipped, with 14 warnings in 219.20 seconds (exit 1). The failed case asserts the presence of the genuine built-in segmentation weight, which is absent from that installation. Table 4.3 separates the two versions and platforms; no current-version native Windows pass is inferred.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 61. 4.3.1 / Table 4.3

**修改前**：Table 4.3. Final Windows automated test result

**修改后**：Table 4.3. Complete automated invocations by source version and environment

**原因**：Align the caption with the evidence now presented.

## 62. 4.3.1 / Table 4.3

**修改前**：Windows, 19 Oct; final full run

**修改后**：Windows baseline, 19 Oct 2026

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 63. 4.3.1 / Table 4.3

**修改前**：[New table row]

**修改后**：Linux/offscreen Qt, 26 Oct 2026; current source | 504 | 1 | 0 | 505 collected; 0 skipped; 14 warnings; 219.20 s; exit 1. Source content recorded in 8c4830c; genuine segmentation weight absent.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 64. 4.3.1 / Table 4.3 source

**修改前**：Source: the full-suite pytest log and XML result of 19 October 2026, beginning at 22:26 (UTC+08:00). Appendix C provides the software version and earlier execution records.

**修改后**：Source: the complete Windows log/XML of 19 October 2026 and Linux/offscreen-Qt log/XML of 26 October 2026. Appendix C connects each invocation to its source state; related subsets are not added to the complete-suite totals.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 65. 4.3.1

**修改前**：The suite ran without test-case selection and completed with no skipped tests. Its 15 warnings concern deprecated Matplotlib/Pyparsing, PyTorch TypedStorage and Hugging Face download interfaces. The 194.10-second duration measures automated testing, not application inference performance.

**修改后**：Both complete invocations ran without test-case selection or skipped cases. The earlier Windows suite and current Linux suite have distinct dependency/platform records and warning counts. Their durations measure automated testing, not inference latency. The current 126-case related run and 14-case 2×-DPI run also passed; each is an independent subset rather than additional completed cases in the 505-case suite.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 66. 4.3.1

**修改前**：The final Windows suite passed the built-in-model availability assertion and the previously affected history, rerun, worker-lifetime and responsive-layout cases. The separate default-Pillow classifier evaluation in Section 4.2.6 supplies predictive measurements; passing software tests and file-availability checks do not measure segmentation accuracy.

**修改后**：The Windows baseline passed its built-in-model availability assertion and the history, rerun, worker-lifetime and layout cases in that source version. The current Linux suite retains the genuine segmentation-file assertion and reports its failure; no placeholder model, test deletion or skip was used. The separate classifier evaluation in Section 4.2.6 supplies predictive measurements. Neither a file-availability check nor a passing fixture measures segmentation accuracy.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 67. 4.3.2 / Table 4.5

**修改前**：[New table row]

**修改后**：Tile preference appeared to be ignored | History/re-run metadata remained in the input-panel cache; unchanged widget values emitted no refresh | Ordinary Run reads current preferences; only recorded Re-run supplies old parameters; finish/restore refresh the new-run summary | 11 focused Linux cases passed with actual crop boxes and history values; related/full-suite records retained

**原因**：Document the confirmed root cause and the actual regression evidence.

## 68. 4.3.2 / Table 4.5

**修改前**：[New table row]

**修改后**：PDF size and blocking export | Full image pixels embedded in small report panels; report generation was synchronous | Export-only display copies, Standard/Original resolution, task-preserving report metadata and cancellable atomic background generation | PDF encoding/data-preservation, layout and worker-lifecycle tests passed; user report size/online preview require actual re-export

**原因**：Document the report-size and responsiveness changes without guaranteeing a hosting service outcome.

## 69. 4.3.2 / Table 4.5

**修改前**：[New table row]

**修改后**：Comparison drag/resize drift | Driver view was recentered during linked updates; viewport resize reused the wrong centre | Update the peer only, preserve source centre, proportional wheel zoom and rubber-band divider resizing | Navigation stability and existing Fit/grid regressions passed on Linux; current native Windows manual case remains pending

**原因**：Include navigation changes added after the baseline.

## 70. 4.3.3

**修改前**：Native Windows automated checks now cover maximise/restore, saved-geometry recovery, repeated narrow/wide comparison, grid alignment and short viewports with accessible Run/Re-run actions. These completed checks resolve the earlier engineering regressions. Appendix D still reserves formal manual outcomes for authorised real-image workflows, real-model cancellation, screenshot verification and the intended display configurations.

**修改后**：The Windows baseline automated checks cover maximise/restore, saved geometry, comparison/grid alignment and compact action panels for that earlier source. Subsequent current-source navigation, metadata wrapping, task-specific progress, model-source and tile-preference checks passed on Linux/offscreen Qt. Appendix D therefore requests a new native Windows execution and formal manual records on the selected final version rather than extending the old Windows Pass to later changes.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 71. 4.3.4

**修改前**：The hardware and CPU runtime are documented in Table 4.4, but no repeated stage-level measurements were recorded for loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving or export. Cold and warm runs have not been separately summarised. Appendix E.3 defines the benchmark protocol; no measured latency, mean, standard deviation or throughput is filled in here.

**修改后**：The Windows hardware and CPU runtime are documented in Table 4.4. No repeated inference-stage or memory benchmark has been supplied, so model loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving and export retain unmeasured status. Appendix E.3 now specifies workload IDs, cold/warm boundaries, repetition counts, raw-record fields and summary rules. Existing export fixture file sizes are a separate file-size observation, not an inference-latency benchmark.

**原因**：Replace a generic future intention with an executable protocol while retaining the absence of measurements.

## 72. 4.3.4

**修改前**：The demonstrated delivery route is source execution in a Windows virtual environment. No PyInstaller build log, version-matched packaged artifact, clean-machine acceptance record or offline execution record was available. Standalone executable and fully offline deployment verification remain future work, separate from successful source startup.

**修改后**：The demonstrated delivery route is source execution. The current repository contains a Windows PyInstaller specification, build script, genuine-resource preflight, bundled-configuration support and release-manifest generation. No corresponding completed build log, distributable artifact or clean-machine/offline acceptance was supplied. Tooling implementation is therefore reported separately from unverified deployment. No OpenVINO runtime or converted model is present.

**原因**：Update build-tool implementation status without claiming a built or validated release.

## 73. 4.5.1 / O1

**修改前**：Windows source startup and complete 370-test suite passed; clean offline executable remains unverified.

**修改后**：Local PyTorch CPU workflow implemented. Windows baseline startup/370-test suite recorded; current Linux 504 passed with one genuine-resource failure. Clean-machine offline delivery unverified.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 74. 4.5.1 / O2

**修改前**：Windows real-classifier loading/validation and automated loader/path cases passed; semantic safety of arbitrary models is not established.

**修改后**：Supported loader and task-default checks implemented. Real classifier loading recorded on Windows; current Linux lacks the genuine segmentation weight. No unrestricted semantic-compatibility claim.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 75. 4.5.1 / O3

**修改前**：Default-Pillow Single image core: 90.68% accuracy / 88.59% macro-F1 on 7,180 native 224 × 224 patches. Segmentation and tiled predictive evaluation pending.

**修改后**：Default-Pillow Single image core: 90.68% accuracy / 88.59% macro-F1 on 7,180 native patches. Current crop/parameter-lifetime fixtures pass; tiled predictive and segmentation evaluation remain pending.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 76. 4.5.1 / O4

**修改前**：Native Windows chart, legend, coordinate/grid and comparison regressions passed; formal real-image inspection tasks and UAT pending.

**修改后**：Current numbered-tile inspection, original-crop detail, coordinate/grid and linked-navigation cases passed on Linux/offscreen Qt. Final-version native real-image tasks and UAT remain pending.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 77. 4.5.1 / O5

**修改前**：Native Windows temporary-artifact/report cases passed; real-image export demonstration pending.

**修改后**：Background atomic/cancellable PDF and two image-quality modes implemented; current file/encoding/metadata tests passed. Synthetic size measurements are reported separately; real-image export capture remains pending.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 78. 4.5.1 / O6

**修改前**：Native Windows persistence/artifact regressions passed; immutable per-run identities and backup not implemented.

**修改后**：SQLite/artifact persistence and clear-view source/history preservation cases passed. Per-run immutable file identities, backup and recovery are not implemented.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 79. 4.5.1 / O7

**修改前**：Native Windows search, calendar, restore and recorded-parameter rerun cases passed; efficiency awaits UAT.

**修改后**：Search, filtering, zero-selection, restore and recorded rerun implemented. Current-preference versus saved-record isolation is regression-tested on Linux; user efficiency remains unmeasured.

**原因**：Match objective assessment to current functionality and actual version-specific evidence.

## 80. 4.5.1

**修改前**：The implementation makes previously implicit choices visible: Single image versus Tiled analysis, source crop size versus network input, named resize backends, and tile-class coverage versus pixel coverage. The Windows patch evaluation supplies a measured default-path classifier result, and the 370-test native Windows run verifies the implemented software contracts under the documented test conditions.

**修改后**：The implementation makes task/mode, source crop versus network input, resize backend and coverage semantics visible. Current refinements strengthen numbered inspection, navigation, export and the separation of new-run preferences from recorded rerun settings. The patch evaluation supplies a measured classifier result; the two environment-labelled software invocations assess different source versions and retain their actual outcomes.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 81. 4.5.3

**修改前**：The complete 370-test native Windows suite provides automated regression evidence for the evaluated source state. Formal manual task acceptance and UAT remain incomplete, including authorised real-image screenshots, representative display configurations and real-model workflow observations. Assistive-technology testing and coverage measurement have not been completed. These activities address usability and deployment conditions beyond the controlled software cases.

**修改后**：The completed 370-test native Windows suite supports the earlier baseline. The current-source Linux/offscreen-Qt suite has 504 passing cases and one genuine segmentation-weight availability failure, with no errors or skips. Later controls and workflows still require final-version native Windows manual acceptance. UAT, authorised current screenshots, representative display/assistive-technology acceptance and coverage measurement remain incomplete.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 82. 4.5.3

**修改前**：Runtime and deployment require further measurement. The documented Windows execution is CPU-based; its installed RTX 4060 was not used. Repeated cold/warm stage timings, memory measurements, PyInstaller build records, clean-machine acceptance and offline dependency checks are unavailable, so the current delivery level is source execution.

**修改后**：Runtime and deployment require further measurement. The recorded Windows execution uses PyTorch CPU, not its installed RTX 4060 GPU or an OpenVINO runtime. A fixed cold/warm benchmark protocol is prepared, but repeated timing and memory results remain unavailable. Windows build tooling is implemented; an actual version-matched package, clean-machine acceptance and offline execution are unverified. The demonstrated delivery remains source execution.

**原因**：Clarify implemented tooling and unperformed evaluation without altering deferred organ/stain conclusions.

## 83. 4.5.4

**修改前**：The immediate priorities are to complete formal real-image Windows acceptance, collect UAT responses and retain the passing regression suite as the baseline for further changes. The default application patch evaluation is complete; further model work should examine patient-grouped internal validation, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**修改后**：The immediate priorities are to resolve genuine resources on the chosen acceptance installation, run the current complete Windows suite, complete authorised real-image manual tasks and execute the frozen UAT protocol. The documented patch evaluation remains the classifier result; larger-crop and tiled predictive work requires its own authorised ground-truth design. No new biological generalisation result is introduced by the current software refinements.

**原因**：Prioritise evidence required for the final source version.

## 84. 4.6

**修改前**：ZY-Path implements model-aware inference, spatial inspection and record continuity. The Windows default-Pillow Single image core reproduces 90.68% accuracy and 88.59% macro-F1 on 7,180 labelled patches. The final native Windows full suite completed with 370 passed, 0 failed, 0 errors and 0 skipped. UAT and the model, performance and deployment limitations remain as specified in Section 4.5.3.

**修改后**：ZY-Path implements model-aware inference, spatial inspection and record continuity, with current refinements to numbered tiles, preferences, reset operations and background report export. The default-Pillow Single image core achieves 90.68% accuracy and 88.59% macro-F1 on the documented native-sized patch test. The Windows baseline passed 370 cases; current-source Linux completed 505 cases with 504 passed and one genuine segmentation-resource failure. The remaining user, manual, performance and deployment evidence is specified in Section 4.5.3.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 85. 5.1

**修改前**：The implementation adds explicit single-image and tiled classification, separate segmentation semantics, linked source/result inspection, task-specific model defaults and cooperative cancellation. In particular, tiled analysis retains actual crop coordinates and areas, exposes its sampling settings and labels coverage as an estimate. History and rerun preserve the recorded task/model/mode instead of silently applying current preferences. These details connect interface behaviour to the meaning of the numerical result.

**修改后**：The implementation adds explicit single-image and tiled classification, independent segmentation presentation, numbered crop inspection, linked original/result navigation, task-specific defaults, cooperative cancellation and background PDF export with two quality settings. Ordinary Run reads current preferences, while recorded rerun restores its own snapshot. Clear view resets transient state without deleting history. These behaviours connect the interface to the meaning and provenance of each completed result.

**原因**：Summarise the actual final software contribution.

## 86. 5.1

**修改前**：The Windows application-default Pillow evaluation produced 6,511 correct predictions from 7,180 native-sized test patches, or 90.68% accuracy and 88.59% macro-F1. It matches the original OpenCV/Albumentations evaluation on every predicted label, while probabilities show small numerical differences. Separately, all 370 native Windows software tests passed without errors or skips, supporting the implemented loading, inspection, persistence, rerun, cancellation and export contracts. Formal manual acceptance and predictive generalisation retain the limits in Section 4.5.3.

**修改后**：The Windows default-Pillow evaluation produced 6,511 correct labels from 7,180 native-sized test patches: 90.68% accuracy and 88.59% macro-F1. Every predicted label agrees with the recorded reference pipeline, with small probability differences. Software verification remains separate: the earlier native Windows baseline passed 370 cases, and the current-source Linux/offscreen-Qt suite reports 504 passed, one missing genuine segmentation-resource failure and no errors/skips. Final-version native acceptance, UAT and broader predictive claims retain the limits in Section 4.5.3.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 87. 5.2

**修改前**：Further evaluation should examine patient- or slide-grouped internal validation, additional external cohorts, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Formal real-image Windows acceptance should complement the completed automated suite, which provides the regression baseline for subsequent development.

**修改后**：Further evaluation should examine patient- or slide-grouped internal validation, additional authorised cohorts and larger-crop/tiled predictive behaviour under documented source geometry. The immediate engineering follow-up is current-version Windows regression and manual acceptance, followed by the predefined timing/memory protocol. Passing subsets must not replace the full-suite result, and unavailable resources must remain reported rather than substituted.

**原因**：Keep future work aligned with the selected current source and honest test reporting.

## 88. 5.2

**修改前**：The third priority is reproducibility and deployment. Add file checksums, dependency manifests and versioned metadata to saved records; define artifact transaction/recovery behaviour and backups; package the application with all permitted resources; and test it on a Windows machine without the development environment. Security and model-licensing review should accompany distribution, especially where serialized model objects remain supported.

**修改后**：The third priority is reproducibility and deployment. Complete version-matched Windows build and clean-machine/offline acceptance using the implemented tooling; retain required resource permissions. Per-run file checksums, dependency manifests, versioned metadata, artifact recovery and backups remain further work. An export-time checksum identifies the currently accessible file and does not establish which immutable weight file produced an older record.

**原因**：Distinguish implemented build support from future provenance and deployment guarantees.

## 89. 5.4

**修改前**：ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis and stronger state management. The measured classifier result and the completed 370-test native Windows suite complement source-startup observations. UAT, formal manual acceptance, segmentation evaluation and verified packaging are the next steps toward stronger usability, generalisation and deployment claims.

**修改后**：ZY-Path implements the central CP1 workflow and extends it with explicit spatial analysis, numbered inspection and stronger state/export management. The measured classifier result and the two dated, platform-specific automated records support different aspects of the work. Current-version Windows manual acceptance, UAT, systematic runtime/memory measurements and clean-machine deployment remain unfinished and must be completed or retained as explicit limits.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 90. Appendix A.2

**修改前**：[New table row]

**修改后**：Current-source regression and refinements | Revision 8c4830c; 26 Oct Linux full/related/DPI records; current export and preference tests | 504 passed, 1 genuine-resource failure, 0 errors/skips; final-version Windows execution pending

**原因**：Record implemented refinements and current evidence separately from proposed outcomes.

## 91. Appendix A.3

**修改前**：Before submission, complete authorised GUI screenshots, formal manual acceptance, UAT and the remaining cover fields. Retain the completed 370-test Windows result and the default-Pillow patch evaluation with their actual source and dataset scope. Final formatting and clean-machine packaging claims follow their corresponding review and execution evidence.

**修改后**：Before submission, select and record the final software source, collect its native Windows result, complete authorised screenshots/manual tasks and the frozen UAT protocol, and supply semester/submission date. Preserve the earlier Windows baseline, current Linux resource failure and classifier evaluation with their real scope. Execute the performance or deployment protocols only when those claims are to be made; otherwise retain their explicit incomplete status.

**原因**：Provide an evidence-based completion sequence for the current edition.

## 92. Appendix C.1

**修改前**：The evaluated application source is recorded in commit 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19. The commit was created on 20 October 2026 from the source content exercised by the completed Windows tests on 19 October; the repaired files match the recorded Windows source after line-ending normalisation. The original logs retain the pre-commit identifier 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Table C.1 lists the evaluation materials, and Table C.2 gives the execution history.

**修改后**：The current application source is commit 8c4830c1281e4a85248c9a2ea9d0adae64bd4525. The 26 October Linux invocation ran that source content before it was committed; the executed-file hashes agree with the committed files. The Windows baseline is 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19, recorded after the 19 October Windows run. Original logs retain their original identifiers. Table C.1 identifies the materials and Table C.2 separates the actual executions.

**原因**：Identify current and earlier source states without rewriting original log identities.

## 93. Appendix C.1 / Table C.1

**修改前**：[New table row]

**修改后**：E20 | 26 Oct current-source Linux/offscreen-Qt full/related/DPI log/XML and source-hash summary | 505 complete-suite cases: 504 passed, 1 genuine segmentation-file failure, 0 errors/skips; related 126 and DPI 14 pass separately. Source recorded in 8c4830c.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 94. Appendix C.1 / Table C.1

**修改前**：[New table row]

**修改后**：E21 | Current data/pdf_report.py; ui/pdf_export_worker.py; PDF layout/quality and worker tests | Background atomic export, recorded metadata, exact palette preservation and Standard/Original resolution fixture sizes

**原因**：Index the current report implementation and actual synthetic export evidence.

## 95. Appendix C.1 / Table C.1

**修改前**：[New table row]

**修改后**：E22 | Current test_tile_preferences_lifetime.py and associated log | 11 focused cases: new Run uses Preferences; Re-run retains record parameters; actual crop boxes/history and active-run snapshot checked

**原因**：Index parameter-lifetime evidence.

## 96. Appendix C.2

**修改前**：Table C.2 distinguishes the completed native Windows run from earlier Windows collection and runtime interruptions. The final invocation completed 370 tests with no failures, errors or skips. A preceding 131-test regression subset passed in 119.90 seconds with 15 warnings; its count is not added to the full-suite total. Classifier performance is reported separately in Section 4.2.6.

**修改后**：Table C.2 separates the completed earlier Windows baseline from the current-source Linux/offscreen-Qt invocation and earlier Windows interruptions. The Windows baseline has 370 passes; the current Linux result has 504 passes and one genuine segmentation-resource failure. The Windows 131-case related subset, current Linux 126-case related subset and 14-case 2×-DPI subset are independent records and are not summed into a complete-suite total.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 97. Appendix C.2 / Table C.2

**修改前**：Table C.2. Windows automated test execution history

**修改后**：Table C.2. Platform- and version-specific automated execution history

**原因**：Align the caption with the evidence now presented.

## 98. Appendix C.2 / Table C.2

**修改前**：[New table row]

**修改后**：Linux/offscreen Qt, 26 Oct; source recorded in 8c4830c | 504 | 1 | 0 | 505 collected; 0 skipped; 14 warnings; 219.20 s; exit 1. Genuine segmentation weight unavailable; no placeholder or skipped test.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 99. Appendix C.2 source

**修改前**：Source: Windows pytest logs, XML results and exit codes of 19 October 2026. “Not final” and “Not run” identify incomplete invocations rather than passing-test totals.

**修改后**：Source: Windows log/XML/exit records of 19 October 2026 and Linux/offscreen-Qt log/XML of 26 October 2026. Incomplete invocations retain Not final/Not run rather than fabricated passing totals.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 100. Appendix D.1

**修改前**：For each manual acceptance case record date, tester, source state, Windows/Python/dependency versions, hardware, Qt display metrics, model/input identity, expected outcome, actual outcome and evidence file. The source-startup log gives partial manual observations, while the completed Windows suite supplies automated coverage for several corresponding behaviours. Table D.1 remains a manual acceptance checklist: its outcomes require the specified real-image task records and must not be filled from automated test totals alone.

**修改后**：For each manual acceptance case record date, tester, final source state, Windows/Python/dependency versions, hardware, actual Qt platform/display metrics, model/input identity, expected outcome, actual outcome and evidence file. The earlier source-startup record and baseline suite do not automatically accept current changes. Table D.1 remains a manual checklist: a Pass requires the specified observed native task record, not a Linux fixture or old Windows total.

**原因**：Distinguish current-source Linux verification from the dated Windows baseline without converting a failure into a pass.

## 101. Appendix D.1 / Table D.1

**修改前**：[New table row]

**修改后**：W13 | Restore old tiles, edit preferences, Run; then use recorded Re-run | Current Run geometry/backend match Preferences; Re-run retains its record; ordinary Run after rerun again uses current preferences

**原因**：Include the current confirmed regression in native acceptance.

## 102. Appendix D.1 / Table D.1

**修改前**：[New table row]

**修改后**：W14 | Use tile numbers, image/table selection and Square; clear view/selection | IDs/boxes/crop preview agree; Square copies once; clear operations preserve saved history/source files

**原因**：Accept the new inspection/reset operations.

## 103. Appendix D.1 / Table D.1

**修改前**：[New table row]

**修改后**：W15 | Export both PDF qualities; cancel an export; reopen the output | Quality and original dimensions are accurately labelled; numeric data agree; cancellation/failed export preserve the previous destination

**原因**：Accept current export quality and lifecycle behaviour.

## 104. Appendix B.3

**修改前**：For each attempted task record start/end or elapsed seconds, outcome (independent success, assisted success, unsuccessful, not attempted), assistance count, critical error and a brief observation. Define a stop rule consistently before testing. An intended cancellation is successful when safe acknowledgement and record preservation occur, not when the model stops instantly. If a prepared file is unavailable, record an environment-blocked attempt rather than blaming the participant or silently substituting another task.

**修改后**：Protocol 1.0 uses a 180-second task limit from the end of the instruction, except T08 export and T09 cancellation, which allow 300 seconds. Observer timing separates user-action time from application waiting where possible. At the limit, record Timeout; offer help only after that outcome is saved. Independent success requires no task-solving hint. Repeating an instruction verbatim is logged as clarification; a directional or procedural hint makes completion assisted. A critical error is an action that produces/exports the wrong nominated result, changes the wrong task default, deletes a required record, or confuses estimated coverage with pixel ground truth. Intended cancellation succeeds on acknowledgement and preservation of completed records. A missing material or crash is recorded as environment-blocked/system failure separately from participant inability. These predefined rules can be revised before the first participant, with a new protocol version, but not selected retrospectively to improve results.

**原因**：Supply concrete assistance/error/stop rules while explicitly identifying them as an unexecuted protocol.

## 105. Appendix B.3 / T01

**修改前**：Load the supplied image and run Single image with the approved model

**修改后**：Load approved P01 and run Single image with classification model M01

**原因**：Specify task material, geometry and observable success before collecting responses.

## 106. Appendix B.3 / T01

**修改前**：Correct image/model/mode and completed output identified without coding

**修改后**：Correct P01/M01/mode and completed output identified; no coding

**原因**：Specify task material, geometry and observable success before collecting responses.

## 107. Appendix B.3 / T02

**修改前**：Select Tiled analysis, set the specified source width/height and run

**修改后**：Load approved P02 (1024 × 768), choose Tiled analysis and set 256 × 256 using Square

**原因**：Specify task material, geometry and observable success before collecting responses.

## 108. Appendix B.3 / T02

**修改前**：Correct explicit mode and source dimensions are used

**修改后**：Recorded source geometry 256 × 256, Pillow bilinear, 12 tiles (4 columns × 3 rows); no claim of an optimal scale

**原因**：Specify task material, geometry and observable success before collecting responses.

## 109. Appendix B.3 / T03

**修改前**：Find a tile's class/confidence and explain coverage

**修改后**：Show tile numbers, select tile #6 and explain its class/confidence and coverage

**原因**：Specify task material, geometry and observable success before collecting responses.

## 110. Appendix B.3 / T03

**修改前**：Identifies actual tile detail; states coverage is a crop-class area estimate, not pixel ground truth

**修改后**：Tile #6 rectangle [256, 256, 512, 512]; image/table/crop agree; explains model score and tile-class estimate

**原因**：Specify task material, geometry and observable success before collecting responses.

## 111. Appendix B.3 / T04

**修改前**：Compare a selected region with the original and use Fit/zoom

**修改后**：Compare the tile-6 region with the original, pan/zoom linked views, then return to Fit

**原因**：Specify task material, geometry and observable success before collecting responses.

## 112. Appendix B.3 / T04

**修改前**：Same source region remains aligned; participant can return to Fit

**修改后**：Corresponding region remains aligned; participant returns to Fit without resetting preferences

**原因**：Specify task material, geometry and observable success before collecting responses.

## 113. Appendix B.3 / T05

**修改前**：Inspect the supplied segmentation result

**修改后**：Open the prepared real-model segmentation result S01; inspect overlay/map and coverage

**原因**：Specify task material, geometry and observable success before collecting responses.

## 114. Appendix B.3 / T05

**修改前**：Distinguishes segmentation labels and pixel coverage from classification tiles

**修改后**：Distinguishes segmentation’s own labels and pixel coverage from classification estimates; no diagnostic correctness task

**原因**：Specify task material, geometry and observable success before collecting responses.

## 115. Appendix B.3 / T06

**修改前**：Search/date-filter history and restore the nominated record

**修改后**：Find and restore prepared tiled record R01 using the assigned keyword/date

**原因**：Specify task material, geometry and observable success before collecting responses.

## 116. Appendix B.3 / T06

**修改前**：Correct stored record shown without initiating inference

**修改后**：Correct R01 shown with its saved result/parameters; no inference or new record

**原因**：Specify task material, geometry and observable success before collecting responses.

## 117. Appendix B.3 / T07

**修改前**：Change a current preference, then rerun the stored record

**修改后**：Set current dimensions to 512 × 512, Re-run R01, then start ordinary Run Inference

**原因**：Specify task material, geometry and observable success before collecting responses.

## 118. Appendix B.3 / T07

**修改前**：Recorded model/mode/parameters used; new record distinguished from restored one

**修改后**：Re-run retains 256 × 256 and 12 tiles; ordinary Run uses current 512 × 512 and 4 tiles; records are distinguished

**原因**：Specify task material, geometry and observable success before collecting responses.

## 119. Appendix B.3 / T08

**修改前**：Export the nominated completed result

**修改后**：Export the nominated completed record as Standard PDF and PNG; identify its metadata

**原因**：Specify task material, geometry and observable success before collecting responses.

## 120. Appendix B.3 / T08

**修改前**：Correct PNG/PDF and actual task/model metadata identified

**修改后**：Correct files/record identity/statistics; PDF quality identified and source dimensions retained

**原因**：Specify task material, geometry and observable success before collecting responses.

## 121. Appendix B.3 / T09

**修改前**：Start the supplied workload and cancel it

**修改后**：Start approved workload C01 and request cancellation; inspect the completed history

**原因**：Specify task material, geometry and observable success before collecting responses.

## 122. Appendix B.3 / T09

**修改前**：Recognises request/acknowledgement; no partial completed record saved

**修改后**：Request and acknowledgement recognised; no partial completed record; previous completed results retained

**原因**：Specify task material, geometry and observable success before collecting responses.

## 123. Appendix B.3 / T10

**修改前**：Save a supplied validated default and restore the built-in default

**修改后**：Set validated real classification model M01 as that task’s default, then restore built-in

**原因**：Specify task material, geometry and observable success before collecting responses.

## 124. Appendix B.3 / T10

**修改前**：Correct task's preference changes; other task/history remain unaffected

**修改后**：Classification default changes/restores; segmentation default and old records remain unchanged

**原因**：Specify task material, geometry and observable success before collecting responses.

## 125. Appendix B.3

**修改前**：[New explanatory paragraph]

**修改后**：The material register maps P01/P02/S01/R01/C01/M01 to actual filenames, checksums, permissions and source/record identifiers. Its current blank source fields mean the pack is not yet authorised for execution. Before each session, restore the same prepared application profile and records; retain the participant’s anonymous ID and software revision. A five-minute orientation uses a separate practice example. T01–T10 keep a fixed order for comparability, so results will acknowledge possible learning/fatigue effects rather than claim a counterbalanced experiment.

**原因**：Make study preparation and remaining material selection explicit.

## 126. Appendix B.1

**修改前**：[New explanatory paragraph]

**修改后**：Before recruitment, record the institution’s actual approval or exemption requirement and its reference if applicable; no approval is claimed here. Explain the permitted recording, quotation and withdrawal arrangements, access-limited storage and disposal under the applicable assessment/appeal and institutional retention rules. The exact approved storage/retention arrangements remain fields to complete in the study register, rather than an invented ethics clearance.

**原因**：Clarify the operational ethics record without fabricating approval or university policy.

## 127. Appendix E.3

**修改前**：Use the documented Windows CPU environment as a benchmark baseline, fixing source dimensions, model, classification mode, resize backend and tile settings. Time cold model loading separately from warm repeated runs; measure preprocessing, forward inference, reconstruction/statistics, GUI display, saving and export as distinct stages. Report repeat count, mean, sample standard deviation, median and range, with memory measurements where available. The recorded pytest durations are excluded from inference timing. Packaging verification additionally requires a matched PyInstaller build record and artifact revision, clean-machine task checks and an offline dependency test; these remain planned activities.

**修改后**：Benchmark protocol 1.0 fixes the application revision, genuine model checksum, Python/dependency versions, CPU/thread setting, source identity/dimensions, task, resize backend and tile/stride/input geometry. Use B01: native 224 × 224 classification; B02: 1024 × 768 classification with 256 × 256 source tiles (12 tiles); B03: 3552 × 3536 classification with 512 × 512 tiles (49 tiles); and B04: one authorised segmentation raster whose dimensions and independent geometry are entered before measurement. Material identifiers are protocol definitions; their actual file assignments remain pending. Keep model loading separate from already-loaded inference, and record full workload metadata for every attempt.

**原因**：Define fixed workloads without presenting them as measured runs.

## 128. Appendix E.3

**修改前**：[New explanatory paragraph]

**修改后**：Perform five fresh-process cold-load repetitions per model and ten warm repetitions per workload after one explicitly excluded warm-up. Define boundaries with a monotonic clock: load/validation; preprocessing; forward work; reconstruction/statistics; GUI-ready display; artifact/database save; and PDF export. Where instrumentation cannot isolate a stage, mark that stage Not measured and report the available end-to-end interval instead of estimating it by subtraction. Record all attempts, failures and cancellations; do not replace slow observations selectively. Summarise valid repetitions with n, mean, sample standard deviation, median and range. Record process baseline/peak RSS where tooling is available and state its sampling interval and definition.

**原因**：Supply repeat counts, timing boundaries, error rules and memory definition for a reproducible benchmark.

## 129. Appendix E.3

**修改前**：[New explanatory paragraph]

**修改后**：For report-size checks, export the same completed result in both PDF qualities with identical appendix/path settings. Record file bytes and generation duration separately from inference, and verify selected numeric rows, labels and image aspect ratios. A successful local open is not an online-hosting preview guarantee. Packaging acceptance additionally records the build command/log, permitted resources, artifact checksum, clean Windows configuration, offline state and each task outcome. No new latency, coverage, packaged-release or clean-machine result is supplied in this revision.

**原因**：Separate file-size evidence, runtime measurement and deployment acceptance.

## 130. 3.2.2

**修改前**：The CP1 target of at least 80% coverage of core/data remains an unmeasured target because the recorded pytest commands did not generate a coverage report. Requirements therefore retain separate implementation and verification status rather than inferring coverage from the number of passing tests.

**修改后**：The CP1 core/data coverage target was measured on 27 October 2026 using coverage.py 7.6.1 over the complete pytest invocation, without omitting source files. Statement coverage was 608/735 lines (82.72%) for core, 428/469 (91.26%) for data and 1,036/1,204 (86.05%) combined. The aggregate target was met in this Linux/offscreen-Qt run. This measures executed statements in these two packages, not branch coverage or UI coverage. The invocation retained its one genuine segmentation-resource failure; passing test totals and coverage are reported separately.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 131. 3.2.2 / N08

**修改前**：No current coverage percentage is claimed

**修改后**：27 Oct Linux/offscreen Qt: core 82.72%, data 91.26%, combined statement coverage 86.05%; target met in this scope, with the complete-suite genuine-resource failure retained

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 132. 3.6.1

**修改前**：[New explanatory paragraph]

**修改后**：A separate 27 October repetition instrumented the complete suite with coverage.py 7.6.1, limited to statement coverage of core and data. It again collected 505 tests: 504 passed, one genuine segmentation-file assertion failed, with 0 errors/skips and 14 warnings in 279.15 seconds (exit 1). The aggregate statement coverage was 86.05%. Instrumented pytest time is test-suite duration, not an inference-performance measurement. Appendix C retains both invocations and the coverage totals.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 133. 3.6.6 / non-functional verification

**修改前**：Windows baseline: 370 passed. Current Linux: 504 passed, 1 file-availability failure, 0 errors/skips. Repeated performance measurement, coverage percentage and clean-machine deployment remain incomplete.

**修改后**：Windows baseline: 370 passed. Current Linux: 504 passed, 1 file-availability failure, 0 errors/skips. Repeated performance measurement, clean-machine deployment remain incomplete. Core/data combined line coverage is 86.05% in the separate 27 Oct Linux run.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 134. 4.3.1

**修改前**：[New explanatory paragraph]

**修改后**：The separate 27 October complete-suite coverage repetition produced the same 504 passed / 1 failed / 0 errors / 0 skipped outcome in 279.15 seconds, with 14 warnings and exit 1. Core and data statement coverage was 82.72% and 91.26%, respectively (86.05% combined); the 80% aggregate target is met for this scope. This does not establish that every functional branch was exercised. Appendix C identifies the complete report and the remaining genuine-resource failure.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 135. 4.5.3

**修改前**：The completed 370-test native Windows suite supports the earlier baseline. The current-source Linux/offscreen-Qt suite has 504 passing cases and one genuine segmentation-weight availability failure, with no errors or skips. Later controls and workflows still require final-version native Windows manual acceptance. UAT, authorised current screenshots, representative display/assistive-technology acceptance and coverage measurement remain incomplete.

**修改后**：The completed 370-test native Windows suite supports the earlier baseline. Current-source Linux/offscreen-Qt invocations have 504 passing cases and one genuine segmentation-weight availability failure, with no errors or skips. The 27 October invocation measured 86.05% core/data statement coverage; branch and UI coverage were not measured. Later controls and workflows still require final-version native Windows manual acceptance. UAT, authorised current screenshots and representative display/assistive-technology acceptance remain incomplete.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 136. Appendix E.3

**修改前**：For report-size checks, export the same completed result in both PDF qualities with identical appendix/path settings. Record file bytes and generation duration separately from inference, and verify selected numeric rows, labels and image aspect ratios. A successful local open is not an online-hosting preview guarantee. Packaging acceptance additionally records the build command/log, permitted resources, artifact checksum, clean Windows configuration, offline state and each task outcome. No new latency, coverage, packaged-release or clean-machine result is supplied in this revision.

**修改后**：For report-size checks, export the same completed result in both PDF qualities with identical appendix/path settings. Record file bytes and generation duration separately from inference, and verify selected numeric rows, labels and image aspect ratios. A successful local open is not an online-hosting preview guarantee. Packaging acceptance additionally records the build command/log, permitted resources, artifact checksum, clean Windows configuration, offline state and each task outcome. No new latency, packaged-release or clean-machine result is supplied in this revision; the separate executed coverage measurement is reported in Section 4.3.1.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 137. Appendix C.1 / Table C.1

**修改前**：[New table row]

**修改后**：E23 | 27 Oct complete-suite coverage.py 7.6.1 log/XML/JSON; source commit 8c4830c | 504 passed, 1 genuine-resource failure, 0 errors/skips; 279.15 s; core 608/735 = 82.72%, data 428/469 = 91.26%, combined 1036/1204 = 86.05% line coverage.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 138. Appendix C.2 / Table C.2

**修改前**：[New table row]

**修改后**：Linux/offscreen Qt, 27 Oct; revision 8c4830c; statement coverage instrumented | 504 | 1 | 0 | 505 collected; 0 skipped; 14 warnings; 279.15 s; exit 1. Same missing genuine segmentation weight. core/data line coverage: 86.05%.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 139. Appendix C.2

**修改前**：[New explanatory paragraph]

**修改后**：The 27 October run used the committed current source directly and instrumented all core/data modules with no omission rules. Its coverage report counts 1,204 executable statements, of which 1,036 were exercised. Line coverage does not substitute for the functional assertions, genuine-resource availability or final-version native Windows acceptance.

**原因**：Replace the unmeasured core/data target with the actual 27 October complete-suite coverage measurement, while retaining its failure and platform scope.

## 140. 3.5.3 / Figure 3.5

**修改前**：Figure 3.5. Implementation-level class diagram. Relationships represent principal ownership or dependency, not a generated inventory of every method. Source: author, based on the implemented application.

**修改后**：Figure 3.5. Implementation-level class diagram. Relationships show selected coordination dependencies and worker inheritance. Source: author, based on the implemented application.

**原因**：Align the caption with the evidence now presented.

## 141. 3.1 / Figure 3.1

**修改前**：Earlier author-created workflow diagram

**修改后**：Current-source explanatory diagram: architecture

**原因**：Align diagram semantics with the implemented classes, parameter ownership and explicit alternatives.

## 142. 3.5 / Figure 3.3.

**修改前**：Earlier author-created workflow diagram

**修改后**：Current-source explanatory diagram: use_case

**原因**：Align diagram semantics with the implemented classes, parameter ownership and explicit alternatives.

## 143. 3.5 / Figure 3.4.

**修改前**：Earlier author-created workflow diagram

**修改后**：Current-source explanatory diagram: sequence

**原因**：Align diagram semantics with the implemented classes, parameter ownership and explicit alternatives.

## 144. 3.5 / Figure 3.5.

**修改前**：Earlier author-created workflow diagram

**修改后**：Current-source explanatory diagram: class_diagram

**原因**：Align diagram semantics with the implemented classes, parameter ownership and explicit alternatives.

## 145. 3.5 / Figure 3.6.

**修改前**：Earlier author-created workflow diagram

**修改后**：Current-source explanatory diagram: activity

**原因**：Align diagram semantics with the implemented classes, parameter ownership and explicit alternatives.

## 146. 3.5.3 / local section layout

**修改前**：Class-diagram prose ended on a near-empty portrait page before a separate landscape page.

**修改后**：Portrait class diagram flows with its introduction; local landscape section excursion removed, existing body style/header/page-number setup retained.

**原因**：Remove the identified sparse page without redesigning document styles.

## 147. Appendix C.1 source

**修改前**：Source: project modules, experiment files and identified test records listed in the table.

**修改后**：Source: application code, experiment files and dated test records.

**原因**：Keep the source concise and adjacent to its table without changing its attribution.

## 148. Appendix C.2 source

**修改前**：Source: Windows log/XML/exit records of 19 October 2026 and Linux/offscreen-Qt log/XML of 26 October 2026. Incomplete invocations retain Not final/Not run rather than fabricated passing totals.

**修改后**：Source: Windows records (19 October) and Linux test/coverage records (26–27 October 2026). Incomplete invocations retain their recorded status.

**原因**：Include the new executed coverage record in the table attribution.
