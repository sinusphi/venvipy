# -*- coding: utf-8 -*-
"""
This module contains the tables.
"""
import webbrowser
import shutil
import os
import logging
from functools import partial

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

import get_data
import creator
from dialogs import ConsoleDialog, ProgBarDialog
from creator import CloningWorker
from manage_pip import PipManager


logger = logging.getLogger(__name__)



class BaseTable(QTableView):
    """The base table for all tables.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.delete_icon = QIcon(
            self.style().standardIcon(QStyle.SP_TrashIcon)
        )
        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )

    def get_selected_item(self):
        """
        Get the item name of the selected row (index 0).
        """
        listed_items = self.selectionModel().selectedRows()
        for index in listed_items:
            selected_item = index.data()
            return selected_item



class VenvTable(BaseTable):
    """List the virtual environments found.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    text_changed = pyqtSignal(str)
    refresh = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.thread = QThread(self)
        self.m_clone_repo_worker = CloningWorker()

        # thread
        self.thread.start()
        self.m_clone_repo_worker.moveToThread(self.thread)
        self.m_clone_repo_worker.started.connect(self.progress_bar.exec_)
        self.m_clone_repo_worker.finished.connect(self.progress_bar.close)
        self.m_clone_repo_worker.finished.connect(self.finish_info)

        # perform a proper stop using quit() and wait()
        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.wait)


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            context_menu.popup(QCursor.pos())

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

        install_packages_action = QAction(
            "Install &additional packages",
            self,
            statusTip="Install additional packages"
        )
        install_packages_action.triggered.connect(
            lambda: self.add_packages(event)
        )

        install_requires_action = QAction(
            "Install from &requirements",
            self,
            statusTip="Install packages from requirements"
        )
        install_requires_action.triggered.connect(
            lambda: self.install_requires(event)
        )

        install_local_action = QAction(
            "Install &local project",
            self,
            statusTip="Install a local project"
        )
        install_local_action.triggered.connect(
            lambda: self.install_local(event)
        )

        install_vsc_action = QAction(
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

        list_packages_action = QAction(
            "&List installed packages",
            self,
            statusTip="List installed packages"
        )
        list_packages_action.triggered.connect(
            lambda: self.list_packages(event, style=1)
        )

        list_freeze_action = QAction(
            "Show &freeze output",
            self,
            statusTip="List the output of 'pip freeze'"
        )
        list_freeze_action.triggered.connect(
            lambda: self.freeze_packages(event, style=2)
        )

        list_deptree_action = QAction(
            "Display &dependency tree",
            self,
            statusTip="List dependencies with 'pipdeptree'"
        )
        list_deptree_action.triggered.connect(
            lambda: self.deptree_packages(event, style=3)
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
        #] MENUS [#==========================================================[#
        #]===================================================================[#

        context_menu.addAction(upgrade_pip_action)

        # install sub menu
        context_menu.addMenu(install_sub_menu)
        install_sub_menu.addAction(install_packages_action)
        install_sub_menu.addAction(install_requires_action)
        install_sub_menu.addAction(install_local_action)
        install_sub_menu.addAction(install_vsc_action)

        # details sub meun
        context_menu.addMenu(details_sub_menu)
        details_sub_menu.addAction(list_packages_action)
        details_sub_menu.addAction(list_freeze_action)
        details_sub_menu.addAction(list_deptree_action)

        context_menu.addAction(save_requires_action)
        context_menu.addAction(open_venv_dir_action)
        context_menu.addAction(delete_venv_action)


    def valid_version(self, venv_path):
        """Test wether the Python version required is installed.
        """
        cfg_file = os.path.join(venv_path, "pyvenv.cfg")
        is_installed = get_data.get_pyvenv_cfg(cfg_file, "installed")
        version = get_data.get_pyvenv_cfg(cfg_file, "version")
        py_path = get_data.get_pyvenv_cfg(cfg_file, "py_path")
        msg_txt = (
            f"This environment requires {version} \nfrom {py_path} which is \nnot installed.\n"
        )

        if is_installed == "no":
            msg_box = QMessageBox(
                QMessageBox.Critical,
                "Error",
                msg_txt,
                QMessageBox.Ok,
                self
            )
            msg_box.exec_()
            return False
        return True


    def venv_exists(self, path):
        """
        Test wether the directory of the selected environment actually exists.
        """
        if os.path.exists(path):
            return True

        msg_box = QMessageBox(
            QMessageBox.Critical,
            "Error",
            "Selected environment could not be found.",
            QMessageBox.Ok,
            self
        )
        msg_box.exec_()
        self.refresh.emit()
        return False


    def has_pip(self, venv_dir, venv_name):
        """Test if `pip` is installed.
        """
        venv_path = os.path.join(venv_dir, venv_name)
        pip_binary = os.path.join(venv_path, "bin", "pip")
        has_pip = os.path.exists(pip_binary)

        if self.venv_exists(venv_path) and self.valid_version(venv_path):
            if has_pip:
                return True
            QMessageBox.information(
                self,
                "Info",
                "This environment has no Pip installed."
            )
            return False
        return False


    def upgrade_pip(self, event):
        """Run `pip install --upgrade pip` command.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            self.console.setWindowTitle("Updating Pip")
            logger.info("Attempting to update Pip...")

            self.manager = PipManager(active_dir, venv)
            self.manager.run_pip(creator.cmds[0], [creator.opts[0], "pip"])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()


    def add_packages(self, event):
        """
        Install additional packages into the selected environment.
        """
        pass


    def install_requires(self, event):
        """
        Install packages from a requirements file into the
        selected environment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            file_name = QFileDialog.getOpenFileName(
                self,
                "Select a requirements"
            )
            file_path = file_name[0]

            if file_path != "":
                creator.fix_requirements(file_path)
                self.console.setWindowTitle("Installing from requirements")
                logger.info("Installing from requirements...")

                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(
                    creator.cmds[0], [creator.opts[1], f"'{file_path}'"]
                )
                self.manager.started.connect(self.console.exec_)

                # display the updated output
                self.manager.textChanged.connect(self.console.update_status)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def install_local(self, event):
        """Install from a local project.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            project_dir = QFileDialog.getExistingDirectory(
                self,
                "Select project directory"
            )
            project_name = os.path.basename(project_dir)

            if project_dir != "":
                self.console.setWindowTitle(f"Installing {project_name}")
                logger.info("Installing from local project path...")

                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(
                    creator.cmds[0], [creator.opts[2], f"'{project_dir}'"]
                )
                self.manager.started.connect(self.console.exec_)

                # display the updated output
                self.manager.textChanged.connect(self.console.update_status)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def install_vsc(self, event):
        """Install from a VSC repository.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_bin = os.path.join(active_dir, venv, "bin", "python")

        if self.has_pip(active_dir, venv):
            url, ok = QInputDialog.getText(
                self,
                "Specify VSC project url",
                "Enter url to repository:" + " " * 65
            )

            if url != "":
                project_name = os.path.basename(url)
                project_url = f"git+{url}#egg={project_name}"
                cmd = (
                    f"{venv_bin} -m pip install --no-cache-dir -e {project_url}"
                )
                self.progress_bar.setWindowTitle(f"Installing {project_name}")
                self.progress_bar.status_label.setText("Cloning repository...")
                logger.info(f"Installing {project_name}...")

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
        active_dir = get_data.get_active_dir_str()
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
                logger.info(f"Saving '{save_path}'...")

                # write 'pip freeze' output to selected file
                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(creator.cmds[2], [">", save_path])

                # show an info message
                message_txt = (f"Saved requirements in \n{save_path}")
                QMessageBox.information(self, "Saved", message_txt)


    def list_packages(self, event, style):
        """
        Open console dialog and list the installed packages. The argument
        `style` controls which style the output should have: `style=1` for
        `pip list`, `style=2` for `pip freeze` and style=3 for a dependency
        output via `pipdeptree`.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            self.console.setWindowTitle(f"Packages installed in:  {venv}")

            self.manager = PipManager(active_dir, f"'{venv}'")
            self.manager.run_pip(creator.cmds[style])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()


    def freeze_packages(self, event, style):
        """Print `pip freeze` output to console window.
        """
        self.list_packages(event, style)


    def deptree_packages(self, event, style):
        """
        Test if `pipdeptree` is installed and ask user wether to
        install it if it's not. Then call `self.list_packages()`
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        pipdeptree_binary = os.path.join(active_dir, venv, "bin", "pipdeptree")
        has_pipdeptree = os.path.exists(pipdeptree_binary)
        message_txt = (
            "This requires the pipdeptree package\nto be installed.\n\n"
            "Do you want to install it?\n"
        )

        if has_pipdeptree:
            self.list_packages(event, style)
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
                    logger.info("Installing pipdeptree...")

                    self.manager = PipManager(active_dir, venv)
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[0], "pipdeptree"]
                    )
                    self.manager.started.connect(self.progress_bar.exec_)
                    self.manager.finished.connect(self.progress_bar.close)
                    self.manager.process_stop()
                    self.list_packages(event, style)


    def open_venv_dir(self, event):
        """Open the selected venv directory.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if os.path.isdir(venv_dir):
            os.system(f"xdg-open '{venv_dir}'")


    def delete_venv(self, event):
        """
        Delete the selected virtual environment by clicking
        delete from the context menu in venv table.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
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
                logging.info(f"Successfully deleted '{venv_path}'")
                self.refresh.emit()



