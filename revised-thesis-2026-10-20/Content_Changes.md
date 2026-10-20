# 本轮内容修改清单

本文仅修订内容、引用及相应目录字段；沿用原文档样式。每项列出位置、修改前、修改后与原因。

## 1. 3.1

**修改前**
The implementation baseline is revision 1f3e01e, supplemented by the lifecycle and responsive-layout repairs evaluated in the final Windows run. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the evaluated source state and the evidence supporting each result.

**修改后**
The implementation is identified by revision 7bd3552. Classification methods are documented by the training code provided by my supervisor, my training/validation records and the corresponding test outputs. The segmentation pathway follows the model and reference inference notebook provided by my supervisor. Appendix C identifies the software version and the source content evaluated in the final Windows run.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 2. 3.6.5

**修改前**
Automated results are labelled by environment, date and evaluated source state. On 19 October 2026, the final native Windows invocation completed all 370 tests with no failures, errors or skips. A preceding 131-test regression subset also passed; its count is not added to the full-suite total. Table 4.3 retains earlier invocations separately.

**修改后**
Automated results are labelled by environment, date and software version. On 19 October 2026, the final native Windows invocation completed all 370 tests with no failures, errors or skips. Table 4.3 presents this completed result; Appendix C retains the preceding regression subset and earlier execution history.

**原因**
Present the final result in the body and retain the full chronology in the appendix without adding subset counts.

## 3. 4.3.1

**修改前**
The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source includes the lifecycle and layout repairs; Appendix C records its baseline and per-file identity.

**修改后**
The final Windows invocation on 19 October 2026 completed the entire 370-test suite with 370 passed, 0 failed, 0 errors and 0 skipped, with 15 warnings in 194.10 seconds (exit 0). It used the native windows Qt platform, Python 3.10.22, PyQt5 5.15.11 and Qt 5.15.2. The evaluated source content is recorded in revision 7bd3552, as identified in Appendix C.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 4. 4.3.1 / Table 4.3

**修改前**
Table 4.3. Automated verification records by environment and evaluated source state

**修改后**
Table 4.3. Final Windows automated test result

**原因**
Focus the main results table on the completed target-platform test invocation.

## 5. 4.3.1 / Table 4.3

**修改前**
Source: dated pytest logs, XML summaries, exit codes and source-state records. The final Windows run began at 22:26 on 19 October 2026 (UTC+08:00); earlier invocations remain separate. Related subset counts are not additive.

**修改后**
Source: the full-suite pytest log and XML result of 19 October 2026, beginning at 22:26 (UTC+08:00). Appendix C provides the software version and earlier execution records.

**原因**
Use a concise source note and move execution chronology to the appendix.

## 6. 4.3.1

**修改前**
Before the full invocation, the related Windows subset passed 131 tests in 119.90 seconds with 15 warnings and exit 0. The full command selected no modules or individual cases and used no collection-error continuation. XML confirms 370 distinct passing cases and no skips. The 15 warnings concern deprecated Matplotlib/Pyparsing, PyTorch TypedStorage and Hugging Face download interfaces.

**修改后**
The suite ran without test-case selection and completed with no skipped tests. Its 15 warnings concern deprecated Matplotlib/Pyparsing, PyTorch TypedStorage and Hugging Face download interfaces. The 194.10-second duration measures automated testing, not application inference performance.

**原因**
Retain material qualifications while moving diagnostic subset details out of the main results narrative.

## 7. 4.3.1

**修改前**
The final Linux/offscreen invocation after the same repairs completed with 369 passed, 1 failed and no collection errors, with 14 warnings in 125.70 seconds. Its remaining failure checks availability of the real segmentation weight, which was absent from that installation. Earlier 17 and 19 October results in Table 4.3 document earlier source/resource states rather than the final Windows outcome.

**修改后**
[Removed; corresponding execution record retained in Appendix C.]

**原因**
Move the environment-specific missing-weight failure and earlier runs to Appendix C; do not omit them from the thesis.

## 8. 4.3.1

**修改前**
Earlier Windows invocations stopped first on the missing training-script prerequisite and later on a running-thread destruction fault. Restoring the genuine script and repairing thread lifetime, queued validation receivers and panel size policies resolved those observed failures in the final full invocation. Table 4.5 summarises the implementation causes and regression evidence.

**修改后**
Earlier Windows runs were interrupted by a missing training-script prerequisite and a worker-thread destruction fault. Restoring the genuine script and correcting worker lifetime, queued validation callbacks and panel size policies resolved the observed regression cases in the final suite. Table 4.5 summarises the implementation corrections; Appendix C retains the earlier run outcomes.

