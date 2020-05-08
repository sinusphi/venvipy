# -*- coding: utf-8 -*-
"""
This module contains the implementation of QTableView.
"""
from functools import partial
import webbrowser
import shutil
import os
from subprocess import Popen

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import (
    QStyle,
    QAction,
    QTableView,
    QMenu,
    QMessageBox,
    QFileDialog,
    QInputDialog
)

from get_data import get_active_dir_str
from dialogs import ConsoleDialog, ProgBarDialog
from manage_pip import PipManager
from creator import (
    CloningWorker,
    fix_requirements,
    cmds,
    opts
)



class VenvTable(QTableView):
    """
    The table that lists the virtual environments
    found in the specified folder.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    text_changed = pyqtSignal(str)
    refresh = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )
        self.drive_icon = QIcon(
            self.style().standardIcon(QStyle.SP_DriveHDIcon)
        )
        self.delete_icon = QIcon(
            self.style().standardIcon(QStyle.SP_TrashIcon)
        )
        self.save_icon = QIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton)
        )
        self.folder_icon = QIcon(
            self.style().standardIcon(QStyle.SP_DirOpenIcon)
        )

        self.progress_bar = ProgBarDialog()
        self.console = ConsoleDialog()
        self.manager = PipManager("", "")
        self.thread = QThread(self)
        self.m_clone_repo_worker = CloningWorker()

        # thread
        self.thread.start()
        self.m_clone_repo_worker.moveToThread(self.thread)
        self.m_clone_repo_worker.started.connect(self.progress_bar.exec_)
        self.m_clone_repo_worker.finished.connect(self.progress_bar.close)
        self.m_clone_repo_worker.finished.connect(self.finish_info)


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # sub menus
        details_sub_menu = QMenu(
            "Det&ails",
            self,
            icon=self.info_icon
        )
        install_sub_menu = QMenu(
            "&Install",
            self,
            icon=QIcon.fromTheme("software-install")
        )
        editable_sub_menu = QMenu(
            "&Editable",
            self,
            icon=QIcon.fromTheme("software-install")
        )


        #]===================================================================[#
        #] ACTIONS [#========================================================[#
        #]===================================================================[#

        upgrade_pip_action = QAction(
            QIcon.fromTheme("system-software-update"),
            "&Upgrade Pip to latest",
            self,
            statusTip="Upgrade Pip to the latest version"
        )
        upgrade_pip_action.triggered.connect(
            lambda: self.upgrade_pip(event)
        )

        install_modules_action = QAction(
            QIcon.fromTheme("list-add"),
            "&Install additional modules",
            self,
            statusTip="Install additional modules"
        )
        install_modules_action.triggered.connect(
            lambda: self.add_modules(event)
        )

        install_requires_action = QAction(
            QIcon.fromTheme("list-add"),
            "Install from &requirements",
            self,
            statusTip="Install modules from requirements"
        )
        install_requires_action.triggered.connect(
            lambda: self.install_requires(event)
        )

        install_local_action = QAction(
            self.drive_icon,
            "Install &local project",
            self,
            statusTip="Install a local project"
        )
        install_local_action.triggered.connect(
            lambda: self.install_local(event)
        )

        install_vsc_action = QAction(
            QIcon.fromTheme("software-install"),
            "Install from &repository",
            self,
            statusTip="Install from VSC repository"
        )
        install_vsc_action.triggered.connect(
            lambda: self.install_vsc(event)
        )

        save_requires_action = QAction(
            self.save_icon,
            "Save &requirements",
            self,
            statusTip="Write requirements to file"
        )
        save_requires_action.triggered.connect(
            lambda: self.save_requires(event)
        )

        list_modules_action = QAction(
            self.info_icon,
            "&List installed modules",
            self,
            statusTip="List installed modules"
        )
        list_modules_action.triggered.connect(
            lambda: self.list_modules(event, style=1)
        )

        freeze_action = QAction(
            self.info_icon,
            "Show &freeze output",
            self,
            statusTip="List the output of 'pip freeze'"
        )
        freeze_action.triggered.connect(
            lambda: self.freeze_output(event, style=2)
        )

        pipdeptree_action = QAction(
            self.info_icon,
            "Show &dependencie tree",
            self,
            statusTip="List dependencies with 'pipdeptree'"
        )
        pipdeptree_action.triggered.connect(
            lambda: self.pipdeptree_output(event, style=3)
        )

        open_venv_dir_action = QAction(
            self.folder_icon,
            "&Open containing folder",
            self,
            statusTip="Open the folder containing the virtual environment"
        )
        open_venv_dir_action.triggered.connect(
            lambda: self.open_venv_dir(event)
        )

        delete_venv_action = QAction(
            self.delete_icon,
            "&Delete environment",
            self,
            statusTip="Delete environment"
        )
        delete_venv_action.triggered.connect(
            lambda: self.delete_venv(event)
        )


        #]===================================================================[#
        #] ADD ACTIONS [#====================================================[#
        #]===================================================================[#

        context_menu.addAction(upgrade_pip_action)

        # install sub menu
        context_menu.addMenu(install_sub_menu)
        install_sub_menu.addAction(install_modules_action)
        install_sub_menu.addAction(install_requires_action)

        # editable sub menu
        install_sub_menu.addMenu(editable_sub_menu)
        editable_sub_menu.addAction(install_local_action)
        editable_sub_menu.addAction(install_vsc_action)

        context_menu.addAction(save_requires_action)

        # details sub meun
        context_menu.addMenu(details_sub_menu)
        details_sub_menu.addAction(list_modules_action)
        details_sub_menu.addAction(freeze_action)
        details_sub_menu.addAction(pipdeptree_action)

        context_menu.addAction(open_venv_dir_action)
        context_menu.addAction(delete_venv_action)

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            context_menu.popup(QCursor.pos())


    def venv_exists(self, path):
        """
        Test wether the directory of the selected environment actually exists.
        """
        if os.path.exists(path):
            return True

        msg_box = QMessageBox(
            QMessageBox.Critical,
            "Error",
            "The selected environment could not be found.",
            QMessageBox.Ok,
            self
        )
        msg_box.exec_()
        self.refresh.emit()
        return False


    def has_pip(self, venv_dir, venv_name):
        """
        Test if `pip` is installed.
        """
        venv_path = os.path.join(venv_dir, venv_name)
        pip_binary = os.path.join(venv_path, "bin", "pip")
        has_pip = os.path.exists(pip_binary)

        if self.venv_exists(venv_path):
            if has_pip:
                return True
            QMessageBox.information(
                self,
                "Info",
                "Environment has been created without pip."
            )
            return False
        return False


    def get_selected_item(self):
        """
        Get the venv name of the selected row.
        """
        listed_venvs = self.selectionModel().selectedRows()
        for index in listed_venvs:
            selected_venv = index.data()
            return selected_venv


    def upgrade_pip(self, event):
        """
        Run `pip install --upgrade pip` command.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            self.console.setWindowTitle("Updating Pip")

            print("[PROCESS]: Updating Pip to the latest version...")
            self.manager = PipManager(active_dir, venv)
            self.manager.run_pip(cmds[0], [opts[0], "pip"])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()


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
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            file_name = QFileDialog.getOpenFileName(
                self,
                "Select a requirements"
            )
            file_path = file_name[0]

            if file_path != "":
                fix_requirements(file_path)
                print("[PROCESS]: Installing from requirements...")
                self.console.setWindowTitle("Installing from requirements")

                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(cmds[0], [opts[1], f"'{file_path}'"])
                self.manager.started.connect(self.console.exec_)

                # display the updated output
                self.manager.textChanged.connect(self.console.update_status)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def install_local(self, event):
        """
        Install from a local project.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        project_dir = QFileDialog.getExistingDirectory(
            self,
            "Select project directory"
        )
        project_name = os.path.basename(project_dir)

        if project_dir != "":
            if self.has_pip(active_dir, venv):
                print("[PROCESS]: Installing from local project path...")
                self.console.setWindowTitle(f"Installing {project_name}")

                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(cmds[0], [opts[2], f"'{project_dir}'"])
                self.manager.started.connect(self.console.exec_)

                # display the updated output
                self.manager.textChanged.connect(self.console.update_status)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def install_vsc(self, event):
        """
        Install from a VSC repository.
        """
        self.clone_process()


    def clone_process(self):
        """
        Clone the repository.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()
        venv_bin = os.path.join(active_dir, venv, "bin", "python")

        url, ok = QInputDialog.getText(
            self,
            "Specify VSC project url",
            "Enter url to repository:" + " " * 65
        )

        if url != "":
            if self.has_pip(active_dir, venv):
                project_name = os.path.basename(url)
                project_url = f"git+{url}#egg={project_name}"
                cmd = (
                    f"{venv_bin} -m pip install --no-cache-dir -e {project_url}"
                )

                print(f"[PROCESS]: Installing {project_name}...")
                self.progress_bar.setWindowTitle(f"Installing {project_name}")
                self.progress_bar.status_label.setText("Cloning repository...")

                wrapper = partial(
                    self.m_clone_repo_worker.run_process, cmd
                )
                QTimer.singleShot(0, wrapper)


    def finish_info(self):
        """
        Show an info message when the cloning process has finished successfully.
        """
        msg_txt = (
            "Successfully installed package       \nfrom VSC repository.\n"
        )
        QMessageBox.information(self, "Done", msg_txt)


    def save_requires(self, event):
        """
        Write the requirements of the selected environment to file.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if self.has_pip(active_dir, venv):
            save_file = QFileDialog.getSaveFileName(
                self,
                "Save requirements",
                directory=f"{venv_dir}/requirements.txt"
            )
            save_path = save_file[0]

            if save_path != "":
                # write 'pip freeze' output to selected file
                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(cmds[2], [">", save_path])

                # show an info message
                print(f"[PROCESS]: Saved requirements in {save_path}...")
                message_txt = (f"Saved requirements in \n{save_path}")
                QMessageBox.information(self, "Saved", message_txt)


    def list_modules(self, event, style):
        """
        Open console dialog and list the installed modules.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            self.console.setWindowTitle(f"Modules installed in:  {venv}")

            print("[PROCESS]: Listing modules...")
            self.manager = PipManager(active_dir, f"'{venv}'")
            self.manager.run_pip(cmds[style])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()


    def freeze_output(self, event, style):
        """
        Print `pip freeze` output to console window.
        """
        self.list_modules(event, style)


    def pipdeptree_output(self, event, style):
        """
        Test if `pipdeptree` is installed and ask user wether to
        install it if it's not. Then call `self.list_modules()`
        """
        message_txt = (
            "This requires the pipdeptree package\nto be installed.\n\n"
            "Do you want to install it?\n"
        )
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()
        pipdeptree_binary = os.path.join(active_dir, venv, "bin", "pipdeptree")
        has_pipdeptree = os.path.exists(pipdeptree_binary)

        if has_pipdeptree:
            self.list_modules(event, style)
        else:
            if self.has_pip(active_dir, venv):
                msg_box_confirm = QMessageBox.question(
                    self,
                    "Confirm",
                    message_txt,
                    QMessageBox.Yes | QMessageBox.Cancel
                )
                if msg_box_confirm == QMessageBox.Yes:
                    self.progress_bar.setWindowTitle("Installing")
                    self.progress_bar.status_label.setText(
                        "Installing pipdeptree..."
                    )
                    print(f"[PROCESS]: Installing pipdeptree...")
                    self.manager = PipManager(active_dir, venv)
                    self.manager.run_pip(cmds[0], [opts[0], "pipdeptree"])
                    self.manager.started.connect(self.progress_bar.exec_)
                    self.manager.finished.connect(self.progress_bar.close)
                    self.manager.process_stop()
                    self.list_modules(event, style)


    def open_venv_dir(self, event):
        """
        Open the selected venv directory.
        """
        active_dir = get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if os.path.isdir(venv_dir):
            Popen(["xdg-open", venv_dir])


    def delete_venv(self, event):
        """
        Delete the selected virtual environment by clicking
        delete from the context menu in venv table.
        """
        venv = self.get_selected_item()
        active_dir = get_active_dir_str()
        venv_path = os.path.join(active_dir, venv)

        if self.venv_exists(venv_path):
            msg_box_critical = QMessageBox.critical(
                self,
                "Confirm",
                f"Are you sure you want to delete '{venv}'?",
                QMessageBox.Yes | QMessageBox.Cancel
            )
            if msg_box_critical == QMessageBox.Yes:
                shutil.rmtree(venv_path)
                print(f"[PROCESS]: Successfully deleted '{venv_path}'")
                self.refresh.emit()



