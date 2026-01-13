#    VenviPy - A Virtual Environment Manager for Python.
#    Copyright (C) 2021 - Youssef Serestou - sinusphi.sq@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License or any
#    later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License version 3 named LICENSE is
#    in the root directory of VenviPy.
#    If not, see <https://www.gnu.org/licenses/licenses.en.html#GPL>.

# -*- coding: utf-8 -*-
"""
Base platform abstraction.
"""
from pathlib import Path


class Platform:
    """Small OS abstraction layer."""
    name = "base"

    def is_windows(self):
        return False

    def is_linux(self):
        return False

    def venv_bin_dir_name(self):
        return "bin"

    def python_exe_name(self):
        return "python"

    def pip_exe_name(self):
        return "pip"

    def venv_python_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / self.python_exe_name()

    def venv_pip_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / self.pip_exe_name()

    def activate_script_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / "activate"

    def default_python_search_path(self) -> str:
        return str(Path.home())

    def site_packages_path(self, venv_dir: Path) -> Path:
        lib_dir = venv_dir / "lib"
        if not lib_dir.exists():
            lib_dir = venv_dir / "Lib"
        return lib_dir / "site-packages"
