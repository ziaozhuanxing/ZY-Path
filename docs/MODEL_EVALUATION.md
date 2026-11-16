# Classification evaluation record

These are external CRC benchmark results, not software-test pass rates, GUI
demonstrations or clinical validation. No segmentation Dice/IoU is reported.

## Provenance and protocol

Li Ziyao trained a compact nine-class DenseNet using Sunway University GPU/HPC
resources and Slurm. The training script was supplied by the supervisor.
NCT-CRC-HE-100K supplied 80,002 training and 19,998 internal-validation patches,
stratified at patch level. Patient independence of that internal split is not
established. CRC-VAL-HE-7K supplied 7,180 external benchmark patches. The dataset
authors describe 50 external-test patients without overlap with the 100K
collection; see [dataset sources and counts](CRC_DATASET.md).

The original built-in checkpoint was selected at epoch 26 during training
through epoch 30. The continuation kept the original split and augmentation,
trained through epoch 100 and selected epoch 43 by **minimum internal validation
loss**. The final epoch was not automatically chosen. The continuation's external
evaluation ran on 9 November 2026 (Slurm job 8272).

Deterministic evaluation uses OpenCV colour decoding, BGR-to-RGB, linear resize
to 224 x 224 and float32 **raw255**. It does not divide by 255 or apply ImageNet
mean/std. Random training augmentations are absent from evaluation. The standard
training collection's prior stain normalisation is a separate operation.

The supplied evaluation used Python 3.10.22, PyTorch 2.1.2+cu121,
TorchVision 0.16.2+cu121, OpenCV 4.8.1 and Albumentations 1.3.1. It produced
per-image predictions, per-class scores, a confusion matrix and a summary.
The evaluation command used `best_model.pth`, CRC-VAL-HE-7K, batch 32,
two data-loader workers and CUDA. The archived evaluator is specific to the
compact DenseNet/raw255 contract; it must not be reused unchanged for DenseNet169.

## Traceable identities

| Resource | SHA-256 |
|---|---|
| Epoch-26 checkpoint | `8f89bd825641fba276066b54432b5d73a62b11ed6c0d70bb94c9f0bc7e2fe325` |
| Epoch-43 checkpoint | `56812c81b48e8b300f87951f91739c1b97bd87a253d16e72a583ee218c3e80f2` |
| Training script | `c2e9f7b0c124e9f1cc9d4a9d27e0f70e788bd2e7bffb6ad8609307c535cf135e` |
| Evaluation script | `c8484688dff111f4c47a3d96cfa60cdd65d2395986ed2018ed4ad04aebef6d23` |
| Train manifest | `94054eaa7969572cee2e62b8925a3940824b44525db1f921c0222f413f994618` |
| Validation manifest | `1af808bf7c4e04a0f4b08f80cec865efc0384b794c59e2913b78176e89e11d1f` |

The original HPC Git HEAD was not recorded in the supplied evaluation. It is
therefore **null** in the machine-readable records; a later application commit
is not substituted for it. The script hashes establish the available source
identity. This limits commit-level reproduction of the original run.

## Results

| Measure | Epoch 26 | Epoch 43 |
|---|---:|---:|
| Correct / total | 6,511 / 7,180 | 6,553 / 7,180 |
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

All epoch-43 class scores are below. Values are percentages, rounded only for display.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| ADI | 98.86 | 83.93 | 90.78 | 1,338 |
| BACK | 100.00 | 100.00 | 100.00 | 847 |
| DEB | 74.56 | 99.41 | 85.21 | 339 |
| LYM | 96.63 | 99.37 | 97.98 | 634 |
| MUC | 90.94 | 96.04 | 93.42 | 1,035 |
| MUS | 64.21 | 80.91 | 71.60 | 592 |
| NORM | 94.33 | 94.33 | 94.33 | 741 |
| STR | 91.35 | 62.71 | 74.37 | 421 |
| TUM | 96.41 | 95.70 | 96.05 | 1,233 |

The aggregate improvement is modest and is not uniform. DEB and MUC F1 decrease;
TUM recall decreases from 96.43% to 95.70%. Internal validation accuracy near
99.57% for the selected candidate is distinct from external accuracy of 91.267%.
Repeated use of a public benchmark is not a prospective clinical validation cohort.

## Records and verification scope

- [Epoch-26 summary](evaluation/epoch26-summary.json),
  [class scores](evaluation/epoch26-classification_report.csv) and
  [confusion matrix](evaluation/epoch26-confusion_matrix.csv).
- [Epoch-43 summary](evaluation/epoch43-summary.json),
  [class scores](evaluation/epoch43-classification_report.csv) and
  [confusion matrix](evaluation/epoch43-confusion_matrix.csv).

Confusion-matrix rows are ground-truth classes and columns are predictions, in
ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM order. The summaries retain full
precision, checkpoint and prediction-CSV hashes, counts and available dependencies.
Raw weights, images and per-image prediction files are not redistributed here.

The repository maintainer independently recalculated these scores from supplied
prediction rows and checked the matrices and reports. This is an arithmetic audit,
**not a new inference run over the original 7,180 images**. The current checkout
does not contain those original external-test images. For a new evaluation, record
the exact committed evaluator, checkpoint/input profile, dataset identity,
preprocessing, dependency versions and untouched output files before reporting
scores. Select checkpoints using development data, not the external benchmark.

The ImageNet-pretrained DenseNet169 comparison is ongoing. No independent
test score or claim that it outperforms the compact classifier is made here.
Segmentation needs corresponding lawful ground-truth masks and a defined
protocol before any Dice/IoU evaluation.
