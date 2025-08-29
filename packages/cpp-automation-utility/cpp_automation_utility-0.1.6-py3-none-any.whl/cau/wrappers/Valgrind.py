"""Valgrind Wrapper."""
import logging
import pathlib
import subprocess

import attrs

logger = logging.getLogger("CAU")

@attrs.define()
class Valgrind:
    """Wrapper class that wraps Valgrind calls."""
    project: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))
    build_directory: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path("build"),
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )
    number_callers: int = attrs.field(default=40, converter=int, validator=attrs.validators.instance_of(int))

    @property
    def test_executable(self) -> pathlib.Path:
        """The path to the test executable to instrument."""
        return self.build_directory/"bin"/f"Test{self.project}"

    @property
    def project_executable(self) -> pathlib.Path:
        """The path to the project executable to instrument."""
        return self.build_directory/"bin"/self.project

    def check_memory(self, executable: pathlib.Path) -> subprocess.CompletedProcess:
        """
        Runs the memory leak check with the given executable.

        Args:
            executable (pathlib.Path): executable to run memory leak check on

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        if not executable.exists():
            message = f"{executable} does not exist!"
            logger.exception(message)
            raise FileNotFoundError(message)

        logger.info("Running memory leak check on %s.", executable)
        command = f"valgrind --tool=memcheck --leak-check=full --num-callers={self.number_callers} {executable}"
        result = subprocess.run(
            command.split(), # noqa: S603
            capture_output=True,
            check=False,
        )

        logger.info(
            "%s \n %s",
            result.stdout.decode(encoding="utf-8"),
            result.stderr.decode(encoding="utf-8"),
        )
        return result
