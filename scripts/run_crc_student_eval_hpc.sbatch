#!/bin/bash
#SBATCH --job-name=crc-student-eval
#SBATCH --account=fet_student
#SBATCH --partition=gpu-2c-l40s-1g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=crc-student-eval-%j.log

set -euo pipefail
if [[ $# -ne 2 || ! "$1" =~ ^[0-9]+$ || ! "$2" =~ ^[0-9]+$ ]]; then
    echo "Usage: sbatch scripts/run_crc_student_eval_hpc.sbatch SUPERVISED_JOB DISTILLED_JOB" >&2
    exit 2
fi
crc_repo=${SLURM_SUBMIT_DIR:-"$PWD"}
cd "$crc_repo"
crc_work=${CRC_WORK:-"$HOME/ZY-Path/dn21_folder_classification"}
crc_python=${CRC_PY:-"$HOME/.venvs/zypath-crc-eval/bin/python"}
crc_test=${CRC_TEST:-"$HOME/ZY-Path/data/CRC-VAL-HE-7K"}
crc_baseline=${CRC_BASELINE:-"$crc_work/experiments/crc-dn169-imagenet-seed42-hue05/best_model.pth"}
crc_supervised="$crc_work/experiments/compact-crc-supervised-$1"
crc_distilled="$crc_work/experiments/compact-crc-distilled-$2"
crc_output="$crc_work/experiments/compact-crc-comparison-${SLURM_JOB_ID:?Submit with sbatch}"
test -x "$crc_python"
test -r "$crc_baseline"
test -r "$crc_supervised/best_model.pth"
test -r "$crc_distilled/best_model.pth"
test -d "$crc_test"
date --iso-8601=seconds
"$crc_python" -u scripts/evaluate_crc_students.py \
    --supervised-run "$crc_supervised" --distilled-run "$crc_distilled" \
    --baseline "$crc_baseline" --test-root "$crc_test" --output-dir "$crc_output" \
    --batch-size 32 --workers 2 --device cuda
date --iso-8601=seconds
