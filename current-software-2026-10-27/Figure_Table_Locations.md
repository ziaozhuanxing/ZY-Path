# 图表正文提及位置

共 20 张图、24 张表；每项均有标题之外的明确正文编号提及。图片和UAT表按各自实际证据范围描述，未收集的参与者结果继续待填。

## Figure 1.1

Figure 1.1. TUM-labelled H&E patch TUM-TCGA-AAHIDTWA.tif, 224 × 224 pixels. Source: CRC-VAL-HE-7K, identified by the author; dataset DOI 10.5281/zenodo.1214456.
标题所在小节：1.1 Background and Motivation；PDF 页：[8]。

- 1.1 Background and Motivation；段落 2；PDF [11]／印刷页 ['1']。
  - Histopathology is a reference method for diagnosing many diseases, including malignancies. In haematoxylin and eosin (H&E) images, the staining of nuclei and cytoplasmic structures provides morphological information that trained professionals interpret in context. Digital imaging makes these observations available for storage, teaching and computational analysis. A model's output, however, is an inference from image appearance and must not be equated with a verified clinical diagnosis (Litjens et al., 2017; Kather et al., 2019). Figure 1.1 illustrates this tissue context using a TUM-labelled patch from CRC-VAL-HE-7K.

## Figure 2.1

Figure 2.1. Three output meanings: whole-image classification, source-tile estimates and pixel segmentation. Author-created conceptual diagram; it contains no model accuracy results.
标题所在小节：2.2.4 Tiled classification, coverage and confidence；PDF 页：[8]。

- 2.2.4 Tiled classification, coverage and confidence；段落 2；PDF [21]／印刷页 ['11']。
  - The model's softmax output is a normalised score over its classes. It is not automatically calibrated as the probability that an interpretation is correct (Guo et al., 2017). A high-confidence majority class across many tiles can arise from genuine image content, sampling scale, preprocessing mismatch or model/domain limitations. ZY-Path exposes per-tile probabilities and coordinates so these possibilities can be investigated rather than using a coloured map as proof of accuracy. Figure 2.1 distinguishes the three output meanings: whole-image classification, tile-class estimates and pixel segmentation.

## Table 2.1

Table 2.1. Scope-based comparison of pathology platforms
标题所在小节：2.4 Comparative Evaluation of Existing Systems；PDF 页：[10]。

- 2.4 Comparative Evaluation of Existing Systems；段落 1；PDF [25]／印刷页 ['15']。
  - Table 2.1 compares platform purposes and documented workflow scope. It separates an unexamined capability from an absent one and uses no aggregate ranking because the applications address different tasks. Source publications are cited in Sections 2.3.1–2.3.5.

## Figure 3.1

Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the project’s Python modules.
标题所在小节：3.1 Overview of System Methodology；PDF 页：[8]。

- 3.1 Overview of System Methodology；段落 2；PDF [29]／印刷页 ['19']。
  - The implemented system has three logical layers. The presentation layer contains the main window, inference/history/action panels, settings and result viewers. The core layer loads models, prepares inputs, executes inference and parses outputs. The data layer stores records and creates export files. MainWindow coordinates transitions between these layers, including saving result artifacts before inserting a completed history record. Figure 3.1 shows these layers and the flow of model, image, result and history artifacts.

## Table 3.1

Table 3.1. Functional requirements and acceptance conditions
标题所在小节：3.2.1 Functional Requirements；PDF 页：[10]。

- 3.2.1 Functional Requirements；段落 1；PDF [31]／印刷页 ['21']。
  - The requirements preserve the original model–image–inference–history workflow and add explicit spatial analysis and state-management requirements revealed during development. A requirement describes intended behaviour; its implementation and evidence status are recorded separately in Section 3.6.6. Table 3.1 specifies each functional requirement and its observable acceptance condition.

## Table 3.2

Table 3.2. Non-functional requirements and verification boundaries
标题所在小节：3.2.2 Non-Functional Requirements；PDF 页：[10]。

- 3.2.2 Non-Functional Requirements；段落 1；PDF [32]／印刷页 ['22']。
  - Table 3.2 links the non-functional requirements to their verification approaches and current implementation boundaries.

## Table 3.3

Table 3.3. Classification class order and fixed display palette v1
标题所在小节：3.3.5 Class probabilities, maps and estimated coverage；PDF 页：[10]。

