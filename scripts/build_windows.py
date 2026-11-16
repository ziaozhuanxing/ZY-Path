"""Audit Windows release inputs, run full tests, then build a portable folder.

No model downloads, placeholder resources, skipped tests or network access.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
MODEL_NAMES = ("crc_dn21_seed42_best.pth", "UPerNet_TME_tissue-panoptils_best_model_100ep.pth")
RESOURCES = ("assets/logo.png", "assets/settings_gear.svg",
             "assets/fonts/NotoSansSC-Regular.ttf", "assets/fonts/OFL-NotoSansSC.txt",
             "models/dn21_folder_classification/train_crc_dn21 (1).py")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_inputs(root):
    missing = []
    files = [root / "models" / name for name in MODEL_NAMES]
    files.extend(root / name for name in RESOURCES)
    for path in files:
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(path.relative_to(root).as_posix())
    config = None
    try:
        from huggingface_hub import hf_hub_download
        config = Path(hf_hub_download("openmmlab/upernet-swin-base", "config.json", local_files_only=True))
    except (ImportError, OSError, ValueError):
        missing.append("local Hugging Face cache: openmmlab/upernet-swin-base/config.json")
    return missing, config


def git_output(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Check resources only; does not claim tests/build passed.")
    args = parser.parse_args()
    if sys.platform != "win32":
        print("Windows releases must be built and tested on Windows.", file=sys.stderr)
        return 2
    if sys.version_info[:2] != (3, 10):
        print("Use the project's Windows Python 3.10 environment.", file=sys.stderr)
        return 2
    missing, config = audit_inputs(ROOT)
    if missing:
        print("Release inputs missing:\n" + "\n".join(f" - {item}" for item in missing))
        return 2
    print("All required release resources are present.")
    if args.check_only:
        print("Resource check only. Full tests, build and clean-machine acceptance have NOT been executed.")
        return 0
    try:
        commit = git_output("rev-parse", "HEAD")
        if git_output("status", "--porcelain", "--untracked-files=all"):
            print("Commit or safely preserve pending changes before creating a reproducible release.", file=sys.stderr)
            return 2
        importlib.metadata.version("pyinstaller")
    except (OSError, subprocess.SubprocessError, importlib.metadata.PackageNotFoundError) as error:
        print(f"Build prerequisite unavailable: {error}", file=sys.stderr)
        return 2
    stage = ROOT / "build" / "windows-inputs"
    destination = ROOT / "dist" / "ZY-Path"
    if destination.exists():
        print("dist/ZY-Path already exists. Preserve that release and move it before building a new one.", file=sys.stderr)
        return 2
    stage.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, QT_QPA_PLATFORM="offscreen", HF_HUB_OFFLINE="1")
    command = [sys.executable, "-m", "pytest", "-ra", "--tb=long", "--color=no",
               f"--junitxml={stage / 'pytest.xml'}"]
    with (stage / "pytest-full.log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
    print((stage / "pytest-full.log").read_text(encoding="utf-8"))
    if result.returncode:
        print("Full pytest did not pass. Build stopped; no tests were skipped.", file=sys.stderr)
        return result.returncode
    if git_output("rev-parse", "HEAD") != commit or git_output("status", "--porcelain", "--untracked-files=all"):
        print("Source changed during testing. Preserve changes and rerun the build from a committed state.", file=sys.stderr)
        return 2
    configuration = stage / "upernet-config"
    configuration.mkdir(exist_ok=True)
    shutil.copyfile(config, configuration / "config.json")
    packages = {}
    for name in ("PyQt5", "torch", "torchvision", "transformers", "Pillow", "fpdf2", "pyinstaller"):
        packages[name] = importlib.metadata.version(name)
    manifest = {
        "source_commit": commit, "python": sys.version, "platform": platform.platform(),
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "packages": packages, "tests": {"command": command[2:], "exit_code": result.returncode},
        "models_sha256": {name: sha256(ROOT / "models" / name) for name in MODEL_NAMES},
        "upernet_config_sha256": sha256(configuration / "config.json"),
        "clean_machine_acceptance": "pending", "offline_acceptance": "pending",
    }
    (stage / "build-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    build = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm",
                            str(ROOT / "packaging" / "ZY-Path.spec")], cwd=ROOT)
    if build.returncode:
        return build.returncode
    shutil.copyfile(ROOT / "docs" / "WINDOWS_RELEASE.md", destination / "WINDOWS_RELEASE.md")
    print(f"Build created at {destination}. Clean-machine and offline acceptance are still pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
