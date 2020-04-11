# -*- coding: utf-8 -*-
"""
This module creates all the stuff requested.
"""
from subprocess import Popen, PIPE
from random import randint
import os

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from manage_pip import PipManager


# pip commands and options
cmds = ["install --no-cache-dir", "list", "freeze"]
opts = ["--upgrade", "--requirement"]


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
        Execute the required steps to create the virtual environment.
        """
        self.started.emit()
        print("[PROCESS]: Creating virtual environment...")

        py_vers, name, location, with_pip, site_packages, symlinks = args

        create_venv(
            py_vers,
            os.path.join(location, f"'{name}'"),
            with_pip=with_pip,
            system_site_packages=site_packages,
            symlinks=symlinks,
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
    py_vers, env_dir, with_pip=False, system_site_packages=False, symlinks=False
):
    """
    Create a virtual environment in a directory.
    """
    pip = "" if with_pip else " --without-pip"
    ssp = " --system-site-packages" if system_site_packages else ""
    sym = " --symlinks" if symlinks else ""

    script = f"{py_vers} -m venv {env_dir}{pip}{ssp}{sym};"

    res = Popen(["bash", "-c", script], stdout=PIPE, text="utf-8")

    out, _ = res.communicate()
    output = out.strip()

    return output


#]===========================================================================[#
#] GENERATE A REQUIREMENTS [#================================================[#
#]===========================================================================[#

def create_requirements(venv_dir, venv_name):
    """
    Generate a requirements.txt file and save in the root directory
    of the virtual environment.
    """
    script = (
        f"source {venv_dir}/{venv_name}/bin/activate;"
        f"pip freeze > {venv_dir}/{venv_name}/requirements.txt;"
        "deactivate;"
    )

    res = Popen(["bash", "-c", script], stdout=PIPE, text="utf-8")

    out, _ = res.communicate()
    output = out.strip()

    return output


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
        "\nThere should be one\n-- and preferably only one --\nobvious way to do it.",
        "\nAlthough that way may not be obvious at first\nunless you're Dutch.",
        "\nNow is better than never.\nAlthough never is often better\nthan *right* now.",
        "\nIf the implementation is hard to explain,\nit's a bad idea.",
        "\nIf the implementation is easy to explain,\nit may be a good idea.",
        "\nNamespaces are one honking great idea\n---\nlet's do more of those!"
    ]

    return this[randint(0, 15)]



if __name__ == "__main__":

    python_version = "/usr/local/bin/python3.8"
    env_directory = "/mnt/SQ-Core/coding/.virtualenvs/DEV/"
    with_pip_opt = None
    with_sys_site_pkgs = None
    with_symlinks = None

    #create_venv(python_version, env_directory)
