"""Collect an unfiltered native Windows regression run; nothing is uploaded."""
import argparse
from datetime import datetime
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ("models/crc_dn21_seed42_best.pth",
             "models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth",
             "models/dn21_folder_classification/train_crc_dn21 (1).py")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def source_state():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    return {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
            "status": git("status", "--porcelain", "--untracked-files=all"),
            "tracked_sha256": {n: sha256(ROOT / n) for n in names if n and (ROOT / n).is_file()},
            "resources_sha256": {n: sha256(ROOT / n) if (ROOT / n).is_file() else None for n in RESOURCES}}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def junit_counts(path):
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    result = {key: sum(int(s.get(key, "0")) for s in suites)
              for key in ("tests", "failures", "errors", "skipped")}
    result["passed"] = result["tests"] - result["failures"] - result["errors"] - result["skipped"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-commit")
    parser.add_argument("--output-root", type=Path, default=ROOT.parent / "ZY-PATH-evidence")
    args = parser.parse_args()
    if sys.platform != "win32" or sys.version_info[:2] != (3, 10):
        parser.error("Use native Windows and the project's 64-bit Python 3.10 environment.")
    try:
        before = source_state()
    except (OSError, subprocess.SubprocessError) as error:
        parser.error(f"Cannot establish source identity: {error}")
    if before["status"]:
        parser.error("Preserve and commit source changes before collecting evidence.")
    if args.expected_commit and before["head"] != args.expected_commit:
        parser.error("HEAD does not match --expected-commit.")
    parent = args.output_root.resolve()
    if parent == ROOT or ROOT in parent.parents:
        parser.error("Evidence must be outside the source checkout.")
    out = parent / datetime.now().astimezone().strftime("windows-%Y%m%d-%H%M%S-%f")
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "source-before.json", before)
    packages = {}
    for name in ("torch", "torchvision", "PyQt5", "PyQt5-Qt5", "pytest", "pytest-qt", "numpy", "Pillow"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None
    write_json(out / "environment.json", {"date": datetime.now().astimezone().isoformat(),
        "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
        "machine": platform.machine(), "packages": packages,
        "QT_QPA_PLATFORM": os.environ.get("QT_QPA_PLATFORM"),
        "QT_SCALE_FACTOR": os.environ.get("QT_SCALE_FACTOR")})
    probe = subprocess.run([sys.executable, "-c",
        "import json; from PyQt5.QtWidgets import QApplication; "
        "from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR; "
        "app=QApplication([]); print(json.dumps({'platform':app.platformName(),"
        "'qt':QT_VERSION_STR,'pyqt':PYQT_VERSION_STR})); "
        "raise SystemExit(0 if app.platformName()=='windows' else 1)"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / "qt-probe.log").write_bytes(probe.stdout)
    command = [sys.executable, "-m", "pytest", "-ra", "--tb=long", "--color=no",
               "--junitxml=" + str(out / "pytest.xml")]
    write_json(out / "command.json", command)
    print("Running complete pytest; no tests are selected, skipped or modified by this collector.", flush=True)
    with (out / "pytest-full.log").open("wb") as log:
        run = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    after = source_state()
    write_json(out / "source-after.json", after)
    try:
        counts = junit_counts(out / "pytest.xml")
    except (OSError, ET.ParseError, ValueError):
        counts = None
    unchanged = before == after
    okay = run.returncode == 0 and probe.returncode == 0 and unchanged and counts is not None
    summary = {"source_before": before["head"], "source_after": after["head"],
        "expected_commit": args.expected_commit, "source_and_resources_unchanged": unchanged,
        "pytest_exit_code": run.returncode, "qt_probe_exit_code": probe.returncode,
        "native_qt_platform_confirmed": probe.returncode == 0, "results": counts,
        "collector_exit_code": 0 if okay else 1,
        "scope": "Source regression; not packaged-release acceptance or model accuracy."}
    write_json(out / "summary.json", summary)
    write_json(out / "checksums.json", {p.name: sha256(p) for p in out.iterdir() if p.is_file()})
    archive = out.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(out.iterdir()):
            bundle.write(path, out.name + "/" + path.name)
    print(json.dumps(summary, indent=2), flush=True)
    print("Evidence archive:", archive, flush=True)
    print("Review private paths before sharing; failures and collection errors remain in the log/XML.")
    return summary["collector_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
