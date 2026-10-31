# Figure evidence and document corrections — 31 October 2026



Preserve original source images/reports and verified numeric results. Correct mixed evidence identities, replace the two requested captures, improve alternative text and unify citation navigation. No application source or tests change.



## 1. 4.2.1

Before: The Windows startup record on 19 October 2026 establishes classifier loading and validation. Figure 4.1 now supplies a direct Windows application capture with an actual Single image result, showing the input, probability chart and export/session regions. Its displayed record #52 identifies a NORM-labelled 224 × 224 input and 99.9% model confidence. This is an observed prediction, not an additional accuracy experiment.

After: The Windows startup record on 19 October 2026 establishes classifier loading and validation. Figure 4.1 shows the Windows overview captured on 31 October: record #84 displays NORM-TCGA-ACCEDPAW.tif at 224 × 224 pixels, the NORM prediction at 99.9% confidence, the probability chart and the export/session actions including Clear view. The selected resize option is OpenCV linear. This is an observed prediction, not an additional accuracy experiment.

Reason: Replace the superseded record52 overview and describe only the actual new record84 screenshot.



## 2. Figure 4.1

Before: Figure 4.1. Windows application overview with Single image classification, probability chart and session/export panels. The displayed analysis is record #52. Source: author’s Windows capture.

After: Figure 4.1. Windows application overview, 31 October 2026: Single image classification of a 224 × 224 patch, NORM at 99.9%, record #84, with OpenCV linear selected. Source: author’s Windows capture.

Reason: Use the new original capture without changing its model output or source pixels.



## 3. 4.2.3

Before: The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 now shows a direct Windows run with the supervisor-provided UPerNet model, aligned source/overlay views and nine-class pixel coverage. The supplied segmentation analysis metadata records imagenet preprocessing, a 1000-pixel source window, stride 512 and network input 224 on CPU. The actual PDF and JSON counts sum to 12,559,872 pixels, equal to 3552 × 3536. The export and screen concern different analysis records; their matching counts are not independent accuracy measurements. Annotated-mask evaluation remains unavailable (Section 4.5.3).

After: The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 shows Windows record #86 dated 31 October, with the supervisor-provided UPerNet model and aligned source/overlay views. The visible statistics include 3,108,889 cancerous-epithelium pixels and 7,998,755 stroma pixels; the scrollable legend continues below the visible rows. Separately, the actual report/JSON records imagenet preprocessing, a 1000-pixel source window, stride 512, network input 224 and CPU execution. Its nine counts sum to 12,559,872 pixels, equal to 3552 × 3536. The report and new screen are different analysis records; agreement of their counts is not an accuracy measurement. Annotated-mask evaluation remains unavailable (Section 4.5.3).

Reason: Use new record86; do not claim that every scrollable legend row is visible or that report65 belongs to the new run.



## 4. Figure 4.4

Before: Figure 4.4. Original/segmentation-overlay comparison for a 3552 × 3536 breast-cancer raster, with linked Fit views at 15.7%, opacity 30% and nine-class pixel coverage. Record #49 uses the supervisor-provided breast-cancer-trained UPerNet model. Source: author’s Windows capture.

After: Figure 4.4. Breast-cancer raster comparison, 31 October 2026, record #86: 3552 × 3536 source, linked Fit views at 15.7% and opacity 30%, using the supervisor-provided UPerNet model. The pixel-coverage legend is scrollable. Source: author’s Windows capture.

Reason: Replace the superseded record49 image and retain the actual scale, opacity and visible scope.



## 5. 4.2.4 / Figure 4.6 discussion

Before: The supplied two-page PDF is 875,021 bytes and identifies Standard quality, software version 1.0, CPU execution, source dimensions and segmentation parameters. It records an analysis timestamp of 25 October 2026 and an export timestamp of 30 October 2026. Its export-time model hash matches the genuine UPerNet resource identity in Appendix E, while the report explicitly states that an export-time hash does not establish the historical inference file. The companion JSON agrees with the PDF’s nine pixel counts. The file listing also shows a PNG, whose source file was not uploaded.

