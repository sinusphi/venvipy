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
Linux platform implementation.
"""
from .base import Platform


class LinuxPlatform(Platform):
    name = "linux"

    def is_linux(self):
        return True

    def default_python_search_path(self) -> str:
        return "/usr/local/bin"

    def site_packages_path(self, venv_dir):
        lib_dir = venv_dir / "lib"
        if not lib_dir.exists():
            return lib_dir / "site-packages"
        python_dirs = [p for p in lib_dir.iterdir() if p.is_dir()]
        if not python_dirs:
            return lib_dir / "site-packages"
        return python_dirs[0] / "site-packages"
