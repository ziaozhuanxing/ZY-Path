### 3.2.2

Before: The CP1 core/data coverage target remains an evaluation objective in the proposal baseline. This edition reports the completed Windows automated execution with its source version and named assertions; it does not infer code coverage from the number of passing cases. Requirements retain separate implementation and verification status.

After: Verification is reported by requirement and named test assertion. The Windows pass count measures executable cases rather than code coverage; the original coverage target is retained in the proposal baseline in Appendix A.

Reason: Replace edition-specific editorial wording with the actual verification measure; do not imply measured coverage.

### 3.3.2

Before: The training loader decodes images with OpenCV, converts BGR to RGB and applies Albumentations Resize(224, 224), vertical/horizontal flips, hue adjustment, rotation and a random-sized crop. Validation uses Resize followed by ToTensorV2 and float conversion. Values remain on the raw255 scale. Training used class-weighted cross-entropy, Adam with initial learning rate 0.001 and weight decay 10⁻⁶, and ReduceLROnPlateau with factor 0.5, patience 3 and minimum learning rate 10⁻⁶; batch size was 32 with two data-loading workers.

After: The training loader decodes images with OpenCV and converts BGR to RGB. Validation uses deterministic Resize(224, 224), ToTensorV2 and float conversion, with values retained on the raw255 scale. Training used class-weighted cross-entropy, Adam with initial learning rate 0.001 and weight decay 10⁻⁶, and ReduceLROnPlateau with factor 0.5, patience 3 and minimum learning rate 10⁻⁶; batch size was 32 with two data-loading workers.

Reason: Remove the duplicated augmentation inventory; the next paragraph retains the full augmentation settings.

### 3.3.4

Before: Source crop dimensions determine the field of view before resampling to 224 × 224. At the source dataset’s nominal 0.5 μm/pixel, a 224-pixel edge spans 112 μm. If a new raster’s resolution r is known in μm/pixel, a candidate crop edge covering that field is approximately 112/r pixels; this is a physical-scale calculation, not evidence of optimal predictive performance. The interface retains 512 × 512 as an editable starting value. Values such as 256 and 300 are exploratory source-crop candidates, while the network input remains 224 × 224. A controlled comparison should keep the crop centre, source image, model, backend and display dimensions fixed. No outcomes from those new-size trials are supplied here.

After: Source crop dimensions determine the field of view before resampling to 224 × 224. At the source dataset’s nominal 0.5 μm/pixel, a 224-pixel edge spans 112 μm. If a new raster’s resolution r is known in μm/pixel, a candidate crop edge covering that field is approximately 112/r pixels; this is a physical-scale calculation, not evidence of optimal predictive performance. The interface retains 512 × 512 as an editable starting value. Values such as 256 and 300 are exploratory source-crop candidates, while the network input remains 224 × 224. A controlled comparison should keep the crop centre, source image, model, backend and display dimensions fixed. Predictive performance at alternative crop sizes requires labelled evaluation at the chosen scale.

Reason: Replace an attachment-review phrase with the methodological requirement; no crop-size experiment is claimed.

### 4.2.1

Before: Current-version additions comprise numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run now reads current preferences independently of restored or rerun records. Their execution-evidence scope is defined in Section 4.3.1.

After: The implementation includes numbered tile inspection and original-crop preview, Square and resize guidance, Clear view and zero-row history selection, synchronised history input previews, stable linked navigation, clearer built-in/local model state, task-specific progress, background PDF generation and selectable report image quality. Ordinary Run reads current preferences independently of restored or rerun records. Their execution-evidence scope is defined in Section 4.3.1.

Reason: Describe the completed implementation directly rather than narrating revision history.

### 4.2.3

