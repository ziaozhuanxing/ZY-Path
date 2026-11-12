# CRC dataset and deterministic input contract

## Sources and verification scope

The source record is [Kather, Halama and Marx (2018), Zenodo v0.1,
DOI 10.5281/zenodo.1214456](https://zenodo.org/records/1214456).
The project author's 20 October 2026 verification of that record confirms the
published date of 7 April 2018, patch size, nominal MPP, Macenko description,
50 external-test patients and absence of patient overlap between the two
collections. A fresh direct request from the development environment on
4 November 2026 returned HTTP 403, so this document does not claim a new
complete retrieval of the record or verification of its current licence text.

The dataset authors' [deep-stroma-histology repository](https://github.com/jnkather/deep-stroma-histology)
was accessible on 4 November 2026. It links this DOI and explicitly distinguishes
the normalised 100K training edition from the separately available
non-normalised edition. The project author confirms downloading
`NCT-CRC-HE-100K.zip`, not the NONORM archive. The supplied training script,
split manifests, deployed checkpoint and external prediction CSV provide the
project-specific configuration and counts below. They are separate sources
from the dataset description.

## Collections

| Property | NCT-CRC-HE-100K | CRC-VAL-HE-7K |
|---|---|---|
| Use here | Training pool and internal validation | External CRC evaluation |
| Total patches | 100,000 | 7,180 |
| Patch dimensions | 224 x 224 pixels | 224 x 224 pixels |
| Nominal sampling | 0.5 micrometres/pixel | 0.5 micrometres/pixel |
| Nominal field of view | 112 x 112 micrometres | 112 x 112 micrometres |
| Domain | H&E colorectal tissue, nine tissue categories | H&E colorectal tissue, same categories |
| Patient relationship | Dataset training collection | 50 colorectal adenocarcinoma patients; no patient overlap with 100K according to the dataset record |

This is a tissue-category classification task. A patch label is not a whole
slide diagnosis, tumour grade, patient prognosis or a segmentation annotation.
The collection does not establish applicability to breast or lung tissue.

## Ordered labels and project evidence counts

The model output order comes from the supplied training script and checkpoint,
not from a display palette. The 100K column is independently counted from the
supplied train/validation manifests combined; the external column is counted
from the supplied 7,180-row prediction CSV's true_class field. These are
manifest/evaluation-record counts, not a new download audit of all image files.

| Output | Label | Tissue category | 100K pool | External records |
|---:|---|---|---:|---:|
| 0 | ADI | Adipose tissue | 10,407 | 1,338 |
| 1 | BACK | Background | 10,566 | 847 |
| 2 | DEB | Debris | 11,512 | 339 |
| 3 | LYM | Lymphocytes | 11,557 | 634 |
| 4 | MUC | Mucus | 8,896 | 1,035 |
| 5 | MUS | Smooth muscle | 13,536 | 592 |
| 6 | NORM | Normal colonic mucosa | 8,763 | 741 |
| 7 | STR | Cancer-associated stroma | 10,446 | 421 |
| 8 | TUM | Colorectal adenocarcinoma epithelium | 14,317 | 1,233 |
| | | Total | 100,000 | 7,180 |

The project's internal split is 80,002 training and 19,998 validation patches,
stratified at patch level. Disjoint file paths do not make that split
patient-disjoint. The external dataset's published patient independence applies
between collections; it does not change the internal split's unit.

## Stain normalisation versus numerical scaling

The standard 100K images are already Macenko colour-normalised. The supplied
training script does not perform an additional online Macenko transform. It
preserves the decoded RGB 0-255 values as float32: raw255 is a numerical input
convention, not a stain-normalisation algorithm.

For the compact raw255 DenseNet checkpoints, do not add ImageNet mean/std,
divide by 255, normalise an already-normalised
dataset again, or choose an arbitrary Macenko template to make an uploaded
image look similar. Such changes require a separately defined and evaluated
pipeline. The application currently does not automatically stain-normalise
uploaded images. Detailed staining/acquisition parameters or a normalisation
template absent from the available sources are not inferred.

This numerical contract is specific to those checkpoints. The separate
ImageNet-pretrained DenseNet169 experiment uses /255 and ImageNet mean/std,
recorded in its own model metadata. Dataset stain normalisation and tensor
normalisation remain distinct operations. See [model provenance](MODELS.md)
and the [completed evaluation records](MODEL_EVALUATION.md).

## Validation-to-application contract

The deterministic validation operations in the supplied script are:

1. OpenCV imread with IMREAD_COLOR: eight-bit, three-channel colour decoding.
2. OpenCV BGR-to-RGB conversion.
3. Albumentations Resize(224, 224), using OpenCV INTER_LINEAR.
4. ToTensorV2 channel-first layout, then float32 with the 0-255 range retained.

The application adds a leading batch dimension and uses evaluation/inference
mode. Its new default performs these corresponding operations in both Single
image and Tiled analysis. OpenCV byte decoding is used if a Windows Unicode
filename cannot be opened through the filename API. Channel order, source
orientation and bit-depth handling are retained consistently in the result,
history restore and PDF source panel.

Vertical/horizontal flips, HueSaturationValue, rotation and random crop in the
training transform are augmentation. They are not missing inference steps.
Ordinary prediction uses the deterministic validation path. The recorded
training environment used OpenCV 4.8.1 and Albumentations 1.3.1; the application
reports its installed versions. Operation-level parity in an installed
environment is not a claim that all codec/library versions are identical.

New preferences start at 224 x 224 source pixels. Existing custom source
dimensions remain editable and are not silently overwritten. A 224-pixel crop
matches the dataset's 112-micrometre field only when the source is also 0.5 MPP.
A 0.25 MPP source would need about 448 source pixels per side for that field.
File dimensions, desktop DPI and apparent cell size do not supply missing MPP.
Partial edge crops still use their real pixels and the documented resize;
they can present a different field of view from a full crop.

The previous Pillow resize default is migrated once to OpenCV. Explicit Pillow
choices made after that are respected. History without image_decoder keeps
Pillow RGB decoding and its saved resize; it is not rewritten to appear as a
new run. Neither a preprocessing correction nor more training epochs is a new
accuracy result. An independent labelled evaluation is needed to measure the
resulting model performance.
