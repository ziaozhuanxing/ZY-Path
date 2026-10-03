from utils.paths import resource_path


def test_resource_path_resolves_project_file() -> None:
    assert resource_path("main.py").is_file()