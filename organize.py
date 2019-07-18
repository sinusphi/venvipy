# -*- coding: utf-8 -*-
"""Collect and serve data."""
from subprocess import Popen, PIPE, CalledProcessError
import os




#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

# look for installed Python versions in common locations
versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3']

notFound = []
versFound = []
pathFound = []

for i, vers in enumerate(versions):
    try:
        # get python versions
        getVers = Popen(
            ["python" + vers, "-V"], stdout=PIPE, universal_newlines=True
        )

        # get paths to the python executables
        getPath = Popen(
            ["which", "python" + vers], stdout=PIPE, universal_newlines=True
        )

        version = getVers.communicate()[0].strip()
        path = getPath.communicate()[0].strip()

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

venvDirs = []
venvVers = []

# get the path (str) to the default dir from file
with open("def/default", 'r') as default:
    defDir = default.read()
    default.close()

# get all folders inside the selected default dir
subDirs = os.listdir(defDir)

# loop over the subdirs of the selected default dir
for i, _dir in enumerate(subDirs):
    # if there's a 'bin' folder inside the subdir, and it contains a
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
            print(err)
            continue

        venvDirs.append(_dir)
        venvVers.append(venvVersion)



if __name__ == "__main__":

    for i in range(len(subDirs)):
        print(venvDirs)
        print(venvVers)
        print(defDir)
