# ZY-Path CP2 thesis materials

## Latest content review revision — 19 October 2026

- [Editable Word content revision](content-revision-2026-10-19/LiZiYao_24018160_CP2_Thesis_Content_Revision.docx)
- [PDF content review copy](content-revision-2026-10-19/LiZiYao_24018160_CP2_Thesis_Content_Revision.pdf)
- [Complete revised package](content-revision-2026-10-19/LiZiYao_24018160_CP2_Content_Revision_Package.zip)
- [Read first (Chinese)](content-revision-2026-10-19/README_本轮先读.md)
- [Detailed before/after change log](content-revision-2026-10-19/Content_Changes.md)

The revised PDF has 98 pages. This is a content review draft using the existing document styles; final formatting follows content approval. It incorporates genuine classification training/evaluation materials and the 19 October Windows logs. The latest Windows pytest invocation stopped during collection with 1 error, 13 warnings, exit code 2 and no obtained pass count; the historical Linux results are retained separately. No new application pytest run was performed during document editing.

UAT, seven screenshot groups and cover semester/submission date remain reserved. Segmentation accuracy, repeated runtime measurements and clean-machine/offline package validation are explicitly unverified. Windows sharing logs redact only the local username and hostname, with both original and sharing checksums recorded. No model weights or supervisor source code are redistributed in the revised package.

To download everything, select **Code → Download ZIP**, or open the complete revised package and choose **Download raw file**. The application branch remains unchanged; this documents-only branch is not a software update.

## Original 17 October draft (retained for comparison)


This independent documents-only branch contains the CP2 thesis and evaluation materials. It does not change the application branch or `main`.

## Downloads

- [Editable Word thesis](LiZiYao_24018160_CP2_Thesis.docx)
- [PDF review copy](LiZiYao_24018160_CP2_Thesis.pdf)
- [Complete package: thesis, questionnaire, scoring workbook, diagrams, evidence and revision notes](LiZiYao_24018160_CP2_Package.zip)
- [SHA-256 checksums](SHA256SUMS.txt)

Open a file and use **Download raw file**, or choose **Code → Download ZIP** on this branch to download everything. No Python or Git installation is required to read these documents.

## Document status

These are review drafts based on application commit `1f3e01e7866d1b1f78103d817214f7dbb1cc5a56`. The thesis is 89 pages. Actual UAT responses and independent model evaluation results have not yet been supplied; the package includes blank evaluation materials and clearly marked pending evidence. Cover date/semester and the listed screenshots also require confirmation or completion.

The recorded application test result is **355 passed, 1 failed, 1 collection error**. The two known missing-file issues are preserved: unavailable real model weights and the missing `models/dn21_folder_classification/train_crc_dn21 (1).py` training script. This document publication does not constitute a new test run.

## 中文说明

本分支仅用于下载论文资料，不是软件更新分支。点击上方完整资料包链接后，选择 Download raw file；也可以在此分支页面选择 Code → Download ZIP。解压完整资料包后，请先阅读 `README_先读我.md`、修订说明及补图与待补证据清单。UAT 和独立模型评估尚无实际结果，未编造实验数据。