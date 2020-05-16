# -*- coding: utf-8 -*-
"""
This module provides all the necessary data.
"""
import xmlrpc.client
import shutil
import csv
import sys
import os
from subprocess import Popen, PIPE
from dataclasses import dataclass

__version__ = "0.2.9"



#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    """_"""
    py_version: str
    py_path: str


def get_python_version(py_path):
    """Return Python version.
    """
    res = Popen(
        [py_path, "-V"],
        stdout=PIPE,
        text="utf-8"
    )
    out, _ = res.communicate()
    python_version = out.strip()
    return python_version


def get_python_installs():
    """Get the available python versions installed.
    """
    versions = ["3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3"]
    py_info_list = []
    csv_file = os.path.expanduser("~/.venvipy/py-installs")

    if not os.path.exists(os.path.expanduser("~/.venvipy")):
        os.mkdir(os.path.expanduser("~/.venvipy"))

    with open(csv_file, "w", newline="") as cf:
        fields = ["PYTHON_VERSION", "PYTHON_PATH"]
        writer = csv.DictWriter(
            cf, delimiter=",", quoting=csv.QUOTE_ALL, fieldnames=fields
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
    add_sys_python()


def add_sys_python():
    """
    Add the system python if running VenviPy in a
    virtual environment.
    """
    csv_file = os.path.expanduser("~/.venvipy/py-installs")
    super_python = os.path.realpath(sys.executable)

    if not os.path.isfile(csv_file):
        get_python_installs()

    with open(csv_file, "a", newline="") as cf:
        fields = ["PYTHON_VERSION", "PYTHON_PATH"]
        writer = csv.DictWriter(
            cf, delimiter=",", quoting=csv.QUOTE_ALL, fieldnames=fields
        )
        writer.writerow({
            "PYTHON_VERSION": get_python_version(super_python),
            "PYTHON_PATH": super_python
        })


#]===========================================================================[#
#] GET VENVS [#==============================================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    """_"""
    venv_name: str
    venv_version: str
    system_site_packages: str
    is_on_system: str


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
        if not os.path.isdir(valid_venv):
            continue

        # build path to pyvenv.cfg file
        cfg_file = os.path.join(valid_venv, "pyvenv.cfg")
        if not os.path.isfile(cfg_file):
            continue

        venv_name = os.path.basename(valid_venv)
        version_found = get_pyvenv_cfg(cfg_file, line=2)
        system_site_packages = get_pyvenv_cfg(cfg_file, line=1)
        is_on_system = is_installed(cfg_file)

        venv_info = VenvInfo(
            venv_name, version_found, system_site_packages, is_on_system
        )
        venv_info_list.append(venv_info)

    return venv_info_list


def is_installed(cfg_file):
    """Check if a Python version is installed.
    """
    with open(cfg_file, "r") as f:
        lines = f.readlines()

    python_path = lines[0][7:].strip()  # e.g. /usr/local/bin
    python_version = lines[2][10:13].strip()  # e.g. 3.8
    target = f"{python_path}/python{python_version}"
    csv_file = os.path.expanduser("~/.venvipy/py-installs")

    if not os.path.isfile(csv_file):
        get_python_installs()

    with open(csv_file, newline="") as cf:
        reader = csv.DictReader(cf, delimiter=",")
        for info in reader:
            if target == info["PYTHON_PATH"]:
                return "yes"
        return "no"


def get_pyvenv_cfg(cfg_file, line):
    """
    Get the required info of a virtual environment
    by reading `pyvenv.cfg` file.
    """
    with open(cfg_file, "r") as f:
        lines = f.readlines()

    if line == 1:
        system_site_packages = lines[1][31:]  # true | false
        if "true" in system_site_packages:
            return "global"
        if "false" in system_site_packages:
            return "isolated"
    if line == 2:
        python_version = lines[2][10:]  # e.g. 3.8.2
        return f"Python {python_version}".strip()
    return "N/A"


def get_active_dir_str():
    """
    Get the default venv directory string from `active` file.
    """
    active_file = os.path.expanduser("~/.venvipy/active")

    if not os.path.exists(os.path.expanduser("~/.venvipy")):
        os.mkdir(os.path.expanduser("~/.venvipy"))

    if os.path.exists(active_file):
        with open(active_file, "r") as f:
            active_dir = f.read()
            return active_dir
    else:
        with open(active_file, "w+") as f:
            active_dir = f.write("")
            return active_dir
    return []


def get_active_dir():
    """
    Get the active venv directory path string from `active`
    file and pass it to `get_venvs()`.
    """
    active_dir = get_active_dir_str()
    return get_venvs(active_dir)


#]===========================================================================[#
#] GET INFOS FROM PYTHON PACKAGE INDEX [#====================================[#
#]===========================================================================[#

@dataclass
class ModuleInfo:
    """_"""
    mod_name: str
    mod_version: str
    mod_summary: str


def get_module_infos(name):
    """
    Get module name, version and description
    from [PyPI](https://pypi.org/pypi).
    """
    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    search_result = client.search({"name": name})

    module_info_list = []

    for i, mod in enumerate(search_result):
        mod_name = mod["name"]
        mod_version = mod["version"]
        mod_summary = mod["summary"]

        mod_info = ModuleInfo(mod_name, mod_version, mod_summary)
        module_info_list.append(mod_info)

    return module_info_list[::-1]



if __name__ == "__main__":
    pass

    #get_python_installs()
