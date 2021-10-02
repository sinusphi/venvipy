#    VenviPy - A Virtual Environment Manager for Python.
#    Copyright (C) 2021 - Youssef Serestou - sinusphi.sq@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License or any
#    later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License version 3 named LICENSE is
#    in the root directory of VenviPy.
#    If not, see <https://www.gnu.org/licenses/licenses.en.html#GPL>.

# -*- coding: utf-8 -*-
"""
This module creates all the stuff requested.
"""
import logging
import shlex
import os
from subprocess import Popen, PIPE, STDOUT
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
    "--use-feature=in-tree-build"  # 3
]



#]===========================================================================[#
#] CUSTOM WORKER [#==========================================================[#
#]===========================================================================[#

class InstallWorker(QObject):
    """
    This worker performs package installs.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    text_changed = pyqtSignal(str)

    @pyqtSlot(str)
    def run_process(self, command):
        """Run the process.
        """
        self.started.emit()
        self.install_process(command)
        self.finished.emit()


    def install_process(self, command):
        """Install a package via subprocess.
        """
        os.environ["PYTHONUNBUFFERED"] = "1"
        errors = []

        with Popen(
            shlex.split(command),
            stdout=PIPE,
            stderr=STDOUT,
            text="utf-8"
        ) as process:
            while process.poll() is None:
                output = process.stdout.readline()

                if output != "":
                    logger.debug(output.strip())
                    if output.lstrip().startswith((
                        "ERROR",
                        "WARNING",
                        "fatal",
                        "remote"
                    )):
                        errors.append(output.strip())
                    else:
                        self.text_changed.emit(output.strip())

            if errors:
                errors.insert(0, " ")
                for line in errors:
                    self.text_changed.emit(line)

            self.text_changed.emit("\n\nPress [ESC] to continue...\n")
            logger.debug(f"Exit code: {process.returncode}")
            return process.returncode



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
        """Execute the commands to create the environment.
        """
        self.started.emit()
        logger.debug("Creating virtual environment...")

        py_vers, name, location, with_pip, with_wheel, site_packages = args
        env_dir = os.path.join(location, f"'{name}'")

        create_venv(
            py_vers,
            env_dir,
            with_pip=with_pip,
            system_site_packages=site_packages
        )

        if with_pip and not with_wheel:
            self.manager = PipManager(location, f"'{name}'")
            self.updating_pip.emit()
            self.manager.run_pip(cmds[0], [opts[0], "pip"])
            self.manager.finished.connect(self.finished.emit)
        elif with_pip and with_wheel:
            self.manager = PipManager(location, f"'{name}'")
            self.installing_wheel.emit()
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

    script = f"{py_vers} -m venv {env_dir}{pip}{ssp};"

    with Popen(
        ["bash", "-c", script],
        stdout=PIPE,
        text="utf-8"
    ) as res:
        out, _ = res.communicate()

    output = out.strip()
    return output


#]===========================================================================[#
#] REQUIREMENTS [#===========================================================[#
#]===========================================================================[#

def fix_requirements(require_file):
    """
    Check the selected requirements file. If it contains
    a `pkg_resources==0.0.0` entry, then comment this line
    to prevent pip from crashing.
    """
    with open(require_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    new_content = []

    for i, line in enumerate(content):
        if line.startswith("pkg_resources==0.0.0"):
            line = line.replace(
                "pkg_resources==0.0.0",
                "#pkg_resources==0.0.0"
            )
            logger.debug(f"Fixed requirements in '{require_file}'")

        new_content.append(line)

    with open(require_file, "w", encoding="utf-8") as f:
        f.writelines(new_content)


#]===========================================================================[#
#] DESCRIPTION [#============================================================[#
#]===========================================================================[#

def save_comment(path, comment):
    """Save a description in `venvipy.cfg` file.
    """
    with open(path, "w+", encoding="utf-8") as f:
        f.write(comment)


#]===========================================================================[#
#] GENERATE A RANDOM LINE FROM THE ZEN OF PYTHON [#==========================[#
#]===========================================================================[#

def random_zen_line():
    """Return a random line from the Zen of Python.
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