**原因**
Explain the resolved problems once rather than reproducing diagnostic chronology in the body.

## 9. Appendix C / Table C.2

**修改前**
0 skipped; native Qt; 15 warnings; 194.10 s; exit 0. Baseline plus reviewed repairs.

**修改后**
0 skipped; native Qt; 15 warnings; 194.10 s; exit 0. Source content recorded in revision 7bd3552.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 10. 4.3.1 / Table 4.3

**修改前**
Interpretation

**修改后**
Execution details

**原因**
Use a descriptive result-table heading.

## 11. 4.3.1 / Table 4.3

**修改前**
0 skipped; native Qt; 15 warnings; 194.10 s; exit 0. Baseline plus reviewed repairs.

**修改后**
0 skipped; 15 warnings; 194.10 s; exit 0. Source revision 7bd3552.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 12. 4.3.1 / Table 4.3; Appendix C / Table C.2

**修改前**
[["Run / environment", "Passed", "Failed", "Collection errors", "Interpretation"], ["Windows, 19 Oct; final full run", "370", "0", "0", "0 skipped; native Qt; 15 warnings; 194.10 s; exit 0. Baseline plus reviewed repairs."], ["Linux, 19 Oct; final full run", "369", "1", "0", "370 collected; 14 warnings; 125.70 s; exit 1. Real segmentation weight unavailable."], ["Linux, 19 Oct; before repairs", "358", "1", "0", "359 collected; 14 warnings; 104.68 s; exit 1. Real segmentation weight unavailable."], ["Windows, 19 Oct; 15:58 run", "Not final", "At least 2", "0 reported", "359 collected; runtime termination; exit 0xC0000409. No final summary."], ["Windows, 19 Oct 2026; first run", "Not run", "Not run", "1", "356 collected; collection interrupted; 13 warnings; 24.76 s; exit 2."], ["Linux, 17 Oct 2026", "355", "1", "1", "Continuation after collection errors; 14 warnings; 110.70 s."]]

**修改后**
Main table: final Windows result only. Appendix C.2: all six dated execution records retained, including collection errors, runtime termination and Linux resource failure.

**原因**
Separate final research results from the debugging chronology without concealing failed or incomplete invocations.

## 13. Appendix C.1

**修改前**
Source baseline: revision 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56, supplemented by the lifecycle and responsive-layout repairs evaluated on 19 October 2026. The passing Windows source state includes changes in nine production modules and four test modules. The evidence package preserves the tracked difference, the thirteen per-file checksums and the reviewed source supplement, including the new worker-lifetime test file; no new software commit is implied. Table C.1 identifies each execution record.

**修改后**
The evaluated application source is recorded in commit 7bd3552765af9d318a02bccd3e2469b95155dbe3, tagged cp2-windows-verified-2026-10-19. The commit was created on 20 October 2026 from the source content exercised by the completed Windows tests on 19 October; the repaired files match the recorded Windows source after line-ending normalisation. The original logs retain the pre-commit identifier 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56. Table C.1 lists the evaluation materials, and Table C.2 gives the execution history.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 14. Appendix C.2

**修改前**
The evidence archive separates the final completed invocations from earlier collection errors, runtime termination and diagnostic subsets. Windows completed 370 tests with no failures, errors or skips; its preceding 131-test subset is not added to that total. Linux completed 369 passing tests and one missing-segmentation-file availability failure. The default-Pillow patch evaluation remains the source of classification metrics, independently of these software-test counts.

**修改后**
Table C.2 distinguishes completed runs from collection errors and runtime termination. The final Windows run completed 370 tests with no failures, errors or skips. A preceding 131-test regression subset passed in 119.90 seconds with 15 warnings; its count is not added to the full-suite total. The final Linux/offscreen run completed with 369 passed, 1 failed and no collection errors in 125.70 seconds, with 14 warnings: the real segmentation weight was unavailable in that installation. Classifier performance is reported separately in Section 4.2.6.

**原因**
Keep concise environment-specific test interpretation and subset accounting in the appendix.

## 15. Appendix C.2 / Table C.2

**修改前**
[No execution-history table in the appendix.]

**修改后**
Table C.2. Automated test execution history; complete original six-run table and its source note.

**原因**
Retain failed and interrupted runs in an appropriate location, using the existing table and caption styles.

