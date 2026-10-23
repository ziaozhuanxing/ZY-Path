# Build on Windows using scripts/build_windows.py, after a successful full pytest.
from pathlib import Path

root = Path(SPECPATH).parent
stage = root / "build" / "windows-inputs"
required = (
    root / "models" / "crc_dn21_seed42_best.pth",
    root / "models" / "UPerNet_TME_tissue-panoptils_best_model_100ep.pth",
    stage / "upernet-config" / "config.json",
    stage / "build-manifest.json",
)
for path in required:
    if not path.is_file():
        raise RuntimeError(f"Missing release input: {path}. Run scripts/build_windows.py first.")

datas = [
    (str(root / "assets"), "assets"),
    (str(required[0]), "models"),
    (str(required[1]), "models"),
    (str(stage / "upernet-config"), "models/upernet-config"),
    (str(stage / "build-manifest.json"), "."),
]
a = Analysis(
    [str(root / "main.py")], pathex=[str(root)], datas=datas,
    hiddenimports=[
        "transformers.models.upernet.configuration_upernet",
        "transformers.models.upernet.modeling_upernet",
        "transformers.models.swin.configuration_swin",
        "transformers.models.swin.modeling_swin",
        "transformers.models.auto.configuration_auto",
        "PIL.TiffImagePlugin",
        "PyQt5.QtSvg",
    ],
    excludes=["PyQt6", "PySide2", "PySide6", "tkinter", "pytest", "pytestqt"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="ZY-Path",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="ZY-Path")