Before: The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 shows Windows record #86 dated 31 October, with the supervisor-provided UPerNet model and aligned source/overlay views. The visible statistics include 3,108,889 cancerous-epithelium pixels and 7,998,755 stroma pixels; the scrollable legend continues below the visible rows. Separately, the actual report/JSON records imagenet preprocessing, a 1000-pixel source window, stride 512, network input 224 and CPU execution. Its nine counts sum to 12,559,872 pixels, equal to 3552 × 3536. The report and new screen are different analysis records; agreement of their counts is not an accuracy measurement. Annotated-mask evaluation remains unavailable (Section 4.5.3).

After: The reference notebook establishes the segmentation architecture, preprocessing, labels and probability fusion. Figure 4.4 shows Windows record #86 dated 31 October, with the supervisor-provided UPerNet model and aligned source/overlay views. The visible statistics include 3,108,889 cancerous-epithelium pixels and 7,998,755 stroma pixels; the scrollable legend continues below the visible rows. Separately, the actual report/JSON records imagenet preprocessing, a 1000-pixel source window, stride 512, network input 224 and CPU execution. Its nine counts sum to 12,559,872 pixels, equal to 3552 × 3536. The report and screen show different analysis records; agreement of their counts is not an accuracy measurement. Annotated-mask evaluation remains unavailable (Section 4.5.3).

Reason: Use stable academic wording for the two distinct recorded analyses.

### 4.2.4

Before: Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The author identifies the follow-up operation as a recorded Re-run: its completed record #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. The second capture confirms 224 × 224 network input, raw255 and OpenCV linear resize. The Done indicator, restored Run Inference button and new session record distinguish this pair from the earlier busy 49/49 capture. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the actual report and companion-file listing.

After: Figure 4.5 documents parameter isolation on Windows. History contains both classification modes. The completed recorded Re-run #83 displays 512 × 512 source tiles and 49 tiles, while the current input summary remains at 256 × 256 and 196 planned tiles. Its parameter strip records 224 × 224 network input, raw255 and OpenCV linear resize. The separate ordinary Run #77 uses the current 256-pixel setting. Figure 4.6 shows the exported report and companion-file listing.

Reason: Retain the observed parameters and record identities while removing references to an abandoned busy capture and file-review narration.

### 4.2.4

Before: Figure 4.6(a–b) reproduces pages 1 and 2 of the same supplied two-page PDF. The 875,021-byte Standard report identifies record #65, analysis time 25 October 2026 at 19:45:38 and export time 30 October 2026 at 14:43:26 +08:00. Its software version is 1.0, with CPU execution and the recorded source dimensions and segmentation parameters. Its export-time model hash matches the UPerNet resource identity in Appendix E; the report distinguishes that hash from historical inference identity. The companion JSON agrees with its timestamp and all nine pixel counts. Panel (c) lists a PNG whose source file was not uploaded.

After: Figure 4.6(a–b) reproduces pages 1 and 2 of the same exported two-page PDF. The 875,021-byte Standard report identifies record #65, analysis time 25 October 2026 at 19:45:38 and export time 30 October 2026 at 14:43:26 +08:00. Its software version is 1.0, with CPU execution and the recorded source dimensions and segmentation parameters. Its export-time model hash matches the UPerNet resource identity in Appendix E; the report distinguishes that hash from historical inference identity. The companion JSON agrees with its timestamp and all nine pixel counts. Panel (c) lists a PNG whose original image file is not part of the companion materials.

Reason: Express report provenance without referring to an upload workflow; retain the original PNG evidence boundary.

### 4.2.5

Before: The English calendar in Figure 4.8 was captured after setting the default locale to Chinese in a controlled run. The corresponding test opens each popup, checks English month/day labels, selects a date and verifies the unchanged date value and query signal. This is stronger evidence than merely setting a locale property without opening the widget.

After: The English calendar in Figure 4.8 was captured after setting the default locale to Chinese in a controlled run. The corresponding test opens each popup, checks English month/day labels, selects a date and verifies the unchanged date value and query signal.

Reason: State the executed checks directly and remove the unnecessary comparison with a weaker hypothetical test.

### 4.2.6

Before: The 30-epoch metrics record selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. The directory name crc-dn21-seed42-10ep and config.json epochs=10 describe the initial run configuration; continuation logs and metrics.csv establish the completed 30-epoch history. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

