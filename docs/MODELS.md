# Models and image interpretation

## Built-in resources

| Task | Expected file | Application path |
|---|---|---|
| Classification | models/crc_dn21_seed42_best.pth | DenseNet checkpoint, nine classes |
| Segmentation | models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth | UPerNet Swin Base state dictionary, nine separate classes |

Weights are separate resources and are not distributed by this source
repository. Keep their original provenance and permissions when sharing them.
Li Ziyao trained the classification checkpoints on NCT-CRC-HE-100K using
Sunway University GPU/HPC resources and Slurm. Their architecture is a compact
custom DenseNet: growth rate 32, blocks (2, 2, 2, 2), 64 initial features,
bn_size 4, drop rate 0 and nine outputs; it has 416,457 parameters. It is not
TorchVision's DenseNet169 and has no ImageNet initialisation.
The classification checkpoint was trained by the project author using a
supervisor-provided training script; the application filename is a renamed copy
of best_model.pth. A separately verified epoch-43 CRC candidate, selected after
100 training epochs, can be imported with its companion input profile; see
[CRC model update](CRC_MODEL_UPDATE.md). The original built-in weights remain
separate for comparison and recorded reruns.
The segmentation model and inference notebook were provided
by the supervisor. The project author has confirmed PanopTILs as its training
dataset. The particular UPerNet training crop/resampling pipeline and independent
Dice/IoU reports have not been established; identifying the dataset does not
establish those settings.

The segmentation contribution is integration of the supplied model and inference
workflow, including preprocessing, overlap/blending, UI workers and visualisation.
Li Ziyao did not train this UPerNet/Swin model or originate those architectures.

| Classification checkpoint | Selected epoch | SHA-256 |
|---|---:|---|
| Original built-in `crc_dn21_seed42_best.pth` | 26 | `8f89bd825641fba276066b54432b5d73a62b11ed6c0d70bb94c9f0bc7e2fe325` |
| Importable `crc_dn21_seed42_epoch43_best.pth` | 43 | `56812c81b48e8b300f87951f91739c1b97bd87a253d16e72a583ee218c3e80f2` |

An ImageNet-pretrained DenseNet169 comparison is a separate, ongoing HPC
experiment. Its nine-output architecture has 12,499,465 parameters and uses
RGB /255 followed by ImageNet mean/std. That convention must not be applied
to the raw255 compact DenseNet checkpoints. No independent CRC test score is
claimed for DenseNet169. See the [evaluation record](MODEL_EVALUATION.md) for
the completed compact-model experiments and their limitations.

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

Loading occurs on CPU and prepares the model for evaluation. An explicit
[input profile](INPUT_PROFILES.md) supplies the boundary dimensions and
normalisation for validation. Without a profile, the legacy probe is
(1, 3, 224, 224). The adapted output must be finite and have:

- classification shape (1, C), with at least two class logits or declared probabilities;
- segmentation shape (1, C, H, W), with nonzero spatial dimensions.

Saved task defaults additionally require the detected task to match the chosen
Classification or Segmentation default. The built-in CRC checkpoint validates
its expected input, preprocessing and class metadata. Tiled analysis separately
checks compatible geometry, model-specific distinct labels, ordered distinct colours and
matching preprocessing metadata.

These checks establish supported execution and output compatibility. They do
not validate model accuracy, tissue-label semantics, stain consistency or
clinical applicability. Load only trusted model files: deserialization can
execute code.

## Classification input and resizing

The built-in classifier uses RGB, float32, raw255 values and a 224 x 224 network
input. raw255 preserves values in the 0-255 range; it does not divide by 255 or
apply ImageNet normalization.

New classification analyses decode with OpenCV IMREAD_COLOR, convert BGR to
RGB and use OpenCV linear (cv2.INTER_LINEAR). This also matches the training
reader's treatment of bit depth and image orientation; resizing a Pillow-decoded
image alone is not sufficient to establish equality. The deterministic
training/validation Resize operation used Albumentations
with OpenCV; recorded versions were Albumentations 1.3.1 and OpenCV 4.8.1.
Installed versions appear in System Information. Matching these operations does
not reproduce every dependency. Random flips, hue augmentation and rotation are
training-only; prediction deliberately uses the validation transform.

At the first upgrade, the former Pillow default changes to OpenCV. Subsequent
explicit choices persist. Pillow bilinear remains a legacy comparison/custom
model option. New records save both image_decoder and resize_backend. Records
without image_decoder retain the former Pillow RGB reader when restored or
re-run; they do not inherit a new decoder from current preferences. Comparisons,
source previews and PDF reports use the same recorded source decoder as the
classification result, including image orientation. Segmentation retains its
own image reader, numerical normalisation and resizing.

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
The application reads explicit calibration or accepts known manual MPP; it
does not estimate physical resolution from appearance or automatically apply
Macenko stain normalization. **Match physical scale** combines calibrated image
MPP with the selected model's documented tissue field.

224 x 224 source pixels is the new starting tile size. Existing custom tile
dimensions are kept; Reset Classification explicitly restores 224 x 224 and
OpenCV linear. At the dataset's 0.5 MPP this represents 112 x 112 micrometres.
Matching a new source's physical scale still requires its actual MPP. For
example, a 0.25 MPP source needs approximately 448 x 448 source pixels for that
same field; a 512-pixel crop at 0.5 MPP instead covers 256 micrometres per side.
The application does not infer this from pixel dimensions or assume that an
uploaded image has the dataset's MPP. In legacy pixel mode, each crop, including
partial edge crops, is resized to the network input. In physical mode, complete
fields are used with explicit skip or reflect edges. Consequently,
one 512-pixel crop can present different tissue context than one dataset patch.

See [CRC dataset and input contract](CRC_DATASET.md) for sources, class counts
and the distinction between dataset stain normalisation and tensor scaling.

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
The received notebook does not establish a physical MPP target. The reference
adapter therefore applies no assumed 0.5 MPP calibration. Other documented
segmentation input contracts use their own profiles and standard adapter.

The [PanopTILs authors' code](https://github.com/PathologyDataScience/MuTILs_Panoptic)
links the same dataset site and documents region and nucleus annotations. Its
`configs/region_GTcodes.csv` distinguishes raw annotation codes from the region
superclasses; the superclass indices 1-8 correspond to the tissue categories
used by the supplied notebook. Raw annotation masks require that mapping before
evaluation. Region coverage is not a count of individual lymphocytes.

That repository's reference model is MuTILs, not this supplied UPerNet. Its
configuration includes original, high-power and ROI sampling levels, and its
WSI configuration contains colour-normalisation settings. These are evidence
about the reference implementation, not a licence to copy its physical fields
or stain-normalisation procedure into an independently trained UPerNet model.

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
& .\.venv\Scripts\python.exe scripts\audit_classification_tiles.py --model models\crc_dn21_seed42_best.pth --image YOUR_IMAGE.png --tile-width 224 --tile-height 224 --resize-backend opencv_linear --image-decoder opencv_color --output tile-check.json
```

This checks implementation consistency; it does not establish biological
classification accuracy or validate the physical scale of the source.