## 16. Appendix A / Table A.3

**修改前**
Revision 1f3e01e

**修改后**
Revision 7bd3552

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 17. Appendix A / Table A.3

**修改前**
Baseline plus lifecycle/layout repairs; evaluated source identified in Appendix C

**修改后**
Committed source matching the completed Windows regression; version identified in Appendix C.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 18. Appendix C / Table C.1

**修改前**
19 Oct 2026 originals: pytest-full.log, pytest.xml, pytest-exit-code.txt, commit.txt, test-date.txt and environment files

**修改后**
19 Oct 2026 Windows pytest log, XML result, exit code, test date and environment records

**原因**
Replace internal audit terminology with neutral descriptions of the research materials.

## 19. Appendix C / Table C.1

**修改前**
370 passed; 0 failed/errors/skipped; 15 warnings; 194.10s; evaluated baseline plus repairs

**修改后**
370 passed; 0 failed/errors/skipped; 15 warnings; 194.10 s; source content recorded in revision 7bd3552.

**原因**
Identify the unchanged, tested source by a committed revision; preserve the actual dates and original identifiers in execution records.

## 20. Appendix C / Table C.1

**修改前**
Final 19 Oct Linux full log/XML and source supplement

**修改后**
19 Oct 2026 Linux full-suite log, XML result and environment record

**原因**
Remove source-supplement wording now that the application state has a committed identifier.

## 21. 3.3.2

**修改前**
The formal nine-class run is identified by its manifests, completed metrics, checkpoint and test-7k outputs. Older three-class scripts and smoke-check experiments remain development materials and are not used to establish the CRC results. Training/validation file-path separation is verified; patient- or slide-level isolation requires grouping information not present in those manifests.

**修改后**
The formal nine-class run is identified by its manifests, completed metrics, checkpoint and test-7k outputs. Older three-class scripts and smoke-check experiments remain development materials and are not used to establish the CRC results. The internal training/validation manifests have disjoint image paths, but the stratified random split operates on patches and does not enforce patient- or slide-level separation.

**原因**
Attach the grouping limitation specifically to the internal split rather than implying that it establishes the external cohort design.

## 22. 4.2.6

**修改前**
The application-default Single image core therefore has a measured result on this labelled patch collection. Arbitrary 512-pixel source crops, tiled maps and physical-scale changes require their own ground-truth and scale design. Patient/slide independence and these generalisation limits are discussed in Section 4.5.3.

**修改后**
The application-default Single image core therefore has a measured result on this labelled patch collection. Arbitrary 512-pixel source crops, tiled maps and physical-scale changes require their own ground-truth and scale design. These generalisation limits are discussed in Section 4.5.3.

**原因**
Avoid repeating an overbroad patient-independence limitation and retain the measured native-patch scope.

## 23. 4.5.4

**修改前**
The immediate priorities are to complete formal real-image Windows acceptance, collect UAT responses and retain the passing regression suite as the baseline for further changes. The default application patch evaluation is complete; further model work should examine patient/slide grouping, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**修改后**
The immediate priorities are to complete formal real-image Windows acceptance, collect UAT responses and retain the passing regression suite as the baseline for further changes. The default application patch evaluation is complete; further model work should examine patient-grouped internal validation, different source dimensions and physical scale. Segmentation evaluation requires authorised aligned masks.

**原因**
Specify future grouped internal validation rather than implying that the external test must be redesigned to establish patient independence.

## 24. 5.2

**修改前**
Further evaluation should examine patient/slide-separated classifier performance, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Formal real-image Windows acceptance should complement the completed automated suite, which provides the regression baseline for subsequent development.

**修改后**
Further evaluation should examine patient- or slide-grouped internal validation, additional external cohorts, source-scale sensitivity, resize behaviour beyond native-sized patches and segmentation against authorised masks. Formal real-image Windows acceptance should complement the completed automated suite, which provides the regression baseline for subsequent development.

**原因**
Align future evaluation recommendations with the distinction between internal validation and the external test cohort.

## 25. Appendix E.1

**修改前**
The Windows summary records Single image, pillow_bilinear, RGB float32 raw255, input size 224 × 224 and 7,180 native 224 × 224 source images. Per-image CSVs independently reproduce 6,511 correct labels, the class-wise report and the confusion counts. All reference labels agree; the largest absolute probability difference is 0.002731651. This run does not exercise resizing of larger crops. Future studies should document patient/slide grouping, duplicate checks and physical scale, and define separate ground truth for Tiled analysis.

