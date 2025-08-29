"""Conan file for {{meta_data.name}} """
import os
import pathlib
import shutil

import conan
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import copy

class {{meta_data.name}}(conan.ConanFile):
    """ Conan recipe for {{meta_data.name}} """
    name = "{{meta_data.name}}"
    version = "{{meta_data.version}}"
    license = "{{meta_data.license}}"
    url = "{{meta_data.repo_url}}"
    homepage = "{{meta_data.project_url}}"
    settings = "os", "arch", "compiler", "build_type"
    cross_building = os.environ.get("PLATFORM") == "win64"

    def requirements(self):
        """Adds dependencies."""
        self.requires("gtest/1.13.0", test=True)

    def generate(self):
        """Generates cmake code for dependencies."""
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

        tool_chain = CMakeToolchain(self, generator="Ninja")
        tool_chain.generate()

    def build(self):
        """Builds {{meta_data.name}}."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        self.package()

    def package(self):
        """Packages {{meta_data.name}}. """
        self._copy_headers()
        self._copy_mingw_libs()

    def _copy_headers(self):
        """
        Copies headers to include directory.
        """
        shutil.copytree(
            pathlib.Path("..")/"include",
            pathlib.Path("include"),
            copy_function=self._verbose_copy,
            dirs_exist_ok=True
        )

    def _copy_mingw_libs(self):
        """
        If we're cross building then copy the relevant mingw libs to bin directory
        """
        if not self.cross_building:
            return

        build_env = self.buildenv.vars(self)
        dlls = ("libstdc++-6", "libgcc_s_seh-1")
        dll_directory = pathlib.Path(build_env["DLL_DIR"])
        bin_folder = pathlib.Path(self.build_folder)/"bin"

        for dll in dlls:
            dll = f"{dll}.dll"
            self.output.success(f"Copying: {dll}")
            copy(self, dll, dll_directory, bin_folder)

        pthreads = pathlib.Path(build_env["CONAN_CMAKE_SYSROOT"])/"lib"/"libwinpthread-1.dll"
        self.output.success(f"Copying: {pthreads.name}")
        copy(self, pthreads.name, pthreads.parent, bin_folder)

    def _verbose_copy(self, source: str, destination: str):
            self.output.success(f"Copying {source} to {destination}")
            shutil.copy2(source, destination)

