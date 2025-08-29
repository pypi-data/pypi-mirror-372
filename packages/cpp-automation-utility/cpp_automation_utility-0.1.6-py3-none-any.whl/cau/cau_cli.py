"""C++ Automation Utility (CAU)."""
import logging
import pathlib
import sys

import click
import importlib_metadata

import cau

version = importlib_metadata.version("cpp-automation-utility")

pass_project_file = click.option("--project-file", default="cauproject.toml", help="Path to cauproject.toml file.")

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version)
@click.pass_context
def cau_cli(ctx: click.core.Context) -> None: # noqa: D103
    ctx.obj = {}

sys.tracebacklimit = 1

logger = logging.getLogger("CAU")

restore_help = "Skip restoration of Conan sources"
build_directory_help = "Build directory of project"
build_type_help = "Build type (Debug|Release)"
platform_help = "Build platform (linux|win64)"

default_build_dir = "build"
default_clang_version = 14

def cli_or_project_value(cli_value: object, project_file_value: object, default_value: object) -> object:
    """
    Takes the value provided via the command line or takes the project file value.

    Args:
        cli_value (object): value provided on command line

        project_file_value (object): value in project file

        default_value (object): default command line value

    Returns:
        object: value from command line or project file
    """
    if cli_value not in {default_value, project_file_value}:
        return cli_value
    return project_file_value

@cau_cli.command(help="Restores conan dependencies")
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@click.option("-t", "--build-type", default="Debug", help=build_type_help)
@click.option("-p", "--platform", default="linux", help=platform_help)
@pass_project_file
@cau.timer
def restore(build_directory: str, build_type: str, platform: str, project_file: str) -> None:
    """Restores conan dependencies."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    conan = cau.Conan(
        build_directory=cli_or_project_value(build_directory, project.structure.build_path, default_build_dir),
        build_type=build_type,
        platform=platform,
    )

    result = conan.restore()
    sys.exit(result.returncode)

@cau_cli.command(help="Runs clang-tidy to lint C++ source files.")
@click.option("-s", "--skip-restore", is_flag=True, default=False, help=restore_help)
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@click.option("-i", "--ignore-pattern", default=None, help="Regex pattern to ignore when linting files.")
@click.option("-v", "--clang-version", default=default_clang_version, help="Version of clang to use")
@click.option("-f", "--force", is_flag=True, default=False, help="Force linting of all files.")
@pass_project_file
@cau.timer
def lint(
    skip_restore: bool,
    build_directory: str,
    ignore_pattern: str,
    clang_version: int,
    project_file: str,
    force: bool,
) -> None:
    """Lint command creates a lint object and calls the lint object."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    if not skip_restore:
        conan = cau.Conan(
            build_directory=cli_or_project_value(build_directory, project.structure.build_path, default_build_dir),
        )
        _ = conan.restore()

    logger.debug("Interrogating git for files")
    git = cau.Git()
    files = git.all_files() if force else git.changed_files()

    logger.debug("Performing lint operation")
    linter = cau.Tidy(
        files=files,
        compile_database_dir=build_directory,
        ignore_pattern=ignore_pattern,
        version=cli_or_project_value(clang_version, project.build.clang_version, default_clang_version),
    )
    result = linter.lint()
    sys.exit(0 if result else 1)

