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


__version__ = "0.3.3"

CFG_DIR = os.path.expanduser("~/.venvipy")
DB_FILE = os.path.expanduser("~/.venvipy/py-installs")
ACTIVE_FILE = os.path.expanduser("~/.venvipy/active")

if os.name == 'nt':
    USER_HOME = os.environ['USERPROFILE']
    USER_LOCAL = os.path.join(USER_HOME, 'AppData', 'Local', 'Programs', 'Python')
    ROOT_LOCAL = "C:\\"
    PATHS = [ROOT_LOCAL, USER_LOCAL]
else:
    USER_HOME = os.environ['HOME']
    USER_LOCAL = os.path.join(USER_HOME, '.local', 'bin', 'python')
    USER_LOCAL_2 = os.path.join(USER_HOME, 'bin', 'python')
    USER_LOCAL_3 = os.path.join(USER_HOME, 'python')
    PATHS = [USER_HOME, USER_LOCAL, USER_LOCAL_2, USER_LOCAL_3]

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
    if os.name == 'nt':
        return os.path.join(bin_path, f"python.exe")
    else:
        return os.path.join(bin_path, f"python{version}")


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


def ensure_active_file():
    """Create the file that holds the selected path to venvs.
    """
    ensure_confdir()
    if not os.path.exists(ACTIVE_FILE):
        with open(ACTIVE_FILE, "w+") as f:
            f.write("")


def get_python_version(py_path):
    """Return Python version.
    """
    res = Popen(
        [py_path, "-V"],
        stdout=PIPE,
        universal_newlines=True
    )
    out, _ = res.communicate()
    python_version = out.strip()
    return python_version


def get_python_installs(relaunching=False):
    """
    Write the found Python versions to `py-installs`. Create
    a new database if `relaunching=True`.
    """
    versions = ["3.9", "3.8", "3.7", "3.6", "3.5", "3.4", "3.3"]
    py_info_list = []
    ensure_confdir()

    if not os.path.exists(DB_FILE) or relaunching:
        with open(DB_FILE, "w", newline="") as cf:
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
                    # For some reason, on windows, shutil.which() upper cases
                    # the python interpreter's extension, as in EXE, when in 
                    # the file system, it is lower case. This causes issues
                    # later when we do string compares in the py_installs CSV DB
                    if os.name == 'nt':
                        python_path = python_path[:-3] + python_path[-3:].lower()
                    python_version = get_python_version(python_path)
                    py_info = PythonInfo(python_version, python_path)
                    py_info_list.append(py_info)
                    writer.writerow({
                        "PYTHON_VERSION": py_info.py_version,
                        "PYTHON_PATH": py_info.py_path
                    })

            # The above code finds python interpreters that are in the execution
            # path; some systems have python interpreters installed that are not
            # in the execution path, by would like to be used for venv creation.
            try:
                # Short of searching the registry (shudder), I thought
                # this might be a good compromise
                py_installs = os.environ['PYTHON_INSTALLS']
                PATHS.extend(py_installs.split(';'))
            except:
                pass

            for path in PATHS:
                # Looking for a directory that starts with 'python'
                for item in os.listdir(path):
                    item_full_path = os.path.join(path, item)
                    if os.path.isdir(item_full_path):
                        if item.lower().startswith('python'):
                            python_path = shutil.which("python", path=item_full_path)
                            if python_path is not None:
                                if os.name == 'nt':
                                    # For some reason, on windows, shutil.which() upper cases
                                    # the python interpreter's extension, as in EXE, when in 
                                    # the file system, it is lower case. This causes issues
                                    # later when we do string compares against the file system.
                                    python_path = python_path[:-3] + python_path[-3:].lower()   

                                python_version = get_python_version(python_path)
                                if python_version:
                                    # It seems that on Windows, the Python 2.7 interpreter
                                    # returns an empty version string to stdout, None to stderr
                                    # and yet the console shows the -V output, go figure.
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

    with open(DB_FILE, "a", newline="") as cf:
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
    with open(DB_FILE, "r") as f:
        lines = f.readlines()
    with open(DB_FILE, "w") as f:
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


def get_venvs(path):
    """
    Get the available virtual environments
    from the specified folder.
    """
    # return an emtpty list if directory doesn"t exist
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

    return venv_info_list[::-1]


def get_pyvenv_cfg(cfg_file, cfg):
    """
    Return the values as string from a `pyvenv.cfg` file.
    Values for `cfg` can be strings: `version`, `py_path`,
    `site_packages` or `installed`.
    """
    with open(cfg_file, "r") as f:
        lines = f.readlines()

    version_str = to_version(lines[2][10:].strip())
    binary_path = to_path(lines[0][7:].strip(), lines[2][10:13].strip())
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
        with open(DB_FILE, newline="") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            for info in reader:
                if binary_path == info["PYTHON_PATH"]:
                    return "yes"
            return "no"

    return "N/A"


def get_active_dir_str():
    """Get the default venv directory string from `active` file.
    """
    ensure_active_file()
    with open(ACTIVE_FILE, "r") as f:
        active_dir = f.read()
        return active_dir
    return ""


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
class PackageInfo:
    """_"""
    pkg_name: str
    pkg_version: str
    pkg_summary: str


def get_package_infos(name):
    """
    Get the package"s name, version and description
    from [PyPI](https://pypi.org/pypi).
    """
    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    search_result = client.search({"name": name})

    package_info_list = []

    for i, pkg in enumerate(search_result):
        pkg_name = pkg["name"]
        pkg_version = pkg["version"]
        pkg_summary = pkg["summary"]

        pkg_info = PackageInfo(pkg_name, pkg_version, pkg_summary)
        package_info_list.append(pkg_info)

    return package_info_list[::-1]
