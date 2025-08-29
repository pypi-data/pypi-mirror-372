"""Test fixtures."""
import dataclasses
import multiprocessing
import os
import pathlib
import subprocess

import git
import pytest
from lcov_cobertura import lcov_cobertura as lcov

from cau.wrappers.Clang import PathCollection

DiffCollection = list[git.Diff]

def create_diff(a_path: os.PathLike, b_path: os.PathLike, change: str) -> git.Diff:
    """
    Helper function to create a git.Diff for testing.

    Args:
        a_path (os.PathLike): path to a side of diff

        b_path (os.PathLike): path to b side of diff

        change (str): change type

    Returns:
        git.Diff: a git diff object
    """
    return git.Diff(
        MockRepo(),
        a_rawpath=bytes(a_path) if a_path is not None else None,
        b_rawpath=bytes(b_path) if b_path is not None else None,
        a_blob_id=None,
        b_blob_id=None,
        a_mode=None,
        b_mode=None,
        new_file=False,
        deleted_file=False,
        copied_file=True,
        raw_rename_from=None,
        raw_rename_to=None,
        diff=None,
        change_type=change,
        score=None,
    )

class MockGit:
    """A mocked git class."""

    def ls_files(self) -> str:
        """
        Mocked list of files in git repo.

        Args:
            self (_type_): _description_

        Raises:
            subprocess.CalledProcessError: _description_

        Returns:
            list(str): files in git repo
        """
        return ("src/fileA.cpp\n"
                "src/fileA.hpp\n"
                "src/fileB.hpp\n"
                ".gitignore\n"
                "somefile.py")

class MockRef:
    """A mocked reference."""

    def __init__(self, name: str) -> None:
        """
        Initializes MockRef.

        Args:
            name (str): reference name
        """
        self._name = name

    @property
    def name(self) -> str:
        """
        Name of ref.

        Returns:
            str: ref name
        """
        return self._name

class MockRemote:
    """A mocked remote."""

    @property
    def refs(self) -> list[MockRef]:
        """
        Remote references.

        Returns:
            list[MockRef]: remote references
        """
        return [MockRef("origin/branchA"), MockRef("origin/main")]

class MockCommit:
    """A mocked commit."""

    def diff(self, _other: str) -> DiffCollection:
        """
        Diff between commits.

        Args:
            other (str): reference

        Returns:
            DiffCollection: commits
        """
        return [
            create_diff(a_path=b"src/fileA.cpp", b_path=b"src/fileA.cpp", change="M"),
            create_diff(a_path=b"src/fileA.hpp", b_path=b"src/fileA.hpp", change="M"),
            create_diff(a_path=b"src/fileB.hpp", b_path=b"src/fileB.hpp", change="M"),
        ]

class MockIndex:
    """Mocked index object."""

    def diff(self, _other: str) -> DiffCollection:
        """
        Diff between commits.

        Args:
            other (str): reference

        Returns:
            DiffCollection: commits
        """
        return [create_diff(a_path=b"src/fileA.cpp", b_path=b"src/fileA.cpp", change="M")]

class MockRepo:
    """Mocking the git.Repo."""

    def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
        """Initializes a MockRepo."""

    def remote(self, name: str = "") -> MockRemote:
        """
        Repo's remote by name.

        Returns:
            MockRemote: remote
        """
        _ = name
        return MockRemote()

    @property
    def submodules(self) -> list:
        """
        Submodules.

        Returns:
            list: empty
        """
        return []

    def rev_parse(self, _name: str) -> MockCommit:
        """
        Mocked revision parse.

        Args:
            _name (str): name of revision

        Returns:
            MockCommit: mocked commit
        """
        return MockCommit()

    @property
    def index(self) -> MockIndex:
        """
        Mock index.

        Returns:
            MockIndex: mocked index
        """
        return MockIndex()

    @property
    def git(self) -> MockGit:
        """
        Mock git.

        Returns:
            MockGit: mocked git
        """
        return MockGit()

@pytest.fixture()
def changed_files() -> PathCollection:
    """
    Changes files fixture.

    Returns:
        DiffCollection: changed files
    """
    return [
        pathlib.Path("src/fileA.cpp"),
        pathlib.Path("src/fileA.hpp"),
        pathlib.Path("src/fileB.hpp"),
    ]

@pytest.fixture()
def repo_files() -> PathCollection:
    """
    Changes files fixture.

    Returns:
        DiffCollection: changed files
    """
    return [
        pathlib.Path("src/fileA.cpp"),
        pathlib.Path("src/fileA.hpp"),
        pathlib.Path("src/fileB.hpp"),
        pathlib.Path(".gitignore"),
        pathlib.Path("somefile.py"),
    ]

@pytest.fixture(name="mock_repo")
def _mock_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocks the repo object functionality.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """
    monkeypatch.setattr("git.Repo", lambda *args, **kwargs: MockRepo(args, kwargs))

@pytest.fixture(name="successful_process")
def _successful_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    successful process.

    Args:
        monkeypatch (pytest.MonkeyPatch): _description_
    """

    @dataclasses.dataclass
    class Success:
        """Mocked class for subproccess.run call."""
        returncode: int = 0
        stdout: bytes = b"A stdout output"
        stderr: bytes = b"A stderr output"

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Success())

@pytest.fixture(name="failed_process")
def _failed_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    failed process.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    def _fail(*args, **kwargs) -> None: # noqa: ANN002, ANN003, ARG001
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(subprocess, "run", _fail)

