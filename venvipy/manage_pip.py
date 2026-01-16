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
This module manages all pip processes.
"""
import shlex
import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess

from platforms import get_platform

logger = logging.getLogger(__name__)



#]===========================================================================[#
#] INSTALL SELECTED PACKAGES [#==============================================[#
#]===========================================================================[#

class PipManager(QObject):
    """
    Manage `pip` processes.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    failed = pyqtSignal()
    text_changed = pyqtSignal(str)


    def __init__(self, venv_dir, venv_name, parent=None):
        super().__init__(parent)

        self._venv_dir = venv_dir
        self._venv_name = venv_name

        self._process = QProcess(self)
        self._process.setWorkingDirectory(venv_dir)

        self._process.readyReadStandardOutput.connect(
            self.on_ready_read_stdout
        )
        self._process.readyReadStandardError.connect(
            self.on_ready_read_stderr
        )

        # started
        self._process.started.connect(self.started)

        # updated
        self._process.stateChanged.connect(self.on_state_changed)

        # finished
        self._process.finished.connect(
            lambda _code, _status: self.finished.emit()
        )
        self._process.finished.connect(self.on_finished)


    def run_pip(self, command="", options=None):
        """
        Run pip commands using the virtual environment interpreter.
        """
        if options is None:
            options = []

        venv_path = Path(self._venv_dir) / self._venv_name
        platform = get_platform()
        venv_python = platform.venv_python_path(venv_path)

        if command == "pipdeptree":
            args = ["-m", "pipdeptree"] + options
        else:
            args = ["-m", "pip"] + shlex.split(command) + options

        self._process.start(str(venv_python), args)


    def process_stop(self):
        """Stop the process."""
        self._process.close()


    @pyqtSlot(QProcess.ProcessState)
    def on_state_changed(self, state):
        """Show the current process state.
        """
        if state == QProcess.ProcessState.Starting:
            logger.debug("Started")
        elif state == QProcess.ProcessState.Running:
            logger.debug("Running")
        elif state == QProcess.ProcessState.NotRunning:
            logger.debug("Done")
            self.text_changed.emit(
                "\n\nPress [ESC] to continue...\n"
            )


    @pyqtSlot(int, QProcess.ExitStatus)
    def on_finished(self, exitCode, exitStatus):
        """Show exit code when finished.
        """
        logger.debug(f"Exit code: {exitCode}")
        self._process.kill()


    @pyqtSlot()
    def on_ready_read_stdout(self):
        """Read from `stdout` and send the output to `update_status()`.
        """
        message = self._process.readAllStandardOutput().data().decode().strip()
        logger.debug(message)
        self.text_changed.emit(message)


    @pyqtSlot()
    def on_ready_read_stderr(self):
        """Read from `stderr`, then kill the process.
        """
        message = self._process.readAllStandardError().data().decode().strip()
        logger.error(message)
        self.text_changed.emit(message)
        self.failed.emit()
        self._process.kill()



if __name__ == "__main__":
    import os
    import sys
    from PyQt6.QtWidgets import QApplication
    from wizard import ConsoleDialog
    import creator

    app = QApplication(sys.argv)
    console = ConsoleDialog()

    current_dir = os.path.dirname(os.path.realpath(__file__))
    _venv_name = "testenv"  # need to have a virtual env in current_dir

    ### TODO: use subprocess instead of QProcess for simpler output handling

    #manager = PipManager(current_dir, _venv_name)
    #manager.text_changed.connect(console.update_status)
    #manager.started.connect(console.show)
    #manager.run_pip(
    #   "freeze",
    #   [creator.opts[4],
    #   str(Path(current_dir) / _venv_name / "requirements.txt"
    #   )]
    #)

    sys.exit(app.exec())
