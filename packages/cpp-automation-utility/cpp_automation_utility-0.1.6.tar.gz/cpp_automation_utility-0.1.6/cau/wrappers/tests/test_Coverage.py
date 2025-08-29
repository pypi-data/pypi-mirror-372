"""Tests for coverage wrapper."""
import os
import pathlib
import subprocess

import pytest

from cau.project import CAUProject
from cau.wrappers.Clang import Coverage

class TestCoverage:
    """Tests for coverage wrapper."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.project = CAUProject()
        self.project.meta_data.name = "AProject"
        self.coverage = Coverage(self.project)

    def test_llvm_profile_file_is_set_on_initialization(self) -> None:
        """Asserts environment variable is properly set."""
        assert os.environ.get("LLVM_PROFILE_FILE") == self.coverage.profile_file

    def test_llvm_profile_file_is_set_when_project_is_set(self) -> None:
        """Asserts environment variable is properly set when project is set."""
        self.project.meta_data.name = "BProject"
        self.coverage.project = self.project
        assert os.environ.get("LLVM_PROFILE_FILE") == self.coverage.profile_file

    def test_test_executable(self) -> None:
        """Asserts test executable path is build properly."""
        assert self.coverage.test_executable == pathlib.Path("build")/"bin"/"TestAProject"

    def test_instrumented_object(self) -> None:
        """Asserts that instrumented object is built properly."""
        assert self.coverage.instrumented_object == pathlib.Path("build")/"lib"/"libAProject.so"

    def test_instrumented_object_header_only(self) -> None:
        """Asserts that instrumented object is the test binary if header only."""
        self.coverage.project.meta_data.header_only = True
        assert self.coverage.instrumented_object == pathlib.Path("build")/"bin"/"TestAProject"

    def test_profile_file(self) -> None:
        """Asserts profile file name is correct."""
        assert self.coverage.profile_file == "AProject.profraw"

    def test_profile_data(self) -> None:
        """Asserts profile data is correct."""
        assert self.coverage.profile_data == "AProject.profdata"

    @pytest.mark.usefixtures("successful_process", "mock_lcov")
    def test_run(self) -> None:
        """
        Asserts coverage commands return exit code 0 if successful.

        Args:
            method_name (str): method to check
        """
        result = self.coverage.run()
        assert result.returncode == 0

    @pytest.mark.usefixtures("failed_process", "mock_lcov")
    def test_run_raises_exception(self) -> None:
        """Asserts method raises exception when not successfule."""
        with pytest.raises(subprocess.CalledProcessError):
            _ = self.coverage.run()
