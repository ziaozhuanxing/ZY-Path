### Cover

Before: Semester: [TO CONFIRM]

After: Semester: 8

Reason: Use the semester provided by the author.

### Cover

Before: Date: [TO CONFIRM]

After: Date: 5 November 2026

Reason: Use the submission date provided by the author; do not change file-creation history to this future date.

### Abstract

Before: ZY-Path is a local desktop application that makes supported histopathology models accessible through a graphical workflow for students, educators and researchers. Built with PyQt5, PyTorch and SQLite, it combines CPU-based Single image and Tiled analysis classification, supervisor-provided segmentation, linked image inspection, recorded history, cooperative cancellation and PNG/PDF export. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native-sized CRC-VAL-HE-7K patches through the default Pillow core; revision d9fb8e5 passed all 548 automated cases on Windows, and all 15 developer-led manual acceptance cases were reported as passed. Ten participant records produced a mean System Usability Scale score of 74.50 (sample SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance, with interpretation and recorded-rerun tasks identifying areas for improvement. The project contributes an integrated, model-aware educational and research workflow; broader predictive generalisation, dedicated performance benchmarking and clean-machine packaged deployment remain outside the completed evaluation.

After: ZY-Path is a local desktop application that makes supported histopathology models accessible through a graphical workflow for students, educators and researchers. Built with PyQt5, PyTorch and SQLite, it combines CPU-based Single image and Tiled analysis classification, supervisor-provided segmentation, linked image inspection, recorded history, cooperative cancellation and PNG/PDF export. The classifier achieved 90.68% accuracy and 88.59% macro-F1 on 7,180 native-sized CRC-VAL-HE-7K patches through the default Pillow core; 548 automated Windows cases passed at revision d9fb8e5, followed by 15 manual acceptance cases at the final revision fbe152a. Ten participant records produced a mean System Usability Scale score of 74.50 (sample SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance, with interpretation and recorded-rerun tasks identifying areas for improvement. The project contributes an integrated educational and research workflow; broader predictive generalisation, dedicated performance benchmarking and clean-machine packaged deployment remain outside the completed evaluation.

Reason: Report the dated manual result while preserving the source identity of the automated result and all existing model/UAT values.

### 3.1

Before: The implementation evaluated in this thesis is revision d9fb8e5. Its complete Windows execution on 2 November 2026 passed all 548 automated cases. Classification methods are documented by the training code provided by my supervisor, my training/validation records and corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the evaluated source and the earlier Windows records.

After: The final implementation described in this thesis is revision fbe152a. I completed its 15-case Windows manual acceptance on 2 November 2026. The preceding revision d9fb8e5 supplies the complete 548-case automated Windows regression from the same date. Classification methods are documented by the training code provided by my supervisor, my training/validation records and corresponding test outputs; the segmentation pathway follows the model and reference notebook provided by my supervisor. Appendix C identifies these source states and their supporting records.

Reason: Identify final-source manual acceptance and preceding-source automated regression explicitly.

### 3.2.2

Before: Windows layout acceptance concerns access to essential controls, resizing, restoration and comparison-view adaptation. Appendix D records the author’s written confirmation of the 15 manual cases; the declaration does not specify execution-time screen geometry, display scale or source revision. Dedicated timing and memory benchmarking is outside the completed evaluation.

After: Windows layout acceptance concerns access to essential controls, resizing, restoration and comparison-view adaptation. I checked the 15 cases in Appendix D on Windows 11 Home Chinese Edition, version 22H2 (OS Build 22621.3593), at 175% display scaling and a 2560 × 1600 display resolution. Dedicated timing and memory benchmarking is outside the completed evaluation.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 3.3.1

Before: Validation executes a float32 RGB probe of shape (1, 3, 224, 224), extracts a tensor or an object's logits field, rejects non-finite values and identifies classification output (1, C) or segmentation output (1, C, H, W). It checks executable structure, not training quality, authenticity, calibration or diagnostic fitness. Models with special input requirements, unsupported dictionaries or missing custom Python classes may still be incompatible even when their file extension is allowed.

After: Validation executes a float32 RGB probe of shape (1, 3, 224, 224), extracts a tensor or an object’s logits field, rejects non-finite values and identifies classification output (1, C) or segmentation output (1, C, H, W). The final revision requires at least two classification logits and checks declared label count against output-channel count during selection, default-model validation and inference. Single-logit binary classifiers are rejected because their sigmoid/threshold semantics are not implemented. These checks establish executable compatibility; predictive and model-trust limits are discussed in Section 4.5.3.

Reason: Describe the final shared compatibility validator and reject unsupported single-logit softmax semantics accurately.

### 3.3.4

Before: Ordinary Run Inference captures the current tile dimensions and resize backend when inference starts. History restoration leaves those defaults intact, while Re-run uses its saved parameter snapshot. Changes made during inference apply to the next run. Regression tests check crop geometry and parameter isolation across restoration, rerun, input changes and clearing the view.

After: Ordinary Run Inference captures the current tile dimensions and resize backend when inference starts. History restoration leaves those defaults intact, while Re-run uses its saved parameter snapshot. Changes made during inference apply to the next run. Regression tests check crop geometry and parameter isolation across restoration, rerun, input changes and clearing the view. Before a tiled run, the coordinator and worker check the crop count against a 10,000-tile limit; the predictor and stored tile-table viewer enforce the same limit. Excessive requests produce an instruction to increase crop dimensions or use a smaller image, without silently changing the selected geometry.

Reason: Document final-source workload protection without presenting the operational limit as a biological training-scale recommendation.

### 3.3.8

Before: UTC timestamps are stored and converted for local display/filtering. A date range is interpreted as inclusive local days and converted to UTC query boundaries. Both date selectors and popup calendars explicitly use English, while the date format remains yyyy-MM-dd. Searches cover image/model names and do not perform visual image-similarity retrieval.

After: UTC timestamps are stored and converted for local display/filtering. A date range is interpreted as inclusive local days, preserving the final microsecond at 23:59:59.999999 when converting the end bound to UTC. Initial search and filter-preserving reload use the same boundary. Both date selectors and popup calendars explicitly use English, while the date format remains yyyy-MM-dd. Searches cover image/model names and do not perform visual image-similarity retrieval.

Reason: Document the corrected inclusive date boundary.

### 3.3.8

Before: Restoring a record reads its saved artifacts and metadata without rerunning the model. Rerun is a separate operation that selects exactly one recorded analysis and uses its model, source image, task, mode, tile dimensions and resize backend. Missing files produce a clear message rather than an unannounced substitution. Current model defaults and preferences do not relabel an existing record. Deletion requires confirmation and removes selected records plus recognised app-owned result artifacts, not the original user image or model.

After: Restoring a record reads its saved artifacts and metadata without rerunning the model. Rerun selects exactly one recorded analysis and uses its model, source image, task, mode, tile dimensions and resize backend. Missing files produce a clear message rather than an unannounced substitution. Current defaults do not relabel an existing record. Confirmed deletion removes selected records and their managed result files, including JSON sidecars, while preserving original inputs, surviving records’ referenced files and files selected for an active operation.

Reason: Describe complete managed-artifact cleanup and reference protection.

### 3.3.8

Before: Saving is not a distributed transaction across image files and SQLite. Artifacts are written through the application coordinator and the record is inserted when saving succeeds; failures are reported. Filesystem errors can still leave incomplete or orphaned artifacts, and backups are not automatic. This is a maintenance/reliability boundary rather than an implemented guarantee of atomic recovery across all resources.

After: The coordinator renders and saves all required result artifacts before inserting a completed history row and replacing the previous view. A handled file-write or database-insert failure removes the newly created partial files, reports the error and retains the preceding completed result. Existing-file collisions do not overwrite prior data. File writes and SQLite are nevertheless separate storage systems: an abrupt process or power failure can still interrupt cleanup, so this is not a distributed filesystem/database transaction.

Reason: Replace the old save-failure description with final-source persistence behaviour while retaining the actual crash-consistency boundary.

### 3.6.3

Before: Developer-led manual acceptance covered the 15 Windows cases in Appendix D. All were recorded as passed in the written acceptance declaration. The cases supplement automated testing with checks of the application’s native interaction workflows.

After: On 2 November 2026, I performed W01–W15 on revision fbe152a using the real-file workflows and expected outcomes listed in Appendix D. All 15 cases met their criteria. The environment was Windows 11 Home Chinese Edition 22H2, OS Build 22621.3593, with 175% display scaling and a 2560 × 1600 display resolution. Table D.1 records the observed behaviour. Display acceptance is limited to the tested 175% setting; other scaling settings and multi-monitor transitions were not part of this manual record.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 3.6.6

Before: Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the completed native Windows automated checks, recorded classifier evaluation, author-declared manual acceptance, completed formative UAT and further model studies.

After: Table 3.6 connects objectives and requirements to source modules and named tests. Its statuses distinguish the 548-case automated Windows regression at d9fb8e5, manual acceptance at fbe152a, recorded classifier evaluation, formative UAT and further model studies.

Reason: Keep requirement outcomes aligned with their actual software revision and evaluation method.

### Table 3.6 source

Before: Source: the complete 2 November Windows log/XML at revision d9fb8e5 and the named project tests. Executable cases in this matrix were included in the 548-case invocation. Recorded classifier evaluation, source-inspection findings, manual tasks and UAT have their own evidence scope.

After: Source: the complete 2 November Windows automated log/XML at d9fb8e5 and named project tests; the 2 November manual record at fbe152a in Appendix D; classifier evaluation and participant records where stated.

Reason: Identify both evidence streams without attributing the earlier complete suite to the final source.

### 3.8

Before: The methodology combines separate task contracts, explicit crop geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation includes source-matched Windows automated testing, classifier test records, the author’s manual acceptance declaration and ten participant response records. These streams answer technical, predictive and usability questions separately.

After: The methodology combines separate task contracts, explicit crop geometry, spatial inspection, recorded rerun and cooperative cancellation. Evaluation includes source-matched Windows automated regression, my dated final-source manual acceptance, classifier test records and ten participant response records. These streams address technical, predictive and usability questions separately.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 4.1

Before: This chapter reports the implemented system and the evaluated source state identified in Appendix C. The complete 548-case Windows result applies to revision d9fb8e5. Interface figures illustrate separate recorded analyses; a displayed analysis timestamp identifies a run, not the source revision of the software displaying it. Section 4.2 presents workflows and classifier evaluation, Section 4.3 reports software tests and native observations, and Section 4.4 reports the ten-participant UAT results.

After: This chapter reports the implemented system and the source states identified in Appendix C. The complete 548-case automated Windows result applies to d9fb8e5; the 15-case manual acceptance applies to the final revision fbe152a. Interface figures illustrate separate recorded analyses from 30–31 October and do not establish their capture-time source revisions. Section 4.2 presents workflows and classifier evaluation, Section 4.3 reports software tests and native observations, and Section 4.4 reports the ten-participant UAT results.

Reason: Introduce the complete final evaluation without inferring screenshot versions.

### 4.2.1

Before: The implementation includes numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run reads current preferences independently of restored or rerun records. Their execution-evidence scope is defined in Section 4.3.1.

After: The implementation includes numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run reads current preferences independently of restored or rerun records. Their execution-evidence scope is defined in Section 4.3.1. The final source also strengthens model/label compatibility checks, failure-safe result persistence, managed-artifact cleanup, date-boundary handling and tiled-workload preflight (Sections 3.3.1, 3.3.4 and 3.3.8).

Reason: Include the final implemented changes described by the actual software commit.

### 4.3.3

Before: The 2 November native Windows suite passed programmatic maximise/restore, saved-geometry, comparison/grid, compact-panel, navigation, metadata wrapping, task-progress, model-source and tile-preference cases. Formal real-image manual acceptance in Appendix D remains distinct from these automated inputs and assertions.

After: The 2 November automated Windows suite at d9fb8e5 passed programmatic maximise/restore, saved-geometry, comparison/grid, compact-panel, navigation, metadata wrapping, task-progress, model-source and tile-preference cases. I subsequently checked the final revision fbe152a through the 15 real-file manual workflows in Appendix D, at 175% scaling and 2560 × 1600 resolution.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 4.3.3

Before: The Windows screenshots document representative image observations of classification, segmentation, linked display, history/default isolation, export and cancellation. Figures 4.1, 4.3 and 4.4 retain their displayed record IDs. In a separate written confirmation, the author reports that all 15 Appendix D manual cases passed. These developer-led outcomes and the dated automated execution provide separate forms of software verification.

After: All 15 manual cases met their criteria. I observed window restoration and responsive comparison, aligned crop inspection, mouse/keyboard toggle behaviour, English date filtering, recorded-parameter rerun, safe cancellation and close, readable settings, report export, task-specific model defaults, missing-file handling and clearing without deleting saved data. The outcomes supplement the earlier automated regression. Figures 4.1, 4.3 and 4.4 retain their own record IDs and dates; the figures are not a continuous recording of this manual session.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 4.9 source

Before: Source: implementation and automated test records, classifier evaluation, the author’s manual acceptance declaration and the corrected participant response dataset.

After: Source: implementation and dated automated/manual Windows records, classifier evaluation and the corrected participant response dataset.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 4.5.1

Before: The implementation makes task/mode, source crop versus network input, resize backend and coverage semantics visible. Current refinements strengthen numbered inspection, navigation, export and the separation of new-run preferences from recorded rerun settings. The patch evaluation supplies a measured classifier result; the completed 548-case Windows execution supplies verification for the evaluated source.

After: The implementation makes task/mode, source crop versus network input, resize backend and coverage semantics visible. Numbered inspection, navigation, export and separation of current preferences from recorded rerun support this workflow. The patch evaluation supplies a classifier result, while the dated automated Windows regression and final-source manual acceptance provide complementary software verification.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 4.5.3

Before: The 548-case Windows suite verifies revision d9fb8e5 under its recorded runtime, and the author separately declares all 15 manual cases passed. UAT adds ten participant records but also a blocked workload and two critical-error entries, so the manual declaration is not extended into a universal reliability claim. Participant usability and automated software verification address different evaluation questions. The small mixed-background sample and absence of a comparator limit generalisation and causal conclusions. Assistive-technology compliance remains unassessed.

After: The 548-case automated Windows result applies to d9fb8e5; my 15-case manual acceptance applies to fbe152a on one Windows computer at 175% scaling. The manual result does not establish behaviour at every display setting or replace a complete automated execution of the later revision. UAT adds ten participant records, including a blocked workload and two critical-error entries. The small mixed-background sample and absence of a comparator limit generalisation and causal conclusions. Assistive-technology compliance remains unassessed.

Reason: Consolidate the final-version, single-display and study-design limitations without repeating obsolete missing-record statements.

### 4.6

Before: ZY-Path implements model-aware inference, spatial inspection and record continuity. The documented classifier result is 90.68% accuracy and 88.59% macro-F1; revision d9fb8e5 passed the complete 548-case Windows suite, and all 15 developer-led manual cases were reported as passed. The ten-response UAT yields mean SUS 74.50 (SD 10.66), with 72 independent and 22 assisted completions among 96 evaluable attempts. Interpretation, recorded rerun and long-workload reliability remain priorities; dedicated efficiency and packaged-deployment validation are outside the completed evaluation.

After: ZY-Path implements model-aware inference, spatial inspection and record continuity. The documented classifier result is 90.68% accuracy and 88.59% macro-F1; automated Windows regression passed 548 cases at d9fb8e5, followed by 15 manual acceptance cases at fbe152a. The ten-response UAT yields mean SUS 74.50 (SD 10.66), with 72 independent and 22 assisted completions among 96 evaluable attempts. Interpretation, recorded rerun and long-workload reliability remain priorities; dedicated efficiency and packaged-deployment validation are outside the completed evaluation.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### 5.1

Before: The classifier evaluation produced 6,511 correct labels from 7,180 native-sized external-test patches, equivalent to 90.68% accuracy and 88.59% macro-F1. Software verification remains separate: revision d9fb8e5 passed all 548 Windows automated cases, and 15 developer-led manual cases were reported as passed. In the ten-participant usability dataset, mean SUS is 74.50 (SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance. These complementary results support the implemented educational/research workflow while retaining the predictive, study-design and deployment limits in Section 4.5.3.

After: The classifier evaluation produced 6,511 correct labels from 7,180 native-sized external-test patches, equivalent to 90.68% accuracy and 88.59% macro-F1. Software verification comprises the complete 548-case Windows automated regression at d9fb8e5 and my 15-case manual acceptance of the final source fbe152a at 175% scaling and 2560 × 1600 resolution. In the ten-participant usability dataset, mean SUS is 74.50 (SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance. These results support the implemented educational/research workflow within the predictive, study-design and deployment limits in Section 4.5.3.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix A.3

Before: The dated Windows automated record, representative images, exported PDF/JSON, 15-case manual declaration and corrected ten-response UAT dataset document the completed evaluation. Further runtime or packaged-deployment claims require the corresponding execution records.

After: The dated Windows automated regression, final-source manual record, representative images, exported PDF/JSON and corrected ten-response UAT dataset document the completed evaluation. Further runtime or packaged-deployment claims require their own execution records.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix C.1

Before: The evaluated application source is commit d9fb8e5e4ef43214ed140a0b3c81d18dd4fc7592. Its complete native Windows Qt execution on 2 November 2026 passed all 548 cases. Source and resource manifests were unchanged through execution, and Git status was clean before and after testing. Table C.1 identifies the supporting materials; Table C.2 retains the earlier Windows outcomes with their own source versions.

After: The final application source is fbe152a5e4bbe14ad6dcc682468ad571d2efd33c, assessed by the 15 manual Windows cases in Appendix D. The complete 548-case automated Windows execution on 2 November 2026 applies to its predecessor d9fb8e5e4ef43214ed140a0b3c81d18dd4fc7592; its source/resource manifests were unchanged through execution and Git status was clean before and after that test. The final source changes are preserved in Final_Source_Changes.diff. Table C.1 identifies the materials and Table C.2 retains the dated automated runs.

Reason: Keep both final source and automated-regression baseline reproducible.

### Appendix C.1

Before: The image collection includes replacement overview record #84 and segmentation record #86 dated 31 October 2026, alongside earlier classification inspection, History, recorded Re-run and default demonstrations. Figure 4.6 uses two pages of one actual report, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. The capture index records individual files, displayed analysis dates, record IDs and available source identities. Screenshot versions are not inferred from record dates or interface appearance; the 548-case automated result remains specifically bound to d9fb8e5.

After: The interface captures date from 30–31 October 2026, including overview record #84 and segmentation record #86, classification inspection, History, recorded Re-run and defaults. Figure 4.6 uses one actual PDF, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. Capture-time commits were not recorded. These interface examples therefore retain their dates without being attributed to d9fb8e5 or fbe152a; their source identities remain separate from the dated automated and manual records.

Reason: Correct capture date range and avoid attaching October captures to November commits.

### Appendix D.1

Before: Table D.1 presents the procedures, acceptance criteria and developer-reported Pass outcomes for W01–W15. The written declaration was received on 1 November 2026. Execution dates, source revision, display scale and detailed case observations were not included in that record; it is therefore reported separately from the dated automated Windows execution.

After: On 2 November 2026, I performed the 15 Windows checks in Table D.1 on revision fbe152a5e4bbe14ad6dcc682468ad571d2efd33c; all met their criteria. I used Windows 11 Home Chinese Edition 22H2 (OS Build 22621.3593), a 2560 × 1600 display and 175% scaling. Environment information was recorded at 21:59:01 UTC+08:00; this is the environment-capture time, not a timed start/end interval for the cases. Git status was clean when the revision was recorded. The observations below document my confirmation of the checklist outcomes; screenshots or a continuous recording were not required. W09 covers 175% scaling only.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 caption

Before: Table D.1. Windows manual acceptance criteria and author-declared outcomes.

After: Table D.1. Windows manual acceptance procedures and observed outcomes.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 source

Before: Source: author’s Windows acceptance protocol and written confirmation received on 1 November 2026. W01–W15 are declared Pass; no new automated execution, timing measurement or case-level observation is inferred.

After: Source: my Windows manual checks, environment record and confirmation of W01–W15 on 2 November 2026. Full case records accompany the thesis in Windows_Manual_Acceptance_Record.csv and .xlsx; the automated test log remains a separate record.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix D.2

Before: Figures 1.1 and 4.1, 4.3–4.6 and 4.9 contain the dataset image and Windows observations, including replacement records #84/#86, completed Re-run #83 and authentic report pages. Figures 4.2, 4.7 and 4.8 retain their labelled development captures. The two cancellation-related views remain independent observations. The W01–W15 acceptance outcomes derive from the separate author declaration, not from treating these figures as a continuous test sequence.

After: Figures 1.1 and 4.1, 4.3–4.6 and 4.9 contain the dataset image and dated Windows examples, including records #84/#86, completed Re-run #83 and the actual PDF pages. Figures 4.2, 4.7 and 4.8 retain their labelled development captures. The two cancellation-related views remain independent observations. My 2 November acceptance record in Table D.1 supplies the case-level outcomes; the older figures are used to illustrate the interface, not to reconstruct that session. The supporting archive includes the cited logs/XML, source differences, manifests, participant workbook, case records and exported PDF/JSON. The original PNG listed in Figure 4.6 was not available; its content is not claimed from the listing alone.

Reason: Explain the accompanying evidence inventory and retain the actual missing-PNG boundary without an editing placeholder.

### Table 3.6 / row 1, column 3

Before: Image-loading and input-error cases passed in the 548-case Windows suite at d9fb8e5. Relevant manual cases are author-declared Pass (Appendix D).

After: Image-loading and input-error cases passed in the 548-case Windows suite at d9fb8e5. Relevant manual checks passed at fbe152a (Appendix D).

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 5, column 3

Before: Automated segmentation cases passed at d9fb8e5. Figure 4.4 and the actual report illustrate real-weight output; relevant manual cases are author-declared Pass. Ground-truth accuracy remains unevaluated.

After: Automated segmentation cases passed at d9fb8e5. Figure 4.4 and the actual report illustrate real-weight output; relevant manual checks passed at fbe152a. Ground-truth accuracy remains unevaluated.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 6, column 3

Before: Coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed at d9fb8e5. Relevant manual cases are author-declared Pass; the declaration specifies no execution-time display scale.

After: Coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed at d9fb8e5. Relevant manual checks passed at fbe152a; the declaration specifies no execution-time display scale.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 7, column 3

Before: Persistence and artifact cases passed at d9fb8e5. Relevant manual cases are author-declared Pass; no independent new case trace is claimed.

After: Persistence and artifact cases passed at d9fb8e5. Relevant manual checks passed at fbe152a; no independent new case trace is claimed.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 10, column 3

Before: Automated export cases passed at d9fb8e5. Figure 4.6 and the actual PDF/JSON support report content; W10/W15 are author-declared Pass. The listed original PNG was not supplied for independent inspection.

After: Automated export cases passed at d9fb8e5. Figure 4.6 and the actual PDF/JSON support report content; W10/W15 passed at fbe152a. The listed original PNG was not supplied for independent inspection.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 11, column 3

Before: Automated cancellation/lifecycle cases passed at d9fb8e5. W08 is author-declared Pass; Figure 4.9 remains two independent cancellation-related views rather than one continuous test sequence.

After: Automated cancellation/lifecycle cases passed at d9fb8e5. W08 passed at fbe152a; Figure 4.9 remains two independent cancellation-related views rather than one continuous test sequence.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 14, column 3

Before: Clear view, zero-selection and source/history preservation passed in the d9fb8e5 Windows suite. W14 is author-declared Pass; participant UAT remains separate.

After: Clear view, zero-selection and source/history preservation passed in the d9fb8e5 Windows suite. W14 passed at fbe152a; participant UAT remains separate.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / row 15, column 3

Before: Windows geometry and compact-layout cases passed at d9fb8e5. W01–W03/W09 are author-declared Pass; no multi-monitor or assistive-technology coverage is inferred.

After: Windows geometry and compact-layout cases passed at d9fb8e5. W01–W03/W09 passed at fbe152a; no multi-monitor or assistive-technology coverage is inferred.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.7 / row 10, column 3

Before: Keep participant outcomes, model evaluation and author-declared manual acceptance separate; obtain independent segmentation labels and source-matched release records.

After: Keep participant outcomes, model evaluation and dated manual acceptance separate; obtain independent segmentation labels and source-matched release records.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 4.5 / row 5, column 3

Before: Automated small-screen/font and maximise/restore cases passed at d9fb8e5; relevant manual cases are author-declared Pass.

After: Automated small-screen/font and maximise/restore cases passed at d9fb8e5; relevant manual checks passed at fbe152a.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 4.5 / row 15, column 3

Before: Automated Windows navigation and Fit/grid cases passed at d9fb8e5; W03/W04 are separately author-declared Pass.

After: Automated Windows navigation and Fit/grid cases passed at d9fb8e5; W03/W04 passed at fbe152a.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 4.9 / row 3, column 2

Before: Default-Pillow patch evaluation remains 90.68% accuracy / 88.59% macro-F1 on 7,180 patches. Actual Windows captures demonstrate Single image, 49-tile classification and supervisor-model segmentation; tiled accuracy and segmentation ground truth remain unevaluated. Relevant manual cases are author-declared Pass (Appendix D).

After: Default-Pillow patch evaluation remains 90.68% accuracy / 88.59% macro-F1 on 7,180 patches. Actual Windows captures demonstrate Single image, 49-tile classification and supervisor-model segmentation; tiled accuracy and segmentation ground truth remain unevaluated. Relevant manual checks passed at fbe152a (Appendix D).

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 4.9 / row 5, column 2

Before: Automated export cases passed; Figure 4.6 and the exported PDF/JSON add real report evidence. The 875,021-byte Standard PDF is one export observation, not a general performance benchmark. W10/W15 are separately author-declared Pass.

After: Automated export cases passed; Figure 4.6 and the exported PDF/JSON add real report evidence. The 875,021-byte Standard PDF is one export observation, not a general performance benchmark. W10/W15 passed at fbe152a.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table A.2 / row 5, column 2

Before: Validate the four core use cases (UC1–UC4) end-to-end; stress-test signal-slot communication across layers; refine the UI according to Section 3.4, including the clinical color palette, WCAG 2.2 Level AA contrast, tooltips and progress indicators.

After: Validate the four core use cases (UC1–UC4) end-to-end; stress-test signal-slot communication across layers; refine the UI according to Section 3.4, including the clinical colour palette, WCAG 2.2 Level AA contrast, tooltips and progress indicators.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table A.3 / row 2, column 2

Before: Windows source/result and crop captures supplied; relevant manual cases are author-declared Pass.

After: Windows source/result and crop captures supplied; relevant manual checks passed at fbe152a.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.2 / N04

Before: Native Windows automated layout cases passed at revision d9fb8e5. Manual W01–W15 outcomes are author-declared; assistive-technology compliance was not assessed.

After: Automated Windows layout cases passed at d9fb8e5. Manual W01–W15 passed at fbe152a on a 2560 × 1600 display at 175% scaling; assistive-technology compliance was not assessed.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / F07

Before: Coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed at d9fb8e5. Relevant manual checks passed at fbe152a; the declaration specifies no execution-time display scale.

After: Coordinate, linked-view, Fit/zoom/grid and compact-viewport cases passed at d9fb8e5. Relevant manual checks passed at fbe152a, with 175% display scaling (Appendix D).

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.6 / F08

Before: Persistence and artifact cases passed at d9fb8e5. Relevant manual checks passed at fbe152a; no independent new case trace is claimed.

After: Persistence/artifact cases passed at d9fb8e5. The final coordinator saves files before inserting a completed record and cleans handled partial writes. Relevant manual checks passed at fbe152a; source differences are retained in Appendix C.

Reason: Distinguish final failure-safe storage implementation from prior automated evidence.

### Table 3.6 / N05,N07–N08

Before: Complete native Windows suite at d9fb8e5: 548 passed; 0 failed/errors/skipped. Dedicated efficiency benchmarking and clean-machine deployment remain outside the completed evaluation.

After: Complete native Windows suite at d9fb8e5: 548 passed, 0 failed/errors/skipped. Manual W01–W15 passed at fbe152a. Dedicated efficiency and clean-machine deployment remain outside this evaluation.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table 3.7 / risk R10

Before: Separate software, model, platform and user evidence

After: Keep participant outcomes, model evaluation and dated manual acceptance separate; obtain independent segmentation labels and source-matched release records.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix A milestones

Before: 548-case Windows record at d9fb8e5; author-declared W01–W15 outcomes; latest author-confirmed ten-response UAT workbook and correction log.

After: 548-case Windows automated record at d9fb8e5; 15-case manual record at fbe152a, 175% scaling; ten-response UAT workbook and correction log.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix A milestones

Before: Automated regression recorded; 15 manual outcomes declared Pass; ten-person formative UAT analysed, with study-design limits.

After: Automated regression recorded; all 15 manual cases passed; ten-person formative UAT analysed within its study scope.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Appendix A milestones

Before: Revision d9fb8e5; current export, navigation, preferences and settings-isolation cases

After: Final revision fbe152a; model metadata, persistence/cleanup, date bounds and tiled-workload refinements; dated manual record and source diff.

Reason: Reflect the subsequent final source without extending the d9fb8e5 automated count.

### Appendix A milestones

Before: Implemented and included in the recorded Windows regression at d9fb8e5; relevant manual cases are separately author-declared Pass.

After: Implemented; W01–W15 manually accepted on 2 Nov at 175% scaling. Complete automated Windows regression remains bound to d9fb8e5.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table C.1 / E24

Before: Author’s actual Windows screenshots, CRC-VAL-HE-7K TUM patch, two-page PDF and segmentation JSON supplied for the 30 Oct revision

After: Author’s Windows captures from 30–31 Oct 2026; CRC-VAL-HE-7K patch; two-page PDF and segmentation JSON.

Reason: Correct the capture range without inventing a capture-time commit.

### Table C.1 / E24

Before: Records 84/86, Re-run 83, report 65 and independent cancellation observations 79/78. Separate written confirmation declares W01–W15 passed; image records are distinct from the source-matched automated execution.

After: Records #84/#86, Re-run #83, report #65 and independent cancellation-related observations #79/#78. Capture-time commits were not recorded. The dated manual record is listed separately below.

Reason: Separate captures from the later manual confirmation.

### Table C.1 / E27–E28

Before: No dated final-source manual record or final-source diff entries.

After: Add final manual acceptance at fbe152a and the source-identity/difference records.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W01

Before: Launch and restore previous geometry

After: Launch, resize/move the normal window, close and reopen

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W01

Before: Normal window fits current available screen and retains usable actions. Declared outcome: Pass.

After: Pass. The normal window remained within the screen; size/position were restored on reopening and essential actions remained accessible.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W02

Before: Maximise, restore, shrink, maximise, restore

After: Maximise, restore, shrink, maximise and restore again

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W02

Before: Native states and normal geometry behave correctly without forced fullscreen. Declared outcome: Pass.

After: Pass. All maximise/restore/resize transitions responded normally, returning to a resizable normal window without unintended fullscreen or missing controls.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W03

Before: Dock narrow, inspect comparison, restore wide

After: Open original comparison, dock narrow and restore wide

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W03

Before: Vertical/horizontal adaptation works without Reset; views remain aligned. Declared outcome: Pass.

After: Pass. The comparison stacked in the narrow layout and returned side by side when widened, without Reset; the corresponding tissue positions stayed aligned.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W04

Before: Fit, 1:1, zoom and resize a 49-tile result

After: Inspect the 49-tile grid at Fit, 1:1 and zoom; resize the window

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W04

Before: Complete aligned 7 × 7 grid; 480/464-pixel edge dimensions recorded. Declared outcome: Pass.

After: Pass. The 3552 × 3536 image produced 49 tiles at 512 × 512. Grid/IDs stayed aligned through view changes; tile 49 measured 480 × 464 at [3072, 3072, 3552, 3536].

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W05

Before: Click toggle labels, padding and indicators; use Tab/Space

After: Click checkbox indicators/text; navigate with Tab and Space

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W05

Before: One transition per click; mouse/keyboard focus styles appropriate. Declared outcome: Pass.

After: Pass. Indicators and labels each toggled once per click. Tab focus was visible and Space changed the focused control.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W06

Before: Open both history calendars

After: Open both history calendars; select dates; search and clear filters

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W06

Before: English month/weekdays; correct selected dates and filtering. Declared outcome: Pass.

After: Pass. Both popups used English months/weekdays. The selected date range filtered the expected records and Clear Filter restored the list.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W07

Before: Restore/rerun after changing current defaults

After: Restore a record; change current defaults; use recorded Re-run

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W07

Before: Recorded model/mode/parameters retained; restore itself does not rerun. Declared outcome: Pass.

After: Pass. Restoring did not create a record or run inference. Re-run retained the stored model/settings despite changed defaults; successful completion added a new record.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W08

Before: Cancel a real workload and close while busy

After: Cancel a running workload; separately close while inference is busy

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W08

Before: Safe acknowledgement/cleanup; no partial completed record. Declared outcome: Pass.

After: Pass. Cancellation stopped safely after the current model operation, retained the preceding result and added no partial completed row. A separate busy-close check exited safely and reopening retained history.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W09

Before: Scroll/maximise Settings at common display scales

After: Inspect all Settings pages and resize at 175% display scaling

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W09

Before: All content reachable, no artificial trailing height or clipped controls. Declared outcome: Pass.

After: Pass at 175% only. All Settings pages and buttons were reachable by scrolling/resizing without inaccessible clipping or excessive trailing blank space. Other display scales were not checked in this session.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W10

Before: Export, reopen PDF/PNG and inspect companion files

After: Export and reopen classification/segmentation PDF, PNG and JSON

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W10

Before: Correct task/model/statistics; files readable; no unwanted identifying data. Declared outcome: Pass.

After: Pass. Classification and segmentation PDF/PNG files opened. Task, model, source dimensions and statistics agreed with the corresponding result and companion JSON.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W11

Before: Validate/save/restore defaults per task

After: Validate/save/restore task defaults and reject a task mismatch

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W11

Before: Clear invalid/missing-file handling and task independence. Declared outcome: Pass.

After: Pass. Compatible defaults saved and restored independently by task. A task-mismatched model produced a clear error and did not replace the valid saved default.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W12

Before: Move required files and attempt restoration/rerun

After: Rename input/model copies; attempt restore/rerun; restore filenames

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W12

Before: Actionable missing-file errors; no silent model substitution. Declared outcome: Pass.

After: Pass. Missing input/model copies produced clear messages and blocked rerun without substituting another file. Restoring filenames made the resources usable again.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W13

Before: Restore old tiles, edit preferences, Run; then use recorded Re-run

After: Run at 512, change to 256, recorded Re-run, then ordinary Run

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W13

Before: Current Run geometry/backend match Preferences; Re-run retains its record; ordinary Run after rerun again uses current preferences. Declared outcome: Pass.

After: Pass. The recorded 512-pixel run used 49 tiles; ordinary Run after changing to 256 used 196. Recorded Re-run used 512/49, and the following ordinary Run returned to 256/196.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W14

Before: Use tile numbers, image/table selection and Square; clear view/selection

After: Inspect numbered crops; use Square, independent height, Clear view and Clear Selection

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W14

Before: IDs/boxes/crop preview agree; Square copies once; clear operations preserve saved history/source files. Declared outcome: Pass.

After: Pass. Tile IDs, table coordinates and crop previews agreed. Square copied width once; height remained independently editable. Clearing the view/selection retained saved records and source files.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W15

Before: Export both PDF qualities; cancel an export; reopen the output

After: Export Standard and Original resolution PDFs; cancel an overwrite of a temporary output

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 / W15

Before: Quality and original dimensions are accurately labelled; numeric data agree; cancellation/failed export preserve the previous destination. Declared outcome: Pass.

After: Pass. Both PDF qualities opened with consistent source dimensions/statistics and the correct quality label. Cancelling an overwrite retained the earlier temporary destination without reporting a successful new export.

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Table D.1 header

Before: Acceptance criterion / declared outcome

After: Observed behaviour / outcome

Reason: Replace the earlier undated blanket declaration with the author-confirmed 2 November 2026 case outcomes and actual Windows/display/source conditions.

### Word document properties / Description

Before: Evidence-aware CP2 revision; UAT/model metrics and designated Windows captures are pending.

After: Design, implementation and evaluation of ZY-Path, a CPU-based desktop application for histopathology classification, tiled analysis, segmentation, linked inspection, local history and report export.

Reason: Replace obsolete revision notes with a formal document description. Preserve the genuine 17 October creation date.

### Table 3.6 / F05

Before: Current Windows crop, mode, legend and actual-area fixture cases passed; tiled-map predictive evaluation pending.

After: Crop, mode, legend and actual-area fixture cases passed at d9fb8e5. Tiled-map predictive accuracy was not evaluated.

Reason: Use completed-report evaluation language while retaining the actual unevaluated predictive/deployment scope.

### Table A.3 / Deployment

Before: Build preparation implemented; deployment verification pending

After: Build preparation implemented; clean-machine deployment is outside this evaluation

Reason: Use completed-report evaluation language while retaining the actual unevaluated predictive/deployment scope.

### Appendices A–E / pagination

Before: Appendix headings could begin after a preceding appendix table; the manual context paragraph could split across pages.

After: A named style based on Heading 2 starts each appendix on a new page; the acceptance-context paragraph stays together.

Reason: Keep appendix openings clear and prevent the manual environment description splitting across pages; retain all existing image spacing and plain table grids.

### Table D.1 source

Before: Source: my Windows manual checks, environment record and confirmation of W01–W15 on 2 November 2026. Full case records accompany the thesis in Windows_Manual_Acceptance_Record.csv and .xlsx; the automated test log remains a separate record.

After: Source: my 2 November 2026 Windows manual checks at fbe152a; accompanying case records: Windows_Manual_Acceptance_Record.csv/.xlsx.

Reason: Keep the source note concise and retain the exact accompanying filenames; complete environment details remain above the table.

### Appendix D.2

Before: Figures 1.1 and 4.1, 4.3–4.6 and 4.9 contain the dataset image and dated Windows examples, including records #84/#86, completed Re-run #83 and the actual PDF pages. Figures 4.2, 4.7 and 4.8 retain their labelled development captures. The two cancellation-related views remain independent observations. My 2 November acceptance record in Table D.1 supplies the case-level outcomes; the older figures are used to illustrate the interface, not to reconstruct that session. The supporting archive includes the cited logs/XML, source differences, manifests, participant workbook, case records and exported PDF/JSON. The original PNG listed in Figure 4.6 was not available; its content is not claimed from the listing alone.

After: Figures 1.1 and 4.1–4.9 retain their captioned sources and dates, including the labelled development fixtures. The cancellation panels remain independent observations. Table D.1 records my 2 November manual session; its outcomes are not inferred from the earlier figures. Appendix C indexes the accompanying source files.

Reason: Consolidate repeated provenance statements and avoid a short standalone appendix continuation; the original-PNG boundary remains in Section 4.2.4, Figure 4.6 and the supporting inventory.

### Appendix D.2

Before: Figures 1.1 and 4.1–4.9 retain their captioned sources and dates, including the labelled development fixtures. The cancellation panels remain independent observations. Table D.1 records my 2 November manual session; its outcomes are not inferred from the earlier figures. Appendix C indexes the accompanying source files.

After: Figure captions identify the dated source materials. My 2 November manual observations are recorded in Table D.1; Appendix C indexes the accompanying evidence.

Reason: Keep the supporting-figure note concise; the detailed capture dates and independent cancellation observations are already stated in Appendix C.1 and the figure captions.