@cau_cli.command(help="Build project via conan")
@click.option("-s", "--skip-restore", is_flag=True, default=False, help=restore_help)
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@click.option("-t", "--build-type", default="Debug", help=build_type_help)
@click.option("-p", "--platform", default="linux", help=platform_help)
@pass_project_file
@cau.timer
def build(skip_restore: bool, build_directory: str, build_type: str, platform: str, project_file: str) -> None:
    """Build command build the project via conan."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    conan = cau.Conan(
        build_directory=cli_or_project_value(build_directory, project.structure.build_path, default_build_dir),
        build_type=build_type,
        platform=platform,
    )
    if not skip_restore:
        conan.restore()
    result = conan.build()
    sys.exit(result.returncode)

@cau_cli.command(help="Cleans project build files")
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@click.option("-a", "--all-files", is_flag=True, default=False, help="Cleans build directory and conan directory")
@click.option("--only-build", is_flag=True, default=False, help="Only delete build directory")
@click.option("--only-conan", is_flag=True, default=False, help="Removes conan dependencies")
@pass_project_file
@cau.timer
def clean(build_directory: str, all_files: bool, only_build: bool, only_conan: bool, project_file: str) -> None:
    """Clean project of build files."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    conan = cau.Conan(
        build_directory=cli_or_project_value(build_directory, project.structure.build_path, default_build_dir),
    )
    if all_files:
        results = [method() for method in (conan.clean_build, conan.clean_conan)]
        result = all(results)
    elif only_build:
        result = conan.clean_build()
    elif only_conan:
        result = conan.clean_conan()
    else:
        sys.exit(0)
    sys.exit(0 if result else 1)

@cau_cli.command(help="Runs test executable and then collects coverage information")
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@click.option("-v", "--clang-version", default=default_clang_version, help="Version of clang to use")
@pass_project_file
@cau.timer
def coverage(build_directory: str, project_file: str, clang_version: int) -> None:
    """Generates coverage information from project test executable."""
    project_config = cau.CAUProject.read(pathlib.Path(project_file))
    coverage_wrapper = cau.Coverage(
        project_config,
        build_directory=cli_or_project_value(build_directory, project_config.structure.build_path, default_build_dir),
        version=cli_or_project_value(clang_version, project_config.build.clang_version, default_clang_version),
    )
    result = coverage_wrapper.run()
    sys.exit(result.returncode)

@cau_cli.command(help="Runs test executable and checks for memory leaks")
@click.option("-p", "--project", required=True, type=str, help="Project name, will run test executable Test<Project>")
@click.option("-b", "--build-directory", default=default_build_dir, help=build_directory_help)
@pass_project_file
@cau.timer
def leak_check(project: str, build_directory: str, project_file: str) -> None:
    """Checks for memory leaks in test executable."""
    project_config = cau.CAUProject.read(pathlib.Path(project_file))
    valgrind_wrapper = cau.Valgrind(
        project=project,
        build_directory=cli_or_project_value(build_directory, project_config.structure.build_path, default_build_dir),
    )
    result = valgrind_wrapper.check_memory(valgrind_wrapper.test_executable)
    sys.exit(result.returncode)

@cau_cli.command(help="Generates header, source, and test files for class/function given name.")
@click.argument("name")
@click.option("-m", "--module", default=None, help="Module or subdirectory name to install files into.")
@click.option("--header-only", is_flag=True, default=False, help="Create a header only. No source file.")
@pass_project_file
@cau.timer
def generate(name: str, module: str | None, project_file: str, header_only: bool) -> None:
    """Generates header, source, and test files for class/function given name."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    logger.info("Generating %s in module %s", name, module if module else "root")
    project.generate(name=name, module=module, header_only=header_only)
    sys.exit(0)

@cau_cli.command(help="Generates a new module directory with a CMakeLists.txt file if it is a top-level module.")
@click.argument("module_names", nargs=-1)
@click.option("--header-only", is_flag=True, default=False, help="Create a header only. No source file.")
@pass_project_file
@cau.timer
def new_module(project_file: str, module_names: str, header_only: bool) -> None:
    """Adds new module structure to project."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    project.add_module(*module_names, header_only=header_only)
    sys.exit(0)

@cau_cli.command(help="Generates a new project from user supplied cauproject.toml file.")
@pass_project_file
@cau.timer
def initialize(project_file: str) -> None:
    """Initializes a new project from the user supplied cauproject.toml file."""
    project = cau.CAUProject.read(pathlib.Path(project_file))
    project.initialize()
    sys.exit(0)

@cau_cli.command(help="Generates a default cauproject.toml file")
@cau.timer
def new_config() -> None:
    """Generates a default cauproject.toml file."""
    logger.info("Creating default cauproject.toml file.")
    project = cau.CAUProject()
    project.write_config()

if __name__ == "__main__":
    cau_cli()
