# Classification tiles

The CRC loader's `_validate_crc_densenet_metadata` checks RGB/in_channels=3,
224×224 network input, raw255 and the ordered classes
ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM. `Preprocessor.transform`
converts to RGB float32, bilinearly resizes, and leaves values in 0–255 for raw255.
The training source was subsequently supplied as an attachment (see evidence below);
production weights are still absent from this checkout.
**Neither original crop dimensions nor magnification/resolution can be inferred
from the network input.** Their training-scale match remains unconfirmed.

In Settings → Preferences, enable large-image classification tiles and set
original-image tile width and height in pixels. This is off by default.
The editable 512×512 starting value is exploratory only, not a training claim;
224×224 remains the network input independently of crop size.
A compatible model must have the exact checkpoint class order and raw255 profile;
unknown/mismatched metadata causes an explanatory error rather than assigning
segmentation labels. Smaller images (both dimensions no greater than the chosen
tile) retain single-image classification. Segmentation is unchanged.

Tiles form a non-overlapping grid. Right/bottom partial crops use only real image
pixels, then resize to the network input; there is no padding, overlap or hidden
background filtering. Every pixel contributes once. The table lists each box
(x0,y0,x1,y1), predicted class and softmax confidence. Class counts include partial
tiles once; area ratios weight actual crop pixels and use the full image as the
denominator. The record summary is the area-weighted mean of tile probabilities,
not a second whole-image prediction or a pixel segmentation confidence.

The fixed classification display palette v1 is independent of segmentation:

| Class | RGB |
|---|---|
| ADI | 230,159,0 |
| BACK | 210,210,210 |
| DEB | 86,180,233 |
| LYM | 0,158,115 |
| MUC | 240,228,66 |
| MUS | 0,114,178 |
| NORM | 213,94,0 |
| STR | 204,121,167 |
| TUM | 120,60,140 |

Results display original and color map with nine-class legend/statistics and a
read-only tile table. The actual model path, classification task, parameters,
edge policy, ordered colors, tile predictions, counts and area ratios are saved
as analysis JSON in the existing artifact storage and in a result JSON sidecar.
History restores that analysis without consulting current settings. PNG export
writes `<filename>.png.json` with the same metadata; PDF includes class statistics,
colors, parameters and tile details. The map remains at original image dimensions.

Advanced use: a checkpoint may include `classification_tiles` metadata, or a
`<model>.pth.classification-tiles.json` sidecar with `tile_size`, `input_size`,
`classes`, `colors`, `preprocess`, and `scale_status`. Size values are [width,height],
colors are nine distinct RGB triples in the exact checkpoint class order.
Settings explicitly enabled by the user take precedence; otherwise declared model
metadata can activate tiling. Metadata cannot substitute for missing checkpoint
class/preprocessing information. Do not mark dimensions as training-confirmed
without actual evidence. No example model files are installed by this feature.

Known full-suite issues retained: missing real built-in model weights cause one
test failure; missing `models/dn21_folder_classification/train_crc_dn21 (1).py`
causes one collection error. No tests are removed or skipped to hide these.

## Uploaded training evidence

The supplied `train_crc_dn21.py` declares the same ordered nine CRC classes and
DenseNet block configuration (2,2,2,2). `TissueDataset.__getitem__` reads with
OpenCV, converts BGR to RGB, applies the transform and casts to float. Validation
uses `A.Resize(224,224)` followed by `ToTensorV2()`; there is no Normalize or
0–1 scaling. Checkpoint/config output explicitly saves `preprocess=raw255`,
`input_size=[224,224]`, and the ordered classes.

Training augmentation also starts with Resize(224,224), then flips, color/rotation
augmentation and RandomSizedCrop in that already resized coordinate system.
This does not establish the original source-image crop size or its physical scale.
Dataset dimensions/magnification require the original split manifests or dataset
provenance. Keep exploratory tile geometry marked unconfirmed.

The supplied `config.py` describes a thyroid three-class pipeline
(c0-non-thyroid, c1-benign, c2-malignant); it is not imported by the CRC training
script. Its patch_size=224 is not evidence for CRC source tile geometry.
Neither attachment defines a classification display palette.

Resize fidelity remains a limitation: the training source uses Albumentations
Resize (without an explicit interpolation argument or dependency version), whereas
current inference uses Pillow BILINEAR. RGB/range/shape are confirmed; numerical
resize equivalence has not been established. Do not claim exact preprocessing
reproduction for resized source images without resolving this implementation and
version difference.

The attachment includes normalize_model_settings and validate_resume_config;
all three existing resume-helper semantic cases were checked directly against
these real functions without importing training dependencies or starting training.
This is not a full pytest run or a fix to the repository test path. The uploaded
source has not been copied over the legacy models/.../train_crc_dn21 (1).py path,
so the previously reported collection error remains unresolved in the checkout.

Attachment `train_crc_dn21.py` SHA-256: `c2e9f7b0c124e9f1cc9d4a9d27e0f70e788bd2e7bffb6ad8609307c535cf135e`.

Attachment `config.py` SHA-256: `23bb8a2268f5bc4dd651b4509d4f606688793d2366d6598cc1b161ad2a0d8288`.
