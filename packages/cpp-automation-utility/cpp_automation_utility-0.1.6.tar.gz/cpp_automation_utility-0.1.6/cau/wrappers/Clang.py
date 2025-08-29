"""Wrappers for clang tools."""
from __future__ import annotations

import copy
import itertools
import logging
import multiprocessing
import os
import pathlib
import re
import subprocess
from typing import ClassVar

import attrs
import rich.progress
from lcov_cobertura import lcov_cobertura as lcov

from cau.project import CAUProject

logger = logging.getLogger("CAU")

PathCollection = list[pathlib.Path]

@attrs.define(hash=False, str=False, eq=False)
class TidyMessage:
    """Class holding different parts of the output message from clang-tidy."""
    file_name: pathlib.Path = attrs.field(converter=pathlib.Path, validator=attrs.validators.instance_of(pathlib.Path))
    line: int = attrs.field(converter=int, validator=attrs.validators.instance_of(int))
    column: int = attrs.field(converter=int, validator=attrs.validators.instance_of(int))
    level: str = attrs.field(converter=str, validator=attrs.validators.instance_of(str))
    diagnostic: str = attrs.field(converter=str, validator=attrs.validators.instance_of(str))
    checks: str = attrs.field(converter=str, validator=attrs.validators.instance_of(str))
    message: str = attrs.field(converter=str, validator=attrs.validators.instance_of(str))
    pattern: ClassVar[re.Pattern] = re.compile(
        r"^(?P<file_name>.*?):"
        r"(?P<line>\d+):"
        r"(?P<column>\d+):"
        r"\s(?P<level>\w+):"
        r"\s(?P<diagnostic>.*)"
        r"\s(?P<checks>\[.*?\])$\n"
        r"(?P<message>(\s.*\n?)+)",
        re.MULTILINE,
    )

    def __str__(self) -> str:
        return f"{self.file_name}:{self.line}:{self.column}: {self.level}: {self.diagnostic} {self.checks}\n{self.message}"

    def __hash__(self) -> int:
        return hash(self.file_name) + self.line + self.column + hash(self.level) + hash(self.checks)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self.file_name == other.file_name and self.line == other.line and self.column == other.column
            and self.level == other.level and self.checks == self.checks
        )

    @classmethod
    def parse(cls, data: str) -> TidyMessage:
        """
        Parses a string into a TidyMessage.

        Args:
            data (str): string to parse

        Returns:
            TidyMessage: parsed message
        """
        matches = cls.pattern.match(data).groupdict()
        return TidyMessage(
            pathlib.Path(matches.get("file_name", "")),
            matches.get("line", 0),
            matches.get("column", 0),
            matches.get("level", ""),
            matches.get("diagnostic", ""),
            matches.get("checks", ""),
            matches.get("message", 0),
        )

    @classmethod
    def parse_all(cls, data: bytes) -> list[TidyMessage]:
        """
        Parses all messages from a stream of bytes.

        Args:
            data (bytes): steam of bytes to parse

        Returns:
            list[TidyMessage]: collection of messages
        """
        return [cls.parse(match[0]) for match in cls.pattern.finditer(data.decode())]

