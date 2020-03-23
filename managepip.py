# -*- coding: utf-8 -*-
"""
This module manages all pip processes.
"""
import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (QApplication, QDialog, QProgressBar, QTextEdit,
                             QVBoxLayout, QDesktopWidget)



#]===========================================================================[#
#] INSTALL SELECTED PACKAGES [#==============================================[#
#]===========================================================================[#

def has_bash():
    """
    Test if bash is available.
    """
    process = QProcess()
    process.start("which bash")
    process.waitForStarted()
    process.waitForFinished()

    if process.exitStatus() == QProcess.NormalExit:
        return bool(process.readAll())

    return False


class PipManager(QObject):
    """
    Manage the installation process.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    textChanged = pyqtSignal(str)


    def __init__(self, venv_dir, venv_name, parent=None):
        super().__init__(parent)

        self._venv_dir = venv_dir
        self._venv_name = venv_name

        self._process = QProcess(self)
        self._process.readyReadStandardError.connect(
            self.onReadyReadStandardError
        )
        self._process.readyReadStandardOutput.connect(
            self.onReadyReadStandardOutput
        )
        self._process.stateChanged.connect(self.onStateChanged)
        self._process.started.connect(self.started)
        self._process.finished.connect(self.finished)
        self._process.finished.connect(self.onFinished)
        self._process.setWorkingDirectory(venv_dir)


    def run_pip(self, command="", options=None):
        """
        Activate the virtual environment and run pip commands.
        """
        if has_bash():
            if options is None:
                options = []

            script = (
                f"source {self._venv_name}/bin/activate;" \
                f"pip {command} {' '.join(options)};" \
                "deactivate;"
            )

            self._process.start("bash", ["-c", script])


    @pyqtSlot(QProcess.ProcessState)
    def onStateChanged(self, state):
        """Show the current process status."""
        if state == QProcess.NotRunning:
            print("[PROCESS]: Stopped")
            self.textChanged.emit(
                "\n\nPress [ESC] to continue..."
            )
        elif state == QProcess.Starting:
            print("[PROCESS]: Started")
        elif state == QProcess.Running:
            print("[PROCESS]: Running")


    @pyqtSlot(int, QProcess.ExitStatus)
    def onFinished(self, exitCode):
        """Show exit code when finished."""
        print(f"[PROCESS]: Exit code: {exitCode}")


    @pyqtSlot()
    def onReadyReadStandardError(self):
        """
        Read from `stderr`, then kill the process.
        """
        message = self._process.readAllStandardError().data().decode().strip()
        print(f"[PROCESS]: {message}")

        self.finished.emit()
        self._process.kill()
        self.textChanged.emit(message)


    @pyqtSlot()
    def onReadyReadStandardOutput(self):
        """
        Read from `stdout` and send the output to `update_status()`.
        """
        message = self._process.readAllStandardOutput().data().decode().strip()
        print(f"[PIP]: {message}")

        self.textChanged.emit(message)



if __name__ == "__main__":
    import sys
    from wizard import ConsoleDialog

    app = QApplication(sys.argv)
    console = ConsoleDialog()

    current_dir = os.path.dirname(os.path.realpath(__file__))
    venv_name = "testenv"  # need to have a virtual env in current_dir

    manager = PipManager(current_dir, venv_name)
    manager.textChanged.connect(console.update_status)
    manager.started.connect(console.show)
    manager.run_pip(
        "freeze", [f" > {current_dir}/{venv_name}/requirements.txt"]
    )

    sys.exit(app.exec_())
