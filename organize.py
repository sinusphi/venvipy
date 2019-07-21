# -*- coding: utf-8 -*-
"""Collect and serve data."""
from subprocess import Popen, PIPE, CalledProcessError
import os

from dataclasses import dataclass



#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

versFound, pathFound, notFound = [], [], []

def get_python_installs():
    """
    Get available Python 3 installations from common locations.
    """
    versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3']

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

            # get paths to the python executables
            res2 = Popen(
                ["which", "python" + vers],
                stdout=PIPE,
                universal_newlines=True
            )
            out2, _ = res2.communicate()
            path = out2.strip()

            versFound.append(version)
            pathFound.append(path)

        except (CalledProcessError, FileNotFoundError):
            # determining the amount of the versions which were not found
            # (need this to display a message in case there's no python 3
            # installation found at all)
            notFound.append(i)



#]===========================================================================[#
#] GET VENVS FROM DEFAULT DIRECTORY [#=======================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    name: str
    directory: str
    version: str


def get_venvs(path):
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

        except Exception as err:
            print(f"{err.args[1]} : [list index: {i} ] {python_binary}")

    return infos


def get_venvs_default():
    """
    Get the default venv directory.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_file = os.path.join(current_dir, "def", "default")

    if os.path.isfile(default_file):
        with open(default_file, 'r') as f:
            default_dir = f.read()
            return get_venvs(default_dir)

    return []


get_python_installs()




if __name__ == "__main__":

    for venv in get_venvs_default():
        print(venv.name, venv.version, venv.directory)



































'''
venvDirs, venvVers, venvPath = [], [], []

def getVenvs():
    """
    Get the sub directories (venv directories) from the default directory.
    """
    # get the path (str) to the default dir from file
    with open("def/default", 'r') as default:
        defDir = default.read()
        default.close()

    # get all folders inside the selected default dir
    subDirs = os.listdir(defDir)

    # loop over the subdirs of the selected default dir
    for i, _dir in enumerate(subDirs):
        # if there's a 'bin' folder within the subdir, and if it contains a
        # file named 'python', then try to get the version
        if ("bin" in os.listdir('/'.join([defDir, _dir]))
        and "python" in os.listdir('/'.join([defDir, _dir, "bin"]))):

            try:
                getVers = Popen(
                    ['/'.join([defDir, _dir, "bin", "python"]), "-V"],
                    stdout=PIPE, universal_newlines=True
                )
                venvVersion = getVers.communicate()[0].strip()

            except Exception as err:
                # in case there's a file named 'python' but
                # isn't a python executable
                print(
                    err.args[1]+':',
                    "[list index:", str(i)+']',
                    '/'.join([defDir, _dir, "bin"])
                )
                continue

            venvDirs.append(_dir)
            venvVers.append(venvVersion)
            venvPath.append(defDir)


get_python_installs()
getVenvs()
'''
