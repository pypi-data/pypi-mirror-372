"""CAU configuration test fixtures."""
import pathlib

import pytest

@pytest.fixture()
def valid_config_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Test CAU project configuration file.

    Args:
        tmp_path (pathlib.Path): pytest temporary path fixture

    Returns:
        pathlib.Path: test file
    """
    config_file = tmp_path/"cauproject.toml"
    text = (
        "[metadata]\n"
        'name = "test_project"\n'
        'version = "1.0.0"\n'
        'license = "RJA"\n'
        'repo_url = "some_url"\n'
        'project_url = "another_url"\n'
        "[build]\n"
        "cross_build = true\n"
        "clang_version = 19\n"
        "gcc_version = 11\n"
        "cpp_standard = 23\n"
        'cmake_min_version = "3.16"\n'
        "[gitlab]\n"
        'docker_image = "some_path"\n'
        "[structure]\n"
        'source = "source"\n'
        'headers = "headers"\n'
        'tests = "unit_tests"\n'
        'build = "some_dir"\n'
        'maximum_module_depth = 10\n'
    )
    config_file.write_text(text, encoding="utf-8")
    return config_file

@pytest.fixture()
def invalid_structure_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Test CAU project file without a structure section.

    Args:
        tmp_path (pathlib.Path): pytest temporary path fixture

    Returns:
        pathlib.Path: test file
    """
    config_file = tmp_path/"cauproject.toml"
    config_file.write_text("[invalid]", encoding="utf-8")
    return config_file
