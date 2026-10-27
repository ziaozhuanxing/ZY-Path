# 图表正文提及位置

共 20 张图、24 张表；每项均有标题之外的明确正文编号提及。待补截图和UAT表仍按待补证据描述。

## Figure 1.1

Figure 1.1. Representative H&E colorectal tissue image (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：1.1 Background and Motivation；PDF 页：[8]。

- 1.1 Background and Motivation；段落 2；PDF [10]／印刷页 ['1']。
  - Histopathology is a reference method for diagnosing many diseases, including malignancies. In haematoxylin and eosin (H&E) images, the staining of nuclei and cytoplasmic structures provides morphological information that trained professionals interpret in context. Digital imaging makes these observations available for storage, teaching and computational analysis. A model's output, however, is an inference from image appearance and must not be equated with a verified clinical diagnosis (Litjens et al., 2017; Kather et al., 2019). Figure 1.1 is reserved for an authorised H&E example illustrating this tissue context.

## Figure 2.1

Figure 2.1. Three output meanings: whole-image classification, source-tile estimates and pixel segmentation. Author-created conceptual diagram; it contains no model accuracy results.
标题所在小节：2.2.4 Tiled classification, coverage and confidence；PDF 页：[8]。

- 2.2.4 Tiled classification, coverage and confidence；段落 2；PDF [19]／印刷页 ['10']。
  - The model's softmax output is a normalised score over its classes. It is not automatically calibrated as the probability that an interpretation is correct (Guo et al., 2017). A high-confidence majority class across many tiles can arise from genuine image content, sampling scale, preprocessing mismatch or model/domain limitations. ZY-Path exposes per-tile probabilities and coordinates so these possibilities can be investigated rather than using a coloured map as proof of accuracy. Figure 2.1 distinguishes the three output meanings: whole-image classification, tile-class estimates and pixel segmentation.

## Table 2.1

Table 2.1. Scope-based comparison of pathology platforms
标题所在小节：2.4 Comparative Evaluation of Existing Systems；PDF 页：[9]。

- 2.4 Comparative Evaluation of Existing Systems；段落 1；PDF [23]／印刷页 ['14']。
  - Table 2.1 compares platform purposes and documented workflow scope. It separates an unexamined capability from an absent one and uses no aggregate ranking because the applications address different tasks. Source publications are cited in Sections 2.3.1–2.3.5.

## Figure 3.1

Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the project’s Python modules.
标题所在小节：3.1 Overview of System Methodology；PDF 页：[8]。

- 3.1 Overview of System Methodology；段落 2；PDF [27]／印刷页 ['18']。
  - The implemented system has three logical layers. The presentation layer contains the main window, inference/history/action panels, settings and result viewers. The core layer loads models, prepares inputs, executes inference and parses outputs. The data layer stores records and creates export files. MainWindow coordinates transitions between these layers, including saving result artifacts before inserting a completed history record. Figure 3.1 shows these layers and the flow of model, image, result and history artifacts.

## Table 3.1

Table 3.1. Functional requirements and acceptance conditions
标题所在小节：3.2.1 Functional Requirements；PDF 页：[9]。

- 3.2.1 Functional Requirements；段落 1；PDF [29]／印刷页 ['20']。
  - The requirements preserve the original model–image–inference–history workflow and add explicit spatial analysis and state-management requirements revealed during development. A requirement describes intended behaviour; its implementation and evidence status are recorded separately in Section 3.6.6. Table 3.1 specifies each functional requirement and its observable acceptance condition.

## Table 3.2

Table 3.2. Non-functional requirements and verification boundaries
标题所在小节：3.2.2 Non-Functional Requirements；PDF 页：[9]。

- 3.2.2 Non-Functional Requirements；段落 1；PDF [30]／印刷页 ['21']。
  - Table 3.2 links the non-functional requirements to their verification approaches and current implementation boundaries.

## Table 3.3

Table 3.3. Classification class order and fixed display palette v1
标题所在小节：3.3.5 Class probabilities, maps and estimated coverage；PDF 页：[9]。

- 3.3.5 Class probabilities, maps and estimated coverage；段落 7；PDF [37]／印刷页 ['28']。
  - This aggregate need not equal the class with the largest r_c because probability mass and hard-class coverage are different summaries. It is not a new whole-image forward pass. The history table therefore shows tile count and largest estimated coverage, leaving whole-image confidence blank; PDF metadata distinguishes “Aggregate tile label” and “Area-weighted mean probability”. Table 3.3 records the classifier’s fixed class order and dedicated nine-colour display palette.

## Table 3.4

Table 3.4. Built-in segmentation labels and display colours
标题所在小节：3.3.6 Segmentation pathway and label restoration；PDF 页：[9]。

- 3.3.6 Segmentation pathway and label restoration；段落 5；PDF [39]／印刷页 ['30']。
  - The nine-label order and RGB colours in Table 3.4 match the reference notebook. Generic compatible segmentation models use a separate prepared-tensor and OutputParser pathway. The model filename’s 100ep and panoptils strings are retained as identifiers; training duration and dataset provenance are not inferred from those strings.

## Table 3.5

Table 3.5. Implemented persistent data structures
标题所在小节：3.3.8 History schema, artifacts and rerun isolation；PDF 页：[9]。

- 3.3.8 History schema, artifacts and rerun isolation；段落 1；PDF [40]／印刷页 ['31']。
  - DatabaseManager uses sqlite3 connections with parameterised statements and transaction handling. The base inference_records table stores paths, task, label/confidence where applicable, result-image path and timestamp. A companion segmentation_artifacts table stores artifact paths and analysis_json; despite its legacy name, it also carries tiled-classification and single-classification parameter metadata. Table 3.5 summarises the persistent structures and the purpose of their principal fields.

## Figure 3.2

Figure 3.2. Annotated final workflow wireframe. This author-created design diagram summarises implemented regions and is not a Windows runtime screenshot.
标题所在小节：3.4.1 Principles and information hierarchy；PDF 页：[8]。

- 3.4.1 Principles and information hierarchy；段落 1；PDF [43]／印刷页 ['34']。
  - The interface keeps the CP1 three-region structure: input controls on the left, analysis/history in the centre and export/session actions on the right. Implementation changes replace fixed panel assumptions with draggable splitters, scrollable contents and bounded window restoration. The aim is to keep essential actions reachable while prioritising the analysis image. Figure 3.2 presents an annotated wireframe of this arrangement and its main user actions.

## Figure 3.3

Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities. Source: author, based on the implemented application.
标题所在小节：3.5.1 Use Case Diagram；PDF 页：[8]。

- 3.5.1 Use Case Diagram；段落 1；PDF [46]／印刷页 ['37']。
  - The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Selecting a model includes compatibility validation. Tiled analysis is an explicit classification variant. Restore saved result and Re-run recorded analysis are separate use cases because only rerun performs inference and creates a new record; Search/filter locates records without executing either operation. Figure 3.3 maps these actions and their scope.

## Figure 3.4

Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records. Source: author, based on the implemented application.
标题所在小节：3.5.2 Sequence Diagram；PDF 页：[8]。

- 3.5.2 Sequence Diagram；段落 1；PDF [47]／印刷页 ['38']。
  - The sequence diagram follows a run after image, task and model selection. MainWindow snapshots the current preferences for ordinary Run or the selected record for Re-run, then starts the worker. Signals deliver progress and a completed result. The coordinator saves completed artifacts and inserts a record only after successful persistence. Figure 3.4 uses guarded alternative fragments for cancellation, pipeline error and persistence failure; these exits are distinct from completed history.

## Figure 3.5

Figure 3.5. Implementation-level class diagram. Relationships show selected coordination dependencies and worker inheritance. Source: author, based on the implemented application.
标题所在小节：3.5.3 Class Diagram；PDF 页：[8]。

- 3.5.3 Class Diagram；段落 1；PDF [49]／印刷页 ['40']。
  - The class diagram shows selected runtime responsibilities rather than every widget. MainWindow coordinates input, history, inference, persistence and export. InferenceEngine depends on model loading, preprocessing and output parsing. PdfExportWorker delegates report generation to ExportManager. Spatial result pages use ImageComparison and ZoomableImageView. Figure 3.5 distinguishes coordination dependencies and worker inheritance for the current implementation.

## Figure 3.6

Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits. Source: author, based on the implemented application.
标题所在小节：3.5.4 Activity Diagram；PDF 页：[8]。

- 3.5.4 Activity Diagram；段落 1；PDF [50]／印刷页 ['41']。
  - The activity diagram distinguishes current-preference Run from recorded-parameter Re-run before selecting the task/mode pathway. Classification crops and segmentation processing regions retain independent geometry. Cancellation is checked at safe points before/after model work and between processing regions. Figure 3.6 labels the decisions and success/error exits; a request does not forcibly interrupt a running forward operation.

## Table 3.6

Table 3.6. Requirements traceability matrix
标题所在小节：3.6.6 Requirements Traceability Matrix；PDF 页：[9]。

- 3.6.6 Requirements Traceability Matrix；段落 1；PDF [54]／印刷页 ['45']。
  - Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the completed native Windows automated checks, recorded classifier evaluation, outstanding manual acceptance, UAT and further model studies.

## Table 3.7

Table 3.7. Risk register and residual mitigations
标题所在小节：3.7 Risk Management and Mitigation Strategies；PDF 页：[9]。

- 3.7 Risk Management and Mitigation Strategies；段落 1；PDF [58]／印刷页 ['49']。
  - The CP1 risks concerning model compatibility, dependencies, packaging, CPU performance, recruitment and data reliability remain relevant. CP2 adds scale ambiguity and misleading spatial statistics because explicit tiled classification introduces sampling choices that a user might mistake for validated tissue measurements. Table 3.7 distinguishes implemented controls from future verification.

## Figure 4.1

Figure 4.1. Final Windows application overview (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.1 Implemented workflow and scope；PDF 页：[8]。

- 4.2.1 Implemented workflow and scope；段落 2；PDF [61]／印刷页 ['52']。
  - The Windows session on 19 October 2026 launched the application from its virtual environment and recorded successful loading and validation of crc_dn21_seed42_best.pth as a nine-class DenseNet with output shape (1, 9). This establishes source-based startup and classifier integration for that session. The observed workflow and window states are detailed in Section 4.3.3. Figure 4.1 reserves the corresponding Windows application overview; the authorised screenshot remains to be inserted.

## Figure 4.2

Figure 4.2. Tiled classification interface with source/result comparison and revised result toggles. Source: author’s Linux/offscreen-Qt development capture; synthetic fixture, not a model result.
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[8]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [62]／印刷页 ['53']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Current-version real-image inspection remains reserved in Figure 4.3, including tile numbers and original-crop detail.
- 4.2.2 Classification results and spatial inspection；段落 4；PDF [63]／印刷页 ['54']。
  - Figure 4.3 reserves real-weight Windows captures of Single image and Tiled analysis; these pending captures are separate from the synthetic interface example in Figure 4.2.

## Figure 4.3

Figure 4.3. Real-weight single-image and tiled classification evidence (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[8]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [62]／印刷页 ['53']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Current-version real-image inspection remains reserved in Figure 4.3, including tile numbers and original-crop detail.
- 4.2.2 Classification results and spatial inspection；段落 4；PDF [63]／印刷页 ['54']。
  - Figure 4.3 reserves real-weight Windows captures of Single image and Tiled analysis; these pending captures are separate from the synthetic interface example in Figure 4.2.

## Figure 4.4

Figure 4.4. Windows segmentation result and aligned comparison (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.3 Segmentation results；PDF 页：[8]。

- 4.2.3 Segmentation results；段落 2；PDF [64]／印刷页 ['55']。
  - The reference notebook establishes the segmentation architecture, preprocessing, labels and probability-fusion procedure. Controlled software tests cover restored dimensions, class counts and blending behaviour. Segmentation predictive performance is treated separately: annotated-mask metrics were not available for this model, as discussed in Section 4.5.3. Figure 4.4 reserves the real-weight Windows segmentation view and aligned source comparison; the capture is still pending.

## Figure 4.5

Figure 4.5. History and recorded-parameter rerun (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.4 History, rerun and export；PDF 页：[8]。

- 4.2.4 History, rerun and export；段落 1；PDF [64]／印刷页 ['55']。
  - History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 reserves the Windows history and recorded-rerun demonstration.

## Figure 4.6

Figure 4.6. Exported report and companion artifacts (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.4 History, rerun and export；PDF 页：[8]。

- 4.2.4 History, rerun and export；段落 2；PDF [65]／印刷页 ['56']。
  - Rerun tests demonstrate that the recorded model/task/mode and analysis settings take precedence over current preferences. Restoring a record does not itself create a new prediction. The export workflow uses the displayed completed record's metadata and can retain task-specific maps/JSON together with the presentation. This prevents a newly selected model from being incorrectly attached to an older visible result. Figure 4.6 reserves an exported report and its companion artifacts for inspection; the real-file capture remains pending.

## Figure 4.7

Figure 4.7. Implemented Guide & Support page with persistent Contents navigation and numbered guidance. Source: author’s Linux/offscreen-Qt development capture; this is interface evidence.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 1；PDF [65]／印刷页 ['56']。
  - Settings includes Appearance, Preferences, Models, Guide & Support, System Information and About. Model defaults are independent per task and require validation. Preferences applies the classification mode immediately while retaining a separate startup default; closed dropdowns scroll the page instead of changing selections accidentally. Guide navigation remains visible and follows the current reading section, while the system-information copy confirmation expires rather than becoming permanent content. Figure 4.7 shows the implemented Guide & Support page and its navigation.

## Figure 4.8

Figure 4.8. English history-calendar popup with a simulated Chinese default locale. Source: author’s Linux/offscreen-Qt development capture; the selected date is test input.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 3；PDF [66]／印刷页 ['57']。
  - The English calendar in Figure 4.8 was captured after setting the default locale to Chinese in a controlled run. The corresponding test opens each popup, checks English month/day labels, selects a date and verifies the unchanged date value and query signal. This is stronger evidence than merely setting a locale property without opening the widget.

## Figure 4.9

Figure 4.9. Cancellation and per-task model defaults on Windows (evidence pending; replace this reserved area with the actual authorised capture).
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[8]。

- 4.2.5 Settings, cancellation and interface polish；段落 4；PDF [67]／印刷页 ['58']。
  - Cancel inference is available during work. Tests cover cancellation at multiple checkpoints and preservation of the previous completed result. The interface waits for the current operation and worker cleanup; it does not advertise instantaneous termination. A final real-model cancellation recording remains useful because the duration of an individual model operation depends on the actual weights, workload and hardware. Figure 4.9 reserves the Windows demonstration of cancellation and task-specific model defaults.

## Figure 4.10

Figure 4.10. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[8]。

- 4.2.6 Classification training and test results；段落 2；PDF [68]／印刷页 ['59']。
  - The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

## Table 4.1

Table 4.1. Classification evaluation summary
标题所在小节：4.2.6 Classification training and test results；PDF 页：[9]。

- 4.2.6 Classification training and test results；段落 3；PDF [68]／印刷页 ['59']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Table 4.2

Table 4.2. Class-wise classification performance on 7,180 test images
标题所在小节：4.2.6 Classification training and test results；PDF 页：[9]。

- 4.2.6 Classification training and test results；段落 3；PDF [68]／印刷页 ['59']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Figure 4.11

Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: the classification experiment’s saved matrix; the Windows default-Pillow predictions independently reproduce every count. Rows are true labels and columns predicted labels.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[8]。

- 4.2.6 Classification training and test results；段落 6；PDF [70]／印刷页 ['61']。
  - Figure 4.11 shows the external-test confusion matrix, allowing the class-wise error patterns to be examined alongside the aggregate metrics.

## Table 4.3

Table 4.3. Complete automated invocations by source version and environment
标题所在小节：4.3.1 Recorded automated results；PDF 页：[9]。

- 3.6.5 Testing Summary；段落 2；PDF [54]／印刷页 ['45']。
  - Automated results are labelled by environment, date and source version. The 19 October Windows baseline completed 370 tests without failures/errors/skips. The current-source 26 October Linux/offscreen-Qt invocation completed 505 cases with 504 passed, one genuine segmentation-weight availability failure and no errors/skips. Table 4.3 presents both complete invocations separately; related subsets and original interruptions remain in Appendix C.
- 4.3.1 Recorded automated results；段落 1；PDF [72]／印刷页 ['63']。
  - The completed Windows invocation on 19 October 2026 passed all 370 cases at baseline source 7bd3552, with 0 failures/errors/skips, 15 warnings and 194.10 seconds (exit 0). The current-source 26 October Linux/offscreen-Qt invocation completed 505 cases: 504 passed, 1 failed, 0 errors and 0 skipped, with 14 warnings in 219.20 seconds (exit 1). The failed case asserts the presence of the genuine built-in segmentation weight, which is absent from that installation. Table 4.3 separates the two versions and platforms; no current-version native Windows pass is inferred.

## Table 4.4

Table 4.4. Windows test host and actual CPU runtime on 19 October 2026
标题所在小节：4.3.1 Recorded automated results；PDF 页：[9]。

- 3.6.1 Development Testing；段落 3；PDF [51]／印刷页 ['42']。
  - The latest Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.
- 4.3.4 Runtime and deployment verification status；段落 1；PDF [77]／印刷页 ['68']。
  - The Windows hardware and CPU runtime are documented in Table 4.4. No repeated inference-stage or memory benchmark has been supplied, so model loading, preprocessing, forward inference, reconstruction/statistics, GUI display, saving and export retain unmeasured status. Appendix E.3 now specifies workload IDs, cold/warm boundaries, repetition counts, raw-record fields and summary rules. Existing export fixture file sizes are a separate file-size observation, not an inference-latency benchmark.

## Figure 4.12

Figure 4.12. Completed Windows pytest report, 19 October 2026. Source: the recorded full-suite log; selected text is reproduced with omissions marked.
标题所在小节：4.3.1 Recorded automated results；PDF 页：[8]。

- 4.3.1 Recorded automated results；段落 6；PDF [74]／印刷页 ['65']。
  - Figure 4.12 reproduces selected lines from the genuine final Windows pytest report; it is a test-log excerpt rather than an application screenshot.

## Table 4.5

Table 4.5. Implementation challenges and verified resolutions
标题所在小节：4.3.2 Challenges, resolutions and evidence；PDF 页：[9]。

- 4.3.1 Recorded automated results；段落 8；PDF [74]／印刷页 ['65']。
  - Earlier Windows runs were interrupted by a missing training-script prerequisite and a worker-thread destruction fault. Restoring the genuine script and correcting worker lifetime, queued validation callbacks and panel size policies resolved the observed regression cases in the final suite. Table 4.5 summarises the implementation corrections; Appendix C retains the earlier run outcomes.

## Table 4.6

Table 4.6. UAT participant profile — awaiting actual responses
标题所在小节：4.4.1 Participant Demographics；PDF 页：[9]。

- 4.4.1 Participant Demographics；段落 1；PDF [78]／印刷页 ['69']。
  - Table 4.6 reserves the participant profile; its entries will be completed only after actual UAT recruitment and consent.

## Table 4.7

Table 4.7. UAT quantitative summary — awaiting valid data
标题所在小节：4.4.2 Quantitative Results；PDF 页：[9]。

- 4.4.2 Quantitative Results；段落 1；PDF [79]／印刷页 ['70']。
  - Table 4.7 defines the reporting fields for valid SUS responses and task outcomes; the numerical results remain pending.

## Table 4.8

Table 4.8. Feature ratings — awaiting actual use and responses
标题所在小节：4.4.3 Feature Usage and Ratings；PDF 页：[9]。

- 4.4.3 Feature Usage and Ratings；段落 1；PDF [79]／印刷页 ['70']。
  - Table 4.8 reserves the feature-use and rating results, distinguishing features actually used from those not attempted.

## Table 4.9

Table 4.9. Objective achievement and outstanding evidence
标题所在小节：4.5.1 Achievement of Research Objectives；PDF 页：[9]。

- 4.5.1 Achievement of Research Objectives；段落 1；PDF [81]／印刷页 ['72']。
  - Table 4.9 maps each research objective to the implemented outcome and the evidence available for assessing its achievement.

## Table A.1

Table A.1. Original CP1 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[9]。

- A.1 Proposal baseline；段落 1；PDF [92]／印刷页 ['83']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.2

Table A.2. Original CP2 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[9]。

- A.1 Proposal baseline；段落 1；PDF [92]／印刷页 ['83']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.3

Table A.3. Evidence-based milestone status
标题所在小节：A.2 Implementation and outstanding milestones；PDF 页：[9]。

- A.1 Proposal baseline；段落 1；PDF [92]／印刷页 ['83']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table B.1

Table B.1. UAT tasks and success criteria
标题所在小节：B.3 Standard task script and observation rules；PDF 页：[9]。

- 3.6.4 User Acceptance Testing (UAT)；段落 2；PDF [53]／印刷页 ['44']。
  - Participants receive the same five-minute orientation and the approved material pack, then attempt the ten tasks in Table B.1. P01 is an authorised native 224 × 224 classification patch; P02 is an authorised 1024 × 768 raster crop prepared consistently from its source; S01 is a saved real-model segmentation record. R01 is a prepared P02 classification record using 256 × 256 source tiles and Pillow bilinear. Those dimensions standardise the interaction task and are not a validated training-scale recommendation. T07 explicitly contrasts Re-run of R01 with ordinary Run after changing current dimensions to 512 × 512. Actual filenames, checksums, permissions and the tested commit must be entered in the supplied material register before testing.
- B.3 Standard task script and observation rules；段落 1；PDF [100]／印刷页 ['91']。
  - Table B.1 specifies the UAT tasks, participant instructions and observable success criteria to be used during the planned study.

## Table C.1

Table C.1. Principal evidence sources
标题所在小节：C.1 Source baseline；PDF 页：[9]。

- C.1 Source baseline；段落 1；PDF [103]／印刷页 ['94']。
  - The current application source is commit 8c4830c1281e4a85248c9a2ea9d0adae64bd4525. The 26 October Linux invocation ran that source content before it was committed; the executed-file hashes agree with the committed files. The Windows baseline is 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19, recorded after the 19 October Windows run. Original logs retain their original identifiers. Table C.1 identifies the materials and Table C.2 separates the actual executions.

## Table C.2

Table C.2. Platform- and version-specific automated execution history
标题所在小节：C.2 Evidence interpretation；PDF 页：[9]。

- C.1 Source baseline；段落 1；PDF [103]／印刷页 ['94']。
  - The current application source is commit 8c4830c1281e4a85248c9a2ea9d0adae64bd4525. The 26 October Linux invocation ran that source content before it was committed; the executed-file hashes agree with the committed files. The Windows baseline is 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19, recorded after the 19 October Windows run. Original logs retain their original identifiers. Table C.1 identifies the materials and Table C.2 separates the actual executions.
- C.2 Evidence interpretation；段落 1；PDF [105]／印刷页 ['96']。
  - Table C.2 separates the completed earlier Windows baseline from the current-source Linux/offscreen-Qt invocation and earlier Windows interruptions. The Windows baseline has 370 passes; the current Linux result has 504 passes and one genuine segmentation-resource failure. The Windows 131-case related subset, current Linux 126-case related subset and 14-case 2×-DPI subset are independent records and are not summed into a complete-suite total.

## Table D.1

Table D.1. Final Windows acceptance cases
标题所在小节：D.1 Native acceptance record；PDF 页：[9]。

- D.1 Native acceptance record；段落 1；PDF [106]／印刷页 ['97']。
  - For each manual acceptance case record date, tester, final source state, Windows/Python/dependency versions, hardware, actual Qt platform/display metrics, model/input identity, expected outcome, actual outcome and evidence file. The earlier source-startup record and baseline suite do not automatically accept current changes. Table D.1 remains a manual checklist: a Pass requires the specified observed native task record, not a Linux fixture or old Windows total.
