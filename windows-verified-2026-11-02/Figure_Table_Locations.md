# 图表正文提及位置

共 20 张图、24 张表；每项均有标题之外的明确正文编号提及。全部图表均有正文编号提及；UAT表保留已完成的真实记录分析。

## Figure 1.1

Figure 1.1. TUM-labelled H&E patch TUM-TCGA-AAHIDTWA.tif, 224 × 224 pixels. Source: CRC-VAL-HE-7K, identified by the author; dataset DOI 10.5281/zenodo.1214456.
标题所在小节：1.1 Background and Motivation；PDF 页：[11]。

- 1.1 Background and Motivation；段落 1；PDF [11]／印刷页 ['1']。
  - Histopathology is a reference method for diagnosing many diseases, including malignancies. In haematoxylin and eosin (H&E) images, the staining of nuclei and cytoplasmic structures provides morphological information that trained professionals interpret in context. Digital imaging makes these observations available for storage, teaching and computational analysis. A model's output, however, is an inference from image appearance and must not be equated with a verified clinical diagnosis (Litjens et al., 2017; Kather et al., 2019). Figure 1.1 illustrates this tissue context using a TUM-labelled patch from CRC-VAL-HE-7K.

## Figure 2.1

Figure 2.1. Three output meanings: whole-image classification, source-tile estimates and pixel segmentation. Author-created conceptual diagram; it contains no model accuracy results.
标题所在小节：2.2.4 Tiled classification, coverage and confidence；PDF 页：[20]。

- 2.2.4 Tiled classification, coverage and confidence；段落 2；PDF [20]／印刷页 ['10']。
  - The model's softmax output is a normalised score over its classes. It is not automatically calibrated as the probability that an interpretation is correct (Guo et al., 2017). A high-confidence majority class across many tiles can arise from genuine image content, sampling scale, preprocessing mismatch or model/domain limitations. ZY-Path exposes per-tile probabilities and coordinates so these possibilities can be investigated rather than using a coloured map as proof of accuracy. Figure 2.1 distinguishes the three output meanings: whole-image classification, tile-class estimates and pixel segmentation.

## Table 2.1

Table 2.1. Scope-based comparison of pathology platforms
标题所在小节：2.4 Comparative Evaluation of Existing Systems；PDF 页：[24]。

- 2.4 Comparative Evaluation of Existing Systems；段落 1；PDF [24]／印刷页 ['14']。
  - Table 2.1 compares platform purposes and documented workflow scope. It separates an unexamined capability from an absent one and uses no aggregate ranking because the applications address different tasks. Source publications are cited in Sections 2.3.1–2.3.5.

## Figure 3.1

Figure 3.1. Implemented logical architecture and artifact flow. Source: author, based on the project’s Python modules.
标题所在小节：3.1 Overview of System Methodology；PDF 页：[29]。

- 3.1 Overview of System Methodology；段落 2；PDF [28]／印刷页 ['18']。
  - The implemented system has three logical layers. The presentation layer contains the main window, inference/history/action panels, settings and result viewers. The core layer loads models, prepares inputs, executes inference and parses outputs. The data layer stores records and creates export files. MainWindow coordinates transitions between these layers, including saving result artifacts before inserting a completed history record. Figure 3.1 shows these layers and the flow of model, image, result and history artifacts.

## Table 3.1

Table 3.1. Functional requirements and acceptance conditions
标题所在小节：3.2.1 Functional Requirements；PDF 页：[30]。

- 3.2.1 Functional Requirements；段落 1；PDF [30]／印刷页 ['20']。
  - The requirements preserve the original model–image–inference–history workflow and add explicit spatial analysis and state-management requirements revealed during development. A requirement describes intended behaviour; its implementation and evidence status are recorded separately in Section 3.6.6. Table 3.1 specifies each functional requirement and its observable acceptance condition.

## Table 3.2

Table 3.2. Non-functional requirements and verification boundaries
标题所在小节：3.2.2 Non-Functional Requirements；PDF 页：[31]。

