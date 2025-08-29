"""Tests for Valgrind Wrapper."""
import contextlib
import os
import pathlib

import pytest

from cau.wrappers.Valgrind import Valgrind

@contextlib.contextmanager
def working_directory(directory: pathlib.Path) -> None:
    """
    Context manager to switch between working directories.

    Args:
        directory (pathlib.Path): temporary directory to work in
    """
    current = pathlib.Path.cwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(current)

class TestValgrind:
    """Tests for Valgrind wrapper."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: pathlib.Path) -> None:
        """
        Setup of test fixtures.

        Args:
            tmp_path (pathlib.Path): pytest tmp_path fixture
        """
        self.valgrind = Valgrind("AProject")
        self.path = tmp_path

        bin_dir = self.path/"build"/"bin"
        bin_dir.mkdir(parents=True)
        executable = bin_dir/"TestAProject"
        executable.write_text("testcode", encoding="utf-8")

    def test_test_executable(self) -> None:
        """Asserts test executable path is built properly."""
        assert self.valgrind.test_executable == pathlib.Path("build")/"bin"/"TestAProject"

    def test_project_executable(self) -> None:
        """Asserts that project executable path is built properly."""
        assert self.valgrind.project_executable == pathlib.Path("build")/"bin"/"AProject"

    @pytest.mark.usefixtures("successful_process")
    def test_check_memory_successful(self) -> None:
        """Asserts that if call to valgrind is successful, exit code 0 is returned."""
        with working_directory(self.path):
            result = self.valgrind.check_memory(self.valgrind.test_executable)
        assert result.returncode == 0

    @pytest.mark.usefixtures("failed_process_no_except")
    def test_check_memory_unsuccessful(self) -> None:
        """Asserts that if call to valgrind is unsuccessful, exit code 1 is returned."""
        with working_directory(self.path):
            result = self.valgrind.check_memory(self.valgrind.test_executable)
        assert result.returncode == 1

    def test_check_memory_raise_exception_if_executable_not_found(self) -> None:
        """Asserts that FileNotFound exception raised if memory check executable not found."""
        with pytest.raises(FileNotFoundError):
            self.valgrind.check_memory(self.valgrind.project_executable)
