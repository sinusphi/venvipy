# -*- coding: utf-8 -*-
"""Collect and serve data."""
from subprocess import Popen, PIPE
from dataclasses import dataclass
import xmlrpc.client
import shutil
import os



#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    """_"""
    version: str
    path: str


def get_python_installs():
    """
    Get the available python versions installed.
    """
    versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3']
    py_info_list = []

    for i, vers in enumerate(versions):
        python_version = f"Python {vers}"
        python_path = shutil.which(f"python{vers}")

        if python_path is not None:
            py_info = PythonInfo(python_version, python_path)
            py_info_list.append(py_info)

    return py_info_list


#]===========================================================================[#
#] GET VENVS FROM DEFAULT DIRECTORY [#=======================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    """_"""
    name: str
    version: str


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

        version = get_python_vers(cfg_file)

        venv_info = VenvInfo(os.path.basename(valid_venv), version)
        venv_info_list.append(venv_info)

    return venv_info_list


def get_python_vers(cfg_file):
    """
    Get the Python version of a virtual environment by
    reading the version str from it's `pyvenv.cfg` file.
    """
    with open(cfg_file, "r") as f:
        lines = f.readlines()

    return f"Python {lines[2][10:]}".strip()


def get_venvs_default():
    """
    Get the default venv directory string from file.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_file = os.path.join(current_dir, "def", "default")

    if os.path.isfile(default_file):
        with open(default_file, "r") as f:
            default_dir = f.read()
            return get_venvs(default_dir)

    return []


#]===========================================================================[#
#] CREATE A VIRTUAL ENVIRONMENT [#===========================================[#
#]===========================================================================[#

def create_venv(py_vers, env_dir, with_pip=False,
                system_site_packages=False, symlinks=False):
    """
    Create a virtual environment in a directory.
    """
    pip = "" if with_pip else " --without-pip"
    ssp = " --system-site-packages" if system_site_packages else ""
    sym = " --symlinks" if symlinks else ""

    script = f"{py_vers} -m venv {env_dir}{pip}{ssp}{sym};"

    res = Popen(
            ["bash", "-c", script],
            stdout=PIPE,
            text="utf-8"
        )

    out, _ = res.communicate()
    output = out.strip()

    return output


#]===========================================================================[#
#] GET INFOS FROM PYTHON PACKAGE INDEX [#====================================[#
#]===========================================================================[#

@dataclass
class PackageInfo:
    pkg_name: str
    pkg_vers: str
    pkg_sum: str


def get_package_infos(name):
    """
    Get package name, version and description from https://pypi.org/pypi.
    """
    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    res = client.search({"name": name})

    infos = []

    for i, proj in enumerate(res):
        pkg_name = proj["name"]
        pkg_vers = proj["version"]
        pkg_sum = proj["summary"]

        info = PackageInfo(pkg_name, pkg_vers, pkg_sum)
        infos.append(info)

    return infos



if __name__ == "__main__":

    for python in get_python_installs():
        print(python.version, python.path)

    #]=======================================================================[#

    # venv in get_venvs_default():
        #print(venv.name, venv.version)

    #]=======================================================================[#

    #test_pkg = "test"

    #for pkg in get_package_infos(test_pkg):
        #print(pkg.pkg_name, pkg.pkg_vers, pkg.pkg_sum)

    #if not get_package_infos(test_pkg):
        #print("No packages found!")
