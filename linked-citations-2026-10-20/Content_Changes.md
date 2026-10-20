# 引用位置与可点击来源：逐项修改清单

正文五段的引用归属调整，以及每处引用的链接目标。文献条目、作者—年份计数和研究结果未变。

## 1. 1.1 / architecture background

**修改前**
Convolutional neural networks support classification and segmentation through learned visual representations. DenseNet provides feature reuse through dense connectivity, while encoder–decoder and multiscale architectures support spatial prediction (Huang et al., 2017; Ronneberger et al., 2015; Xiao et al., 2018). Their practical use also depends on apparently small implementation choices: the channel order, numerical range, interpolation method, class order and image scale must agree with the model's requirements. A visually convincing result does not by itself demonstrate that these choices are correct.

**修改后**
Convolutional neural networks support classification and segmentation through learned visual representations. DenseNet provides feature reuse through dense connectivity (Huang et al., 2017). U-Net illustrates an encoder–decoder approach to spatial prediction (Ronneberger et al., 2015), while UPerNet combines multiscale processing for scene parsing (Xiao et al., 2018). Their practical use also depends on apparently small implementation choices: the channel order, numerical range, interpolation method, class order and image scale must agree with the model’s requirements. A visually convincing result does not by itself demonstrate that these choices are correct.

**原因**
Place each source immediately after the specific platform, architecture or technology claim it supports; retain author–year citations and the existing evidence.

## 2. 1.1 / QuPath, Slideflow and WSInfer

**修改前**
Existing pathology platforms offer graphical inspection and analysis: QuPath provides an extensible image-analysis environment, Slideflow Studio supports whole-slide visualisation, and WSInfer integrates reusable pretrained models with QuPath (Bankhead et al., 2017; Dolezal et al., 2024; Kaczmarzyk et al., 2024). ZY-Path addresses a focused workflow within this landscape by connecting supported local model loading, distinct analysis modes, spatial inspection and persistent inference records in one desktop application.

**修改后**
Existing pathology platforms offer graphical inspection and analysis. QuPath provides an extensible image-analysis environment (Bankhead et al., 2017). Slideflow Studio supports whole-slide visualisation (Dolezal et al., 2024). WSInfer integrates reusable pretrained models with QuPath (Kaczmarzyk et al., 2024). ZY-Path addresses a focused workflow within this landscape by connecting supported local model loading, distinct analysis modes, spatial inspection and persistent inference records in one desktop application.

**原因**
Place each source immediately after the specific platform, architecture or technology claim it supports; retain author–year citations and the existing evidence.

## 3. 2.2.2 / classification architectures

**修改前**
Image classification assigns a category to an image or patch, whereas semantic segmentation assigns categories to spatial locations. ZY-Path supports both tasks through separate model pathways. Residual networks, DenseNet and EfficientNet illustrate alternative classification designs based on residual learning, dense feature reuse and compound scaling respectively (He et al., 2016; Huang et al., 2017; Tan & Le, 2019).

**修改后**
Image classification assigns a category to an image or patch, whereas semantic segmentation assigns categories to spatial locations. ZY-Path supports both tasks through separate model pathways. Residual networks use shortcut connections (He et al., 2016), DenseNet uses dense feature reuse (Huang et al., 2017), and EfficientNet applies compound scaling (Tan & Le, 2019).

**原因**
Place each source immediately after the specific platform, architecture or technology claim it supports; retain author–year citations and the existing evidence.

## 4. 2.2.3 / U-Net, UPerNet and Swin

**修改前**
U-Net established an influential encoder–decoder approach to biomedical segmentation with skip connections that preserve spatial information (Ronneberger et al., 2015). UPerNet instead combines multiscale feature processing for scene parsing; the current built-in integration reconstructs a UPerNet model with a Swin Base backbone through Transformers (Xiao et al., 2018; Liu et al., 2021). U-Net is relevant background, not the architecture of the built-in segmentation checkpoint.

**修改后**
U-Net established an influential encoder–decoder approach to biomedical segmentation with skip connections that preserve spatial information (Ronneberger et al., 2015). UPerNet combines multiscale feature processing for scene parsing (Xiao et al., 2018). The current built-in integration reconstructs UPerNet through Transformers using a Swin Base backbone (Liu et al., 2021). U-Net is relevant background, not the architecture of the built-in segmentation checkpoint.