@pytest.fixture(name="failed_process_no_except")
def _failed_process_no_except(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Failed process with no exception.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    @dataclasses.dataclass
    class Process:
        """Mocked failed process."""
        returncode: int = 1
        stdout: bytes = b"A stdout output"
        stderr: bytes = b"A stderr output"

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Process())

@pytest.fixture()
def modified() -> PathCollection:
    """
    A path collection of all modified files.

    Returns:
        PathCollection: modified files
    """
    return [
        pathlib.Path("src/fileA.cpp"),
        pathlib.Path("src/fileA.hpp"),
        pathlib.Path("src/fileB.hpp"),
        pathlib.Path("src/fileB.cpp"),
        pathlib.Path("src/fileC.cpp"),
        pathlib.Path("src/fileC.hpp"),
        pathlib.Path("src/fileD.cpp"),
        pathlib.Path("src/fileD.hpp"),
        pathlib.Path("src/fileE.hpp"),
    ]

@pytest.fixture()
def modified_sources() -> PathCollection:
    """
    Modified source file paths.

    Returns:
        PathCollection: source file paths
    """
    source = pathlib.Path("src")
    return [source/f"file{x}.cpp" for x in "ABCD"]

@pytest.fixture()
def modified_headers() -> PathCollection:
    """
    Modified header file paths.

    Returns:
        PathCollection: header file paths
    """
    source = pathlib.Path("src")
    return [source/f"file{x}.hpp" for x in "E"]

@pytest.fixture()
def modified_real_files(tmp_path: pathlib.Path) -> PathCollection:
    """
    Writes a test source file on disk and creates path collection.

    Args:
        tmp_path (pathlib.Path): temporary path fixture

    Returns:
        PathCollection: path collection
    """
    source = tmp_path/"src"
    source.mkdir()
    a_cpp = source/"a.cpp"
    a_cpp.write_text('#include "b.hpp"\n')
    e_hpp = source/"e.hpp"
    e_hpp.write_text('#include "d.hpp')

    return [
        tmp_path/"src"/"a.cpp",
        tmp_path/"src"/"a.hpp",
        tmp_path/"src"/"b.hpp",
        tmp_path/"src"/"c.hpp",
        tmp_path/"src"/"d.hpp",
        tmp_path/"src"/"e.hpp",
    ]

@pytest.fixture()
def modified_real_headers(tmp_path: pathlib.Path) -> PathCollection:
    """
    Expected modifed headers.

    Args:
        tmp_path (pathlib.Path): temporary path fixture

    Returns:
        PathCollection: header paths
    """
    return [tmp_path/"src"/"c.hpp", tmp_path/"src"/"e.hpp"]

@pytest.fixture(name="successful_multiprocess")
def _successful_multiprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocked successful multiprocess object.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    @dataclasses.dataclass
    class MockProcess:
        """Mocked successful process."""
        returncode: int = 0

        def __hash__(self) -> int:
            return self.returncode

    @dataclasses.dataclass
    class MockProcessApplyResult(list):
        """Mocked ProcessMapResult."""

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            """Initializes a MockProcessApplyResult."""

        def wait(self) -> None:
            """Mocked wait."""

    @dataclasses.dataclass
    class MockPool:
        """Mocked process pool."""

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            """Initializes MockPool."""

        def __enter__(self) -> None:
            return self

        def __exit__(self, exc_type, exc_value, exc_tb) -> None: # noqa: ANN001
            return

        def apply_async(self, *args, **kwargs) -> MockProcessApplyResult: # noqa: ANN002, ANN003, ARG002
            """
            Mocked apply async.

            Returns:
                MockProcessApplyResult: result
            """
            kwargs["callback"]([pathlib.Path("src/fileA.cpp"), MockProcess()])
            return MockProcessApplyResult()

    monkeypatch.setattr(multiprocessing, "Pool", MockPool)

@pytest.fixture(name="unsuccessful_multiprocess")
def _unsuccessful_multiprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocked unsuccessful multiprocess object.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    @dataclasses.dataclass
    class MockProcess:
        """Mocked successful process."""
        returncode: int = 1
        stdout: bytes = b"stdout"

        def __hash__(self) -> int:
            return self.returncode

    @dataclasses.dataclass
    class MockProcessApplyResult(list):
        """Mocked ProcessMapResult."""

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            """Initializes a MockedProcessApplyResult."""

        def wait(self) -> None:
            """Mocked wait."""

    @dataclasses.dataclass
    class MockPool:
        """Mocked process pool."""

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            """Initializes a MockPool."""

        def __enter__(self) -> None:
            return self

        def __exit__(self, exc_type, exc_value, exc_tb) -> None: # noqa: ANN001
            return

        def apply_async(self, *args, **kwargs) -> MockProcessApplyResult: # noqa: ANN002, ANN003, ARG002
            """
            Mocked apply async.

            Returns:
                MockProcessApplyResult: result
            """
            kwargs["callback"]([pathlib.Path("src/fileA.cpp"), MockProcess()])
            return MockProcessApplyResult()

    monkeypatch.setattr(multiprocessing, "Pool", MockPool)

@pytest.fixture(name="mock_lcov")
def _mock_lcov(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mocked lcov class for testing.

    Args:
        monkeypatch (pytest.MonkeyPatch): monkeypatch fixture
    """

    class MockLcov:
        """Mocked LcovCovertura class."""

        def __init__(self, *args, **kwargs) -> None: # noqa: ANN002, ANN003
            """Initializes a MockLcov."""

        def convert(self) -> str:
            """
            Mocked convert.

            Returns:
                str: converted string
            """
            return "converted"

    monkeypatch.setattr(lcov, "LcovCobertura", MockLcov)
