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
This module provides several necessary data.
"""
import re
import os
import sys
import csv
import shutil
import logging
from subprocess import Popen, PIPE
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests

__version__ = "0.3.6"

CFG_DIR = os.path.expanduser("~/.venvipy")
DB_FILE = os.path.expanduser("~/.venvipy/py-installs")
ACTIVE_DIR = os.path.expanduser("~/.venvipy/selected-dir")
ACTIVE_VENV = os.path.expanduser("~/.venvipy/active-venv")
PYPI_URL = "https://pypi.org/search/"


logger = logging.getLogger(__name__)

#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    """Info about Python installs."""
    py_version: str
    py_path: str


def to_version(value):
    """Convert a value to a readable version string.
    """
    return f"Python {value}"


def to_path(bin_path, version):
    """Return the absolute path to a python binary.
    """
    return os.path.join(bin_path, f"python{version}")


def is_writable(target_dir):
    """Test whether a directory is writable.
    """
    if os.path.exists(target_dir):
        test_file = os.path.join(target_dir, "test_file")

        try:
            logger.debug("Testing whether filesystem is writable...")
            with open(test_file, "w+", encoding="utf-8") as f:
                f.write("test")

            os.remove(test_file)
            logger.debug("Filesystem is writable")
            return True

        except OSError as e:
            logger.debug(f"Filesystem is read-only\n{e}")
            return False

    else:
        logger.debug(f"No such file or directory: {target_dir}")
        return False

    return False


def ensure_confdir():
    """Create `~/.venvipy` config directory.
    """
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)


def ensure_dbfile():
    """Create the database in `~/.venvipy/py-installs`.
    """
    if not os.path.exists(DB_FILE):
        get_python_installs()


def ensure_active_dir():
    """Create the file that holds the selected path to venvs.
    """
    ensure_confdir()
    if not os.path.exists(ACTIVE_DIR):
        with open(ACTIVE_DIR, "w+", encoding="utf-8") as f:
            f.write("")


def ensure_active_venv():
    """Create the file that holds the selected path to venvs.
    """
    ensure_confdir()
    if not os.path.exists(ACTIVE_VENV):
        with open(ACTIVE_VENV, "w+", encoding="utf-8") as f:
            f.write("")


def get_python_version(py_path):
    """Return Python version.
    """
    with Popen([py_path, "-V"], stdout=PIPE, text="utf-8") as res:
        out, _ = res.communicate()

    python_version = out.strip()
    return python_version


def get_python_installs(relaunching=False):
    """
    Write the found Python versions to `py-installs`. Create
    a new database if `relaunching=True`.
    """
    versions = [
        "3.11", "3.10", "3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3"
    ]
    py_info_list = []
    ensure_confdir()

    if not os.path.exists(DB_FILE) or relaunching:
        with open(DB_FILE, "w", newline="", encoding="utf-8") as cf:
            fields = ["PYTHON_VERSION", "PYTHON_PATH"]
            writer = csv.DictWriter(
                cf,
                delimiter=",",
                quoting=csv.QUOTE_ALL,
                fieldnames=fields
            )
            writer.writeheader()

            for i, version in enumerate(versions):
                python_path = shutil.which(f"python{version}")
                if python_path is not None:
                    python_version = get_python_version(python_path)
                    py_info = PythonInfo(python_version, python_path)
                    py_info_list.append(py_info)
                    writer.writerow({
                        "PYTHON_VERSION": py_info.py_version,
                        "PYTHON_PATH": py_info.py_path
                    })

            cf.close()

            # add the system's Python manually if running in a virtual env
            if "VIRTUAL_ENV" in os.environ:
                system_python = os.path.realpath(sys.executable)
                add_python(system_python)

        return py_info_list[::-1]
    return False


def add_python(py_path):
    """
    Write (append) a Python version and its path to `py-installs`.
    """
    ensure_dbfile()

    with open(DB_FILE, "a", newline="", encoding="utf-8") as cf:
        fields = ["PYTHON_VERSION", "PYTHON_PATH"]
        writer = csv.DictWriter(
            cf,
            delimiter=",",
            quoting=csv.QUOTE_ALL,
            fieldnames=fields
        )
        writer.writerow({
            "PYTHON_VERSION": get_python_version(py_path),
            "PYTHON_PATH": py_path
        })
        cf.close()

    # remove the interpreter if running in a virtual env
    if "VIRTUAL_ENV" in os.environ:
        remove_env()


def remove_env():
    """
    Remove our interpreter if we're running in a virtual
    environment.
    """
    with open(DB_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if sys.executable not in line.strip("\n"):
                f.write(line)


#]===========================================================================[#
#] GET VENVS [#==============================================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    """_"""
    venv_name: str
    venv_version: str
    site_packages: str
    is_installed: str
    venv_comment: str


def get_venvs(path):
    """
    Get the available virtual environments
    from the specified folder.
    """
    # return an emtpty list if directory doesn't exist
    if not os.path.isdir(path):
        return []

    venv_info_list = []

    for i, venv in enumerate(os.listdir(path)):
        # build path to venv directory
        valid_venv = os.path.join(path, venv)

        # only look for dirs
        if not os.path.isdir(valid_venv):
            continue

        # build path to pyvenv.cfg file
        cfg_file = os.path.join(valid_venv, "pyvenv.cfg")
        if not os.path.isfile(cfg_file):
            continue

        # build path to venvipy.cfg file
        venvipy_cfg_file = os.path.join(valid_venv, "venvipy.cfg")

        venv_name = os.path.basename(valid_venv)
        venv_version = get_config(cfg_file, "version")
        site_packages = get_config(cfg_file, "site_packages")
        is_installed = get_config(cfg_file, "installed")
        venv_comment = get_comment(venvipy_cfg_file)

        venv_info = VenvInfo(
            venv_name,
            venv_version,
            site_packages,
            is_installed,
            venv_comment
        )
        venv_info_list.append(venv_info)

    return venv_info_list[::-1]


def get_config(cfg_file, cfg):
    """
    Return the values as string from a `pyvenv.cfg` file.
    Values for `cfg` can be: `version`, `py_path`,
    `site_packages`, `installed`, `comment`.
    """
    with open(cfg_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines[2][13] == ".":
        version = lines[2][10:13].strip()  # python 3.x
    else:
        version = lines[2][10:14].strip()  # python 3.10+

    version_str = to_version(lines[2][10:].strip())
    binary_path = to_path(lines[0][7:].strip(), version)
    site_packages = lines[1][31:].strip()

    if cfg == "version":
        return version_str

    if cfg == "py_path":
        return binary_path

    if cfg == "site_packages":
        if site_packages == "true":
            return "global"
        if site_packages == "false":
            return "isolated"
        return "N/A"

    if cfg == "installed":
        ensure_dbfile()
        with open(DB_FILE, newline="", encoding="utf-8") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            for info in reader:
                if binary_path == info["PYTHON_PATH"]:
                    return "yes"
            return "no"

    return "N/A"


def get_active_dir_str():
    """Return path to selected directory.
    """
    ensure_active_dir()
    with open(ACTIVE_DIR, "r", encoding="utf-8") as f:
        selected_dir = f.read()
        return selected_dir
    return ""


def get_selected_dir():
    """
    Get the selected directory path from `selected-dir`
    file. Return `get_venvs()`.
    """
    selected_dir = get_active_dir_str()
    return get_venvs(selected_dir)


def get_comment(cfg_file):
    """Get the comment string from `venvipy_cfg` file.
    """
    if os.path.exists(cfg_file):
        with open(cfg_file, "r", encoding="utf-8") as f:
            venv_comment = f.read()

        return venv_comment
    return ""


#]===========================================================================[#
#] GET INFOS FROM PYTHON PACKAGE INDEX [#====================================[#
#]===========================================================================[#

@dataclass
class PackageInfo:
    """_"""
    pkg_name: str
    pkg_version: str
    pkg_release_date: str
    pkg_summary: str


def get_package_infos(pkg):
    """
    Scrape package infos from [PyPI](https://pypi.org).
    """
    snippets = []
    package_info_list = []

    for page in range(1, 3):
        params = {"q": pkg, "page": page}
        with requests.Session() as session:
            res = session.get(PYPI_URL, params=params)

        soup = BeautifulSoup(res.text, "html.parser")
        snippets += soup.select('a[class*="snippet"]')

        if not hasattr(session, "start_url"):
            session.start_url = res.url.rsplit("&page", maxsplit=1).pop(0)

    for snippet in snippets:
        pkg_name = re.sub(
            r"\s+",
            " ",
            snippet.select_one('span[class*="package-snippet__name"]').text.strip()
        )
        pkg_version = re.sub(
            r"\s+",
            " ",
            snippet.select_one('span[class*="package-snippet__version"]').text.strip()
        )
        pkg_release_date = re.sub(
            r"\s+",
            " ",
            snippet.select_one('span[class*="package-snippet__created"]').text.strip()
        )
        pkg_summary = re.sub(
            r"\s+",
            " ",
            snippet.select_one('p[class*="package-snippet__description"]').text.strip()
        )

        pkg_info = PackageInfo(
            pkg_name,
            pkg_version,
            pkg_release_date,
            pkg_summary
        )
        package_info_list.append(pkg_info)

    return package_info_list[::-1]