After: Figure 4.6(a–b) reproduces pages 1 and 2 of the same supplied two-page PDF. The 875,021-byte Standard report identifies record #65, analysis time 25 October 2026 at 19:45:38 and export time 30 October 2026 at 14:43:26 +08:00. Its software version is 1.0, with CPU execution and the recorded source dimensions and segmentation parameters. Its export-time model hash matches the UPerNet resource identity in Appendix E; the report distinguishes that hash from historical inference identity. The companion JSON agrees with its timestamp and all nine pixel counts. Panel (c) lists a PNG whose source file was not uploaded.

Reason: The old panel was dated23October, but actualPDF and JSON both identify25October; use one consistent authentic report without falsifying timestamps.



## 6. Figure 4.6 panel labels

Before: (a) Opened report; (b) actual report metadata page

After: (a) Actual PDF page 1; (b) page 2 of the same PDF

Reason: Remove the older23October screenshot from the primary report example.



## 7. Figure 4.6 caption

Before: Figure 4.6. Actual Standard-quality segmentation PDF, its metadata page and Windows file listing. Analysis record #65 is dated 25 October; the PDF was exported on 30 October 2026. The listed PNG is not included in the uploaded evidence. Source: author’s report and captures.

After: Figure 4.6. Pages 1–2 of the same actual Standard segmentation PDF and its Windows file listing. Record #65: analysis 25 October 2026, 19:45:38; export 30 October 2026. The listed PNG source file was not supplied. Source: author’s PDF, rendered faithfully, and file-list capture.

Reason: Make the same-report pairing and actual authoritative dates explicit.



## 8. 4.2.5

Before: Figure 4.9(a–b) documents an actual classification operation at 228/400 processing regions and the subsequent acknowledgement, “Inference cancelled. Previous completed results are unchanged.” Completed record #79 remains displayed. The transient Cancelling state was not captured, and this pair does not by itself audit every history/database entry. Panels (c–d) show default-path configuration with a test model and restoration of the built-in segmentation default. The author identifies dummy_segmentation.pt as a test model; these panels demonstrate settings interaction rather than genuine trained-model predictive performance.

After: Figure 4.9(a–b) contains two independent cancellation-related observations. Panel (a) shows classification progress at 228/400 while the Session panel displays completed record #79 at 14:32:35. Panel (b) shows “Inference cancelled. Previous completed results are unchanged,” with record #78 at 14:30:40; Segmentation is selected in the input controls while the retained result is classification. These are not a before/after pair from one demonstrated operation and do not establish database cleanup. Panels (c–d) demonstrate default configuration with the explicitly identified test model dummy_segmentation.pt and restoration of the built-in segmentation default; they do not measure trained-model predictive performance.

Reason: Correct79/78 mismatch and changed task selection; remove the unsupported continuous-cancellation claim.



## 9. Figure 4.9(a)

Before: (a) A new classification operation is running

After: (a) Classification progress; Session shows record #79

Reason: Distinguish the active operation from the retained completed record.



## 10. Figure 4.9(b)

Before: (b) Cancellation acknowledged; previous result remains visible

After: (b) Separate cancellation acknowledgement; Session shows #78

Reason: Do not present the separate record78 view as the completion of panel(a).



## 11. Figure 4.9 caption

Before: Figure 4.9. Windows cancellation and default-model controls: (a) 228/400 processing progress; (b) cancellation acknowledged with completed record #79 retained; (c) configuration using the controlled test model dummy_segmentation.pt; (d) restored built-in default. The transient Cancelling screen was not captured. Source: author’s Windows captures.

After: Figure 4.9. Independent cancellation-related views: (a) classification at 228/400 with Session record #79; (b) cancellation acknowledgement with record #78 and Segmentation selected. These are not one continuous sequence. Panels (c–d) show test-model default configuration and restored built-in default. Source: author’s Windows captures.

Reason: Use accurate record IDs and explicit independent-observation scope.



## 12. 4.1

