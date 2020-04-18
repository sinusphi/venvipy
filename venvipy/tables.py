# -*- coding: utf-8 -*-
"""
This module contains the implementation of QTableView.
"""
import shutil
import os

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QTableView,
    QMenu,
    QMessageBox,
    QFileDialog
)

from get_data import get_active_dir_str
from dialogs import ConsoleDialog
from manage_pip import PipManager
from creator import (
    fix_requirements,
    cmds,
    opts
)



class VenvTable(QTableView):
    """
    The table that lists the virtual environments
    found in the specified folder.
    """
    refresh = pyqtSignal()

    def contextMenuEvent(self, event):
        self.contextMenu = QMenu(self)

        # sub menus
        self.detailsSubMenu = QMenu(
            "Det&ails",
            self,
            icon=QIcon.fromTheme("info")
        )

        self.installSubMenu = QMenu(
            "&Install",
            self,
            icon=QIcon.fromTheme("software-install")
        )

        # actions
        upgradePipAction = QAction(
            QIcon.fromTheme("system-software-update"),
            "&Upgrade Pip to latest",
            self,
            statusTip="Upgrade Pip to the latest version"
        )
        self.contextMenu.addAction(upgradePipAction)
        upgradePipAction.triggered.connect(lambda: self.upgrade_pip(event))

        self.contextMenu.addMenu(self.installSubMenu)

        addModulesAction = QAction(
            QIcon.fromTheme("list-add"),
            "&Install additional modules",
            self,
            statusTip="Install additional modules"
        )
        self.installSubMenu.addAction(addModulesAction)
        addModulesAction.triggered.connect(lambda: self.add_modules(event))

        installRequireAction = QAction(
            QIcon.fromTheme("list-add"),
            "Install from &requirements",
            self,
            statusTip="Install modules from requirements"
        )
        self.installSubMenu.addAction(installRequireAction)
        installRequireAction.triggered.connect(
            lambda: self.install_requires(event)
        )

        saveRequireAction = QAction(
            QIcon.fromTheme("document-save"),
            "Save &requirements",
            self,
            statusTip="Write requirements to file"
        )
        self.contextMenu.addAction(saveRequireAction)
        saveRequireAction.triggered.connect(
            lambda: self.save_requires(event)
        )

        #self.contextMenu.addSeparator()
        self.contextMenu.addMenu(self.detailsSubMenu)

        listModulesAction = QAction(
            QIcon.fromTheme("dialog-information"),
            "&List installed modules",
            self,
            statusTip="List installed modules"
        )
        self.detailsSubMenu.addAction(listModulesAction)
        listModulesAction.triggered.connect(
            lambda: self.list_modules(event, style=1)
        )

        freezeAction = QAction(
            QIcon.fromTheme("dialog-information"),
            "Show &freeze output",
            self,
            statusTip="List the output of 'pip freeze'"
        )
        self.detailsSubMenu.addAction(freezeAction)
        freezeAction.triggered.connect(
            lambda: self.freeze_output(event, style=2)
        )

        deleteAction = QAction(
            QIcon.fromTheme("delete"),
            "&Delete environment",
            self,
            statusTip="Delete environment"
        )
        self.contextMenu.addAction(deleteAction)
        deleteAction.triggered.connect(lambda: self.delete_venv(event))

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            self.contextMenu.popup(QCursor.pos())


    def get_selected_item(self):
        """
        Get the venv name of the selected row.
        """
        listed_venvs = self.selectionModel().selectedRows()
        for index in listed_venvs:
            selected_venv = index.data()
            return selected_venv


    def upgrade_pip(self, event):
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        self.console = ConsoleDialog()
        self.console.setWindowTitle("Updating Pip")

        #print("[PROCESS]: Updating Pip to the latest version...")
        self.manager = PipManager(active_dir, venv)
        self.manager.run_pip(cmds[0], [opts[0], "pip"])
        self.manager.started.connect(self.console.exec_)

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # clear the content on window close
        if self.console.close:
            self.console.consoleWindow.clear()


    def add_modules(self, event):
        """
        Install additional modules into the selected environment.
        """
        pass


    def install_requires(self, event):
        """
        Install modules from a requirements file into the
        selected environment.
        """
        file_name = QFileDialog.getOpenFileName(self, "Select a requirements")
        file_path = file_name[0]
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        if file_path != "":
            fix_requirements(file_path)

            self.console = ConsoleDialog()
            self.console.setWindowTitle("Installing from requirements")

            #print("[PROCESS]: Installing from requirements...")
            self.manager = PipManager(active_dir, venv)
            self.manager.run_pip(cmds[0], [opts[1], f"'{file_path}'"])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.consoleWindow.clear()


    def save_requires(self, event):
        """
        Write the requirements of the selected environment to file.
        """
        save_file = QFileDialog.getSaveFileName(self, "Save requirements")
        save_path = save_file[0]
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        if save_path != "":
            # write 'pip freeze' output to selected file
            self.manager = PipManager(active_dir, venv)
            self.manager.run_pip(cmds[2], [">", save_path])

            # show an info message
            message_txt = (f"Saved requirements in: \n{save_path}")
            QMessageBox.information(self, "Saved", message_txt)


    def list_modules(self, event, style):
        """
        Open console dialog and list the installed modules.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        self.console = ConsoleDialog()
        self.console.setWindowTitle(f"Modules installed in:  {venv}")

        #print("[PROCESS]: Listing modules...")
        self.manager = PipManager(active_dir, f"'{venv}'")
        self.manager.run_pip(cmds[style])
        self.manager.started.connect(self.console.exec_)

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # clear the content on window close
        if self.console.close:
            self.console.consoleWindow.clear()


    def freeze_output(self, event, style):
        """
        Show `pip freeze` output in console window.
        """
        self.list_modules(event, style=2)


    def delete_venv(self, event):
        """
        Delete the selected virtual environment by clicking
        delete from the context menu in venv table.
        """
        venv = self.get_selected_item()

        if venv is not None:
            messageBoxConfirm = QMessageBox.critical(self,
                "Confirm", f"Are you sure you want to delete '{venv}'?",
                QMessageBox.Yes | QMessageBox.Cancel
            )

            if messageBoxConfirm == QMessageBox.Yes:
                active_dir = get_active_dir_str()

                venv_to_delete = os.path.join(active_dir, venv)
                shutil.rmtree(venv_to_delete)
                #print(
                    #f"[PROCESS]: Successfully deleted '{active_dir}/{venv}'"
                #)

                self.refresh.emit()



class ResultsTable(QTableView):
    """
    The table that lists the [PyPI](https://pypi.org/pypi) results on
    the wizard's `Install Modules` page.
    """
    contextTriggered = pyqtSignal()

    def contextMenuEvent(self, event):
        self.contextMenu = QMenu(self)

        # actions
        installAction = QAction(
            QIcon.fromTheme("software-install"),
            "Install module",
            self,
            statusTip="&Install module"
        )
        self.contextMenu.addAction(installAction)
        installAction.triggered.connect(lambda: self.contextTriggered.emit())

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            self.contextMenu.popup(QCursor.pos())