- 3.2.2 Non-Functional Requirements；段落 1；PDF [31]／印刷页 ['21']。
  - Table 3.2 links the non-functional requirements to their verification approaches and current implementation boundaries.

## Table 3.3

Table 3.3. Classification class order and fixed display palette v1
标题所在小节：3.3.5 Class probabilities, maps and estimated coverage；PDF 页：[38]。

- 3.3.5 Class probabilities, maps and estimated coverage；段落 7；PDF [38]／印刷页 ['28']。
  - This aggregate need not equal the class with the largest r_c because probability mass and hard-class coverage are different summaries. It is not a new whole-image forward pass. The history table therefore shows tile count and largest estimated coverage, leaving whole-image confidence blank; PDF metadata distinguishes “Aggregate tile label” and “Area-weighted mean probability”. Table 3.3 records the classifier’s fixed class order and dedicated nine-colour display palette.

## Table 3.4

Table 3.4. Built-in segmentation labels and display colours
标题所在小节：3.3.6 Segmentation pathway and label restoration；PDF 页：[40]。

- 3.3.6 Segmentation pathway and label restoration；段落 5；PDF [40]／印刷页 ['30']。
  - The nine-label order and RGB colours in Table 3.4 match the reference notebook. Generic compatible segmentation models use a separate prepared-tensor and OutputParser pathway. The model filename’s 100ep and panoptils strings are retained as identifiers; training duration and dataset provenance are not inferred from those strings.

## Table 3.5

Table 3.5. Implemented persistent data structures
标题所在小节：3.3.8 History schema, artifacts and rerun isolation；PDF 页：[41]。

- 3.3.8 History schema, artifacts and rerun isolation；段落 1；PDF [41]／印刷页 ['31']。
  - DatabaseManager uses sqlite3 connections with parameterised statements and transaction handling. The base inference_records table stores paths, task, label/confidence where applicable, result-image path and timestamp. A companion segmentation_artifacts table stores artifact paths and analysis_json; despite its legacy name, it also carries tiled-classification and single-classification parameter metadata. Table 3.5 summarises the persistent structures and the purpose of their principal fields.

## Figure 3.2

Figure 3.2. Annotated final workflow wireframe. This author-created design diagram summarises implemented regions and is not a Windows runtime screenshot.
标题所在小节：3.4.1 Principles and information hierarchy；PDF 页：[44]。

- 3.4.1 Principles and information hierarchy；段落 1；PDF [44]／印刷页 ['34']。
  - The interface keeps the CP1 three-region structure: input controls on the left, analysis/history in the centre and export/session actions on the right. Implementation changes replace fixed panel assumptions with draggable splitters, scrollable contents and bounded window restoration. The aim is to keep essential actions reachable while prioritising the analysis image. Figure 3.2 presents an annotated wireframe of this arrangement and its main user actions.

## Figure 3.3

Figure 3.3. Use case diagram for the implemented local analysis workflow. File/model trust and clinical interpretation remain external responsibilities. Source: author, based on the implemented application.
标题所在小节：3.5.1 Use Case Diagram；PDF 页：[47]。

- 3.5.1 Use Case Diagram；段落 1；PDF [46]／印刷页 ['36']。
  - The primary actor is an educational/research user. No administrator or clinical approval role is implemented. Selecting a model includes compatibility validation. Tiled analysis is an explicit classification variant. Restore saved result and Re-run recorded analysis are separate use cases because only rerun performs inference and creates a new record; Search/filter locates records without executing either operation. Figure 3.3 maps these actions and their scope.

## Figure 3.4

Figure 3.4. Sequence diagram for a run and its persistence boundary. Cancellation is acknowledged after a safe checkpoint; artifact-save failures must not be represented as successful saved records. Source: author, based on the implemented application.
标题所在小节：3.5.2 Sequence Diagram；PDF 页：[48]。