**原因**
Place each source immediately after the specific platform, architecture or technology claim it supports; retain author–year citations and the existing evidence.

## 5. 2.6 / technology stack

**修改前**
PyQt5 supplies windows, layouts, signals and worker threads (Riverbank Computing, n.d.; The Qt Company, n.d.). QGraphicsView provides source-coordinate transformations, linked navigation and vector grid painting. PyTorch supplies model execution and inference_mode (Paszke et al., 2019); NumPy and Pillow support image conversion (NumPy Developers, n.d.; Pillow Contributors, n.d.). Matplotlib renders the Single image probability chart (Hunter, 2007), and fpdf2 generates structured PDF reports (fpdf2 Contributors, n.d.). These choices connect the interface to a local scientific-Python stack without a web backend.

**修改后**
PyQt5 supplies windows, layouts, signals and worker threads (Riverbank Computing, n.d.). Qt’s QGraphicsView provides source-coordinate transformations, linked navigation and vector grid painting (The Qt Company, n.d.). PyTorch supplies model execution and inference_mode (Paszke et al., 2019). NumPy supports array-based image conversion (NumPy Developers, n.d.), while Pillow supplies image decoding and resampling (Pillow Contributors, n.d.). Matplotlib renders the Single image probability chart (Hunter, 2007), and fpdf2 generates structured PDF reports (fpdf2 Contributors, n.d.). These choices connect the interface to a local scientific-Python stack without a web backend.

**原因**
Place each source immediately after the specific platform, architecture or technology claim it supports; retain author–year citations and the existing evidence.

## 6. Citation hyperlink style

**修改前**
Body citations were plain text.

**修改后**
Use the named Hyperlink character style for clickable citations.

**原因**
Make links recognisable while preserving the existing body font and original styles.

## 7. References / [1]–[32]

**修改前**
No individual reference bookmarks.

**修改后**
Add a unique bookmark to each unchanged reference entry; books without a verified external URL link to their entry.

**原因**
Provide a dependable internal destination without inventing publication links.

## 8. 1.1 Background and Motivation / paragraph 202

**修改前**
Litjens et al., 2017

**修改后**
Litjens et al., 2017 → https://doi.org/10.1016/j.media.2017.07.005

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 9. 1.1 Background and Motivation / paragraph 202

**修改前**
Kather et al., 2019

**修改后**
Kather et al., 2019 → https://doi.org/10.1371/journal.pmed.1002730

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 10. 1.1 Background and Motivation / paragraph 204

**修改前**
(Huang et al., 2017)

**修改后**
(Huang et al., 2017) → https://arxiv.org/abs/1608.06993

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 11. 1.1 Background and Motivation / paragraph 204

**修改前**
(Ronneberger et al., 2015)

**修改后**
(Ronneberger et al., 2015) → https://doi.org/10.1007/978-3-319-24574-4_28

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 12. 1.1 Background and Motivation / paragraph 204

**修改前**
(Xiao et al., 2018)

**修改后**
(Xiao et al., 2018) → https://arxiv.org/abs/1807.10221

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 13. 1.1 Background and Motivation / paragraph 205

**修改前**
(Bankhead et al., 2017)

**修改后**
(Bankhead et al., 2017) → https://doi.org/10.1038/s41598-017-17204-5

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 14. 1.1 Background and Motivation / paragraph 205

**修改前**
(Dolezal et al., 2024)

**修改后**
(Dolezal et al., 2024) → https://doi.org/10.1186/s12859-024-05758-x

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 15. 1.1 Background and Motivation / paragraph 205

**修改前**
(Kaczmarzyk et al., 2024)

**修改后**
(Kaczmarzyk et al., 2024) → https://doi.org/10.1038/s41698-024-00499-9

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 16. 1.3 Hypothesis / paragraph 222

**修改前**
Brooke, 1996

**修改后**
Brooke, 1996 → #bib_ref_18

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 17. 1.3 Hypothesis / paragraph 222

**修改前**
Bangor et al., 2009

**修改后**
Bangor et al., 2009 → #bib_ref_01

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 18. 2.2.1 Digital histopathology and the unit of analysis / paragraph 266

**修改前**
(Litjens et al., 2017)