- 3.3.5 Class probabilities, maps and estimated coverage；段落 7；PDF [39]／印刷页 ['29']。
  - This aggregate need not equal the class with the largest r_c because probability mass and hard-class coverage are different summaries. It is not a new whole-image forward pass. The history table therefore shows tile count and largest estimated coverage, leaving whole-image confidence blank; PDF metadata distinguishes “Aggregate tile label” and “Area-weighted mean probability”. Table 3.3 records the classifier’s fixed class order and dedicated nine-colour display palette.

## Table 3.4

Table 3.4. Built-in segmentation labels and display colours
标题所在小节：3.3.6 Segmentation pathway and label restoration；PDF 页：[10]。

- 3.3.6 Segmentation pathway and label restoration；段落 5；PDF [41]／印刷页 ['31']。
  - The nine-label order and RGB colours in Table 3.4 match the reference notebook. Generic compatible segmentation models use a separate prepared-tensor and OutputParser pathway. The model filename’s 100ep and panoptils strings are retained as identifiers; training duration and dataset provenance are not inferred from those strings.

## Table 3.5

Table 3.5. Implemented persistent data structures
标题所在小节：3.3.8 History schema, artifacts and rerun isolation；PDF 页：[10]。

- 3.3.8 History schema, artifacts and rerun isolation；段落 1；PDF [42]／印刷页 ['32']。
  - DatabaseManager uses sqlite3 connections with parameterised statements and transaction handling. The base inference_records table stores paths, task, label/confidence where applicable, result-image path and timestamp. A companion segmentation_artifacts table stores artifact paths and analysis_json; despite its legacy name, it also carries tiled-classification and single-classification parameter metadata. Table 3.5 summarises the persistent structures and the purpose of their principal fields.

## Figure 3.2

Figure 3.2. Annotated final workflow wireframe. This author-created design diagram summarises implemented regions and is not a Windows runtime screenshot.
标题所在小节：3.4.1 Principles and information hierarchy；PDF 页：[8]。

- 3.4.1 Principles and information hierarchy；段落 1；PDF [45]／印刷页 ['35']。
  - The interface keeps the CP1 three-region structure: input controls on the left, analysis/history in the centre and export/session actions on the right. Implementation changes replace fixed panel assumptions with draggable splitters, scrollable contents and bounded window restoration. The aim is to keep essential actions reachable while prioritising the analysis image. Figure 3.2 presents an annotated wireframe of this arrangement and its main user actions.

## Figure 3.3

Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities. Source: author, based on the implemented application.
标题所在小节：3.5.1 Use Case Diagram；PDF 页：[8]。

- 3.5.1 Use Case Diagram；段落 1；PDF [47]／印刷页 ['37']。
  - The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Selecting a model includes compatibility validation. Tiled analysis is an explicit classification variant. Restore saved result and Re-run recorded analysis are separate use cases because only rerun performs inference and creates a new record; Search/filter locates records without executing either operation. Figure 3.3 maps these actions and their scope.

## Figure 3.4

Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records. Source: author, based on the implemented application.
标题所在小节：3.5.2 Sequence Diagram；PDF 页：[8]。

- 3.5.2 Sequence Diagram；段落 1；PDF [49]／印刷页 ['39']。
  - The sequence diagram follows a run after image, task and model selection. MainWindow snapshots the current preferences for ordinary Run or the selected record for Re-run, then starts the worker. Signals deliver progress and a completed result. The coordinator saves completed artifacts and inserts a record only after successful persistence. Figure 3.4 uses guarded alternative fragments for cancellation, pipeline error and persistence failure; these exits are distinct from completed history.

## Figure 3.5

Figure 3.5. Implementation-level class diagram. Relationships show selected coordination dependencies and worker inheritance. Source: author, based on the implemented application.
标题所在小节：3.5.3 Class Diagram；PDF 页：[8]。

- 3.5.3 Class Diagram；段落 1；PDF [50]／印刷页 ['40']。
  - The class diagram shows selected runtime responsibilities rather than every widget. MainWindow coordinates input, history, inference, persistence and export. InferenceEngine depends on model loading, preprocessing and output parsing. PdfExportWorker delegates report generation to ExportManager. Spatial result pages use ImageComparison and ZoomableImageView. Figure 3.5 distinguishes coordination dependencies and worker inheritance for the current implementation.

## Figure 3.6

Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits. Source: author, based on the implemented application.
标题所在小节：3.5.4 Activity Diagram；PDF 页：[8]。