- 3.5.2 Sequence Diagram；段落 1；PDF [48]／印刷页 ['38']。
  - The sequence diagram follows a run after image, task and model selection. MainWindow snapshots the current preferences for ordinary Run or the selected record for Re-run, then starts the worker. Signals deliver progress and a completed result. The coordinator saves completed artifacts and inserts a record only after successful persistence. Figure 3.4 uses guarded alternative fragments for cancellation, pipeline error and persistence failure; these exits are distinct from completed history.

## Figure 3.5

Figure 3.5. Implementation-level class diagram. Relationships show selected coordination dependencies and worker inheritance. Source: author, based on the implemented application.
标题所在小节：3.5.3 Class Diagram；PDF 页：[49]。

- 3.5.3 Class Diagram；段落 1；PDF [49]／印刷页 ['39']。
  - The class diagram shows selected runtime responsibilities rather than every widget. MainWindow coordinates input, history, inference, persistence and export. InferenceEngine depends on model loading, preprocessing and output parsing. PdfExportWorker delegates report generation to ExportManager. Spatial result pages use ImageComparison and ZoomableImageView. Figure 3.5 distinguishes coordination dependencies and worker inheritance for the current implementation.

## Figure 3.6

Figure 3.6. Activity diagram from parameter selection to completed persistence, with safe cancellation and error exits. Source: author, based on the implemented application.
标题所在小节：3.5.4 Activity Diagram；PDF 页：[51]。

- 3.5.4 Activity Diagram；段落 1；PDF [50]／印刷页 ['40']。
  - The activity diagram distinguishes current-preference Run from recorded-parameter Re-run before selecting the task/mode pathway. Classification crops and segmentation processing regions retain independent geometry. Cancellation is checked at safe points before/after model work and between processing regions. Figure 3.6 labels the decisions and success/error exits; a request does not forcibly interrupt a running forward operation.

## Table 3.6

Table 3.6. Requirements traceability matrix
标题所在小节：3.6.6 Requirements Traceability Matrix；PDF 页：[55]。

- 3.6.6 Requirements Traceability Matrix；段落 1；PDF [55]／印刷页 ['45']。
  - Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the completed native Windows automated checks, recorded classifier evaluation, author-declared manual acceptance, completed formative UAT and further model studies.

## Table 3.7

Table 3.7. Risk register and residual mitigations
标题所在小节：3.7 Risk Management and Mitigation Strategies；PDF 页：[58]。

- 3.7 Risk Management and Mitigation Strategies；段落 1；PDF [58]／印刷页 ['48']。
  - The CP1 risks concerning model compatibility, dependencies, packaging, CPU performance, recruitment and data reliability remain relevant. CP2 adds scale ambiguity and misleading spatial statistics because explicit tiled classification introduces sampling choices that a user might mistake for validated tissue measurements. Table 3.7 distinguishes implemented controls from future verification.

## Figure 4.1

Figure 4.1. Windows application overview, 31 October 2026: Single image classification of a 224 × 224 patch, NORM at 99.9%, record #84, with OpenCV linear selected. Source: author’s Windows capture.
标题所在小节：4.2.1 Implemented workflow and scope；PDF 页：[61]。

- 4.2.1 Implemented workflow and scope；段落 2；PDF [60]／印刷页 ['50']。
  - The Windows startup record on 19 October 2026 establishes classifier loading and validation. Figure 4.1 shows the Windows overview captured on 31 October: record #84 displays NORM-TCGA-ACCEDPAW.tif at 224 × 224 pixels, the NORM prediction at 99.9% confidence, the probability chart and the export/session actions including Clear view. The selected resize option is OpenCV linear. This is an observed prediction, not an additional accuracy experiment.

## Figure 4.2

Figure 4.2. Tiled classification interface with source/result comparison and revised result toggles. Source: author’s Qt-simulated development capture; synthetic fixture, not a model result.
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[62]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [61]／印刷页 ['51']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Figure 4.3 provides separate actual-image Windows observations, including tile numbers and original-crop inspection.