**修改后**
(Litjens et al., 2017) → https://doi.org/10.1016/j.media.2017.07.005

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 19. 2.2.1 Digital histopathology and the unit of analysis / paragraph 267

**修改前**
(Kather et al., 2019)

**修改后**
(Kather et al., 2019) → https://doi.org/10.1371/journal.pmed.1002730

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 20. 2.2.2 Classification architectures and pretrained deployment / paragraph 270

**修改前**
(He et al., 2016)

**修改后**
(He et al., 2016) → https://doi.org/10.1109/CVPR.2016.90

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 21. 2.2.2 Classification architectures and pretrained deployment / paragraph 270

**修改前**
(Huang et al., 2017)

**修改后**
(Huang et al., 2017) → https://arxiv.org/abs/1608.06993

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 22. 2.2.2 Classification architectures and pretrained deployment / paragraph 270

**修改前**
(Tan & Le, 2019)

**修改后**
(Tan & Le, 2019) → https://proceedings.mlr.press/v97/tan19a.html

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 23. 2.2.2 Classification architectures and pretrained deployment / paragraph 271

**修改前**
(Huang et al., 2017)

**修改后**
(Huang et al., 2017) → https://arxiv.org/abs/1608.06993

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 24. 2.2.2 Classification architectures and pretrained deployment / paragraph 272

**修改前**
He et al., 2016

**修改后**
He et al., 2016 → https://doi.org/10.1109/CVPR.2016.90

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 25. 2.2.2 Classification architectures and pretrained deployment / paragraph 272

**修改前**
Tan & Le, 2019

**修改后**
Tan & Le, 2019 → https://proceedings.mlr.press/v97/tan19a.html

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 26. 2.2.3 Semantic segmentation and multiscale context / paragraph 275

**修改前**
(Ronneberger et al., 2015)

**修改后**
(Ronneberger et al., 2015) → https://doi.org/10.1007/978-3-319-24574-4_28

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 27. 2.2.3 Semantic segmentation and multiscale context / paragraph 275

**修改前**
(Xiao et al., 2018)

**修改后**
(Xiao et al., 2018) → https://arxiv.org/abs/1807.10221

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 28. 2.2.3 Semantic segmentation and multiscale context / paragraph 275

**修改前**
(Liu et al., 2021)

**修改后**
(Liu et al., 2021) → https://arxiv.org/abs/2103.14030

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 29. 2.2.4 Tiled classification, coverage and confidence / paragraph 279

**修改前**
(Guo et al., 2017)

**修改后**
(Guo et al., 2017) → https://proceedings.mlr.press/v70/guo17a.html

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 30. 2.2.5 No-code interaction and transparent constraints / paragraph 283

**修改前**
(Kaczmarzyk et al., 2024)

**修改后**
(Kaczmarzyk et al., 2024) → https://doi.org/10.1038/s41698-024-00499-9

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 31. 2.2.5 No-code interaction and transparent constraints / paragraph 284

**修改前**
(Gamma et al., 1994)

**修改后**
(Gamma et al., 1994) → #bib_ref_19

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 32. 2.2.7 Human-centred design and evaluation / paragraph 289

**修改前**
(Yen & Bakken, 2012)

**修改后**
(Yen & Bakken, 2012) → https://doi.org/10.1136/amiajnl-2010-000020

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 33. 2.2.7 Human-centred design and evaluation / paragraph 289

**修改前**
(Nielsen, 1994)

**修改后**
(Nielsen, 1994) → https://doi.org/10.1145/191666.191729

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 34. 2.2.7 Human-centred design and evaluation / paragraph 290

**修改前**
(Brooke, 1996)

**修改后**
(Brooke, 1996) → #bib_ref_18

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 35. 2.2.7 Human-centred design and evaluation / paragraph 290

**修改前**
Bangor et al. (2009)

**修改后**
Bangor et al. (2009) → #bib_ref_01

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 36. 2.2.7 Human-centred design and evaluation / paragraph 291

**修改前**
(Brooke, 1996)

**修改后**
(Brooke, 1996) → #bib_ref_18

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 37. 2.3.1 QuPath / paragraph 294

**修改前**
(Bankhead et al., 2017)

**修改后**
(Bankhead et al., 2017) → https://doi.org/10.1038/s41598-017-17204-5

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 38. 2.3.2 Slideflow and Slideflow Studio / paragraph 297

**修改前**
(Dolezal et al., 2024)

