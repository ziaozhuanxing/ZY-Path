# Models and image interpretation

## Built-in resources

| Task | Expected file | Application path |
|---|---|---|
| Classification | models/crc_dn21_seed42_best.pth | DenseNet checkpoint, nine classes |
| Segmentation | models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth | UPerNet Swin Base state dictionary, nine separate classes |

Weights are separate resources and are not distributed by this source
repository. Keep their original provenance and permissions when sharing them.
The classification checkpoint was trained by the project author using a
supervisor-provided training script; the application filename is a renamed copy
of best_model.pth. The segmentation model and inference notebook were provided
by the supervisor. Segmentation training data/provenance and independent
Dice/IoU reports have not been established.

Source execution of built-in UPerNet requires the existing local
openmmlab/upernet-swin-base configuration cache. Runtime loading uses
local_files_only=True. The Windows build bundles that configuration for frozen
execution; a fresh-machine offline run still needs actual acceptance testing.

## Compatibility validation

ModelLoader accepts .pt and .pth files up to 500 MiB. Supported representations
are TorchScript, a saved PyTorch module that the environment can deserialize,
supported architecture checkpoints and the recognized UPerNet state dictionary.
An arbitrary state dictionary without reconstructable architecture information
is not automatically supported.

Loading occurs on CPU and prepares the model for evaluation. A float32 probe
with shape (1, 3, 224, 224) checks that the adapted output is finite and has:

- classification shape (1, C), with at least one class;
- segmentation shape (1, C, H, W), with nonzero spatial dimensions.

Saved task defaults additionally require the detected task to match the chosen
Classification or Segmentation default. The built-in CRC checkpoint validates
its expected input, preprocessing and class metadata. Tiled analysis separately
checks compatible geometry, nine distinct labels, ordered distinct colours and
matching preprocessing metadata.

These checks establish supported execution and output compatibility. They do
not validate model accuracy, tissue-label semantics, stain consistency or
clinical applicability. Load only trusted model files: deserialization can
execute code.

## Classification input and resizing

The built-in classifier uses RGB, float32, raw255 values and a 224 x 224 network
input. raw255 preserves values in the 0-255 range; it does not divide by 255 or
apply ImageNet normalization.

Pillow bilinear remains the application default. OpenCV linear uses
cv2.INTER_LINEAR. The training/evaluation Resize operation used Albumentations
with OpenCV; recorded versions were Albumentations 1.3.1 and OpenCV 4.8.1.
Installed versions appear in System Information. Choosing OpenCV linear does
not reproduce every dependency or training augmentation.

The two implementations can produce different pixels when resizing and
therefore different predictions. The selected backend is applied consistently
to single images and individual classification crops and is retained for rerun.
Agreement on already-224 x 224 patches does not imply agreement on larger crops.

Other supported models use their available preprocessing profile. The generic
ImageNet profile scales to 0-1 and applies the standard ImageNet mean/std.
Confirm the model's training convention before use.

## Source scale and network input

The classification dataset is described by
[Kather, Halama and Marx (2018), Zenodo](https://doi.org/10.5281/zenodo.1214456).
NCT-CRC-HE-100K contains 224 x 224 patches at nominal 0.5 micrometres/pixel;
its standard edition is Macenko colour-normalized. CRC-VAL-HE-7K contains
7,180 patches from 50 patients with no patient overlap with the 100K dataset.
The project's internal random patch split is not thereby patient-disjoint.

Dataset patch geometry is separate from the resolution of an uploaded image.
The application does not automatically measure physical resolution or apply
Macenko stain normalization to that image.

512 x 512 source pixels is an editable starting tile size. Physical-scale
matching and optimality have not been verified. Each real crop, including
partial edge crops, is resized to the 224 x 224 network input. Consequently,
one 512-pixel crop can present different tissue context than one dataset patch.

## Classification palette

These fixed display colours are independent of segmentation and do not change
the model's ordered output labels.

| Order | Class | RGB |
|---:|---|---|
| 0 | ADI | 230, 159, 0 |
| 1 | BACK | 210, 210, 210 |
| 2 | DEB | 86, 180, 233 |
| 3 | LYM | 0, 158, 115 |
| 4 | MUC | 240, 228, 66 |
| 5 | MUS | 0, 114, 178 |
| 6 | NORM | 213, 94, 0 |
| 7 | STR | 204, 121, 167 |
| 8 | TUM | 120, 60, 140 |

Custom classification tile metadata may be stored in the checkpoint or in
`<model>.pth.classification-tiles.json`. It declares `tile_size`, `input_size`,
`classes`, `colors`, `preprocess` and optional `scale_status`/`resize_backend`.
Dimensions are [width, height]; colours must match checkpoint class order.
The selected run parameters and recorded rerun metadata are validated against
the loaded model. Metadata does not silently enable tiled mode or establish a
training-scale match.

## Segmentation path and palette

Built-in UPerNet inference uses source tiles of 1000 pixels, stride 512,
224 x 224 network input and ImageNet numerical normalization. Small sources
are reflect-padded to the segmentation tile size. Overlapping class
probabilities are fused with a Hann-derived weight window, then the label map
is restored with nearest-neighbour interpolation and cropped to source size.
These are segmentation parameters, not classification Preferences settings.

| ID | Segmentation class | RGB |
|---:|---|---|
| 0 | Exclude | 0, 0, 0 |
| 1 | Cancerous epithelium | 255, 0, 0 |
| 2 | Stroma | 0, 255, 0 |
| 3 | TILs | 0, 0, 255 |
| 4 | Normal epithelium | 255, 255, 0 |
| 5 | Junk/Debris | 128, 0, 128 |
| 6 | Blood | 0, 255, 255 |
| 7 | Other | 255, 165, 0 |
| 8 | Whitespace/Empty | 255, 255, 255 |

Segmentation predictions are not ground truth for the classifier. Tile-class
coverage and segmentation pixel coverage are different measurements.

## Classification diagnostics

scripts/audit_classification_tiles.py compares representative real crops from
the first, middle and final tiles with standalone crop inference. It reports
tensor equality, labels/probabilities, source boxes and resize pixel differences.
The image and genuine model must be accessible on the machine running it.

```powershell
& .\.venv\Scripts\python.exe scripts\audit_classification_tiles.py --model models\crc_dn21_seed42_best.pth --image YOUR_IMAGE.png --tile-width 512 --tile-height 512 --resize-backend pillow_bilinear --output tile-check.json
```

This checks implementation consistency; it does not establish biological
classification accuracy or validate the physical scale of the source.
