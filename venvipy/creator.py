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
        logger.debug(f"Installing from VSC url '{command}'")

        clone_repo(command)
        self.finished.emit()


#]===========================================================================[#
#] CLONE AND INSTALL FROM GIT REPO [#========================================[#
#]===========================================================================[#

def clone_repo(command):
    """
    Clone a repository and install it into a virtual environment.
    """
    if os.name == 'nt':
        split_cmd = shlex.split(command)
        logger.debug(split_cmd)
        cmds = command.split(' ')

        split_cmd[0] = cmds[0]

        process = Popen(
            split_cmd, stdout=PIPE, universal_newlines=True
        )
    else:
        process = Popen(
            shlex.split(command), stdout=PIPE, universal_newlines=True
        )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            logger.debug(output.strip())
    rc = process.poll()
    return rc

#]===========================================================================[#
#] CUSTOM WORKER TO BOOTSTRAP PIP [#=========================================[#
#]===========================================================================[#
class InstallPipWorker(QObject):
    """
    This worker performs package install in develp mode via subprocess.
    """
    started = pyqtSignal()
    finished = pyqtSignal()

    @pyqtSlot(str)
    def run_process(self, venv_location, venv_name):
        """
        Run the process.
        """
        self.started.emit()
        logger.debug(f"Installing pip with curl to '{venv_name}'")

        install_pip(venv_location, venv_name)
        self.finished.emit()

#]===========================================================================[#
#] INSTALL PIP VIA CURL & BOOTSTRAP INSTALLER [#=============================[#
#]===========================================================================[#
def install_pip(venv_location, venv_name):
    """
    Its possible to create an virtual env that has no pip installed.
    In which case venvi offered no solution via the UI to install pip.
    So this is an attempt to provide a pip bootstrap installer via:

    https://pip.pypa.io/en/stable/installing/
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python get-pip.py
    """
    if os.name == 'nt':
        subdir = 'Scripts'
    else:
        subdir = 'bin'

    pip_lives_here = os.path.join(venv_location, venv_name, subdir)
    curdir = os.getcwd()
    os.chdir(pip_lives_here)
    down_load_pip_installer = "curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    process = Popen(
        shlex.split(down_load_pip_installer), stdout=PIPE, universal_newlines=True
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            logger.debug(output.strip())
    rc = process.poll()

    if os.path.exists('get-pip.py'):
        command = list()
        command.append(os.path.join(pip_lives_here, "python"))
        command.append('get-pip.py')

        process = Popen(
            command, stdout=PIPE, universal_newlines=True
        )
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                logger.debug(output.strip())
        rc = process.poll()
        return(rc)
    else:
        return(-1)

#]===========================================================================[#
#] WORKER (CREATE VIRTUAL ENVIRONMENT) [#====================================[#
#]===========================================================================[#

class CreationWorker(QObject):
    """
    Worker that performs the creation process.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    updating_pip = pyqtSignal()
    installing_wheel = pyqtSignal()

    @pyqtSlot(tuple)
    def install_venv(self, args):
        """
        Execute the commands to create the environment.
        """
        self.started.emit()
        logger.debug("Creating virtual environment...")

        py_vers, name, location, with_pip, with_wheel, site_packages = args
        if os.name == 'nt':
            env_dir = os.path.join(location, f"{name}")
        else:
            env_dir = os.path.join(location, f"'{name}'")

        create_venv(
            py_vers,
            env_dir,
            with_pip=with_pip,
            system_site_packages=site_packages
        )

        if with_pip and not with_wheel:
            if os.name == 'nt':
                self.manager = PipManager(location, f"{name}")
            else:
                self.manager = PipManager(location, f"'{name}'")
            self.updating_pip.emit()
            self.manager.run_pip(cmds[0], [opts[0], "pip"])
            self.manager.finished.connect(self.finished.emit)
        elif with_pip and with_wheel:
            if os.name == 'nt':
                self.manager = PipManager(location, f"{name}")
            else:
                self.manager = PipManager(location, f"'{name}'")
            self.installing_wheel.emit()
            if os.name == 'nt':
                # Stupid Windows is giving us an error about not
                # having privilege to remove pip for its upgrade;
                # this works when we are not doing both pip and
                # wheel together, so we reverse the order
                self.manager.run_pip(cmds[0], [opts[0], "wheel pip"])
            else:
                self.manager.run_pip(cmds[0], [opts[0], "pip wheel"])
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
    ):
    """Create a virtual environment in a directory.
    """
    pip = " --without-pip" if not with_pip else ""
    ssp = " --system-site-packages" if system_site_packages else ""

    if os.name == 'nt':
        script = f"{py_vers} -m venv {env_dir}{pip}{ssp}"
        logger.debug(script)
        res = Popen(
            script,
            stdout=PIPE,
            universal_newlines=True
        )
    else:
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