Before: This chapter reports the implemented system and the evaluated source state identified in Appendix C. Section 4.2 presents implemented workflows and a distinct classifier evaluation; Section 4.3 reports software tests and native observations; Section 4.4 reserves the UAT results. Environment and date labels identify each completed or interrupted invocation.

After: This chapter reports the implemented system and the evaluated source state identified in Appendix C. The complete 508-case Windows result applies to revision 3a935ef. Interface figures illustrate separate recorded analyses; a displayed analysis timestamp identifies a run, not the source revision of the software displaying it. Section 4.2 presents workflows and classifier evaluation, Section 4.3 reports software tests and native observations, and Section 4.4 reserves UAT results.

Reason: Separate source-matched automated verification from screenshots without inferring code versions from saved-record dates.



## 13. Appendix C.1

Before: The image collection contains direct-run screenshots, separate History/default demonstrations and completed recorded Re-run #83 with its parameter view. Figure captions identify the displayed analysis records and distinguish screen results from separate export artifacts. The custom-default demonstration uses an explicitly identified test model.

After: The image collection includes replacement overview record #84 and segmentation record #86 dated 31 October 2026, alongside earlier classification inspection, History, recorded Re-run and default demonstrations. Figure 4.6 uses two pages of one actual report, record #65, analysed on 25 October and exported on 30 October. Figure 4.9(a–b) shows different retained records, #79 and #78, rather than a continuous cancellation sequence. The capture index records individual files, displayed analysis dates, record IDs and available source identities. Screenshot versions are not inferred from record dates or interface appearance; the 508-case automated result remains specifically bound to 3a935ef.

Reason: Supply a concise per-evidence identity policy and correct the two mixed-source figures.



## 14. 4.2.2

Before: Figure 4.3(a–b) shows Single image and Tiled analysis for the same named 3552 × 3536 raster. The Single image result selects STR with 42.6% confidence. The tiled view reports 40 STR, five MUC, one MUS and three NORM tiles, with estimated area coverage 82.06%, 9.98%, 1.89% and 6.07%, respectively. Its 512-pixel source crops use RGB/raw255 and OpenCV linear resize to 224 × 224. Panel (c), from a separate analysis, identifies tile 31 as NORM at 59.47%, with rectangle [1024, 2048, 1536, 2560]. These observations demonstrate presentation and crop inspection; they do not supply ground-truth tile accuracy.

After: Figure 4.3(a–b) shows Single image and Tiled analysis for the same named 3552 × 3536 raster. The Single image result selects STR with 42.6% confidence. The tiled view reports 40 STR, five MUC, one MUS and three NORM tiles, with estimated area coverage 82.06%, 9.98%, 1.89% and 6.07%, respectively. Its 512-pixel source crops use RGB/raw255 and OpenCV linear resize to 224 × 224. Panel (c), from a separate analysis, identifies tile 31 as NORM at 59.47%, with rectangle [1024, 2048, 1536, 2560]. These observations demonstrate presentation and crop inspection; they do not supply ground-truth tile accuracy. The classification captures deliberately select OpenCV INTER_LINEAR, corresponding to the training script’s linear-resize choice; Pillow bilinear remains the application default and the backend of the independent evaluation in Section 4.2.6. Matching this resize choice does not establish physical-scale or stain matching.

Reason: Explain why screenshots show the optional backend while the measured default-Pillow result remains correctly described.



## 15. Appendix D.2

Before: Figures 1.1 and 4.1, 4.3–4.6 and 4.9 contain the dataset image and Windows captures, including completed recorded Re-run #83 and its parameter view. Figures 4.2, 4.7 and 4.8 retain their labelled development captures. Running and cancellation acknowledgement are documented without requiring a transient Cancelling screenshot. The capture index distinguishes displayed records, test-model configuration and actual report artifacts. The accompanying acceptance workbook records which case sequences remain to be completed.

