# CRC classification candidate: epoch 43

The 100-epoch continuation completed on 9 November 2026. Minimum internal
validation loss selected epoch 43, not the final epoch. The supplied best
checkpoint has SHA-256
`56812c81b48e8b300f87951f91739c1b97bd87a253d16e72a583ee218c3e80f2`.
It retains the custom DenseNet architecture with block configuration
`(2, 2, 2, 2)` and 416,457 parameters; it is not DenseNet121.

## Import without changing the existing built-in model

1. Keep the original `models/crc_dn21_seed42_best.pth` for existing analyses.
2. Name the new weight file `crc_dn21_seed42_epoch43_best.pth`.
3. Copy the matching JSON from `model_profiles/` beside those weights, keeping
   its complete name `crc_dn21_seed42_epoch43_best.pth.zypath-model.json`.
4. Select Classification, clear Use Built-in Model, and choose the new `.pth`
   using Browse Model. The companion JSON loads automatically after its weight
   checksum and class order have been checked. Model input shows the contract.
5. Use Settings > Models to save a validated classification startup default
   if desired. Browsing alone changes the current session's selection.

Both files may be kept in `models/` or another stable local folder. Moving the
weights without their companion JSON loses the declared image reader and
physical field. Keep their names and association together. Historical reruns
still require their recorded original weights and paths.

This is a data-only addition. Existing model-profile loading supports this
checkpoint; the inference implementation and segmentation pipeline are unchanged.
No automatic built-in replacement or Windows release acceptance is implied.

## Input contract

Ordered labels are ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR and TUM.
The deterministic path is OpenCV IMREAD_COLOR, BGR-to-RGB, INTER_LINEAR resize
to 224 x 224 and float32 raw255. There is no division by 255 or ImageNet
normalisation. Training hue augmentation remains p=1 and is not used at inference.

The training collection's nominal 0.5 micrometres/pixel and 224-pixel patches
establish a nominal 112 x 112 micrometre reference field. This is a model
requirement, not an inferred calibration for uploaded images. Physical matching
requires the actual image MPP; otherwise use pixel mode. For a 0.252 MPP image,
matching selects a 444 x 444 native crop before resizing to 224 x 224.
Source detail and staining still affect applicability. Dataset stain
normalisation and tensor numerical scaling are distinct; see
[CRC dataset](CRC_DATASET.md) and [input profiles](INPUT_PROFILES.md).

## Independent CRC-VAL-HE-7K results

The supplied GPU evaluation covered the same 7,180 labelled patches as the
earlier comparison. These results describe that dataset, not arbitrary uploaded
images or other tissue sites. Percentages below are rounded.

| Metric | Previous epoch-26 checkpoint | New epoch-43 checkpoint |
|---|---:|---:|
| Correct predictions | 6,511 | 6,553 |
| Accuracy | 90.682% | 91.267% |
| Macro-F1 | 0.885879 | 0.893046 |
| MUS precision | 61.24% | 64.21% |
| MUS recall | 73.14% | 80.91% |
| MUS F1 | 66.67% | 71.60% |
| STR precision | 79.14% | 91.35% |
| STR recall | 65.80% | 62.71% |
| STR F1 | 71.85% | 74.37% |
| MUS predicted as STR | 73 | 24 |
| STR predicted as MUS | 74 | 81 |

DEB and MUC F1 decreased; TUM recall decreased from 96.43% to 95.70%.
The candidate has better aggregate scores but is not uniformly better by class.
Retain the earlier model and assess the intended workflow before changing its
default. Internal validation used a random patch split, not a verified
patient-disjoint split. Epoch 43 internal validation accuracy of 99.57% is
separate from the independent-test accuracy of 91.267%.

The supplied prediction CSVs allow arithmetic and paired-record checks.
Recomputing their metrics does not rerun inference on the original test images.