- 3.5.4 Activity Diagram；段落 1；PDF [51]／印刷页 ['41']。
  - The activity diagram distinguishes current-preference Run from recorded-parameter Re-run before selecting the task/mode pathway. Classification crops and segmentation processing regions retain independent geometry. Cancellation is checked at safe points before/after model work and between processing regions. Figure 3.6 labels the decisions and success/error exits; a request does not forcibly interrupt a running forward operation.

## Table 3.6

Table 3.6. Requirements traceability matrix
标题所在小节：3.6.6 Requirements Traceability Matrix；PDF 页：[10]。

- 3.6.6 Requirements Traceability Matrix；段落 1；PDF [56]／印刷页 ['46']。
  - Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the completed native Windows automated checks, recorded classifier evaluation, outstanding manual acceptance, UAT and further model studies.

## Table 3.7

Table 3.7. Risk register and residual mitigations
标题所在小节：3.7 Risk Management and Mitigation Strategies；PDF 页：[10]。

- 3.7 Risk Management and Mitigation Strategies；段落 1；PDF [59]／印刷页 ['49']。
  - The CP1 risks concerning model compatibility, dependencies, packaging, CPU performance, recruitment and data reliability remain relevant. CP2 adds scale ambiguity and misleading spatial statistics because explicit tiled classification introduces sampling choices that a user might mistake for validated tissue measurements. Table 3.7 distinguishes implemented controls from future verification.

## Figure 4.1

Figure 4.1. Windows application overview with Single image classification, probability chart and session/export panels. The displayed analysis is record #52. Source: author’s Windows capture.
标题所在小节：4.2.1 Implemented workflow and scope；PDF 页：[8]。

- 4.2.1 Implemented workflow and scope；段落 2；PDF [61]／印刷页 ['51']。
  - The Windows startup record on 19 October 2026 establishes classifier loading and validation. Figure 4.1 now supplies a direct Windows application capture with an actual Single image result, showing the input, probability chart and export/session regions. Its displayed record #52 identifies a NORM-labelled 224 × 224 input and 99.9% model confidence. This is an observed prediction, not an additional accuracy experiment.

## Figure 4.2

Figure 4.2. Tiled classification interface with source/result comparison and revised result toggles. Source: author’s Qt-simulated development capture; synthetic fixture, not a model result.
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[8]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [62]／印刷页 ['52']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Figure 4.3 provides separate actual-image Windows observations, including tile numbers and original-crop inspection.

## Figure 4.3

Figure 4.3. Windows classification workflow on a supervisor-provided breast-cancer raster: (a) Single image; (b) 49 numbered 512 × 512 source tiles; (c) crop inspection from the separate analysis #48. The CRC-trained classifier uses raw255 and OpenCV linear resize to 224 × 224. Source: author’s Windows captures.
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[8]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [63]／印刷页 ['53']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Figure 4.3 provides separate actual-image Windows observations, including tile numbers and original-crop inspection.
- 4.2.2 Classification results and spatial inspection；段落 4；PDF [63]／印刷页 ['53']。
  - Figure 4.3(a–b) shows Single image and Tiled analysis for the same named 3552 × 3536 raster. The Single image result selects STR with 42.6% confidence. The tiled view reports 40 STR, five MUC, one MUS and three NORM tiles, with estimated area coverage 82.06%, 9.98%, 1.89% and 6.07%, respectively. Its 512-pixel source crops use RGB/raw255 and OpenCV linear resize to 224 × 224. Panel (c), from a separate analysis, identifies tile 31 as NORM at 59.47%, with rectangle [1024, 2048, 1536, 2560]. These observations demonstrate presentation and crop inspection; they do not supply ground-truth tile accuracy.
- 4.2.2 Classification results and spatial inspection；段落 8；PDF [64]／印刷页 ['54']。
  - The 3552 × 3536 breast-cancer raster in Figure 4.3 produces 49 crops at a 512 × 512 setting, with smaller right and bottom edges. Controlled tests verify unique source crops, RGB/raw255 preparation, class order, edge handling and area conservation. Applying the CRC-trained classifier to this image demonstrates the interface and sampling workflow; breast-tissue classification accuracy has not been evaluated. Its unknown physical resolution also prevents training-scale matching. The CRC patch results in Section 4.2.6 do not measure this tiled map.

## Figure 4.4