**修改后**
(Dolezal et al., 2024) → https://doi.org/10.1186/s12859-024-05758-x

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 39. 2.3.3 WSInfer and QuPath integration / paragraph 300

**修改前**
(Kaczmarzyk et al., 2024)

**修改后**
(Kaczmarzyk et al., 2024) → https://doi.org/10.1038/s41698-024-00499-9

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 40. 2.3.4 Cytomine / paragraph 303

**修改前**
(Marée et al., 2016)

**修改后**
(Marée et al., 2016) → https://doi.org/10.1093/bioinformatics/btw013

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 41. 2.3.5 Commercial environments / paragraph 306

**修改前**
(Aiforia, n.d.)

**修改后**
(Aiforia, n.d.) → https://www.aiforia.com/aiforia-create

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 42. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 320

**修改前**
Kreibich, 2010

**修改后**
Kreibich, 2010 → #bib_ref_20

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 43. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 320

**修改前**
SQLite, n.d.

**修改后**
SQLite, n.d. → https://sqlite.org/zeroconf.html

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 44. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(Riverbank Computing, n.d.)

**修改后**
(Riverbank Computing, n.d.) → https://www.riverbankcomputing.com/static/Docs/PyQt5/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 45. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(The Qt Company, n.d.)

**修改后**
(The Qt Company, n.d.) → https://doc.qt.io/qt-5/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 46. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(Paszke et al., 2019)

**修改后**
(Paszke et al., 2019) → https://proceedings.neurips.cc/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 47. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(NumPy Developers, n.d.)

**修改后**
(NumPy Developers, n.d.) → https://numpy.org/doc/stable/user/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 48. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(Pillow Contributors, n.d.)

**修改后**
(Pillow Contributors, n.d.) → https://pillow.readthedocs.io/en/stable/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 49. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(Hunter, 2007)

**修改后**
(Hunter, 2007) → https://doi.org/10.1109/MCSE.2007.55

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 50. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 321

**修改前**
(fpdf2 Contributors, n.d.)

**修改后**
(fpdf2 Contributors, n.d.) → https://github.com/py-pdf/fpdf2

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 51. 2.6 Technological Infrastructure and Implementation Considerations / paragraph 323

**修改前**
(PyInstaller Development Team, n.d.)

**修改后**
(PyInstaller Development Team, n.d.) → https://pyinstaller.org/en/stable/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 52. 3.2.3 Ethical Considerations / paragraph 352

**修改前**
(PyTorch Contributors, n.d.)

**修改后**
(PyTorch Contributors, n.d.) → https://pytorch.org/docs/stable/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 53. 3.2.4 Accessibility Compliance / paragraph 355

**修改前**
(W3C, 2023)

**修改后**
(W3C, 2023) → https://www.w3.org/TR/WCAG22/

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 54. 3.4.1 Principles and information hierarchy / paragraph 417

**修改前**
Nielsen, 1994

**修改后**
Nielsen, 1994 → https://doi.org/10.1145/191666.191729

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 55. 3.4.1 Principles and information hierarchy / paragraph 417

**修改前**
Yen & Bakken, 2012

**修改后**
Yen & Bakken, 2012 → https://doi.org/10.1136/amiajnl-2010-000020

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 56. 4.2.6 Classification training and test results / paragraph 534

**修改前**
(Kather et al., 2018)

**修改后**
(Kather et al., 2018) → https://doi.org/10.5281/zenodo.1214456

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 57. 4.2.6 Classification training and test results / paragraph 535

**修改前**
(Kather et al., 2018)

**修改后**
(Kather et al., 2018) → https://doi.org/10.5281/zenodo.1214456

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 58. 4.4.2 Quantitative Results / paragraph 577

**修改前**
(Brooke, 1996)

**修改后**
(Brooke, 1996) → #bib_ref_18

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 59. 4.5.3 Limitations and Constraints / paragraph 606

**修改前**
(Kather et al., 2018)

**修改后**
(Kather et al., 2018) → https://doi.org/10.5281/zenodo.1214456

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.

## 60. B.4 System Usability Scale questionnaire / paragraph 705

**修改前**
(Brooke, 1996)

**修改后**
(Brooke, 1996) → #bib_ref_18

**原因**
Link the unchanged author–year citation to the existing source URL or the corresponding book reference entry.