class Tidy:
    """clang-tidy wrapper class."""
    _source_extensions = (".cpp", ".cc", ".cxx", ".c")
    _header_extensions = (".hpp", ".hh", ".hxx", ".h")

    def __init__(
        self,
        files: PathCollection = None,
        config: pathlib.Path | None = None,
        compile_database_dir: pathlib.Path | None = None,
        ignore_pattern: str | None = None,
        version: int = 14,
    ) -> None:
        """
        Initializes the clang-tidy wrapper class.

        Args:
            files (PathCollection, optional): files that have been modified. Defaults to None.

            config (pathlib.Path | None, optional): clang-tidy configuration file path. Defaults to None.

            compile_database_dir (pathlib.Path | None, optional): compilation database directory path. Defaults to None.

            ignore_pattern (str | None, optional): pattern for linter to ignore file for linting. Defaults to None.

            version (int, optional): version of clang to run tidy against
        """
        self._config: pathlib.Path = config or pathlib.Path.cwd()/".gitlab"/".clang-tidy"
        self._compile_database_dir: pathlib.Path = compile_database_dir or pathlib.Path.cwd()/"build"
        self._files: PathCollection = files or []
        self._ignore_pattern: re.Pattern = re.compile(ignore_pattern or r"$^")
        self._sources: PathCollection = []
        self._headers: PathCollection = []
        self._results: list(subprocess.CompletedProcess) = []
        self._version: int = version

        logger.debug("Changed files: %s", files)
        if self._files:
            self.__parse()
            self.__remove_headers_with_source()
            self.__remove_if_included(self.sources)
            self.__remove_if_included(copy.deepcopy(self.headers))
            self._headers.sort()

    def lint(self) -> bool:
        """
        Performs linting files in project.

        Returns:
            bool: successful or not
        """
        files = self.files
        if not files:
            logger.info("No files found to lint!")
            return True

        progress_bar = rich.progress.Progress(
            rich.progress.TextColumn("[progress.description]{task.description}"),
            rich.progress.SpinnerColumn(),
        )

        with progress_bar:
            task_ids = {file_path: progress_bar.add_task(f"[green] {file_path}") for file_path in files}
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:

                def _callback(result: subprocess.CompletedProcess) -> None:
                    file_name, process = result
                    self._results.append(process)

                    progress_bar.update(task_ids.get(file_name), completed=100.0)

                _ = [pool.apply_async(self._lint_file, (file_path, ), callback=_callback).wait() for file_path in files]

        logger.debug("Results: %s", self._results)

        messages = [TidyMessage.parse_all(process.stdout) for process in self._results if process.returncode != 0]
        _ = [logger.error(message) for message in set(itertools.chain.from_iterable(messages))]
        return all(process.returncode == 0 for process in self._results)

    @property
    def sources(self) -> PathCollection:
        """
        Found  modified source files.

        Returns:
            PathCollection: source files
        """
        return self._sources

    @property
    def headers(self) -> PathCollection:
        """
        Found modified header files.

        Returns:
            PathCollection: header files
        """
        return self._headers

    @property
    def files(self) -> PathCollection:
        """
        Collection of files to be linted.

        Returns:
            PathCollection: files to lint
        """
        files = list(set(self.sources + self.headers))
        files = [f for f in files if not self._ignore_pattern.match(f.name)]
        files.sort()
        return files

    def __parse(self) -> None:
        """Parse diffs for valid changes and separate into source and header files."""
        self._sources = [path for path in self._files if path.suffix in self._source_extensions]
        self._headers = [path for path in self._files if path.suffix in self._header_extensions]

    def __remove_headers_with_source(self) -> None:
        """Removes header files that have a corresponding source file as it is assumed that the header will be contained in the source.""" # noqa: E501
        source_names = [source.stem for source in self.sources]
        self.__remove_headers([header for header in self.headers if header.stem in source_names])

    def __remove_if_included(self, files: PathCollection) -> None:
        """
        Removes header if included in the file contents.

        Args:
            files (PathCollection): files to to check
        """
        for file_ in files:

            if not self.headers:
                break

            if not file_.exists():
                continue

            with file_.open("r", encoding="utf-8") as source_file:
                contents = source_file.read()
                self.__remove_headers([header for header in self.headers if header.name in contents])

    def __remove_headers(self, to_remove: PathCollection) -> None:
        """
        Removes filtered header.

        Args:
            to_remove (PathCollection): header to remove
        """
        self._headers = list(set(self.headers) - set(to_remove))

    def _lint_file(self, file_path: pathlib.Path) -> None:
        """
        Lints a file.

        Args:
            file_path (pathlib.Path): path to file to lint
        """
        logger.debug("Linting file:  %s", file_path)
        result = subprocess.run(  # noqa: PLW1510
            f"clang-tidy-{self._version} {file_path} --config-file={self._config} -p {self._compile_database_dir}".split(),  # noqa: S603
            capture_output=True,
        )

        return file_path, result