## Figure 4.3

Figure 4.3. Windows classification workflow on a supervisor-provided breast-cancer raster: (a) Single image; (b) 49 numbered 512 × 512 source tiles; (c) crop inspection from the separate analysis #48. The CRC-trained classifier uses raw255 and OpenCV linear resize to 224 × 224. Source: author’s Windows captures.
标题所在小节：4.2.2 Classification results and spatial inspection；PDF 页：[63]。

- 4.2.2 Classification results and spatial inspection；段落 3；PDF [62]／印刷页 ['52']。
  - Figure 4.2 is a retained earlier Qt result-view capture using a deterministic synthetic fixture. It illustrates the grid, paired views and statistics placement. The fixture contains 49 tiles with 47 STR, one NORM and one MUC assignments. These are prescribed test data, not predictions on the coloured source pattern. Figure 4.3 provides separate actual-image Windows observations, including tile numbers and original-crop inspection.
- 4.2.2 Classification results and spatial inspection；段落 4；PDF [62]／印刷页 ['52']。
  - Figure 4.3(a–b) shows Single image and Tiled analysis for the same named 3552 × 3536 raster. The Single image result selects STR with 42.6% confidence. The tiled view reports 40 STR, five MUC, one MUS and three NORM tiles, with estimated area coverage 82.06%, 9.98%, 1.89% and 6.07%, respectively. Its 512-pixel source crops use RGB/raw255 and OpenCV linear resize to 224 × 224. Panel (c), from a separate analysis, identifies tile 31 as NORM at 59.47%, with rectangle [1024, 2048, 1536, 2560]. These observations demonstrate presentation and crop inspection; they do not supply ground-truth tile accuracy. The classification captures deliberately select OpenCV INTER_LINEAR, corresponding to the training script’s linear-resize choice; Pillow bilinear remains the application default and the backend of the independent evaluation in Section 4.2.6. Matching this resize choice does not establish physical-scale or stain matching.
- 4.2.2 Classification results and spatial inspection；段落 8；PDF [63]／印刷页 ['53']。
  - The 3552 × 3536 breast-cancer raster in Figure 4.3 produces 49 crops at a 512 × 512 setting, with smaller right and bottom edges. Controlled tests verify unique source crops, RGB/raw255 preparation, class order, edge handling and area conservation. Applying the CRC-trained classifier to this image demonstrates the interface and sampling workflow; breast-tissue classification accuracy has not been evaluated. Its unknown physical resolution also prevents training-scale matching. The CRC patch results in Section 4.2.6 do not measure this tiled map.

## Figure 4.4

Figure 4.4. Breast-cancer raster comparison, 31 October 2026, record #86: 3552 × 3536 source, linked Fit views at 15.7% and opacity 30%, using the supervisor-provided UPerNet model. The pixel-coverage legend is scrollable. Source: author’s Windows capture.
标题所在小节：4.2.3 Segmentation results；PDF 页：[65]。

- 4.2.3 Segmentation results；段落 2；PDF [64]／印刷页 ['54']。
  - The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 shows Windows record #86 dated 31 October, with the supervisor-provided UPerNet model and aligned source/overlay views. The visible statistics include 3,108,889 cancerous-epithelium pixels and 7,998,755 stroma pixels; the scrollable legend continues below the visible rows. Separately, the actual report/JSON records imagenet preprocessing, a 1000-pixel source window, stride 512, network input 224 and CPU execution. Its nine counts sum to 12,559,872 pixels, equal to 3552 × 3536. The report and new screen are different analysis records; agreement of their counts is not an accuracy measurement. Annotated-mask evaluation remains unavailable (Section 4.5.3).

## Figure 4.5

Figure 4.5. Windows parameter isolation: (a) History modes; (b) completed Re-run #83 with recorded 512 × 512/49 tiles and its parameter strip, despite current 256 × 256/196-tile defaults; (c) separate ordinary Run #77 with 256 × 256/196 tiles. Source: author’s Windows captures.
标题所在小节：4.2.4 History, rerun and export；PDF 页：[67]。

