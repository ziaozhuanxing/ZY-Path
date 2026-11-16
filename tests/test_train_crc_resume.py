import ast
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "models"
    / "dn21_folder_classification"
    / "train_crc_dn21 (1).py"
)


def load_resume_helpers():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    wanted = {"normalize_model_settings", "validate_resume_config"}
    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    namespace = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), SCRIPT_PATH, "exec"), namespace)
    return namespace["validate_resume_config"]


validate_resume_config = load_resume_helpers()


def make_config(model_settings):
    return {
        "epochs": 2,
        "model_settings": model_settings,
        "batch_size": 32,
    }


def test_equivalent_block_config_sequence_types_pass() -> None:
    saved = make_config({"growth_rate": 32, "block_config": [2, 2, 2, 2]})
    current = make_config({"growth_rate": 32, "block_config": (2, 2, 2, 2)})

    validate_resume_config(saved, current)


@pytest.mark.parametrize(
    "saved_settings",
    [
        {"growth_rate": 32, "block_config": [1, 2, 2, 2]},
        {"growth_rate": 16, "block_config": [2, 2, 2, 2]},
    ],
)
def test_different_architecture_settings_fail(saved_settings) -> None:
    current = make_config({"growth_rate": 32, "block_config": (2, 2, 2, 2)})

    with pytest.raises(ValueError, match="model_settings"):
        validate_resume_config(make_config(saved_settings), current)
