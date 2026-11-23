# CRC classification experiments

The **Review** control in **Tile details** filters crops whose top model score
is below 90%. These are individual crop scores, including when the viewer
shows a fused map. The filter keeps the crop numbers and the original results
available. A high score can also be incorrect.

## Compare single-pass and multi-view inference

Use a verified nine-class CRC checkpoint with its ZY-Path input profile, and
the 7,180 original CRC-VAL-HE-7K patches in their class folders. Both methods
use the checkpoint's normal decoding and preprocessing. D4 averages the
original prediction with seven rotations and reflections. Selective D4
applies that average to crops whose original top score is below 90%.
The reported selective pass count is calculated from the evaluated outputs;
runtime is measured for the baseline and full D4 passes.

Run from the ZY-Path checkout on Sunway HPC. These experiments reuse the
application's restricted checkpoint loader, which needs PyTorch 2.6 or newer.
Use a separate environment so the existing training environment can keep its
original versions. For a GPU node with CUDA 12.4 driver support, for example:

```bash
"$HOME/.conda/envs/zypath-train/bin/python" -m venv "$HOME/.venvs/zypath-crc-eval"
CRC_PY="$HOME/.venvs/zypath-crc-eval/bin/python"
"$CRC_PY" -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
"$CRC_PY" -m pip install 'numpy>=1.26,<1.27' 'Pillow>=10,<11' opencv-python-headless==4.11.0.86
```

```bash
CRC_PY="$HOME/.venvs/zypath-crc-eval/bin/python"
CRC_WORK="$HOME/ZY-Path/dn21_folder_classification"
CRC_MODEL="$CRC_WORK/experiments/crc-dn169-imagenet-seed42-hue05/best_model.pth"
CRC_TEST="$HOME/ZY-Path/data/CRC-VAL-HE-7K"
srun -A fet_student -p gpu-2c-l40s-1g --gres=gpu:1 \
  --cpus-per-task=4 --mem=16G --time=02:00:00 \
  "$CRC_PY" scripts/benchmark_crc_classifier.py \
  --model "$CRC_MODEL" --test-root "$CRC_TEST" \
  --output-dir "$CRC_WORK/experiments/dn169-d4-comparison"
```

Keep the same test images for both methods. Compare macro-F1, both directions
of MUS/STR confusion and the additional inference time. Review coverage and
retained accuracy have a different denominator from overall accuracy.
The output includes per-image scores, counts, a confusion matrix and the
verified model profile. CRC-VAL-HE-7K is an existing external benchmark.
Use a new patient-independent cohort to substantiate any change chosen after
seeing results on it.

## Compare a pathology-pretrained representation

[MahmoodLab UNI2-h](https://github.com/mahmoodlab/UNI) provides a frozen H&E
and IHC encoder and examples of fitting a linear classifier on its features.
Request access from the [official weight page](https://huggingface.co/MahmoodLab/UNI2-h)
and place the downloaded checkpoint in private storage. From the project
root, use the separate evaluation environment prepared above:

```bash
"$HOME/.venvs/zypath-crc-eval/bin/python" -m pip install timm==1.0.22 safetensors
sbatch scripts/run_crc_uni2_hpc.sbatch "$HOME/private/UNI2-h/pytorch_model.bin"
```

Replace the weight path if it differs on your account. The job writes
`uni2-crc-JOBID.log` in the submission directory and saves the comparison
under `dn21_folder_classification/experiments/uni2-h-crc-JOBID`. Its first
GPU step verifies the encoder with a batch of development patches. The
probe fits the classification head on development training patches, records
validation separately, and evaluates DenseNet and the probe on identical
test records. Compare `baseline_test_total` with `uni2_h_test_total` for
the full test pass, including image loading and excluding model loading.
The existing development split is stratified at patch level.
Any evidence of patient-level independence must come from its provenance.
The saved head is a research artifact for use with the same authorized
encoder.