**修改后**
The Windows summary records Single image, pillow_bilinear, RGB float32 raw255, input size 224 × 224 and 7,180 native 224 × 224 source images. Per-image CSVs independently reproduce 6,511 correct labels, the class-wise report and the confusion counts. All reference labels agree; the largest absolute probability difference is 0.002731651. This run does not exercise resizing of larger crops. Future studies should add patient-grouped internal validation, duplicate checks and physical-scale analysis, and define separate ground truth for Tiled analysis.

**原因**
Retain the actual evaluation while making further internal-validation and spatial-analysis needs precise.

## 26. List of Tables

**修改前**
Old Table 4.3 caption; no Table C.2 entry.

**修改后**
Updated Table 4.3 caption and added linked Table C.2 entry.

**原因**
Synchronise the table list using existing fields and styles.

## 27. 4.2.6

**修改前**
The selected-epoch validation accuracy exceeds test accuracy by approximately 8.41 percentage points. Internal validation draws from the same 100,000-image pool as training, whereas the 7,180-image test is a separate collection. Class proportions also differ: ADI represents 10.41% of the 100K pool versus 18.64% of the test set, DEB 11.51% versus 4.72%, and MUS 13.54% versus 8.25%. These observed differences do not identify a single cause of the gap. Both validation and original test scripts use deterministic Resize, ToTensorV2 and float32 raw255; the Windows application-path rerun produces the same test labels and does not explain away that gap.

**修改后**
The selected-epoch validation accuracy exceeds external test accuracy by approximately 8.41 percentage points. Internal validation uses a stratified random patch-level split of the same 100,000-image pool as training, without patient grouping. In contrast, the CRC-VAL-HE-7K dataset documentation describes a test cohort of 50 patients with no patient overlap with NCT-CRC-HE-100K (Kather et al., 2018). The two estimates therefore assess different generalisation conditions. Class proportions also differ: ADI represents 10.41% of the 100K pool versus 18.64% of the test set, DEB 11.51% versus 4.72%, and MUS 13.54% versus 8.25%. These results do not isolate the contribution of patient grouping, cohort differences or class composition to the observed gap.

**原因**
Distinguish the external dataset cohort design described by the dataset documentation from the patch-level internal split, without treating a plausible explanation as a demonstrated cause.

## 28. 4.2.6

**修改前**
Training used the NCT-CRC-HE-100K.zip archive, identified as the standard normalised release rather than the separately named non-normalised alternative. The dataset authors’ repository documents that normalised 100K release and the availability of the alternative (Kather, n.d.). Stain normalisation of source images is distinct from numerical raw255/ImageNet tensor profiles. The test archive’s stain processing and acquisition matching were not independently characterised, so the score gap is not attributed to a proven stain mismatch.

**修改后**
Training used NCT-CRC-HE-100K.zip, the standard Macenko stain-normalised release, rather than the separately distributed NONORM version (Kather et al., 2018). The dataset documentation specifies 224 × 224 pixels at 0.5 μm/pixel for both NCT-CRC-HE-100K and CRC-VAL-HE-7K. Stain normalisation of source images is distinct from raw255 or ImageNet numerical preprocessing of input tensors. Both validation and original test scripts use deterministic Resize, ToTensorV2 and float32 raw255; the Windows application-default Pillow rerun preserves every external-test predicted label. The observed score gap is not evidence of a stain-processing mismatch.

**原因**
Cite the dataset record directly, specify the confirmed archive variant and distinguish source-image stain processing from tensor scaling and resize-backend comparison. Use the official description checked by the author on 20 October 2026; add nominal patch resolution without inventing a staining-based explanation for the score difference.

## 29. 4.2.6

**修改前**
Both the class-wise results and the lower macro-F1 show that a global accuracy number alone is insufficient. Patient/slide grouping, archive identity, stain characteristics and source resolution should be recorded in a follow-up evaluation. The current image-path checks establish disjoint file lists, not patient-level independence.

**修改后**
Both the class-wise results and the lower macro-F1 show that a global accuracy number alone is insufficient. The external test provides patient-independent patch evaluation according to the dataset design, while the internal validation score should not be interpreted as a patient-separated estimate. Patient-grouped internal validation and additional external cohorts would help assess how performance transfers across patients and collection conditions.

**原因**
Distinguish the external dataset cohort design described by the dataset documentation from the patch-level internal split, without treating a plausible explanation as a demonstrated cause.

## 30. 4.5.3

