"""Test fixtures."""
from __future__ import annotations

import logging
import pathlib

import pytest

import cau

logger = logging.getLogger("CAU")

@pytest.fixture(name="mock_conan")
def _mock_conan(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocks Conan wrapper.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    class MockProcess:
        returncode: int = 0

    class MockConan:

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN003, ANN002
            pass

        def restore(self) -> MockProcess:
            print("Restored Conan")
            return MockProcess()

        def build(self) -> MockProcess:
            print("Build successful")
            return MockProcess()

        def clean_build(self) -> bool:
            print("Cleaned out build directory")
            return True

        def clean_conan(self) -> bool:
            print("Cleaned out conan directory")
            return True

    monkeypatch.setattr(cau, "Conan", lambda *args, **kwargs: MockConan(args, kwargs))

@pytest.fixture(name="mock_git")
def _mock_git(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocked git wrapper.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    class MockGit:

        def changed_files(self) -> list:
            print("Got changes from git")
            return []

        def all_files(self) -> str:
            print("Got all files")
            return "c"

    monkeypatch.setattr(cau, "Git", MockGit)

@pytest.fixture(name="mock_tidy")
def _mock_tidy(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocked tidy wrapper.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    class MockTidy:

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            pass

        def lint(self) -> bool:
            print("Lint was successful")
            return True

    monkeypatch.setattr(cau, "Tidy", lambda *args, **kwargs: MockTidy(args, kwargs))

@pytest.fixture(name="mock_coverage")
def _mock_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocks coverage wrapper.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkey patch fixture
    """

    class MockProcess:
        returncode: int = 0

    class MockCoverage:

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            pass

        def run(self) -> MockProcess:
            print("Running coverage")
            return MockProcess()

    monkeypatch.setattr(cau, "Coverage", MockCoverage)

@pytest.fixture(name="mock_valgrind")
def _mock_valgrind(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocks Valgrind wrapper.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkey patch fixture
    """

    class MockProcess:
        returncode: int = 0

    class MockValgrind:

        test_executable = pathlib.Path("some_path")

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            pass

        def check_memory(self, executable) -> MockProcess: # noqa: ANN001, ARG002
            print("Running memory check")
            return MockProcess()

    monkeypatch.setattr(cau, "Valgrind", MockValgrind)

@pytest.fixture(name="mock_project")
def _mock_project(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocks CAUProject.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkey patch fixture
    """

    class MockStructure:

        def __init__(self) -> None:
            self.build_path = pathlib.Path("build")

    class MockBuild:

        def __init__(self) -> None:
            self.clang_version = 14

    class MockCAUProject:

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003, ARG002
            self.structure = MockStructure()
            self.build = MockBuild()

        @staticmethod
        def read(project_file: pathlib.Path) -> MockCAUProject: # noqa: ARG004
            return MockCAUProject()

        def generate(self, *args, **kwargs) -> None: # noqa: ANN003, ARG002, ANN002
            return

        def add_module(self, *args, **kwargs) -> None: # noqa: ANN002, ARG002, ANN003
            logger.info("Creating new module.")

        def initialize(self) -> None:
            logger.info("Initializing new project")

        def write_config(self) -> None:
            logger.info("Creating default cauproject.toml file.")

    monkeypatch.setattr(cau, "CAUProject", MockCAUProject)