Figure 4.4. Original/segmentation-overlay comparison for a 3552 × 3536 breast-cancer raster, with linked Fit views at 15.7%, opacity 30% and nine-class pixel coverage. Record #49 uses the supervisor-provided breast-cancer-trained UPerNet model. Source: author’s Windows capture.
标题所在小节：4.2.3 Segmentation results；PDF 页：[8]。

- 4.2.3 Segmentation results；段落 2；PDF [65]／印刷页 ['55']。
  - The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 now shows a direct Windows run with the supervisor-provided UPerNet model, aligned source/overlay views and nine-class pixel coverage. The supplied segmentation analysis metadata records imagenet preprocessing, a 1000-pixel source window, stride 512 and network input 224 on CPU. The actual PDF and JSON counts sum to 12,559,872 pixels, equal to 3552 × 3536. The export and screen concern different analysis records; their matching counts are not independent accuracy measurements. Annotated-mask evaluation remains unavailable (Section 4.5.3).

## Figure 4.5

Figure 4.5. Windows parameter isolation: (a) History modes; (b) completed Re-run #83 with recorded 512 × 512/49 tiles and its parameter strip, despite current 256 × 256/196-tile defaults; (c) separate ordinary Run #77 with 256 × 256/196 tiles. Source: author’s Windows captures.
标题所在小节：4.2.4 History, rerun and export；PDF 页：[8]。

- 4.2.4 History, rerun and export；段落 1；PDF [66]／印刷页 ['56']。
  - History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 reserves the Windows history and recorded-rerun demonstration.
- 4.2.4 History, rerun and export；段落 2；PDF [66]／印刷页 ['56']。
  - Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The author identifies the follow-up operation as a recorded Re-run: its completed record #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. The second capture confirms 224 × 224 network input, raw255 and OpenCV linear resize. The Done indicator, restored Run Inference button and new session record distinguish this pair from the earlier busy 49/49 capture. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the actual report and companion-file listing.

## Figure 4.6

Figure 4.6. Actual Standard-quality segmentation PDF, its metadata page and Windows file listing. Analysis record #65 is dated 25 October; the PDF was exported on 30 October 2026. The listed PNG is not included in the uploaded evidence. Source: author’s report and captures.
标题所在小节：4.2.4 History, rerun and export；PDF 页：[8]。

- 4.2.4 History, rerun and export；段落 2；PDF [66]／印刷页 ['56']。
  - Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The author identifies the follow-up operation as a recorded Re-run: its completed record #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. The second capture confirms 224 × 224 network input, raw255 and OpenCV linear resize. The Done indicator, restored Run Inference button and new session record distinguish this pair from the earlier busy 49/49 capture. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the actual report and companion-file listing.

## Figure 4.7

Figure 4.7. Implemented Guide & Support page with persistent Contents navigation and numbered guidance. Source: author’s Qt-simulated development capture; this is interface evidence.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 1；PDF [69]／印刷页 ['59']。
  - Settings includes Appearance, Preferences, Models, Guide & Support, System Information and About. Model defaults are independent per task and require validation. Preferences applies the classification mode immediately while retaining a separate startup default; closed dropdowns scroll the page instead of changing selections accidentally. Guide navigation remains visible and follows the current reading section, while the system-information copy confirmation expires rather than becoming permanent content. Figure 4.7 shows the implemented Guide & Support page and its navigation.

## Figure 4.8

Figure 4.8. English history-calendar popup with a simulated Chinese default locale. Source: author’s Qt-simulated development capture; the selected date is test input.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 2；PDF [70]／印刷页 ['60']。
  - The English calendar in Figure 4.8 was captured after setting the default locale to Chinese in a controlled run. The corresponding test opens each popup, checks English month/day labels, selects a date and verifies the unchanged date value and query signal. This is stronger evidence than merely setting a locale property without opening the widget.

## Figure 4.9

Figure 4.9. Windows cancellation and default-model controls: (a) 228/400 processing progress; (b) cancellation acknowledged with completed record #79 retained; (c) configuration using the controlled test model dummy_segmentation.pt; (d) restored built-in default. The transient Cancelling screen was not captured. Source: author’s Windows captures.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 3；PDF [71]／印刷页 ['61']。
  - Figure 4.9(a–b) documents an actual classification operation at 228/400 processing regions and the subsequent acknowledgement, “Inference cancelled. Previous completed results are unchanged.” Completed record #79 remains displayed. The transient Cancelling state was not captured, and this pair does not by itself audit every history/database entry. Panels (c–d) show default-path configuration with a test model and restoration of the built-in segmentation default. The author identifies dummy_segmentation.pt as a test model; these panels demonstrate settings interaction rather than genuine trained-model predictive performance.

