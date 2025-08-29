"""CAU project configuration file."""
from __future__ import annotations

import itertools
import logging
import pathlib
from typing import TYPE_CHECKING

import attrs
import jinja2
import tomli

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger("CAU")
jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("cau.project"), autoescape=jinja2.select_autoescape())
default_docker_image = "registry.gitlab.com/aldridgesoftwaredesigns/docker-images/cpp:latest"

class MaximumModuleDepthError(Exception):
    """Exception for when requested module addition depth outside the bounds of the project."""

@attrs.define()
class MetaData:
    """Project metadata."""
    name: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))
    version: str = attrs.field(default="0.0.0", converter=str, validator=attrs.validators.instance_of(str))
    license: str = attrs.field(default="MIT", converter=str, validator=attrs.validators.instance_of(str))
    repo_url: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))
    project_url: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))
    header_only: bool = attrs.field(default=False, converter=bool, validator=attrs.validators.instance_of(bool))

    @staticmethod
    def read(data: dict[str, str]) -> MetaData:
        """
        Reads from dictionary values of what the project's metadata is.

        Args:
            data (dict[str, str]): raw data from toml

        Returns:
            MetaData: Parsed MetaData
        """
        if data is None:
            return MetaData()

        return MetaData(
            name=data.get("name", ""),
            version=data.get("version", "0.0.0"),
            license=data.get("license", "MIT"),
            repo_url=data.get("repo_url", ""),
            project_url=data.get("project_url", ""),
            header_only=bool(data.get("header_only", False)),
        )

@attrs.define()
class Structure:
    """CAU Project directory structure."""
    source_path: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path()/"src",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )

    header_path: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path()/"include",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )

    test_path: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path()/"tests",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )

    build_path: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path()/"build",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )

    max_depth: int = attrs.field(default=2, converter=int, validator=attrs.validators.instance_of(int))

    @staticmethod
    def read(structure_data: dict[str, str]) -> Structure:
        """
        Reads from dictionary values of what the project structure should look like into data structure.

        Args:
            structure_data (dict[str, str]): raw data from toml.

        Returns:
            ProjectStructure: Parsed ProjectStructure
        """
        if structure_data is None:
            return Structure()

        return Structure(
            source_path=structure_data.get("source", "src"),
            header_path=structure_data.get("headers", "include"),
            test_path=structure_data.get("tests", "tests"),
            build_path=structure_data.get("build", "build"),
            max_depth=structure_data.get("maximum_module_depth", 2),
        )

    def paths(self, header_only: bool = False) -> Iterator[pathlib.Path]:
        """
        All major paths in the project structure.

        Args:
            header_only (bool, optional): generate a header only. Defaults to False.

        Returns:
            Iterator[pathlib.Path]: major project paths
        """
        if not header_only:
            yield self.source_path
        yield self.header_path
        yield self.test_path

@attrs.define()
class Build:
    """Holds build information."""
    cross_build: bool = attrs.field(default=False, converter=bool, validator=attrs.validators.instance_of(bool))
    clang_version: int = attrs.field(default=14, converter=int, validator=attrs.validators.instance_of(int))
    gcc_version: int = attrs.field(default=10, converter=int, validator=attrs.validators.instance_of(int))
    cpp_standard: int = attrs.field(default=20, converter=int, validator=attrs.validators.instance_of(int))
    cmake_min_version: str = attrs.field(default="3.29", converter=str, validator=attrs.validators.instance_of(str))

    @staticmethod
    def read(data: dict[str, str]) -> Build:
        """
        Reads from dictionary values of what the build properties for the project are into data structure.

        Args:
            data (dict[str, str]): raw data from toml.

        Returns:
            Build: Parsed Build properties
        """
        if data is None:
            return Build()

        return Build(
            cross_build=data.get("cross_build", False),
            clang_version=data.get("clang_version", 14),
            gcc_version=data.get("gcc_version", 10),
            cpp_standard=data.get("cpp_standard", 20),
            cmake_min_version=data.get("cmake_min_version", "3.29"),
        )

@attrs.define()
class Gitlab:
    """Gitlab configuration."""
    docker_image: str = attrs.field(
        default=default_docker_image,
        converter=str,
        validator=attrs.validators.instance_of(str),
    )
    code_quality: bool = attrs.field(default=True, converter=bool, validator=attrs.validators.instance_of(bool))
    sast: bool = attrs.field(default=True, converter=bool, validator=attrs.validators.instance_of(bool))
    secrets: bool = attrs.field(default=True, converter=bool, validator=attrs.validators.instance_of(bool))
    self_managed: bool = attrs.field(default=False, converter=bool, validator=attrs.validators.instance_of(bool))

    @staticmethod
    def read(data: dict[str, str]) -> Gitlab:
        """
        Reads from dictionary values of what the gitlab pipeline configuration is.

        Args:
            data (dict[str, str]): raw data from toml

        Returns:
            Gitlab: Parsed Gitlab properties
        """
        if data is None:
            return Gitlab()

        return Gitlab(
            docker_image=data.get("docker_image", default_docker_image),
            code_quality=data.get("code_quality", True),
            sast=data.get("sast", True),
            secrets=data.get("secrets", True),
            self_managed=data.get("self_managed", False),
        )

    def need_to_include(self) -> bool:
        """
        Checks if template writer will need to write an include block.

        Returns:
            bool: if includes are needed
        """
        return any(x for x in (self.code_quality, self.sast, self.secrets))

