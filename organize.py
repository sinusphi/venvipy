# -*- coding: utf-8 -*-
"""Collect and serve data."""
from subprocess import Popen, PIPE
from dataclasses import dataclass
import xmlrpc.client
import os




#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    version: str
    path: str


def get_python_installs():
    """
    Determine if Python 3 installations exist and where they are.
    """
    versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3']

    infos = []

    for i, vers in enumerate(versions):
        try:
            # get python versions
            res1 = Popen(
                ["python" + vers, "-V"],
                stdout=PIPE,
                universal_newlines=True
            )
            out1, _ = res1.communicate()
            version = out1.strip()

            # get paths to the python binaries
            res2 = Popen(
                ["which", "python" + vers],
                stdout=PIPE,
                universal_newlines=True
            )
            out2, _ = res2.communicate()
            path = out2.strip()

            info = PythonInfo(version, path)
            infos.append(info)

        except FileNotFoundError as err:
            print(f"{err.args[1]}")

    return infos


#]===========================================================================[#
#] GET VENVS FROM DEFAULT DIRECTORY [#=======================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    name: str
    directory: str
    version: str


def get_venvs(path):
    """
    Get the venv directories from default directory.
    """
    if not os.path.isdir(path):
        return []

    infos = []

    for i, _dir in enumerate(os.listdir(path)):

        bin_folder = os.path.join(path, _dir, "bin")
        if not os.path.isdir(bin_folder):
            continue

        python_binary = os.path.join(bin_folder, "python")
        if not os.path.isfile(python_binary):
            continue

        try:
            res = Popen(
                [python_binary, "-V"],
                stdout=PIPE,
                universal_newlines=True
            )
            out, _ = res.communicate()
            version = out.strip()

            info = VenvInfo(_dir, path, version)
            infos.append(info)

        except OSError as err:
            print(f"{err.args[1]}: {python_binary}")

    return infos


def get_venvs_default():
    """
    Get the default venv directory string from file.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_file = os.path.join(current_dir, "def", "default")

    if os.path.isfile(default_file):
        with open(default_file, 'r') as f:
            default_dir = f.read()
            return get_venvs(default_dir)

    return []


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
        if name is None:
            break

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

    for venv in get_venvs_default():
        print(venv.name, venv.version, venv.directory)

    #]=======================================================================[#

    test_pkg = "requests"

    for pkg in get_package_infos(test_pkg):
        print(pkg.pkg_name, pkg.pkg_vers, pkg.pkg_sum)
