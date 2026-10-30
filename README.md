# ZY-Path CP2 thesis materials

## Latest: clean diagrams and plain Word tables — 30 October 2026

- [Download editable Word thesis](current-software-2026-10-27/LiZiYao_24018160_CP2_Thesis_Updated.docx)
- [Download PDF review copy — 108 pages](current-software-2026-10-27/LiZiYao_24018160_CP2_Thesis_Updated.pdf)
- [Download complete materials package](current-software-2026-10-27/LiZiYao_24018160_CP2_Updated_Package.zip)
- [36 figure/table revision records](current-software-2026-10-27/Content_Changes.md)
- [Chinese revision summary](current-software-2026-10-27/README_先读.md)
- [Diagram SVG/PNG masters and reproducible builder](current-software-2026-10-27/Figure_Builder)
- [Figure/table presentation checks](current-software-2026-10-27/Evidence/Figure_Table_Presentation_Checks.json)
- [Citation locations](current-software-2026-10-27/Citation_Locations.md)
- [Figure/table prose references](current-software-2026-10-27/Figure_Table_Locations.md)
- [Verified Windows result](current-software-2026-10-27/Evidence/Verified_Windows_508_Summary.json)

Figures 3.1 and 3.3–3.6 have been rebuilt with explicit orthogonal routes, separated labels and consistent spacing. Figure 3.2 remains unchanged after inspection. Worker inheritance in Figure 3.5 now matches the code: InferenceEngine derives through _OwnedWorkerThread; PdfExportWorker directly derives from QThread.

All 31 Word tables, including the seven evidence placeholder boxes, now use plain Table Grid with white cells, black text and 0.5-point solid black internal/outer borders. Coloured headers and banded shading are removed. Table text and data, manuscript prose, citation destinations and existing research results remain unchanged. Five diagram image parts are replaced; other images remain unchanged. All five revised images share their final PDF page with their caption, and table pagination/source notes have been checked.

The 108-page PDF includes refreshed contents and 172 checked cached page references. The 32 references, 53 black non-underlined citation links, 20 figures and 24 numbered tables retain their existing prose mentions. Screenshots, UAT and cover placeholders retain their actual unfilled status. No new evaluation evidence is fabricated.

Application source remains **3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5**. Its previously verified native Windows result is unchanged: **508 passed, 0 failed, 0 errors, 0 skipped**, 16 warnings, exit 0, pytest summary 268.74 seconds. This revision changes only thesis presentation and supporting materials; software tests are not rerun. The software branch and main remain unchanged.

Previous editorial changes are retained in Editorial_Review_20261027_Changes, and the 90-record Windows-evidence revision list remains in Windows_508_Evidence_Content_Changes. Existing dated Windows records and correction diffs remain available. Private meeting notes and unrelated platform-test attachments stay excluded.
