# -*- coding: utf-8 -*-
"""
This module manages all pip processes.
"""
import os
import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess
from PyQt5.QtWidgets import QApplication


logger = logging.getLogger(__name__)



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
    Manage `pip` processes.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    failed = pyqtSignal()
    textChanged = pyqtSignal(str)

    test = pyqtSignal()


    def __init__(self, venv_dir, venv_name, parent=None):
        super().__init__(parent)

        self._venv_dir = venv_dir
        self._venv_name = venv_name

        logger.debug(f"Pip Manager - Venv Name: {venv_name}")
        logger.debug(f"Pip Manager -  Venv Dir: {venv_dir}")

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
        self._process.finished.connect(self.finished)
        self._process.finished.connect(self.on_finished)

    def run_pip(self, command="", options=None):
        """
        Activate the virtual environment and run pip commands.

        Parameters
        ----------
        command : str
            Defined in creator.py, will be one of the following:
                "install --no-cache-dir"
                "list"
                "freeze"
                "pipdeptree"
        options : str
            Defined in creator.py, will be one of the following:
                "--upgrade"
                "--requirement"
                "--editable"
        """
        if os.name == 'nt':
            if options is None:
                    options = []

            venv_path = os.path.join(self._venv_dir, self._venv_name).replace('/', '\\')
            pip = f"pip {command} {' '.join(options)}"
            pipdeptree = f"pipdeptree {' '.join(options)}"
            task = pipdeptree if command == "pipdeptree" else pip

            if task == pip:
                if pip[-3:] == "pip":
                    # We are upgrading pip itself, Windows 10 error suggests 
                    # we use the full path to python in this case
                    # even after successful activation of venv. There error
                    # is issued from "pip install --no-cache-dir --upgrade pip"
                    # and suggests we do "python.exe -m pip install --no-cache-dir --upgrade pip"
                    # with full path to the interpreter.... go figure.
                    prefix = os.path.join(venv_path, 'Scripts', 'python.exe')
                    task = f"{prefix} -m {task}"

            script = f'{venv_path}\\Scripts\\activate.bat && {task} && {venv_path}\\Scripts\\deactivate.bat'
            
            logger.debug(f"run_pip script: '{script}'")
            self._process.start("cmd.exe", ["/c", script])

            # The interactive way...
            # self._process.start("cmd.exe")
            # self._process.write(f"{venv_path}\\Scripts\\activate.bat\r\n".encode("utf-8"))
            # #self._process.write(f"{task}\r\n".encode("utf-8"))
            # self._process.write("pip.exe freeze --all > junk.txt\r\n".encode("utf-8"))
            # self._process.write(f"{venv_path}\\Scripts\\deactivate.bat\r\n".encode("utf-8"))
            # self._process.write("exit\r\n".encode("utf-8"))

        else:    
            if has_bash():
                if options is None:
                    options = []

                venv_path = os.path.join(self._venv_dir, self._venv_name)
                pip = f"pip {command} {' '.join(options)};"
                pipdeptree = f"pipdeptree {' '.join(options)};"
                task = pipdeptree if command == "pipdeptree" else pip

                script = (
                    f"source {venv_path}/bin/activate;"
                    f"{task}"
                    "deactivate;"
                )
                self._process.start("bash", ["-c", script])


    def process_stop(self):
        """Stop the process."""
        self._process.close()


    @pyqtSlot(QProcess.ProcessState)
    def on_state_changed(self, state):
        """Show the current process state.
        """
        if state == QProcess.Starting:
            #print("[PROCESS]: Started")
            logger.debug("Started")
        elif state == QProcess.Running:
            #print("[PROCESS]: Running")
            logger.debug("Running")
        elif state == QProcess.NotRunning:
            #print("[PROCESS]: Stopped")
            logger.debug("Done.")
            self.textChanged.emit(
                "\n\nPress [ESC] to continue..."
            )


    @pyqtSlot(int, QProcess.ExitStatus)
    def on_finished(self, exitCode):
        """Show exit code when finished.
        """
        #print(f"[PROCESS]: Exit code: {exitCode}")
        logger.debug(f"Exit code: {exitCode}")
        self._process.kill()


    @pyqtSlot()
    def on_ready_read_stdout(self):
        """Read from `stdout` and send the output to `update_status()`.
        """
        message = self._process.readAllStandardOutput().data().decode().strip()
        #print(f"[PIP STDOUT]: {message}")
        logger.debug(f"stdout: {message}")
        self.textChanged.emit(message)

    @pyqtSlot()
    def on_ready_read_stderr(self):
        """Read from `stderr`, then kill the process.
        """
        message = self._process.readAllStandardError().data().decode().strip()
        #print(f"[PIP STDERR]: {message}")
        logger.error(f"stderr: '{message}'")
        self.textChanged.emit(message)

        self.failed.emit()
        self._process.kill()



if __name__ == "__main__":
    import sys
    from wizard import ConsoleDialog

    app = QApplication(sys.argv)
    console = ConsoleDialog()

    current_dir = os.path.dirname(os.path.realpath(__file__))
    _venv_name = "testenv"  # need to have a virtual env in current_dir

    manager = PipManager(current_dir, _venv_name)
    manager.textChanged.connect(console.update_status)
    manager.started.connect(console.show)
    if os.name == 'nt':
        manager.run_pip(
            "freeze --all", [f" > {current_dir}\\{_venv_name}\\requirements.txt"]
        )
    else:
        manager.run_pip(
            "freeze", [f" > {current_dir}/{_venv_name}/requirements.txt"]
        )

    sys.exit(app.exec_())
