# -*- coding: utf-8 -*-
import shutil
import csv
import sys
import os
from dataclasses import dataclass
from subprocess import Popen, PIPE




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
    """Write the found Python versions to `py-installs` csv file."""
    versions = ["3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3"]
    csv_file = os.path.expanduser("~/.venvipy/py-installs")
    py_info_list = []

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
    Write the the system Python's version and path to `py-installs`
    csv file if running VenviPy in a virtual environment.
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


@dataclass
class VenvInfo:
    """_"""
    venv_name: str
    venv_version: str
    site_packages: str
    is_installed: str


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
        venv_version = get_pyvenv_cfg(cfg_file, "version")
        site_packages = get_pyvenv_cfg(cfg_file, "site_packages")
        is_installed = get_pyvenv_cfg(cfg_file, "installed")

        venv_info = VenvInfo(
            venv_name, venv_version, site_packages, is_installed
        )
        venv_info_list.append(venv_info)

    return venv_info_list


def to_version(value):
    """Convert a value to a readable version string."""
    return f"Python {value}"


def to_path(bin_path, version):
    """Return the absolute path to a python binary."""
    return os.path.join(bin_path, f"python{version}")


def get_pyvenv_cfg(cfg_file, cfg):
    """Return the values from `pyvenv.cfg` file."""
    with open(cfg_file, "r") as f:
        lines = f.readlines()

    version_str = to_version(lines[2][10:].strip())
    binary_path = to_path(lines[0][7:].strip(), lines[2][10:13].strip())
    site_packages = lines[1][31:].strip()
    csv_file = os.path.expanduser("~/.venvipy/py-installs")

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
        if not os.path.isfile(csv_file):
            get_python_installs()
        with open(csv_file, newline="") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            for info in reader:
                if binary_path == info["PYTHON_PATH"]:
                    return "yes"
            return "no"

    return "N/A"




if __name__ == "__main__":
    os.system("clear")

    config_file = "/mnt/SQ-Core/coding/.virtualenvs/DEV/test-0000/pyvenv.cfg"

    py_version = get_pyvenv_cfg(config_file, cfg="version")
    site_pkgs = get_pyvenv_cfg(config_file, cfg="site_packages")
    binary_location = get_pyvenv_cfg(config_file, cfg="py_path")
    is_present = get_pyvenv_cfg(config_file, cfg="installed")

    print(py_version)
    print(site_pkgs)
    print(binary_location)
    print(is_present)