After: Figures 1.1 and 4.1, 4.3–4.6 and 4.9 contain the dataset image and Windows observations, including the replacement record #84/#86 captures, completed Re-run #83 and the authentic report pages. Figures 4.2, 4.7 and 4.8 retain their labelled development captures. Running and cancellation acknowledgement are independent observations, not a continuous case record. The accompanying acceptance workbook identifies the remaining manual sequences; no new formal Pass is assigned from these screenshots.

Reason: Keep manual acceptance partial after correcting the cancellation evidence pairing.



## 16. Appendix C.1 / E24

Before: Classification/segmentation display, completed recorded Re-run #83, parameter isolation, actual report and cancellation observations; test-model settings distinguished. The acceptance workbook separates partial observations from unperformed sequences.

After: Record84/86 replacement views, completed recorded Re-run83, actual report65 pages/JSON, and independent cancellation-related observations79/78. Test-model settings and remaining manual sequences are distinguished.

Reason: Index corrected evidence identities without claiming one version-matched acceptance execution.



## 17. All53 body citations

Before: Mixed external-source and internal-bibliography destinations; hyperlink styles already black and non-underlined.

After: All53 author/year citations consistently link to their corresponding bibliography entry; existing verified DOI/official URLs and reference text remain unchanged. Black non-underlined styles are retained for visited and unvisited links.

Reason: Unify click behaviour without changing citation wording, bibliographic facts or CP1 author/year presentation.



## 18. All31 embedded images

Before: 17images had descriptions and14had none; most screenshot descriptions were filenames only.

After: All31 image occurrences have meaningful English titles/descriptions covering the actual content, identifiers and synthetic/independent-observation limitations.

Reason: Improve document accessibility without modifying image pixels, diagrams or layout geometry.



## 19. Supporting acceptance materials / W08

Before: Incorrectly described both captures as a sequence retainingrecord79.

After: Record79progress and separate record78acknowledgement are distinguished;continuous cancellation/history/close checks remain incomplete. Status staysPartially evidenced.

Reason: Synchronise the workbook/CSV/guide with the corrected original-image interpretation.



## 20. Supporting materials / capture index and submission manifest

Before: Capture index paired a23October report screenshot with25OctoberPDF metadata and described record78 acknowledgement as79; two replacement images and submission manifest absent.

After: Index preserves superseded originals, adds replacementrecords84/86 and exactPDFpage1 rendering, corrects independent79/78observations, and lists all cited companion materials with their actual completion status.

Reason: Keep manuscript, source images, manual workbook and delivered files consistent.



## 21. 4.2.4 / 4.3.3 editorial consistency

Before: History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 reserves the Windows history and recorded-rerun demonstration.

After: History stores completed records and supports keyword/date filtering, restoration and a separate rerun action. A tiled-classification row reports tile count and the largest estimated class coverage; its Confidence cell remains “-” rather than implying a whole-image confidence. Detailed per-tile confidence is available when the result is restored. The internal aggregate remains available with its explicitly different PDF terminology. Figure 4.5 illustrates Windows history and recorded rerun.

Reason: Remove a stale placeholder verb and avoid extending prior direct-run confirmation to replacement captures.



## 22. 4.2.4 / 4.3.3 editorial consistency

Before: The Windows screenshots document representative actual-image observations of classification, segmentation, linked display, history/default isolation, export and cancellation. Figures 4.1, 4.3 and 4.4 show direct runs and retain their displayed record IDs. The Appendix D evidence register records eight partially evidenced cases and seven without a complete execution record; no new formal Pass or Fail is assigned. Completion of the remaining case sequences is distinct from the 508 automated test passes.

After: The Windows screenshots document representative actual-image observations of classification, segmentation, linked display, history/default isolation, export and cancellation. Figures 4.1, 4.3 and 4.4 document observed results and retain their displayed record IDs. The Appendix D evidence register records eight partially evidenced cases and seven without a complete execution record; no new formal Pass or Fail is assigned. Completion of the remaining case sequences is distinct from the 508 automated test passes.

Reason: Remove a stale placeholder verb and avoid extending prior direct-run confirmation to replacement captures.