- 4.2.4 History, rerun and export；段落 1；PDF [65]／印刷页 ['55']。
  - History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 illustrates Windows history and recorded rerun.
- 4.2.4 History, rerun and export；段落 2；PDF [65]／印刷页 ['55']。
  - Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The author identifies the follow-up operation as a recorded Re-run: its completed record #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. The second capture confirms 224 × 224 network input, raw255 and OpenCV linear resize. The Done indicator, restored Run Inference button and new session record distinguish this pair from the earlier busy 49/49 capture. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the actual report and companion-file listing.

## Figure 4.6

Figure 4.6. Pages 1–2 of the same actual Standard segmentation PDF and its Windows file listing. Record #65: analysis 25 October 2026, 19:45:38; export 30 October 2026. The listed PNG source file was not supplied. Source: author’s PDF, rendered faithfully, and file-list capture.
标题所在小节：4.2.4 History, rerun and export；PDF 页：[68]。

- 4.2.4 History, rerun and export；段落 2；PDF [65]／印刷页 ['55']。
  - Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The author identifies the follow-up operation as a recorded Re-run: its completed record #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. The second capture confirms 224 × 224 network input, raw255 and OpenCV linear resize. The Done indicator, restored Run Inference button and new session record distinguish this pair from the earlier busy 49/49 capture. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the actual report and companion-file listing.
- 4.2.4 History, rerun and export；段落 4；PDF [66]／印刷页 ['56']。
  - Figure 4.6(a–b) reproduces pages 1 and 2 of the same supplied two-page PDF. The 875,021-byte Standard report identifies record #65, analysis time 25 October 2026 at 19:45:38 and export time 30 October 2026 at 14:43:26 +08:00. Its software version is 1.0, with CPU execution and the recorded source dimensions and segmentation parameters. Its export-time model hash matches the UPerNet resource identity in Appendix E; the report distinguishes that hash from historical inference identity. The companion JSON agrees with its timestamp and all nine pixel counts. Panel (c) lists a PNG whose source file was not uploaded.
- C.1 Evaluated source and evidence；段落 3；PDF [109]／印刷页 ['99']。
  - The image collection includes replacement overview record #84 and segmentation record #86 dated 31 October 2026, alongside earlier classification inspection, History, recorded Re-run and default demonstrations. Figure 4.6 uses two pages of one actual report, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. The capture index records individual files, displayed analysis dates, record IDs and available source identities. Screenshot versions are not inferred from record dates or interface appearance; the 548-case automated result remains specifically bound to d9fb8e5.

## Figure 4.7

Figure 4.7. Implemented Guide & Support page with persistent Contents navigation and numbered guidance. Source: author’s Qt-simulated development capture; this is interface evidence.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[69]。

- 4.2.5 Settings, cancellation and interface polish；段落 1；PDF [68]／印刷页 ['58']。
  - Settings includes Appearance, Preferences, Models, Guide & Support, System Information and About. Model defaults are independent per task and require validation. Preferences applies the classification mode immediately while retaining a separate startup default; closed dropdowns scroll the page instead of changing selections accidentally. Guide navigation remains visible and follows the current reading section, while the system-information copy confirmation expires rather than becoming permanent content. Figure 4.7 shows the implemented Guide & Support page and its navigation.

## Figure 4.8

Figure 4.8. English history-calendar popup with a simulated Chinese default locale. Source: author’s Qt-simulated development capture; the selected date is test input.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[69]。

- 4.2.5 Settings, cancellation and interface polish；段落 2；PDF [69]／印刷页 ['59']。
  - The English calendar in Figure 4.8 was captured after setting the default locale to Chinese in a controlled run. The corresponding test opens each popup, checks English month/day labels, selects a date and verifies the unchanged date value and query signal. This is stronger evidence than merely setting a locale property without opening the widget.