## Figure 4.10

Figure 4.10. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[9]。

- 4.2.6 Classification training and test results；段落 2；PDF [73]／印刷页 ['63']。
  - The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

## Table 4.1

Table 4.1. Classification evaluation summary
标题所在小节：4.2.6 Classification training and test results；PDF 页：[10]。

- 4.2.6 Classification training and test results；段落 3；PDF [74]／印刷页 ['64']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Table 4.2

Table 4.2. Class-wise classification performance on 7,180 test images
标题所在小节：4.2.6 Classification training and test results；PDF 页：[10]。

- 4.2.6 Classification training and test results；段落 3；PDF [74]／印刷页 ['64']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Figure 4.11

Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: the classification experiment’s saved matrix; the Windows default-Pillow predictions independently reproduce every count. Rows are true labels and columns predicted labels.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[9]。

- 4.2.6 Classification training and test results；段落 6；PDF [75]／印刷页 ['65']。
  - Figure 4.11 shows the external-test confusion matrix, allowing the class-wise error patterns to be examined alongside the aggregate metrics.

## Table 4.3

Table 4.3. Complete Windows automated execution for the evaluated source.
标题所在小节：4.3.1 Recorded automated results；PDF 页：[10]。

- 3.6.5 Testing Summary；段落 2；PDF [56]／印刷页 ['46']。
  - On 27 October 2026, revision 3a935ef completed the full native Windows Qt suite: 508 passed, 0 failed, 0 errors and 0 skipped, with 16 warnings in 268.74 seconds (exit 0). Table 4.3 presents this current-source result. Appendix C retains earlier Windows invocations with their original dates and versions; they are not added to the current total.
- 4.3.1 Recorded automated results；段落 1；PDF [77]／印刷页 ['67']。
  - On 27 October 2026, revision 3a935ef completed all 508 collected tests on native Windows Qt: 508 passed, 0 failed, 0 errors and 0 skipped. The pytest summary reports 16 warnings and 268.74 seconds, with exit code 0. Table 4.3 presents this source-matched result. The recorded commit and source/resource manifests agree before and after the execution.

## Table 4.4

Table 4.4. Windows hardware record (19 October) and test runtime (27 October).
标题所在小节：4.3.1 Recorded automated results；PDF 页：[10]。

- 3.6.1 Development Testing；段落 4；PDF [53]／印刷页 ['43']。
  - The 27 October Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.
- 4.3.4 Runtime and deployment verification status；段落 1；PDF [83]／印刷页 ['73']。
  - The Windows hardware and CPU runtime are documented in Table 4.4. No repeated inference-stage or memory benchmark has been supplied, so model loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving and export retain unmeasured status. Appendix E.3 now specifies workload IDs, cold/warm boundaries, repetition counts, raw-record fields and summary rules. Existing export fixture file sizes are a separate file-size observation, not an inference-latency benchmark.

## Figure 4.12

Figure 4.12. Complete Windows pytest report, 27 October 2026, revision 3a935ef. Source: the recorded full-suite log; selected text is reproduced with omissions marked.
标题所在小节：4.3.1 Recorded automated results；PDF 页：[9]。

- 4.3.1 Recorded automated results；段落 6；PDF [79]／印刷页 ['69']。
  - Figure 4.12 reproduces selected lines from the completed 27 October Windows pytest log at revision 3a935ef; it is a test-log excerpt rather than an application screenshot.

## Table 4.5

Table 4.5. Implementation challenges, corrections and supporting evidence.
标题所在小节：4.3.2 Challenges, resolutions and evidence；PDF 页：[10]。

- 4.3.1 Recorded automated results；段落 8；PDF [79]／印刷页 ['69']。
  - Earlier Windows executions encountered a missing training script and thread-lifetime faults. The subsequent 8c4830c invocation reached execution but reported 17 failures and three teardown errors, attributable to settings leakage, compact layouts and platform-dependent path handling. Revision 3a935ef corrected these issues and completed all 508 cases. Table 4.5 summarises the resolutions; Appendix C distinguishes the executions and identifies the source changes.

## Table 4.6

Table 4.6. UAT participant profile — awaiting actual responses
标题所在小节：4.4.1 Participant Demographics；PDF 页：[10]。