After: The completed 30-epoch run selects epoch 26 by minimum validation loss (0.0275519), with validation accuracy 99.09% and macro-F1 99.09%. Continuation records establish the training history described in Section 3.3.2. Figure 4.10 illustrates the epoch-to-epoch variation in validation loss and accuracy.

Reason: Keep the measured selection and completed duration; avoid repeating the legacy directory-name explanation already retained in the methodology.

### 4.3.4

Before: The demonstrated delivery route is source execution. The current repository contains a Windows PyInstaller specification, build script, genuine-resource preflight, bundled-configuration support and release-manifest generation. No corresponding completed build log, distributable artifact or clean-machine/offline acceptance was supplied. Tooling implementation is therefore reported separately from unverified deployment.

After: The demonstrated delivery route is source execution. The repository contains a Windows PyInstaller specification, build script, genuine-resource preflight, bundled-configuration support and release-manifest generation. A completed version-matched distributable and clean-machine/offline acceptance are outside this evaluation.

Reason: Use authorial evaluation language and distinguish implemented tooling from unexecuted deployment without an attachment-review tone.

### 4.5.1 / Table 4.9 title

Before: Table 4.9. Objective achievement and outstanding evidence

After: Table 4.9. Objective achievement and evaluation scope

Reason: Use a completed-report title; preserve the actual evaluation boundaries in the table.

### 5.1