**修改前**
Classification performance is specific to its data and preprocessing. The 90.68% accuracy and 88.59% macro-F1 are reproduced by the original evaluation and the application-default Single image core on native 224 × 224 test patches. That agreement does not establish performance after resizing arbitrary source crops or under different physical scales. Stratified patch-level splitting and disjoint file paths do not establish patient/slide independence or exclude content duplicates. Calibration and tiled-map ground truth were not evaluated.

**修改后**
Classification performance is specific to its data and preprocessing. The 90.68% accuracy and 88.59% macro-F1 are reproduced by the original evaluation and the application-default Single image core on native 224 × 224 external-test patches. The dataset documentation identifies the external cohort as patient-independent from NCT-CRC-HE-100K; the internal training/validation split, however, is patch-based and does not enforce patient or slide separation (Kather et al., 2018). Its 99.09% validation accuracy may therefore be optimistic for cross-patient generalisation. The observed gap does not isolate a principal causal factor. Performance on arbitrary resized crops, different physical scales and tiled maps, together with calibration and content-duplicate checks, requires further evaluation.

**原因**
Distinguish the external dataset cohort design described by the dataset documentation from the patch-level internal split, without treating a plausible explanation as a demonstrated cause.

## 31. References

**修改前**
Kather, J.N. (n.d.) deep-stroma-histology: Code and dataset guidance for histological tissue classification. Project repository. https://github.com/jnkather/deep-stroma-histology

**修改后**
Kather, J.N., Halama, N. and Marx, A. (2018). 100,000 histological images of human colorectal cancer and healthy tissue (v0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.1214456

**原因**
Replace the code-repository citation with the version-specific dataset DOI; retain the manuscript’s author–year reference style. Use the author-confirmed authors, publication year and version. The published date is 7 April 2018; the later repository creation date is not used as the publication date.

## 32. 3.3.3

**修改前**
Source crop dimensions determine the field of view before resampling to 224 × 224. The interface keeps this choice explicit and labels the 512 × 512 starting value as unconfirmed relative to training scale. The evaluation consequences are discussed in Section 4.5.3.

**修改后**
Source crop dimensions determine the field of view before resampling to 224 × 224. The dataset’s nominal source-patch dimensions and resolution are documented in Section 4.2.6. The interface retains 512 × 512 as an editable starting value; its physical-scale equivalence to the training data is unverified for an arbitrary uploaded image. The evaluation consequences are discussed in Section 4.5.3.

**原因**
Distinguish the now documented training dataset geometry from the unverified physical scale of arbitrary application inputs.

## 33. 4.5.3

**修改前**
Large raster tiling is implemented, but native WSI pyramid reading, physical-scale extraction and memory-bounded streaming remain outside scope. Full-resolution arrays and restored masks consume memory. The editable 512 × 512 classification starting value has unconfirmed training-scale equivalence, and rectangular edge crops are resized to the fixed network input.

**修改后**
Large raster tiling is implemented, but native WSI pyramid reading, physical-scale extraction and memory-bounded streaming remain outside scope. Full-resolution arrays and restored masks consume memory. The source datasets have a nominal resolution of 0.5 μm/pixel, but the application does not establish the physical resolution of arbitrary raster inputs. Its editable 512 × 512 classification starting value therefore has unverified training-scale equivalence, and rectangular edge crops are resized to the fixed network input.

**原因**
Retain the real spatial-analysis limitation without incorrectly describing the published training dataset scale as unknown.

## 34. 5.3

**修改前**
The second contribution is a practical separation of inference semantics in the interface and stored metadata. Whole-image classification, tile-class coverage and segmentation pixel coverage remain distinguishable. Source-crop geometry, edge areas, resize choices, class order and the unconfirmed training scale are exposed rather than hidden behind a visually plausible output.

**修改后**
The second contribution is a practical separation of inference semantics in the interface and stored metadata. Whole-image classification, tile-class coverage and segmentation pixel coverage remain distinguishable. Source-crop geometry, edge areas, resize choices, class order and the unverified physical-scale equivalence of uploaded images are exposed rather than hidden behind a visually plausible output.

**原因**
Keep the contribution consistent with the documented dataset scale and the application’s limits on input-image physical metadata.

## 35. 3.7 / Table 3.7

**修改前**
UAT interpretation task and training-scale confirmation

**修改后**
UAT interpretation task and confirmation of the uploaded image’s physical scale

**原因**
Distinguish known dataset resolution from unknown physical resolution of a user-selected image.
