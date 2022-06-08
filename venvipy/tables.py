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
This module contains the tables.
"""
import os
import shutil
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
from creator import InstallWorker
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
        Return `str` from `name` column of the selected row.
        """
        listed_items = self.selectionModel().selectedRows()
        for index in listed_items:
            selected_item = index.data()
            return selected_item


    def get_comment(self):
        """
        Return `str` from `comment` column of the selected row.
        """
        index = self.currentIndex()
        row_index = self.selectionModel().selectedRows()
        row_comment = index.sibling(row_index[0].row(), 4).data()
        return row_comment



class VenvTable(BaseTable):
    """List the virtual environments found.
    """
    started = pyqtSignal()
    finished = pyqtSignal()
    text_changed = pyqtSignal(str)
    refresh = pyqtSignal()
    start_installer = pyqtSignal()


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
        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )

        self.progress_bar = ProgBarDialog()
        self.console = ConsoleDialog()
        self.thread = QThread(self)
        self.m_install_worker = InstallWorker()

        # thread
        self.thread.start()
        self.m_install_worker.moveToThread(self.thread)

        self.m_install_worker.started.connect(self.console.exec_)
        self.m_install_worker.text_changed.connect(
            self.console.update_status
        )

        # perform a proper stop using quit() and wait()
        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.wait)


    def contextMenuEvent(self, event):

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
            lambda: self.upgrade_pip(event, pkg="pip")
        )

        install_wheel_action = QAction(
            QIcon.fromTheme("system-software-update"),
            "Install &Wheel",
            self,
            statusTip="Install wheel package"
        )
        install_wheel_action.triggered.connect(
            lambda: self.install_wheel(event, pkg="wheel")
        )

        install_packages_action = QAction(
            "Install &packages from PyPI",
            self,
            statusTip="Install packages from PyPI"
        )
        install_packages_action.triggered.connect(
            lambda: self.install_pypi_packages(event)
        )

        install_requires_action = QAction(
            "Install from a &requirements file",
            self,
            statusTip="Install packages from requirements"
        )
        install_requires_action.triggered.connect(
            lambda: self.install_requires(event)
        )

        install_local_action = QAction(
            "Install from a &local project directory",
            self,
            statusTip="Install from a local stored project directory"
        )
        install_local_action.triggered.connect(
            lambda: self.install_local(event)
        )

        install_vcs_action = QAction(
            "Install from a &VCS project url",
            self,
            statusTip="Install from a VCS url"
        )
        install_vcs_action.triggered.connect(
            lambda: self.install_vcs(event)
        )

        save_requires_action = QAction(
            self.save_icon,
            "Save &requirements",
            self,
            statusTip="Generate a requirements file"
        )
        save_requires_action.triggered.connect(
            lambda: self.save_requires(event)
        )

        comment_add_action = QAction(
            self.info_icon,
            "&Add or modify description",
            self,
            statusTip="Add or modify description"
        )
        comment_add_action.triggered.connect(
            lambda: self.comment_add(event)
        )

        comment_remove_action = QAction(
            self.info_icon,
            "&Remove description",
            self,
            statusTip="Remove description"
        )
        comment_remove_action.triggered.connect(
            lambda: self.comment_remove(event)
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
            "Delete &environment",
            self,
            statusTip="Delete environment"
        )
        delete_venv_action.triggered.connect(
            lambda: self.delete_venv(event)
        )


        #]===================================================================[#
        #] MENUS [#==========================================================[#
        #]===================================================================[#

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
        comment_sub_menu = QMenu(
            "&Description",
            self,
            icon=self.info_icon
        )

        context_menu.addAction(upgrade_pip_action)
        context_menu.addAction(install_wheel_action)

        # install sub menu
        context_menu.addMenu(install_sub_menu)
        install_sub_menu.addAction(install_packages_action)
        install_sub_menu.addAction(install_requires_action)
        install_sub_menu.addAction(install_local_action)
        install_sub_menu.addAction(install_vcs_action)

        # details sub meun
        context_menu.addMenu(details_sub_menu)
        details_sub_menu.addAction(list_packages_action)
        details_sub_menu.addAction(list_freeze_action)
        details_sub_menu.addAction(list_deptree_action)

        # comment sub menu
        context_menu.addMenu(comment_sub_menu)
        comment_sub_menu.addAction(comment_add_action)
        comment_sub_menu.addAction(comment_remove_action)

        context_menu.addAction(save_requires_action)
        context_menu.addAction(open_venv_dir_action)
        context_menu.addAction(delete_venv_action)


    def valid_version(self, venv_path):
        """Test wether the Python version required is installed.
        """
        cfg_file = os.path.join(venv_path, "pyvenv.cfg")
        is_installed = get_data.get_config(cfg_file, "installed")
        version = get_data.get_config(cfg_file, "version")
        py_path = get_data.get_config(cfg_file, "py_path")
        msg_txt = (
            f"This environment requires {version} \n"
            f"from {py_path} which is \nnot installed.\n"
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
        Test wether the directory of the selected environment exists.
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

        # refresh venv table
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


    def upgrade_pip(self, event, pkg):
        """Run `pip install --upgrade pip` command.
        """
        self.install_sys_pkg(pkg)


    def install_wheel(self, event, pkg):
        """Run `pip install --upgrade wheel` command.
        """
        self.install_sys_pkg(pkg)


    def install_sys_pkg(self, pkg):
        """Run `pip install --upgrade <pkg>` command.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        if self.has_pip(active_dir, venv):
            self.console.setWindowTitle(f"Installing latest {pkg}")
            logger.debug(f"Installing latest version of {pkg}...")

            self.manager = PipManager(active_dir, venv)
            self.manager.run_pip(creator.cmds[0], [creator.opts[0], f"{pkg}"])
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.text_changed.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()


    def install_pypi_packages(self, event):
        """
        Install packages from [PyPI](https://pypi.org)
        into the selected environment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_path = os.path.join(active_dir, venv)

        if self.has_pip(active_dir, venv):
            with open(get_data.ACTIVE_VENV, "w") as f:
                f.write(venv_path)

            self.start_installer.emit()


    def install_requires(self, event):
        """
        Install packages from a requirements file into the
        selected environment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_bin = os.path.join(active_dir, venv, "bin", "python")

        if self.has_pip(active_dir, venv):
            file_name = QFileDialog.getOpenFileName(
                self,
                "Specify a requirements file"
            )
            file_path = file_name[0]

            if file_path != "":
                creator.fix_requirements(file_path)
                logger.debug("Installing from requirements...")
                cmd = (
                    f"{venv_bin} -m pip {creator.cmds[0]} {creator.opts[1]} {file_path}"
                )
                self.console.setWindowTitle(
                    "Installing from requirements file"
                )
                wrapper = partial(self.m_install_worker.run_process, cmd)
                QTimer.singleShot(0, wrapper)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def install_local(self, event):
        """Install from a local project directory.
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
                if get_data.is_writable(project_dir):
                    self.console.setWindowTitle(f"Installing {project_name}")
                    logger.debug("Installing from local project directory...")

                    self.manager = PipManager(active_dir, venv)
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[3], f"'{project_dir}'"]
                    )
                    self.manager.started.connect(self.console.exec_)

                    # display the updated output
                    self.manager.text_changed.connect(self.console.update_status)

                    # clear the content on window close
                    if self.console.close:
                        self.console.console_window.clear()

                else:
                    msg_txt = (
                        "Filesystem not writable.\n\n"
                        "Unable to create the '.egg-info'      \n"
                        "folder inside the project directory.      \n\n"
                    )
                    QMessageBox.warning(self, "Abort", msg_txt)


    def install_vcs(self, event):
        """Install from VCS.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_bin = os.path.join(active_dir, venv, "bin", "python")

        if self.has_pip(active_dir, venv):
            url, ok = QInputDialog.getText(
                self,
                "Specify project",
                "Enter link to repository:" + " " * 80
            )

            if url != "":
                self.vcs_project_url = url[:-4] if url.endswith(".git") else url
                self.vcs_project_name = os.path.basename(self.vcs_project_url)
                formatted_project_url = (
                    f"git+{self.vcs_project_url}#egg={self.vcs_project_name}"
                )
                cmd = (
                    f"{venv_bin} -m pip {creator.cmds[0]} {formatted_project_url}"
                )
                self.console.setWindowTitle(
                    f"Installing {self.vcs_project_name}"
                )
                wrapper = partial(self.m_install_worker.run_process, cmd)
                QTimer.singleShot(0, wrapper)

                # clear the content on window close
                if self.console.close:
                    self.console.console_window.clear()


    def save_requires(self, event):
        """
        Pip freeze a requirements of the selected environment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if self.has_pip(active_dir, venv):
            save_file = QFileDialog.getSaveFileName(
                self,
                "Save requirements",
                directory=os.path.join(venv_dir, "requirements.txt")
            )
            save_path = save_file[0]

            if save_path != "":
                # write 'pip freeze' output to selected file
                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(creator.cmds[2], [">", save_path])
                logger.debug(f"Saved '{save_path}'")

                # show an info message
                message_txt = (f"Saved requirements in \n{save_path}")
                QMessageBox.information(self, "Saved", message_txt)

                # comment the 'pkg_resources==0.0.0' entry
                creator.fix_requirements(save_path)


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
            self.manager.text_changed.connect(self.console.update_status)

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
            "This requires pipdeptree             \nto be installed.\n\n"
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
                    logger.debug("Installing pipdeptree...")

                    self.manager = PipManager(active_dir, venv)
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[0], "pipdeptree"]
                    )
                    self.manager.started.connect(self.progress_bar.exec_)
                    self.manager.finished.connect(self.progress_bar.close)
                    self.manager.process_stop()
                    self.list_packages(event, style)


    def comment_add(self, event):
        """Add / modify a comment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        comment_old = self.get_comment()
        venvipy_cfg = os.path.join(active_dir, venv, "venvipy.cfg")

        if not os.path.exists(venvipy_cfg):
            comment_new, ok = QInputDialog.getText(
                self,
                "Enter description",
                "\nEnter a description:" + " " * 70
            )
            if len(comment_new) > 0:
                # save a new description
                creator.save_comment(venvipy_cfg, comment_new)
                logger.debug("Description saved")

        else:
            comment_new, ok = QInputDialog.getText(
                self,
                "Modify description",
                "\nModify your description:" + " " * 70,
                text=comment_old
            )
            if len(comment_new) > 0:
                # modify an existing description
                creator.save_comment(venvipy_cfg, comment_new)
                logger.debug("Description updated")
            else:
                # keep the old description
                creator.save_comment(venvipy_cfg, comment_old)

        # refresh venv table
        self.refresh.emit()


    def comment_remove(self, event):
        """Remove comment.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venvipy_cfg = os.path.join(active_dir, venv, "venvipy.cfg")

        if os.path.exists(venvipy_cfg):
            msg_box_warning = QMessageBox.warning(
                self,
                "Remove comment",
                "Delete this comment.        \n"
                "Are you sure?\n",
                QMessageBox.Yes | QMessageBox.Cancel
            )
            if msg_box_warning == QMessageBox.Yes:
                os.remove(venvipy_cfg)
                logger.debug(f"Successfully deleted '{venvipy_cfg}'")
                self.refresh.emit()


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
                "Delete venv",
                f"Delete '{venv}'?           \n"
                "Are you sure?\n",
                QMessageBox.Yes | QMessageBox.Cancel
            )
            if msg_box_critical == QMessageBox.Yes:
                shutil.rmtree(venv_path)
                logger.debug(f"Successfully deleted '{venv_path}'")
                self.refresh.emit()



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
            "Remove this item from list.       \n"
            "Are you sure?\n",
            QMessageBox.Yes | QMessageBox.Cancel
        )
        if msg_box_warning == QMessageBox.Yes:
            with open(get_data.DB_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(get_data.DB_FILE, "w", encoding="utf-8") as f:
                for line in lines:
                    if item not in line:
                        f.write(line)

            logger.debug(f"Removed '{item}' from database")
            self.drop_item.emit()