@attrs.define()
class CAUProject:
    """CAU Project."""
    meta_data: MetaData = attrs.field(
        factory=MetaData,
        validator=attrs.validators.instance_of(MetaData),
    )
    structure: Structure = attrs.field(
        factory=Structure,
        validator=attrs.validators.instance_of(Structure),
    )
    build: Build = attrs.field(factory=Build, validator=attrs.validators.instance_of(Build))
    gitlab: Gitlab = attrs.field(factory=Gitlab, validator=attrs.validators.instance_of(Gitlab))

    @staticmethod
    def read(project_file: pathlib.Path) -> CAUProject:
        """
        Reads cau project file.

        Args:
            project_file (pathlib.Path): path to project file

        Returns:
            CAUProject: project configuration
        """
        if not project_file.exists():
            return CAUProject()

        with project_file.open("rb") as project:
            config_dict = tomli.load(project)

        return CAUProject(
            meta_data=MetaData.read(config_dict.get("metadata", None)),
            structure=Structure.read(config_dict.get("structure", None)),
            build=Build.read(config_dict.get("build", None)),
            gitlab=Gitlab.read(config_dict.get("gitlab", None)),
        )

    def write_config(self) -> None:
        """Writes configuration file to disk."""
        self.__write_file(pathlib.Path(), pathlib.Path("cauproject.toml"), "project.toml", project=self)

    def initialize(self) -> None:
        """Initializes a CAU project."""
        logger.info("Initializing new project %s", self.meta_data.name)
        _ = [path.mkdir() for path in self.structure.paths(header_only=self.meta_data.header_only)]
        self.__setup_conan()
        self.__setup_gitlab()
        self.__setup_docs()
        self.__setup_vscode()
        self.__setup_cmake()
        self.__setup_hello_world()

    def generate(self, name: str, module: str | None = None, header_only: bool = False) -> None:
        """
        Generates header, source, and test files for class/function header.

        Args:
            name (str): header name

            module (str, optional): module or subdirectory to put source into. Defaults to None.

            header_only (bool, optional): generate a header only. Defaults to False.
        """
        module = module or ""

        header_only = header_only or self.meta_data.header_only

        self.__write_file(self.structure.header_path/module, pathlib.Path(f"{name}.hpp"), "header.hpp", name=name)
        if not header_only:
            self.__write_file(self.structure.source_path/module, pathlib.Path(f"{name}.cpp"), "source.cpp", name=name)
        self.__write_file(
            self.structure.test_path/module,
            pathlib.Path(f"{name.lower()}_test.cpp"),
            "test.cpp",
            name=name,
        )

    def add_module(self, *module_names: str, header_only: bool = False) -> None:
        """
        Adds module/submodule(s) to project.

        Args:
            module_names (str): names of module/submodule(s)

            header_only (bool, optional): generate a header only. Defaults to False.
        """
        if len(module_names) > self.structure.max_depth:
            message = (
                f"Maximum depth of modules of {self.structure.max_depth} have been reached!"
                "Modify path or update the allowed module depth."
            )
            logger.exception(message)
            raise MaximumModuleDepthError(message)

        module_path = pathlib.Path(*module_names)
        header_only = header_only or self.meta_data.header_only
        logger.info("Creating new module with structure: %s", module_path)
        paths = [path/module_path for path in self.structure.paths(header_only=header_only)]
        _ = [path.mkdir(parents=True) for path in paths]
        module_name = module_names[-1]

        # only write CMake file if the module is a root module
        if len(module_names) < self.structure.max_depth and not header_only:
            self.__write_file(
                self.structure.source_path/module_path,
                pathlib.Path("CMakeLists.txt"),
                "cmake/module_cmakelists.txt",
                module_name=module_name,
            )
            logger.info(
                "CMakeLists.txt created for %s. Be sure to add `add_subdirectory` directive project root CMakeLists.txt!",
            )

    def __write_file(
        self,
        path: pathlib.Path,
        file_name: pathlib.Path,
        template_name: str,
        **template_args: dict[str, object],
    ) -> None:
        full_path = path/file_name
        template = jinja_env.get_template(template_name)
        with full_path.open("w", encoding="utf-8") as to_write:
            to_write.write(template.render(template_args))

    def __setup_conan(self) -> None:

        logger.info("Creating conanfile")
        self.__write_file(pathlib.Path(), pathlib.Path("conanfile.py"), "conan/conanfile.py", meta_data=self.meta_data)

        profile_path = pathlib.Path(".conan")/"profiles"
        profile_path.mkdir(parents=True)

        profile_files = ("Default", "Debug", "Release")
        operating_systems = ("linux", "win64") if self.build.cross_build else ("linux", )

        logger.info("Creating conan profiles")
        _ = [
            self.__write_file(profile_path, f"{os}{config}", f"conan/profiles/{os}{config}", build=self.build)
            for os, config in itertools.product(operating_systems, profile_files)
        ]

        self.__write_file(profile_path, "default", "conan/profiles/linuxDebug", build=self.build)

    def __setup_gitlab(self) -> None:
        gitlab_path = pathlib.Path(".gitlab")
        gitlab_path.mkdir()

        logger.info("Setting up gitlab pipeline.")
        self.__write_file(pathlib.Path(), ".gitlab-ci.yml", "gitlab/pipeline.yml", meta_data=self.meta_data)
        self.__write_file(gitlab_path, "Build.gitlab-ci.yml", "gitlab/build.yml", gitlab=self.gitlab, build=self.build)
        self.__write_file(
            gitlab_path,
            "Test.gitlab-ci.yml",
            "gitlab/test.yml",
            meta_data=self.meta_data,
            gitlab=self.gitlab,
        )

        logger.info("Creating clang files")
        self.__write_file(gitlab_path, ".clang-tidy", "gitlab/clang_tidy", build=self.build)
        self.__write_file(pathlib.Path(), ".clang-format", "gitlab/clang_format")

        logger.info("Creating gitignore")
        self.__write_file(pathlib.Path(), ".gitignore", "gitlab/gitignore")

        if self.gitlab.code_quality:
            logger.info("Creating code quality configuration")
            self.__write_file(pathlib.Path(), ".codeclimate.yml", "gitlab/code_climate.yml")

    def __setup_docs(self) -> None:
        docs_path = pathlib.Path("docs")
        (docs_path/"source").mkdir(parents=True)

        logger.info("Creating docs pipeline files")

        self.__write_file(
            docs_path,
            "Docs.gitlab-ci.yml",
            "docs/docs.yml",
            meta_data=self.meta_data,
            gitlab=self.gitlab,
        )

        logger.info("Creating doxygen file")
        self.__write_file(
            docs_path/"source",
            "Doxyfile.in",
            "docs/doxygen",
            meta_data=self.meta_data,
        )

        logger.info("Creating pyproject file for docs")
        self.__write_file(
            pathlib.Path(),
            "pyproject.toml",
            "docs/pyproject",
            meta_data=self.meta_data,
        )

        logger.info("Creating docs make file")
        self.__write_file(
            docs_path,
            "Makefile",
            "docs/Makefile",
        )

        logger.info("Creating docs conf.py file")
        self.__write_file(
            docs_path/"source",
            "conf.py",
            "docs/conf.py",
            meta_data=self.meta_data,
        )

        logger.info("Creating docs index.md file")
        self.__write_file(
            docs_path/"source",
            "index.md",
            "docs/index.md",
            meta_data=self.meta_data,
        )

    def __setup_vscode(self) -> None:
        logger.info("Setting up vscode config")
        vscode_path = pathlib.Path(".vscode")
        vscode_path.mkdir()

        self.__write_file(vscode_path, "tasks.json", "vscode/tasks.json")
        self.__write_file(vscode_path, "launch.json", "vscode/launch.json", meta_data=self.meta_data)
        self.__write_file(vscode_path, "settings.json", "vscode/settings.json")

    def __setup_cmake(self) -> None:
        logger.info("Creating cmake files")
        root_path = pathlib.Path()
        cmake = "CMakeLists.txt"
        self.__write_file(root_path, cmake, "cmake/root_cmakelists.txt", project=self)
        self.__write_file(self.structure.test_path, cmake, "cmake/test_cmakelists.txt", project=self)

    def __setup_hello_world(self) -> None:
        logger.info("Creating hello world sources")
        self.__write_file(
            self.structure.header_path,
            "hello.hpp",
            "hello/hello.hpp",
            header_only=self.meta_data.header_only,
        )
        if not self.meta_data.header_only:
            self.__write_file(self.structure.source_path, "hello.cpp", "hello/hello.cpp")
        self.__write_file(self.structure.test_path, "hello_test.cpp", "hello/hello_test.cpp")