## Figure 4.9

Figure 4.9. Independent cancellation-related views: (a) classification at 228/400 with Session record #79; (b) cancellation acknowledgement with record #78 and Segmentation selected. These are not one continuous sequence. Panels (c–d) show test-model default configuration and restored built-in default. Source: author’s Windows captures.
标题所在小节：4.2.5 Settings, cancellation and interface polish；PDF 页：[71]。

- 4.2.5 Settings, cancellation and interface polish；段落 3；PDF [70]／印刷页 ['60']。
  - Figure 4.9(a–b) contains two independent cancellation-related observations. Panel (a) shows classification progress at 228/400 while the Session panel displays completed record #79 at 14:32:35. Panel (b) shows “Inference cancelled. Previous completed results are unchanged,” with record #78 at 14:30:40; Segmentation is selected in the input controls while the retained result is classification. These are not a before/after pair from one demonstrated operation and do not establish database cleanup. Panels (c–d) demonstrate default configuration with the explicitly identified test model dummy_segmentation.pt and restoration of the built-in segmentation default; they do not measure trained-model predictive performance.
- C.1 Evaluated source and evidence；段落 3；PDF [109]／印刷页 ['99']。
  - The image collection includes replacement overview record #84 and segmentation record #86 dated 31 October 2026, alongside earlier classification inspection, History, recorded Re-run and default demonstrations. Figure 4.6 uses two pages of one actual report, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. The capture index records individual files, displayed analysis dates, record IDs and available source identities. Screenshot versions are not inferred from record dates or interface appearance; the 548-case automated result remains specifically bound to d9fb8e5.

## Figure 4.10

Figure 4.10. Classification training and validation over 30 recorded epochs, with the selected epoch 26 marked. Source: author’s plot of experiments/crc-dn21-seed42-10ep/metrics.csv.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[72]。

- 4.2.6 Classification training and test results；段落 2；PDF [72]／印刷页 ['62']。
  - The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

## Table 4.1

Table 4.1. Classification evaluation summary
标题所在小节：4.2.6 Classification training and test results；PDF 页：[73]。

- 4.2.6 Classification training and test results；段落 3；PDF [73]／印刷页 ['63']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Table 4.2

Table 4.2. Class-wise classification performance on 7,180 test images
标题所在小节：4.2.6 Classification training and test results；PDF 页：[73]。

- 4.2.6 Classification training and test results；段落 3；PDF [73]／印刷页 ['63']。
  - Table 4.1 summarises the classifier’s training selection and external-test evaluation; Table 4.2 reports precision, recall and F1 for each class.

## Figure 4.11

Figure 4.11. Nine-class confusion matrix for CRC-VAL-HE-7K. Source: the classification experiment’s saved matrix; the Windows default-Pillow predictions independently reproduce every count. Rows are true labels and columns predicted labels.
标题所在小节：4.2.6 Classification training and test results；PDF 页：[74]。

- 4.2.6 Classification training and test results；段落 6；PDF [74]／印刷页 ['64']。
  - Figure 4.11 shows the external-test confusion matrix, allowing the class-wise error patterns to be examined alongside the aggregate metrics.

## Table 4.3

Table 4.3. Complete Windows automated execution for the evaluated source.
标题所在小节：4.3.1 Recorded automated results；PDF 页：[77]。

- 3.6.5 Testing Summary；段落 2；PDF [54]／印刷页 ['44']。
  - On 2 November 2026, revision d9fb8e5 completed the full native Windows Qt suite: 548 passed, 0 failed, 0 errors and 0 skipped, with 16 warnings in 224.89 seconds (exit 0). Table 4.3 presents this current-source result. Appendix C retains earlier Windows invocations with their original dates and versions; they are not added to the current total.
