# -*- coding: utf-8 -*-
"""
This module creates all the stuff requested.
"""
import logging
import shlex
import os
from subprocess import Popen, PIPE
from random import randint

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from manage_pip import PipManager


logger = logging.getLogger(__name__)

# commands / options
cmds = [
    "install --no-cache-dir",  # 0
    "list",  # 1
    "freeze",  # 2
    "pipdeptree",  # 3
]
opts = [
    "--upgrade",  # 0
    "--requirement",  # 1
    "--editable",  # 2
]



#]===========================================================================[#
#] CUSTOM WORKER [#==========================================================[#
#]===========================================================================[#

class CloningWorker(QObject):
    """
    This worker performs package install in develp mode via subprocess.
    """
    started = pyqtSignal()
    finished = pyqtSignal()

    @pyqtSlot(str)
    def run_process(self, command):
        """
        Run the process.
        """
        self.started.emit()
        logger.info("Installing from VSC url...")

        clone_repo(command)
        self.finished.emit()


#]===========================================================================[#
#] CLONE AND INSTALL FROM GIT REPO [#========================================[#
#]===========================================================================[#

def clone_repo(command):
    """
    Clone a repository and install it into a virtual environment.
    """
    process = Popen(
        shlex.split(command), stdout=PIPE, universal_newlines=True
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            logger.info(output.strip())
    rc = process.poll()
    return rc


#]===========================================================================[#
#] WORKER (CREATE VIRTUAL ENVIRONMENT) [#====================================[#
#]===========================================================================[#

class CreationWorker(QObject):
    """
    Worker that performs the creation process.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    updatePipMsg = pyqtSignal()

    @pyqtSlot(tuple)
    def install_venv(self, args):
        """
        Execute the commands to create the environment.
        """
        self.started.emit()
        logger.info("Creating virtual environment...")

        py_vers, name, location, with_pip, site_packages = args
        env_dir = os.path.join(location, f"'{name}'")

        create_venv(
            py_vers,
            env_dir,
            with_pip=with_pip,
            system_site_packages=site_packages
            #symlinks=symlinks
        )

        if with_pip:
            # update pip to the latest version
            self.manager = PipManager(location, f"'{name}'")
            self.updatePipMsg.emit()
            self.manager.run_pip(cmds[0], [opts[0], "pip"])
            self.manager.finished.connect(self.finished.emit)

        else:
            self.finished.emit()


#]===========================================================================[#
#] CREATE A VIRTUAL ENVIRONMENT [#===========================================[#
#]===========================================================================[#

def create_venv(
        py_vers,
        env_dir,
        with_pip=False,
        system_site_packages=False
        #symlinks=False
    ):
    """Create a virtual environment in a directory.
    """
    pip = "" if with_pip else " --without-pip"
    ssp = " --system-site-packages" if system_site_packages else ""
    #sym = " --symlinks" if symlinks else ""

    script = f"{py_vers} -m venv {env_dir}{pip}{ssp};"

    res = Popen(
        ["bash", "-c", script],
        stdout=PIPE,
        universal_newlines=True
    )
    out, _ = res.communicate()
    output = out.strip()
    return output


#]===========================================================================[#
#] REQUIREMENTS [#===========================================================[#
#]===========================================================================[#

def fix_requirements(require_file):
    """
    Check the selected requirements file. If it contains
    a `pkg-resources==0.0.0` entry, then comment this line
    to prevent pip from crashing.
    """
    with open(require_file, "r+") as f:
        content = f.read()

        if "#pkg-resources==0.0.0" in content:
            pass  # skip if line is already commented

        elif "pkg-resources==0.0.0" in content:
            content = content.replace(
                "pkg-resources==0.0.0", "#pkg-resources==0.0.0"
            )
            f.seek(0)
            f.write(content)


#]===========================================================================[#
#] GENERATE A RANDOM LINE FROM THE ZEN OF PYTHON [#==========================[#
#]===========================================================================[#

def random_zen_line():
    """
    Return a random line from the Zen of Python.
    """
    this = [
        "\nBeautiful is better than ugly.",
        "\nExplicit is better than implicit.",
        "\nSimple is better than complex.",
        "\nComplex is better than complicated.",
        "\nFlat is better than nested.",
        "\nSparse is better than dense.",
        "\nReadability counts.",
        "\nSpecial cases aren't special enough\nto break the rules.\nAlthough practicality beats purity.",
        "\nErrors should never pass silently.\nUnless explicitly silenced.",
        "\nIn the face of ambiguity,\nrefuse the temptation to guess.",
        "\nThere should be one\n-- and preferably only one --\nobvious way to do it.\nAlthough that way may not be obvious at first\nunless you're Dutch.",
        "\nNow is better than never.\nAlthough never is often better\nthan *right* now.",
        "\nIf the implementation is hard to explain,\nit's a bad idea.",
        "\nIf the implementation is easy to explain,\nit may be a good idea.",
        "\nNamespaces are one honking great idea\n---\nlet's do more of those!"
    ]
    return this[randint(0, 14)]



if __name__ == "__main__":
    pass
