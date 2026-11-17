"""Bind saved output files to the analysis row that describes them."""
from pathlib import Path
from core.model_profile import file_sha256

SCHEMA = "zypath.result-artifacts.v1"


def artifact_manifest(paths):
    return {"schema": SCHEMA, "files": {
        role: {"path": str(Path(path).resolve()), "sha256": file_sha256(path),
               "size_bytes": Path(path).stat().st_size}
        for role, path in paths.items() if path is not None}}


def verify_saved_artifacts(analysis, expected_paths=None):
    """Return False for legacy records; reject changed/missing new artifacts.

    This detects accidental replacement/corruption. It is not a digital signature
    against someone who can also edit the history database.
    """
    manifest = analysis.get("artifact_manifest")
    if manifest is None:
        return False
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("The saved result integrity information is invalid. The history record has been kept.")
    entries = manifest.get("files")
    if not isinstance(entries, dict) or "result" not in entries:
        raise ValueError("The saved result integrity information is incomplete.")
    for role, entry in entries.items():
        try:
            path = Path(entry["path"])
            expected = (expected_paths or {}).get(role)
            if expected is not None and path.resolve() != Path(expected).resolve():
                raise ValueError("Result path differs from its integrity record")
            if (path.stat().st_size != entry["size_bytes"] or file_sha256(path) != entry["sha256"]):
                raise ValueError("Result bytes changed")
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ValueError(f"Saved {role} artifact is missing or has changed. The result cannot be verified; its history record has been kept. Re-run from the verified source to create a new result.") from error
    return True


def record_artifact_paths(record):
    return {"result": record.get("result_image_path"), "labels": record.get("result_labels_path"),
            "colors": record.get("result_color_mask_path"), "overlay": record.get("result_overlay_path")}