- 4.3.1 Recorded automated results；段落 1；PDF [76]／印刷页 ['66']。
  - On 2 November 2026, revision d9fb8e5 completed all 548 collected tests on native Windows Qt: 548 passed, 0 failed, 0 errors and 0 skipped. The pytest summary reports 16 warnings and 224.89 seconds, with exit code 0. Table 4.3 presents this source-matched result. The recorded commit and source/resource manifests agree before and after the execution.

## Table 4.4

Table 4.4. Windows hardware record (19 October) and test runtime (2 November).
标题所在小节：4.3.1 Recorded automated results；PDF 页：[77]。

- 3.6.1 Development Testing；段落 4；PDF [52]／印刷页 ['42']。
  - The 2 November Windows test record uses Python 3.10.22, pytest 9.1.1, pluggy 1.6.0, PyQt5 5.15.11, Qt runtime/compiled version 5.15.2, anyio 4.15.1 and pytest-qt 4.5.0. PyTorch 2.1.2+cpu reported CUDA unavailable and 24 CPU threads. Table 4.4 gives the host hardware and separates its installed GPU from the actual computation device.
- 4.3.4 Runtime and deployment verification status；段落 1；PDF [82]／印刷页 ['72']。
  - Table 4.4 documents the Windows hardware and CPU runtime. A dedicated repeated latency or memory benchmark was not conducted. Test-suite duration and the classifier evaluation-loop duration are not used as inference-performance measurements; no quantitative speed or memory-efficiency claim is made.

## Figure 4.12

Figure 4.12. Complete Windows pytest report, 2 November 2026, revision d9fb8e5. Source: the recorded full-suite log; selected text is reproduced with omissions marked.
标题所在小节：4.3.1 Recorded automated results；PDF 页：[78]。

- 4.3.1 Recorded automated results；段落 6；PDF [78]／印刷页 ['68']。
  - Figure 4.12 reproduces selected lines from the completed 2 November Windows pytest log at revision d9fb8e5; it is a test-log excerpt rather than an application screenshot.

## Table 4.5

Table 4.5. Implementation challenges, corrections and supporting evidence.
标题所在小节：4.3.2 Challenges, resolutions and evidence；PDF 页：[79]。

- 4.3.1 Recorded automated results；段落 8；PDF [78]／印刷页 ['68']。
  - Earlier Windows iterations exposed missing training prerequisites, thread-lifetime faults, settings leakage and platform-dependent layout/path assumptions. The 2 November execution additionally exercises the correction for window-state event reentrancy and explicit Qt enter/move/hover input in the scrollbar tests. Revision d9fb8e5 completed all 548 cases. Table 4.5 summarises the resolutions; Appendix C retains the dated earlier outcomes and source differences.

## Table 4.6

Table 4.6. Participant profile and reported study conditions
标题所在小节：4.4.1 Participant Demographics；PDF 页：[83]。

- 4.4.1 Participant Demographics；段落 1；PDF [83]／印刷页 ['73']。
  - Table 4.6 summarises the ten consenting respondents, their reported backgrounds and study display conditions. All supplied SUS forms are complete, with no participant excluded after the confirmed consent correction.

## Table 4.7

Table 4.7. SUS distribution and participant-task outcomes
标题所在小节：4.4.2 Quantitative Results；PDF 页：[84]。

- 4.4.2 Quantitative Results；段落 1；PDF [84]／印刷页 ['74']。
  - Table 4.7 summarises SUS and task outcomes. The mean SUS is 74.50, sample standard deviation 10.66, median 72.50 and range 55.00–90.00. The inclusive-interpolation IQR is 11.88. These values describe perceived usability, not a task-success percentage.

## Table 4.8

Table 4.8. Feature ratings with response-specific denominators
标题所在小节：4.4.3 Feature Usage and Ratings；PDF 页：[85]。

- 4.4.3 Feature Usage and Ratings；段落 1；PDF [85]／印刷页 ['75']。
  - Table 4.8 reports feature-specific ratings on the supplied 1–5 ease/clarity scale. Each mean is calculated from numerical responses only; blank ratings are retained as missing rather than converted into low scores.

