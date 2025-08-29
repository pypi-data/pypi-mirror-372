"""Tests for Git module."""
import pytest

from cau.wrappers.Git import Git, PathCollection

@pytest.mark.usefixtures("mock_repo")
class TestGit:
    """Tests for git wrapper class."""
    git_wrapper = None

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.git_wrapper = Git()

    def test_changed_files(self, changed_files: PathCollection) -> None:
        """
        Asserts changed files returns correct file paths.

        Args:
            changed_files (PathCollection): expected file paths
        """
        self.git_wrapper = Git()
        expected = changed_files
        expected.sort(key=lambda p: p.name)
        result = self.git_wrapper.changed_files()
        result.sort(key=lambda p: p.name)
        assert result == expected

    def test_all_files(self, repo_files: PathCollection) -> None:
        """
        Asserts that all files returns correct paths.

        Args:
            repo_files (PathCollection): expected file paths
        """
        self.git_wrapper = Git()
        expected = repo_files
        expected.sort(key=lambda p: p.name)
        result = self.git_wrapper.all_files()
        result.sort(key=lambda p: p.name)
        assert result == expected