class ResultsTable(QTableView):
    """
    The table that lists the [PyPI](https://pypi.org/pypi) results on
    the wizard's `Install Modules` page.
    """
    context_triggered = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )


    def contextMenuEvent(self, event):
        self.context_menu = QMenu(self)

        install_action = QAction(
            QIcon.fromTheme("software-install"),
            "&Install module",
            self,
            statusTip="Install module"
        )
        self.context_menu.addAction(install_action)
        # connect to install_module() in InstallModules() in wizard
        install_action.triggered.connect(
            lambda: self.context_triggered.emit()
        )

        open_pypi_action = QAction(
            self.info_icon,
            "&Open on PyPI",
            self,
            statusTip="Open on Python Package Index"
        )
        self.context_menu.addAction(open_pypi_action)
        open_pypi_action.triggered.connect(
            lambda: self.open_on_pypi(event)
        )

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            self.context_menu.popup(QCursor.pos())


    def get_selected_item(self):
        """
        Get the venv name of the selected row.
        """
        listed_venvs = self.selectionModel().selectedRows()
        for index in listed_venvs:
            selected_venv = index.data()
            return selected_venv


    def open_on_pypi(self, event):
        """
        Open pypi.org and show the project description
        of the selected package.
        """
        package = self.get_selected_item()
        webbrowser.open(f"pypi.org/project/{package}/#description")
