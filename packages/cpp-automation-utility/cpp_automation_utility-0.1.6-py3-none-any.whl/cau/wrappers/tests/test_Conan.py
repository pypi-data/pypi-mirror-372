"""Tests Conan wrapper class."""
import os
import pathlib
import shutil
import subprocess

import pytest

from cau.wrappers.Conan import Conan

class TestConan:
    """Tests for conan cli wrappers."""
    conan = None

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.conan = Conan()

    def test_conan_home_is_set_on_init(self) -> None:
        """Asserts CONAN_HOME environment variable is properly set on init."""
        assert os.environ.get("CONAN_HOME") == str(self.conan.home)

    def test_conan_home_is_set_via_setter(self) -> None:
        """Asserts CONAN_HOME is properly set via setter."""
        self.conan.home = pathlib.Path("someawkwardpath")
        assert os.environ.get("CONAN_HOME") == str(self.conan.home)

    def test_platform_is_set_on_init(self) -> None:
        """Asserts PLATFORM environment variable is properly set on init."""
        assert os.environ.get("PLATFORM") == str(self.conan.platform)

    def test_platform_is_set_via_setter(self) -> None:
        """Asserts PLATFORM environment variable is properly set via setter."""
        self.conan.platform = pathlib.Path("win64")
        assert os.environ.get("PLATFORM") == str(self.conan.platform)

    @pytest.mark.usefixtures("successful_process")
    def test_restore(self) -> None:
        """Asserts that if the restore was successful, error code of 0 is returned."""
        result = self.conan.restore()
        assert result.returncode == 0

    @pytest.mark.usefixtures("failed_process")
    def test_restore_raises_exception_if_not_successful(self) -> None:
        """Asserts that an exception is raised if process call not successful."""
        with pytest.raises(subprocess.CalledProcessError):
            _ = self.conan.restore()

    def test_profile(self) -> None:
        """Asserts that the conan profile property is properly constructed."""
        assert self.conan.profile == "linuxDebug"

    @pytest.mark.usefixtures("successful_process")
    def test_build(self) -> None:
        """Asserts that if build was successful, error code of 0 is returned."""
        result = self.conan.build()
        assert result.returncode == 0

    @pytest.mark.usefixtures("failed_process")
    def test_build_raises_exception_if_not_successful(self) -> None:
        """Asserts that if build failed, an exception is raised."""
        with pytest.raises(subprocess.CalledProcessError):
            _ = self.conan.build()

    def test_clean_build_is_successful(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Asserts true is returned if clean build is successful.

        Args:
            monkeypatch (pytest.Monkeypatch): monkeypatch fixture
        """
        monkeypatch.setattr(shutil, "rmtree", lambda *args, **kwargs: None) # noqa: ARG005
        assert self.conan.clean_build()

    def test_clean_build_is_unsuccessful(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Asserts False is returned if clean build is unsuccessful.

        Args:
            monkeypatch (pytest.MonkeyPatch): _description_
        """

        def _raise(*args, **kwargs) -> None: # noqa: ARG001, ANN003, ANN002
            raise OSError

        monkeypatch.setattr(shutil, "rmtree", _raise)
        assert not self.conan.clean_build()

    def test_clean_conan_is_successful(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Asserts true is returned if clean conan is successful.

        Args:
            monkeypatch (pytest.Monkeypatch): monkeypatch fixture
        """
        monkeypatch.setattr(shutil, "rmtree", lambda *args, **kwargs: None) # noqa: ARG005
        assert self.conan.clean_conan()

    def test_clean_conan_is_unsuccessful(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Asserts False is returned if clean conan is unsuccessful.

        Args:
            monkeypatch (pytest.MonkeyPatch): _description_
        """

        def _raise(*args, **kwargs) -> None: # noqa: ARG001, ANN003, ANN002
            raise OSError

        monkeypatch.setattr(shutil, "rmtree", _raise)
        assert not self.conan.clean_conan()