- 4.4.1 Participant Demographics；段落 1；PDF [84]／印刷页 ['74']。
  - Table 4.6 reserves the participant profile; its entries will be completed only after actual UAT recruitment and consent.

## Table 4.7

Table 4.7. UAT quantitative summary — awaiting valid data
标题所在小节：4.4.2 Quantitative Results；PDF 页：[10]。

- 4.4.2 Quantitative Results；段落 1；PDF [84]／印刷页 ['74']。
  - Table 4.7 defines the reporting fields for valid SUS responses and task outcomes; the numerical results remain pending.

## Table 4.8

Table 4.8. Feature ratings — awaiting actual use and responses
标题所在小节：4.4.3 Feature Usage and Ratings；PDF 页：[10]。

- 4.4.3 Feature Usage and Ratings；段落 1；PDF [85]／印刷页 ['75']。
  - Table 4.8 reserves the feature-use and rating results, distinguishing features actually used from those not attempted.

## Table 4.9

Table 4.9. Objective achievement and outstanding evidence
标题所在小节：4.5.1 Achievement of Research Objectives；PDF 页：[10]。

- 4.5.1 Achievement of Research Objectives；段落 1；PDF [87]／印刷页 ['77']。
  - Table 4.9 maps each research objective to the implemented outcome and the evidence available for assessing its achievement.

## Table A.1

Table A.1. Original CP1 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[10]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.2

Table A.2. Original CP2 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[10]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.3

Table A.3. Evidence-based milestone status
标题所在小节：A.2 Implementation and outstanding milestones；PDF 页：[10]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table B.1

Table B.1. UAT tasks and success criteria
标题所在小节：B.3 Standard task script and observation rules；PDF 页：[10]。

- 3.6.4 User Acceptance Testing (UAT)；段落 2；PDF [55]／印刷页 ['45']。
  - Participants receive the same five-minute orientation and the approved material pack, then attempt the ten tasks in Table B.1. P01 is an authorised native 224 × 224 classification patch; P02 is an authorised 1024 × 768 raster crop prepared consistently from its source; S01 is a saved real-model segmentation record. R01 is a prepared P02 classification record using 256 × 256 source tiles and Pillow bilinear. Those dimensions standardise the interaction task and are not a validated training-scale recommendation. T07 explicitly contrasts Re-run of R01 with ordinary Run after changing current dimensions to 512 × 512. Actual filenames, checksums, permissions and the tested commit must be entered in the supplied material register before testing.
- B.3 Standard task script and observation rules；段落 1；PDF [106]／印刷页 ['96']。
  - Table B.1 specifies the UAT tasks, participant instructions and observable success criteria to be used during the planned study.

## Table C.1

Table C.1. Principal evidence sources
标题所在小节：C.1 Evaluated source and evidence；PDF 页：[10]。

- C.1 Evaluated source and evidence；段落 1；PDF [109]／印刷页 ['99']。
  - The evaluated application source is commit 3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5. Its complete native Windows Qt execution on 27 October 2026 passed all 508 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.

## Table C.2

Table C.2. Windows automated execution history.
标题所在小节：C.2 Evidence interpretation；PDF 页：[10]。

- C.1 Evaluated source and evidence；段落 1；PDF [109]／印刷页 ['99']。
  - The evaluated application source is commit 3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5. Its complete native Windows Qt execution on 27 October 2026 passed all 508 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.
- C.2 Evidence interpretation；段落 1；PDF [112]／印刷页 ['102']。
  - Table C.2 reports the completed current Windows execution separately from earlier Windows invocations. The preceding 8c4830c run had 505 distinct test identities, with 17 failures and 3 teardown errors attached to failing cases; its JUnit aggregate included 508 reports. The current 3a935ef invocation has 508 distinct cases, all passing. The older 131-case subset is an independent record and is not added to either complete-suite total.

## Table D.1

Table D.1. Final Windows acceptance cases
标题所在小节：D.1 Native acceptance record；PDF 页：[10]。

- D.1 Native acceptance record；段落 1；PDF [113]／印刷页 ['103']。
  - For each manual acceptance case record date, tester, evaluated source state, Windows/Python/dependency versions, hardware, actual Qt platform/display metrics, model/input identity, expected outcome, actual outcome and evidence file. Table D.1 remains a real-image manual checklist. The completed automated suite is supporting evidence, not a prefilled Pass for human-observed tasks.
