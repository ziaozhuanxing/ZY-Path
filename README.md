# ZY-Path CP2 thesis materials

## Latest native Windows result and startup correction — 3 November 2026

The uploaded fbe152a complete native Windows run recorded **584 passed, 1 failed, 0 errors and 0 skipped among 585 cases**. The sole failure concerns restoring a maximized startup window to its saved 520 × 360 normal size. It is not an all-pass execution. Source and genuine model/training resources remained unchanged.

The narrow correction is software revision **63ce699411b3ad1350864286b7b28902cd7d136c**. Its original size/persistence assertions and 1500 ms timeout are retained, with new failure diagnostics and four additional regressions. Native Windows verification of the correction is still required. The current manuscript links below are the preceding dated draft; the new failure and corrected source will be consolidated into its result/history after that verification is supplied.

- [Result and fix explanation](windows-startup-correction-2026-11-03/Windows_Startup_Restore_Fix.md)
- [Verified Windows result](windows-startup-correction-2026-11-03/Verified_Windows_585_Result.json)
- [Exact source/test changes](windows-startup-correction-2026-11-03/Startup_Restore_Fix.diff)
- [Collector: startup checks first, then complete suite](windows-startup-correction-2026-11-03/Windows_Tools/Collect_Windows_Evidence.py)

The new collector's `--check-startup-first` option stops early with diagnostics if the startup cases fail, and otherwise invokes the complete unfiltered suite. The two executions retain separate logs/XML; their counts must not be summed. Raw machine-specific evidence remains in the private submission materials.

## Preceding manuscript draft — 3 November 2026

- [Editable Word thesis](final-corrections-2026-11-03/LiZiYao_24018160_CP2_Thesis_Updated.docx)
- [PDF thesis — 119 pages](final-corrections-2026-11-03/LiZiYao_24018160_CP2_Thesis_Updated.pdf)
- [Correction list: location, before, after and reason](final-corrections-2026-11-03/Correction_Changes.md)
- [Document checks](final-corrections-2026-11-03/Document_Checks.json)
- [Actual Word fields and PDF contents-page audit](final-corrections-2026-11-03/Navigation_Field_Audit.json)
- [Reference/citation locations](final-corrections-2026-11-03/Citation_Locations.md)
- [Figure/table mentions in the prose](final-corrections-2026-11-03/Figure_Table_Locations.md)
- [Supporting-material inventory](final-corrections-2026-11-03/Supporting_Materials_Inventory.csv)
- [Complete native Windows test collector](final-corrections-2026-11-03/Windows_Tools/Collect_Windows_Evidence.py)

This edition restores 172 functional PAGEREF fields within three structurally valid TOC fields. Each actual Word cached page label and each visible PDF contents-list label was independently checked against the target's actual body page and printed footer. It also restores the distinct existing control in risk R10, distinguishes analysis/export/capture dates, uses British optimiser in prose and identifies the manual table as summaries of the author's confirmed detailed checklist outcomes.

The cover retains Semester 8 and 5 November 2026. All 56 required numbered sections, five chapters, 20 figures, 24 tables, 32 references and 53 author/year citation links remain. Original image pixels, display dimensions and alternative descriptions are retained. Figure whitespace, plain black solid tables and table source-note placement have been checked.

### Evidence described in that manuscript draft

That draft identifies source **fbe152a5e4bbe14ad6dcc682468ad571d2efd33c**. The author confirmed W01–W15 on 2 November 2026 at Windows 11 Home Chinese Edition 22H2 (22621.3593), 175% scaling and 2560 × 1600 resolution. The 21:59:01 UTC+08:00 timestamp identifies environment capture; no individual task timings or other display scales are inferred.

The draft retains the earlier **548 passed, 0 failed, 0 errors, 0 skipped at d9fb8e5** record. The fbe152a execution had not yet been supplied when that draft was prepared. Its subsequently uploaded 584/585 result is recorded at the top of this page; the corrected source is 63ce699 and still requires native Windows verification. Use the new startup-first collector linked above for that verification, rather than the older draft collector.

The original classifier result remains 90.68% accuracy and 88.59% macro-F1 on 7,180 native-sized CRC-VAL-HE-7K patches. UAT remains ten participants, mean SUS 74.50 (sample SD 10.66), with 72 independent and 22 assisted completions among 96 evaluable attempts. Original negative outcomes and limitations remain.

Private supporting materials contain the original test logs/XML/manifests, source differences, manual records and participant workbook. They remain outside the public update. The listed original PNG for Figure 4.6 was not supplied; the genuine exported PDF and its JSON are retained. Capture dates are not inferred from analysis timestamps.

## Earlier editions

- [2 November manual-acceptance edition](final-manual-acceptance-2026-11-02)
- [Windows regression and layout edition](windows-verified-2026-11-02)

Only this thesis-materials branch is updated. The software branch and main are unchanged.