@attrs.define
class Coverage:
    """Wrapper for obtaining coverage statistics."""
    project: CAUProject = attrs.field(
        factory=CAUProject,
        validator=attrs.validators.instance_of(CAUProject),
        on_setattr=[
            lambda self, _, project: self._on_project_set(project),
            attrs.setters.validate,
        ],
    )
    build_directory: pathlib.Path = attrs.field(
        factory=lambda: "build",
        validator=attrs.validators.instance_of(pathlib.Path),
        converter=pathlib.Path,
    )

    version: int = attrs.field(default=14, converter=int, validator=attrs.validators.instance_of(int))

    _lcov_data: bytes = attrs.field(factory=bytes, init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        _ = self._on_project_set(self.project)

    @property
    def test_executable(self) -> pathlib.Path:
        """
        Test executable to run coverage statistics from.

        Returns:
            pathlib.Path: path to test executable
        """
        return self.build_directory/"bin"/f"Test{self.project.meta_data.name}"

    @property
    def instrumented_object(self) -> pathlib.Path:
        """
        Object that has instrumented build.

        Returns:
            pathlib.Path: path to instrumented object
        """
        if self.project.meta_data.header_only:
            return self.test_executable
        return self.build_directory/"lib"/F"lib{self.project.meta_data.name}.so"

    @property
    def profile_file(self) -> str:
        """
        Generated profile file name.

        Returns:
            str: profile file
        """
        return f"{self.project.meta_data.name}.profraw"

    @property
    def profile_data(self) -> str:
        """
        Generated profile data name.

        Returns:
            str: profile data
        """
        return f"{self.project.meta_data.name}.profdata"

    def run(self) -> subprocess.CompletedProcess:
        """Runs test executable and processes coverage information into html and cobetura files."""
        result = subprocess.run(self.test_executable, check=True) # noqa: S603
        self.__merge()
        self.__report()
        self.__generate_html()
        self.__export_to_lcov()
        self.__export_to_cobertura()
        return result

    def __merge(self) -> None:
        """
        Merges profile file into data file.

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        _ = subprocess.run(
            f"llvm-profdata-{self.version} merge {self.profile_file} -o {self.profile_data}".split(), # noqa: S603
            check=True,
        )

    def __report(self) -> None:
        """
        Generates coverage report.

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        _ = subprocess.run(
            (  # noqa: S603
                f"llvm-cov-{self.version} report "
                f"-object {self.instrumented_object} "
                f"-instr-profile={self.profile_data} "
                "-show-branch-summary=false -show-region-summary=false "
                "--ignore-filename-regex=.*_test.cpp"
            ).split(),
            check=True,
        )

    def __generate_html(self) -> None:
        """Generates coverage report in html format."""
        _ = subprocess.run(
            (  # noqa: S603
                f"llvm-cov-{self.version} show "
                f"-object {self.instrumented_object} "
                f"-instr-profile={self.profile_data} "
                "-format html -output-dir=CoverageReport "
                "--ignore-filename-regex=.*_test.cpp"
            ).split(),
            check=True,
        )

    def __export_to_lcov(self) -> subprocess.CompletedProcess:
        """
        Converts report format to lcoverage.

        Returns:
            subprocess.CompletedProcess: process metadata
        """
        result = subprocess.run(
            (  # noqa: S603
                f"llvm-cov-{self.version} export "
                f"-object {self.instrumented_object} "
                f"-instr-profile={self.profile_data} "
                "-format lcov "
                "--ignore-filename-regex=.*_test.cpp"
            ).split(),
            check=True,
            capture_output=True,
        )
        self._lcov_data = result.stdout

    def __export_to_cobertura(self) -> None:
        """Exports coverage data to covertura file."""
        converter = lcov.LcovCobertura(self._lcov_data.decode(encoding="utf-8"))
        with pathlib.Path("coverage.xml").open("w", encoding="utf-8") as coverage:
            coverage.write(converter.convert())

    def _on_project_set(self, project: CAUProject) -> None:
        os.environ["LLVM_PROFILE_FILE"] = f"{project.meta_data.name}.profraw"
        return project
