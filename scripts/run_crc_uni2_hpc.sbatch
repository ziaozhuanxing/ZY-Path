#!/bin/bash
#SBATCH --job-name=crc-uni2-h
#SBATCH --account=fet_student
#SBATCH --partition=gpu-2c-l40s-1g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=08:00:00
#SBATCH --output=uni2-crc-%j.log

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: sbatch scripts/run_crc_uni2_hpc.sbatch /path/to/official/UNI2-h/pytorch_model.bin" >&2
    exit 2
fi

crc_repo=${SLURM_SUBMIT_DIR:-"$PWD"}
cd "$crc_repo"
crc_weights=$1
crc_work=${CRC_WORK:-"$crc_repo/dn21_folder_classification"}
crc_python=${CRC_PY:-"$HOME/.venvs/zypath-crc-eval/bin/python"}
crc_baseline=${CRC_BASELINE:-"$crc_work/experiments/crc-dn169-imagenet-seed42-hue05/best_model.pth"}
crc_test=${CRC_TEST:-"$crc_repo/data/CRC-VAL-HE-7K"}
crc_output="$crc_work/experiments/uni2-h-crc-${SLURM_JOB_ID:?Submit with sbatch}"

for file in "$crc_weights" "$crc_baseline" "$crc_work/splits/seed42/train.json" "$crc_work/splits/seed42/val.json"; do
    if [[ ! -f "$file" || ! -r "$file" ]]; then
        printf 'Required file is unavailable: %s\n' "$file" >&2
        exit 2
    fi
done

if [[ ! -x "$crc_python" || ! -d "$crc_test" || -e "$crc_output" ]]; then
    printf 'Check Python, the CRC test directory and the new output path: %s | %s | %s\n' \
        "$crc_python" "$crc_test" "$crc_output" >&2
    exit 2
fi

"$crc_python" -c 'import torch, torchvision, timm
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable in the evaluation environment.")
if tuple(int(v) for v in torch.__version__.split("+")[0].split(".")[:2]) < (2, 6):
    raise SystemExit("The ZY-Path baseline checkpoint loader requires PyTorch 2.6 or newer.")
print(f"Device: {torch.cuda.get_device_name(0)} | torch: {torch.__version__} | timm: {timm.__version__}")'

printf 'Output directory: %s\n' "$crc_output"
exec "$crc_python" -u scripts/probe_crc_foundation.py \
    --baseline "$crc_baseline" --uni2-h-weights "$crc_weights" \
    --train-manifest "$crc_work/splits/seed42/train.json" \
    --val-manifest "$crc_work/splits/seed42/val.json" \
    --test-root "$crc_test" --batch-size 8 --workers 2 --device cuda \
    --output-dir "$crc_output"
