"""Wrapper around Conan cli commands."""
import logging
import os
import pathlib
import shutil
import subprocess

import attrs

logger = logging.getLogger("CAU")

@attrs.define()
class Conan:
    """Wrapper object around conan cli commands."""
    home: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path(pathlib.Path.cwd())/".conan",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
        on_setattr=[lambda self, _, home: self._on_home_set(home), attrs.setters.convert, attrs.setters.validate],
    )
    build_directory: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path("build"),
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
        on_setattr=[attrs.setters.convert, attrs.setters.validate],
    )
    build_type: str = attrs.field(factory=lambda: "Debug", converter=str, validator=attrs.validators.instance_of(str))
    platform: str = attrs.field(
        factory=lambda: "linux",
        converter=str,
        validator=attrs.validators.instance_of(str),
        on_setattr=[
            lambda self, _, platform: self._on_platform_set(platform),
            attrs.setters.convert,
            attrs.setters.validate,
        ],
    )

    def __attrs_post_init__(self) -> None:
        _ = self._on_home_set(self.home)
        _ = self._on_platform_set(self.platform)

    @property
    def profile(self) -> str:
        """
        Conan profile to use when building based on platform and build type.

        Returns:
            str: build profile
        """
        return f"{self.platform}{self.build_type}"

    def restore(self) -> subprocess.CompletedProcess:
        """
        Calls conan install to get dependencies.

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        command = f"conan install . --output-folder {self.build_directory} --build=missing --profile {self.profile}"
        return subprocess.run(
            command.split(), # noqa: S603
            check=True,
            stdout=subprocess.PIPE,
        )

    def build(self) -> subprocess.CompletedProcess:
        """
        Calls conan build to build project.

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        command = f"conan build {pathlib.Path.cwd()} --output-folder {self.build_directory} --profile {self.profile}"
        return subprocess.run(
            command.split(), # noqa: S603
            check=True,
        )

    def clean_build(self) -> bool:
        """
        Cleans build directory.

        Returns:
            bool: successfully cleaned the build directory
        """
        return Conan._clean(self.build_directory)

    def clean_conan(self) -> bool:
        """
        Cleans conan directory.

        Returns:
            bool: successfully cleaned the conan directory
        """
        return Conan._clean(self.home/"p")

    @staticmethod
    def _clean(directory: pathlib.Path) -> bool:
        """
        Clean (remove) the provided directory.

        Args:
            directory (pathlib.Path): remove the directory

        Returns:
            bool: removal was successful
        """
        try:
            shutil.rmtree(directory)
        except OSError as ex:
            logger.exception("Could not remove %s due to %s", directory, ex.args)
            return False
        return True

    def _on_home_set(self, home: pathlib.Path) -> pathlib.Path:
        os.environ["CONAN_HOME"] = str(home)
        return home

    def _on_platform_set(self, platform: pathlib.Path) -> pathlib.Path:
        os.environ["PLATFORM"] = str(platform)
        return platform