Before: The classifier evaluation produced 6,511 correct labels from 7,180 native-sized external-test patches, equivalent to 90.68% accuracy and 88.59% macro-F1. Software verification remains separate: revision d9fb8e5 passed all 548 Windows automated cases, and 15 developer-led manual cases were reported as passed. In the supplied ten-person usability dataset, mean SUS is 74.50 (SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance. These complementary results support the implemented educational/research workflow while retaining the predictive, study-design and deployment limits in Section 4.5.3.

After: The classifier evaluation produced 6,511 correct labels from 7,180 native-sized external-test patches, equivalent to 90.68% accuracy and 88.59% macro-F1. Software verification remains separate: revision d9fb8e5 passed all 548 Windows automated cases, and 15 developer-led manual cases were reported as passed. In the ten-participant usability dataset, mean SUS is 74.50 (SD 10.66); 72 of 96 evaluable tasks were completed independently and 22 with assistance. These complementary results support the implemented educational/research workflow while retaining the predictive, study-design and deployment limits in Section 4.5.3.

Reason: Remove file-supply narration without changing any study result.

### Appendix A.3

Before: The dated Windows automated record, representative images, actual PDF/JSON, 15-case manual declaration and corrected ten-response UAT dataset are available. Semester and submission date remain to be supplied. Additional runtime or packaged-deployment claims require corresponding execution records.

After: The dated Windows automated record, representative images, exported PDF/JSON, 15-case manual declaration and corrected ten-response UAT dataset document the completed evaluation. Further runtime or packaged-deployment claims require the corresponding execution records.

Reason: Keep the cover fields on the cover rather than repeating an editing reminder in the academic body.

### All 20 body figures / 28 image paragraphs

Before: Mixed image paragraph spacing, including 0 pt before/after for several screenshots.

After: Figure Image paragraph style: centred, 18 pt before and after, single image line spacing, image kept with following label/caption; figure-caption paragraph kept together.

Reason: Provide a clear blank-line equivalent above and below photographs and diagrams without inserting unstable empty text paragraphs; keep the cover and all original image pixels/dimensions.

### Figures 4.3, 4.5 and 4.9 / multi-panel pagination

Before: All panel images chained together; additional white space could force a caption onto a page without its image.

After: Allow a page break after panel (a); keep the remaining panels with their final caption, and label the second group as continued. All original image dimensions are retained.

Reason: Maintain 18 pt image white space while avoiding isolated captions or shrinking the screenshot text.

### 3.3.3 Classification preprocessing and resize provenance

Before: The original evaluation used Albumentations 1.3.1 and OpenCV 4.8.1, with A.Resize(224, 224) retaining its default linear interpolation. Pillow bilinear and OpenCV INTER_LINEAR can differ when resampling is necessary. A Windows rerun through the default Pillow pathway is now reported in Section 4.2.6; all 7,180 source patches were already 224 × 224, so this run validates the native-sized patch pathway rather than general equivalence when larger crops are resized.

After: The original evaluation used Albumentations 1.3.1 and OpenCV 4.8.1, with A.Resize(224, 224) retaining its default linear interpolation. Pillow bilinear and OpenCV INTER_LINEAR can differ when resampling is necessary. A Windows rerun through the default Pillow pathway is reported in Section 4.2.6; all 7,180 source patches were already 224 × 224, so this run validates the native-sized patch pathway rather than general equivalence when larger crops are resized.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.2.4 History, rerun and export

Before: Figure 4.6. Pages 1–2 of the same actual Standard segmentation PDF and its Windows file listing. Record #65: analysis 25 October 2026, 19:45:38; export 30 October 2026. The listed PNG source file was not supplied. Source: author’s PDF, rendered faithfully, and file-list capture.

After: Figure 4.6. Pages 1–2 of the same actual Standard segmentation PDF and its Windows file listing. Record #65: analysis 25 October 2026, 19:45:38; export 30 October 2026. The listed PNG is not included in the companion materials. Source: author’s PDF, rendered faithfully, and file-list capture.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.4.1 Participant Demographics

Before: Table 4.6 summarises the ten consenting respondents, their reported backgrounds and study display conditions. All supplied SUS forms are complete, with no participant excluded after the confirmed consent correction.

After: Table 4.6 summarises the ten consenting respondents, their reported backgrounds and study display conditions. All SUS forms are complete, with no participant excluded after the confirmed consent correction.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.4.3 Feature Usage and Ratings

Before: Table 4.8 reports feature-specific ratings on the supplied 1–5 ease/clarity scale. Each mean is calculated from numerical responses only; blank ratings are retained as missing rather than converted into low scores.

After: Table 4.8 reports feature-specific ratings on the participant 1–5 ease/clarity ratings. Each mean is calculated from numerical responses only; blank ratings are retained as missing rather than converted into low scores.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.4.3 Feature Usage and Ratings

Before: Source: supplied feature-rating records; 1 = very difficult/unclear, 5 = very easy/clear.

After: Source: participant feature-rating records; 1 = very difficult/unclear, 5 = very easy/clear.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.4.5 Qualitative Feedback Analysis

Before: Four respondents (P01, P02, P04 and P07) discuss tile-class coverage explicitly; their accounts include both understanding and initial confusion. P01 writes, “Tile coverage looked like an exact area until I read that it is estimated from tile classes.” Recorded versus current settings appears for P01 and P06, consistent with the six assisted T07 completions. The supplied learnability and guidance themes involve P02, P03, P05, P07 and P08. P07’s negative case is retained: “No, not without a tutorial; too many new concepts at once.” P09 highlights long-workload reliability. P05 and P10 are not quoted because they withheld quotation permission.

After: Four respondents (P01, P02, P04 and P07) discuss tile-class coverage explicitly; their accounts include both understanding and initial confusion. P01 writes, “Tile coverage looked like an exact area until I read that it is estimated from tile classes.” Recorded versus current settings appears for P01 and P06, consistent with the six assisted T07 completions. The learnability and guidance themes involve P02, P03, P05, P07 and P08. P07’s negative case is retained: “No, not without a tutorial; too many new concepts at once.” P09 highlights long-workload reliability. P05 and P10 are not quoted because they withheld quotation permission.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### 4.4.5 Qualitative Feedback Analysis

Before: The findings prioritise clearer coverage explanations, more explicit Run/Re-run distinctions, easier first-use guidance and investigation of the reported long-workload closure. Export identity and keyboard navigation also merit further review. These are recommendations from the supplied responses, not claims that new fixes have already been implemented or tested.

After: The findings prioritise clearer coverage explanations, more explicit Run/Re-run distinctions, easier first-use guidance and investigation of the reported long-workload closure. Export identity and keyboard navigation also merit further review. These are recommendations from the participant responses, not claims that new fixes have already been implemented or tested.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### B.3 Standard task script and observation rules

Before: Table B.1 gives the task instructions and success criteria used to interpret the supplied T01–T10 outcome records. Instructions describe the intended protocol; a missing execution detail is not reconstructed from the protocol alone.

After: Table B.1 gives the task instructions and success criteria used to interpret the recorded T01–T10 outcomes. Instructions describe the intended protocol; a missing execution detail is not reconstructed from the protocol alone.

Reason: Use academic descriptions of recorded results rather than file-supply or editing-process wording; preserve values and evidence scope.

### Embedded-image alternative text

Before: Some alternative descriptions contained compressed words, missing punctuation or inconsistent raw255 formatting.

After: All 31 images retain English alternative text; 18 descriptions have corrected spacing and punctuation, with the same record identities, values and evidence scope.

Reason: Improve accessible reading without changing any image pixels or layout.

### 1.4 / project-objective list

Before: Automatic list numbers appeared before the explicit O1–O7 identifiers, e.g. 1. O1.

After: O1–O7 serve as the sole objective identifiers, using a consistent hanging-indent paragraph style.

Reason: Remove duplicate numbering while keeping every objective and its traceability code unchanged.

### Figure and table captions / preliminary lists

Before: Some caption titles ended with a period and others did not.

After: All 44 body figure/table captions end with a period; the corresponding list entries match.

Reason: Apply consistent caption punctuation without changing numbering, source text or hyperlink fields.

### Whole document / revision highlighting

Before: 2 highlighting/shading properties remained in text paragraphs or runs.

After: No textual revision highlighting remains; all content and reported negative cases are preserved.

Reason: Remove review markup from the submission copy without altering the underlying data or findings.

### Table of Contents and List of Figures

Before: The figure list repeated full captions and source notes, and 4 pt entry spacing created short continuation pages.

After: The figure list uses concise titles with the same figure numbers and live page-reference fields; full captions and sources remain in the body. Contents/list entries retain 10.5 pt type and use 2 pt after-spacing.

Reason: Make preliminary navigation easier to scan without shrinking the font or removing any body heading or figure.

### All 24 tables / source-note pagination

Before: A few trailing source notes could move to the following page without any table row.

After: Each source note follows its table and stays with the final row; headers continue to repeat and table rows remain unsplit.

Reason: Prevent detached source notes while retaining plain solid black table borders.

### Appendix E.3 / duplicated final paragraph

Before: Existing PDF file-size observations describe the recorded exports or synthetic export fixtures only. They do not establish inference latency or guarantee preview support on an external hosting service.

After: [Duplicate removed; the same export-size scope remains in Section 4.2.4.]

Reason: Avoid an almost empty final page and consolidate an already stated limitation. No measurement, test or finding is removed.

### Appendix E.3 / final-page balance

Before: A dedicated timing or memory benchmark is not part of the completed evaluation. If undertaken later, it should fix the software revision, hardware, model and image identities, preprocessing and crop geometry; separate model loading from already-loaded inference and report repeated measurements rather than a single display time.

Packaging validation is a separate release activity: retain the build record, permitted resources and artifact identity, then exercise the application on a clean Windows machine without relying on development caches. Offline operation must be checked explicitly. No successful packaged build or clean-machine run is claimed here.

After: No repeated timing/memory benchmark or clean-machine packaged-deployment evaluation was conducted. Future tests should identify the revision, hardware, model/image files and settings; separate loading from already-loaded inference; repeat measurements; and verify the recorded build, permitted resources and offline behaviour on a clean Windows machine.

Reason: Consolidate the repeated timing/deployment protocol into one concise paragraph, retaining its unexecuted status and required controls while avoiding a nearly empty final page.