## Table 4.9

Table 4.9. Objective achievement and outstanding evidence
标题所在小节：4.5.1 Achievement of Research Objectives；PDF 页：[87]。

- 4.5.1 Achievement of Research Objectives；段落 1；PDF [87]／印刷页 ['77']。
  - Table 4.9 maps each research objective to the implemented outcome and the evidence available for assessing its achievement.

## Table A.1

Table A.1. Original CP1 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[98]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.2

Table A.2. Original CP2 planning baseline, retained from the submitted proposal
标题所在小节：A.1 Proposal baseline；PDF 页：[100]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table A.3

Table A.3. Evidence-based milestone status
标题所在小节：A.2 Implementation and outstanding milestones；PDF 页：[103]。

- A.1 Proposal baseline；段落 1；PDF [98]／印刷页 ['88']。
  - Table A.1 retains the CP1 planning baseline, and Table A.2 retains the original CP2 plan. References there to ResNet-50, ImageNet preprocessing, a >94% target, coverage targets and executable packaging describe the proposal, not the final implementation or achieved results. Table A.3 gives the updated status; Chapters 3 and 4 report the implemented DenseNet/raw255 contract and measured outcomes.

## Table B.1

Table B.1. UAT tasks and success criteria
标题所在小节：B.3 Standard task script and observation rules；PDF 页：[106]。

- 3.6.4 User Acceptance Testing (UAT)；段落 2；PDF [54]／印刷页 ['44']。
  - Table B.1 defines ten tasks covering single-image classification, tile configuration and interpretation, comparison, segmentation, history, recorded rerun, export, cancellation and defaults. Task outcomes come from the response workbook; Appendix B reproduces the task instructions and success criteria.
- B.3 Standard task script and observation rules；段落 1；PDF [106]／印刷页 ['96']。
  - Table B.1 gives the task instructions and success criteria used to interpret the supplied T01–T10 outcome records. Instructions describe the intended protocol; a missing execution detail is not reconstructed from the protocol alone.

## Table C.1

Table C.1. Principal evidence sources
标题所在小节：C.1 Evaluated source and evidence；PDF 页：[109]。

- C.1 Evaluated source and evidence；段落 1；PDF [109]／印刷页 ['99']。
  - The evaluated application source is commit d9fb8e5e4ef43214ed140a0b3c81d18dd4fc7592. Its complete native Windows Qt execution on 2 November 2026 passed all 548 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.

## Table C.2

Table C.2. Windows automated execution history.
标题所在小节：C.2 Evidence interpretation；PDF 页：[112]。

- C.1 Evaluated source and evidence；段落 1；PDF [109]／印刷页 ['99']。
  - The evaluated application source is commit d9fb8e5e4ef43214ed140a0b3c81d18dd4fc7592. Its complete native Windows Qt execution on 2 November 2026 passed all 548 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.
- C.2 Evidence interpretation；段落 1；PDF [111]／印刷页 ['101']。
  - Table C.2 distinguishes the complete 2 November execution at d9fb8e5, with 548 distinct passing cases, from earlier Windows runs. The 27 October run at 3a935ef passed 508 cases. The earlier 8c4830c run contained 505 distinct test identities, with 17 failures and three teardown errors attached to failing cases; its JUnit aggregate contained 508 reports. The 131-case subset is an independent execution and is not added to any complete-suite total.

## Table D.1

Table D.1. Windows manual acceptance criteria and author-declared outcomes
标题所在小节：D.1 Native acceptance record；PDF 页：[114]。

- D.1 Native acceptance record；段落 1；PDF [113]／印刷页 ['103']。
  - Table D.1 presents the procedures, acceptance criteria and developer-reported Pass outcomes for W01–W15. The written declaration was received on 1 November 2026. Execution dates, source revision, display scale and detailed case observations were not included in that record; it is therefore reported separately from the dated automated Windows execution.