class ResultsTable(BaseTable):
    """Contains the results from PyPI.
    """
    context_triggered = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            context_menu.popup(QCursor.pos())

        install_action = QAction(
            QIcon.fromTheme("software-install"),
            "&Install module",
            self,
            statusTip="Install module"
        )
        context_menu.addAction(install_action)
        # connect to install_package() in InstallPackages() in wizard
        install_action.triggered.connect(
            lambda: self.context_triggered.emit()
        )

        open_pypi_action = QAction(
            self.info_icon,
            "&Open on PyPI",
            self,
            statusTip="Open on Python Package Index"
        )
        context_menu.addAction(open_pypi_action)
        open_pypi_action.triggered.connect(
            lambda: self.open_on_pypi(event)
        )


    def open_on_pypi(self, event):
        """
        Open pypi.org and show the project description
        of the selected package.
        """
        url = "https://pypi.org/project"
        package = self.get_selected_item()
        webbrowser.open("/".join([url, package, "#description"]))



class InterpreterTable(BaseTable):
    """
    List the Python installs found.
    """
    drop_item = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            context_menu.popup(QCursor.pos())

        remove_py_action = QAction(
            self.delete_icon,
            "&Remove from list",
            self,
            statusTip="Remove this item from the table"
        )
        context_menu.addAction(remove_py_action)
        remove_py_action.triggered.connect(
            lambda: self.remove_python(event)
        )


    def remove_python(self, event):
        """Remove a Python version from the table.
        """
        item = self.get_selected_item()

        msg_box_warning = QMessageBox.warning(
            self,
            "Confirm",
            "Remove this item from list.     \nAre you sure?",
            QMessageBox.Yes | QMessageBox.Cancel
        )
        if msg_box_warning == QMessageBox.Yes:
            with open(get_data.DB_FILE, "r") as f:
                lines = f.readlines()
            with open(get_data.DB_FILE, "w") as f:
                for line in lines:
                    if item not in line:
                        f.write(line)

            logging.info(f"Removed '{item}' from database")
            self.drop_item.emit()
