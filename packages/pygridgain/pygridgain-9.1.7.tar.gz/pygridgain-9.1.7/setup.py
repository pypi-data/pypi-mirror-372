# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import multiprocessing
import os
import platform
import subprocess
import sys
from pprint import pprint

import setuptools
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

PACKAGE_NAME = "pygridgain"
EXTENSION_NAME = f"{PACKAGE_NAME}._native_extension"


def _read_version(version_path):
    with open(version_path, "r") as fd:
        ver = fd.read().strip()
        if not ver:
            raise RuntimeError("Cannot find version information")
        return ver


version = _read_version(os.path.join(PACKAGE_NAME, "_version.txt"))


def cmake_project_version(ver):
    """
    Strips the pre-release portion of the project version string to satisfy CMake requirements
    """
    dash_index = ver.find("-")
    if dash_index != -1:
        return ver[:dash_index]
    return ver


# Command line flags forwarded to CMake (for debug purpose)
cmake_cmd_args = []
for f in sys.argv:
    if f.startswith("-D"):
        cmake_cmd_args.append(f)


class CMakeExtension(Extension):
    def __init__(self, name, cmake_lists_dir=".", sources=[], **kwa):
        Extension.__init__(self, name, sources=sources, **kwa)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)


class CMakeBuild(build_ext):
    def build_extensions(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("Cannot find CMake executable")

        for ext in self.extensions:
            ext_dir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            cfg = "Release"
            ext_file = os.path.splitext(os.path.basename(self.get_ext_filename(ext.name)))[0]

            cmake_args = [
                f"-DCMAKE_BUILD_TYPE={cfg}",
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={ext_dir}",
                f"-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_{cfg.upper()}={self.build_temp}",
                f"-DEXTENSION_FILENAME={ext_file}",
                f"-DIGNITE_VERSION={cmake_project_version(version)}",
            ]

            if platform.system() == "Windows":
                plat = "x64" if platform.architecture()[0] == "64bit" else "Win32"
                cmake_args += [
                    "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE",
                    f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{cfg.upper()}={ext_dir}",
                ]
                if self.compiler.compiler_type == "msvc":
                    cmake_args += [
                        f"-DCMAKE_GENERATOR_PLATFORM={plat}",
                    ]
                else:
                    raise RuntimeError("Only MSVC is supported for Windows currently")

            cmake_args += cmake_cmd_args

            pprint(cmake_args)

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            cpu_count = multiprocessing.cpu_count()

            # Config and build the extension
            subprocess.check_call(["cmake", ext.cmake_lists_dir] + cmake_args, cwd=self.build_temp)
            subprocess.check_call(["cmake", "--build", ".", "-j", str(cpu_count), "--config", cfg, "-v"], cwd=self.build_temp)


def run_setup():
    setuptools.setup(
        packages=setuptools.find_packages(),
        version=version,
        ext_modules=[CMakeExtension(EXTENSION_NAME)],
        cmdclass=dict(build_ext=CMakeBuild),
    )


if __name__ == "__main__":
    run_setup()
