"""Tests for CAU project config file."""
import contextlib
import os
import pathlib

import pytest

from cau.project.project import Build, CAUProject, Gitlab, MaximumModuleDepthError, MetaData, Structure

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

def test_project_file_correctly_read(valid_config_file: pathlib.Path) -> None:
    """
    Asserts that cau project file is read in correctly.

    Args:
        valid_config_file (pathlib.Path): config file fixture
    """
    meta_data = MetaData(
        name="test_project",
        version="1.0.0",
        license="RJA",
        repo_url="some_url",
        project_url="another_url",
    )
    structure = Structure(
        source_path=pathlib.Path()/"source",
        header_path=pathlib.Path()/"headers",
        test_path=pathlib.Path()/"unit_tests",
        build_path=pathlib.Path()/"some_dir",
        max_depth=10,
    )
    build = Build(cross_build=True, clang_version=19, gcc_version=11, cpp_standard=23, cmake_min_version="3.16")

    gitlab = Gitlab(docker_image="some_path")
    expected = CAUProject(meta_data=meta_data, structure=structure, build=build, gitlab=gitlab)

    assert CAUProject.read(valid_config_file) == expected

def test_default_structure_returned_if_no_structure_defined(invalid_structure_file: pathlib.Path) -> None:
    """
    Asserts that if no structure section is defined the project structure is default.

    Args:
        invalid_structure_file (pathlib.Path): test invalid config file
    """
    assert CAUProject.read(invalid_structure_file).structure == Structure()

class TestProject:
    """Tests for project."""
    project = None
    path = None

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: pathlib.Path) -> None:
        """Setup of test fixtures."""
        meta_data = MetaData(
            name="test_project",
            version="1.0.0",
            license="RJA",
            repo_url="some_url",
            project_url="another_url",
        )
        build = Build(cross_build=True)
        self.project = CAUProject(meta_data=meta_data, build=build)
        self.path = tmp_path

    def _setup_test_folders(self) -> None:
        """Setup of test folders."""
        source = self.path/"src"
        source.mkdir()

        include = self.path/"include"
        include.mkdir()

        tests = self.path/"tests"
        tests.mkdir()

    def test_generate(self) -> None:
        """Asserts generate creates the correct number of source files."""
        self._setup_test_folders()
        with working_directory(self.path):
            self.project.generate("AClass")
        assert len(list(self.path.glob("**/*.hpp"))) == 1
        assert len(list(self.path.glob("**/*.cpp"))) == 2 # noqa: PLR2004

    def test_generate_with_module(self) -> None:
        """Asserts generate creates the correct number of source files."""
        self._setup_test_folders()
        module = "SomeModule"
        source = self.path/"src"/module
        source.mkdir()

        include = self.path/"include"/module
        include.mkdir()

        tests = self.path/"tests"/module
        tests.mkdir()

        with working_directory(self.path):
            self.project.generate("AClass", module=module)

        assert len(list(self.path.glob("**/*.hpp"))) == 1
        assert len(list(self.path.glob("**/*.cpp"))) == 2 # noqa: PLR2004

    def test_add_module(self) -> None:
        """Asserts that adding a module creates the correct file structure."""
        self._setup_test_folders()
        with working_directory(self.path):
            self.project.add_module("module")

        assert (self.path/"src"/"module").exists()
        assert (self.path/"include"/"module").exists()
        assert (self.path/"tests"/"module").exists()
        assert len(list(self.path.glob("**/*.txt"))) == 1

    def test_add_module_with_submodules(self) -> None:
        """Asserts that adding a multiple level module creates the correct file structure."""
        self._setup_test_folders()
        with working_directory(self.path):
            self.project.add_module("module", "submodule")

        assert (self.path/"src"/"module/submodule").exists()
        assert (self.path/"include"/"module/submodule").exists()
        assert (self.path/"tests"/"module/submodule").exists()
        assert len(list(self.path.glob("**/*.txt"))) == 0

    def test_add_module_raises_maximum_module_depth_error_when_number_of_modules_exceeds_allowed(self) -> None:
        """Asserts that when adding a three-depth module, exception is raised."""
        self._setup_test_folders()
        with pytest.raises(MaximumModuleDepthError):
            self.project.add_module("module", "submodule", "too_many")

    def test_initialize(self) -> None:
        """Asserts that project initialization creates the correct number of files."""
        with working_directory(self.path):
            self.project.initialize()

        assert len(list(self.path.glob("conanfile.py"))) == 1
        assert (self.path/"src").exists()
        assert (self.path/"include").exists()
        assert (self.path/"tests").exists()
        assert (self.path/".conan"/"profiles").exists()
        assert len(list(self.path.glob(".conan/profiles/*"))) == 7 # noqa: PLR2004
        assert (self.path/".gitlab").exists()
        assert (self.path/".gitlab-ci.yml").exists()
        assert (self.path/".codeclimate.yml").exists()
        assert (self.path/".clang-format").exists()
        assert (self.path/".gitignore").exists()
        assert (self.path/"pyproject.toml").exists()
        assert len(list(self.path.glob(".gitlab/*"))) == 3 # noqa: PLR2004
        assert (self.path/"docs"/"source").exists()
        assert len(list(self.path.glob("docs/*"))) == 3 # noqa: PLR2004
        assert len(list(self.path.glob("docs/source/*"))) == 3 # noqa: PLR2004
        assert (self.path/".vscode").exists()
        assert len(list(self.path.glob(".vscode/*"))) == 3 # noqa: PLR2004
        assert (self.path/"CMakeLists.txt").exists()
        assert (self.path/"tests"/"CMakeLists.txt").exists()
        assert (self.path/"src"/"hello.cpp").exists()
        assert (self.path/"include"/"hello.hpp").exists()
        assert (self.path/"tests"/"hello_test.cpp").exists()

    def test_config_write(self) -> None:
        """Asserts that project configuration file is written."""
        with working_directory(self.path):
            self.project.write_config()

        assert (self.path/"cauproject.toml").exists()
