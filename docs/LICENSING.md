# Licensing and attribution review

No blanket MIT or other root licence has been added. A public GitHub repository
is not itself a grant covering all code, images, fonts, models and datasets.
The author/institution should confirm ownership and the terms for shared
training/inference material before choosing a source-code licence.

| Component | Current position |
|---|---|
| ZY-Path application code | Source is visible; no general reuse licence selected in this repository. |
| Supervisor-supplied segmentation checkpoint/notebook | Externally provided research resources; no redistribution permission established here. Weights/notebook are not included in this update. |
| Classification weights | Trained by the author with a supervisor-provided script; weights are not committed or licensed by this update. |
| CRC images/dataset | Kather, Halama and Marx, [Zenodo record 1214456](https://doi.org/10.5281/zenodo.1214456). Dataset terms govern the source images; the screenshots credit the single public patch and describe the montage adaptation. |
| PanopTILs | Dataset identified by the supervisor as the segmentation training source; no dataset or original images are redistributed here. |
| PyQt5 | Installed package declares **GPL v3**; commercial licensing is another upstream option. A source-code MIT label alone would not resolve bundled Qt/PyQt distribution obligations. |
| PyTorch / TorchVision | BSD-family licences in the installed distributions. |
| Transformers / OpenCV | Apache 2.0 in the reviewed installed distributions. |
| Pillow / NumPy / Matplotlib | HPND / BSD-family / PSF-style terms respectively; retain upstream notices applicable to distributed versions. |
| fpdf2 / pypdf | fpdf2 declares LGPLv3+; pypdf retains its own BSD-style licence. |
| Bundled Noto Sans SC font | SIL Open Font License 1.1; [font source and hashes](../assets/fonts/README.md), [included OFL text](../assets/fonts/OFL-NotoSansSC.txt). |
| Logo and project-specific graphics | Present in the project; original creation/ownership is not documented as an independent reusable asset licence. No new licence is assigned here. |

This is an inventory of the available evidence, not clearance to redistribute a
portable application with every external resource. Before publishing a binary,
review the exact bundled dependencies/notices and confirm model and dataset
permissions. The current portfolio does not publish a Windows binary or the
supervisor's weights. See [release acceptance](WINDOWS_RELEASE.md).

The screenshot gallery uses a publicly released, de-identified CRC example with
dataset attribution; it does not publish previously supplied breast images of
unclear public-display provenance. Consult the original dataset record's terms
before reusing the underlying imagery. The current audit did not retrieve and
relicense the full dataset or grant any additional rights to it.
