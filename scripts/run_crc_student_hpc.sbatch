#!/bin/bash
#SBATCH --job-name=crc-student
#SBATCH --account=fet_student
#SBATCH --partition=gpu-2c-l40s-1g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=crc-student-%j.log

set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 || ( "$1" != supervised && "$1" != distilled ) ]]; then
    echo "Usage: sbatch scripts/run_crc_student_hpc.sbatch supervised | distilled /path/to/teacher/run" >&2
    exit 2
fi
crc_repo=${SLURM_SUBMIT_DIR:-"$PWD"}
cd "$crc_repo"
crc_work=${CRC_WORK:-"$crc_repo/dn21_folder_classification"}
crc_python=${CRC_PY:-"$HOME/.venvs/zypath-crc-eval/bin/python"}
crc_teacher=${2:-}
crc_output="$crc_work/experiments/compact-crc-$1-${SLURM_JOB_ID:?Submit with sbatch}"
args=(--method "$1" --train-manifest "$crc_work/splits/seed42/train.json"
      --val-manifest "$crc_work/splits/seed42/val.json" --output-dir "$crc_output"
      --epochs 30 --batch-size 32 --workers 2 --device cuda)
if [[ "$1" == distilled ]]; then
    if [[ -z "$crc_teacher" ]]; then
        echo "Distilled training requires the completed teacher run directory." >&2
        exit 2
    fi
    test -r "$crc_teacher/teacher_training_targets.npz"
    args+=(--teacher-targets "$crc_teacher/teacher_training_targets.npz")
fi
test -x "$crc_python"
printf 'Student output: %s\n' "$crc_output"
exec "$crc_python" -u scripts/distill_crc_student.py "${args[@]}"
