"""Tests for Linters."""
import re

import pytest

from cau.wrappers.Clang import PathCollection, Tidy

class TestTidy:
    """Tests for Tidy."""
    linter = None

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.linter = Tidy()

    def test_sources(self, modified: PathCollection, modified_sources: PathCollection) -> None:
        """
        Asserts all source files are found.

        Args:
            modified (PathCollection): collection of touched files

            modified_sources (PathCollection): expected source files
        """
        self.linter = Tidy(modified)
        assert self.linter.sources == modified_sources

    def test_headers(self, modified: PathCollection, modified_headers: PathCollection) -> None:
        """
        Asserts all header files are found.

        Args:
            modified (PathCollection): collection of touched files

            modified_headers (PathCollection): expected source files
        """
        self.linter = Tidy(modified)
        assert self.linter.headers == modified_headers

    def test_headers_clear_of_included_headers(
        self,
        modified_real_files: PathCollection,
        modified_real_headers: PathCollection,
    ) -> None:
        """
        Asserts that if a source file includes a header, the header is not in the header collection.

        Args:
            modified_real_files (PathCollection): modified files on disk

            modified_real_headers (PathCollection): expected headers
        """
        self.linter = Tidy(modified_real_files)
        assert self.linter.headers == modified_real_headers

    def test_files_are_ignored_when_provided_a_regex(
        self,
        modified_real_files: PathCollection,
        modified_real_headers: PathCollection,
    ) -> None:
        """
        Asserts that if an ignore pattern is provided, the ignored files are not gathered for linting.

        Args:
            modified_real_files (PathCollection): modified files on disk

            modified_real_headers (PathCollection): expected files to lint
        """
        self.linter = Tidy(modified_real_files, ignore_pattern=re.compile(r".*\.cpp"))
        assert self.linter.files == modified_real_headers

    @pytest.mark.usefixtures("successful_multiprocess")
    def test_lint_returns_true_if_successful(self, modified: PathCollection) -> None:
        """
        Asserts that True is returned if lint was successful.

        Args:
            modified (PathCollection): modified file list
        """
        self.linter = Tidy(files=modified)
        assert self.linter.lint()

    @pytest.mark.usefixtures("unsuccessful_multiprocess")
    def test_lint_returns_false_if_unsuccessful(self, modified: PathCollection) -> None:
        """
        Asserts that False is returned if lint was not successful.

        Args:
            modified (PathCollection): modified file list
        """
        self.linter = Tidy(files=modified)
        assert not self.linter.lint()
