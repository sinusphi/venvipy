# -*- coding: utf-8 -*-
"""
This module contains the tables.
"""
import webbrowser
import shutil
import os
import logging
from functools import partial
from importlib import import_module

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import pyqtSignal, QThread, QTimer, QUrl
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
from dialogs import ConsoleDialog, ProgBarDialog, ProjectsDialog
from creator import CloningWorker, InstallPipWorker
from manage_pip import PipManager
from venvi_cfg import VenvConfigMgr

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
    add_pkgs = pyqtSignal(str)

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

        self.thread2 = QThread(self)
        self.m_install_pip_worker = InstallPipWorker()
        
        self.thread2.start()
        self.m_install_pip_worker.moveToThread(self.thread2)
        self.m_install_pip_worker.started.connect(self.progress_bar.exec_)
        self.m_install_pip_worker.finished.connect(self.progress_bar.close)
        self.m_install_pip_worker.finished.connect(self.finish_info_2)

        self.thread2.finished.connect(self.thread2.quit)
        self.thread2.finished.connect(self.thread2.wait)

        self.pip_mgr_fail_msg = None

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

        generate_scripts_action = QAction(
            self.save_icon,
            "Generate venv access scripts",
            self,
            statusTip="Write venv access scripts to project dir"
        )
        generate_scripts_action.triggered.connect(
            lambda: self.generate_scripts(event)
        )

        list_projects_action = QAction(
            #self.save_icon,
            "List dev project dirs that access this venv",
            self,
            statusTip="List dev project dirs that access this venv"
        )
        list_projects_action.triggered.connect(
            lambda: self.list_projects(event, style=1)
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
        context_menu.addAction(generate_scripts_action)
        context_menu.addAction(list_projects_action)
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

    def check_venv_for_importable_pip(self, venv_dir, venv_name):
        """For pip to truly be installed and usable, not only does
        the pip executable need to exist, so too does the pip
        python module need to be importable. 

        This method returns True if the pip module can be imported 
        from inside the venv, False otherwise.

        This check is required, because if a previous pip installation
        fails, rather than removing itself, it seems that pip simply
        disables its module by renaming the pip module "~ip" and 
        leaving the pip executable file in place. This behavior,
        was causing the has_pip() module below to return true just
        because the pip executable existed, eventhough the pip module
        was not importable; thus causing the subsequent upgrade_pip()
        call to fail.
        """
        pip_importable = False

        self.manager = PipManager(venv_dir, venv_name)

        #self.manager.started.connect(self.console.exec_)

        # display the updated output
        #self.manager.textChanged.connect(self.console.update_status)
        
        self.manager.failed_msg.connect(self.process_pip_mgr_fail_msg)

        self.manager.run_pip_import()

        if self.pip_mgr_fail_msg:
            logger.debug(f"PIP MGR FAIL MSG: '{self.pip_mgr_fail_msg}'")
            s = self.pip_mgr_fail_msg.replace("'", "")
            s = s.replace('"', '')
            s = s.lower()
            if s.find("no module named pip") != -1:
                pip_importable = False
            else:
                pip_importable = True
        else:
            pip_importable = True

        self.pip_mgr_fail_msg = None
        logger.debug(f"PIP IMPORTABLE: {pip_importable}")
        return(pip_importable)

    def process_pip_mgr_fail_msg(self, fail_msg):
        logger.debug(f"process_pip_mgr_fail_msg: '{fail_msg}'")
        self.pip_mgr_fail_msg = fail_msg

    def has_pip(self, venv_dir, venv_name):
        """Test if `pip` is installed.
        """
        venv_path = os.path.join(venv_dir, venv_name)
        if os.name == 'nt':
            pip_binary = os.path.join(venv_path, "Scripts", "pip.exe")
        else:
            pip_binary = os.path.join(venv_path, "bin", "pip")
        has_pip = os.path.exists(pip_binary)

        # The above is not sufficient, because the pip executable can
        # be installed, but the python pip module may not be, or may
        # be incorrectly installed in site-packages as "~ip" which would
        # be "pip" if the pip module had been correctly installed. This
        # situation will cause the upgrade_pip() call below to fail
        # because python cannot find the pip module since its named "~ip".
        # However, we cannot simply attempt to import pip here because 
        # the venv has not yet been activated. We need to activate the 
        # venv and try then try and import pip...
        if has_pip:
            # The pip executable exists, but can be import the pip module?
            has_pip = self.check_venv_for_importable_pip(venv_dir, venv_name)

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
            logger.debug("Attempting to update Pip...")

            self.manager = PipManager(active_dir, venv)

            # On Windows this call to run_pip BEFORE doing the connect calls
            # below is problematic, though it works fine on Ubuntu.
            # Have to move the run_pip call until AFTER the connect calls
            # for the connect slots to work on Windows.
            #self.manager.run_pip(creator.cmds[0], [creator.opts[0], "pip"])
            
            self.manager.started.connect(self.console.exec_)

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            self.manager.run_pip(creator.cmds[0], [creator.opts[0], "pip"])

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()

        else:
            # no pip, ask to install it
            response = QMessageBox.question(self, 'Need Pip?', "Would you like to install pip?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if response == QMessageBox.Yes:
                wrapper = partial(
                    self.m_install_pip_worker.run_process, active_dir, venv
                )
                QTimer.singleShot(0, wrapper)
                



    def add_packages(self, event):
        """
        Install additional packages into the selected environment.
        """
        self.add_pkgs.emit(self.get_selected_item())


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
                logger.debug("Installing from requirements...")

                self.manager = PipManager(active_dir, venv)
                if os.name == 'nt':
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[1], f"{file_path}"]
                    )
                else:
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
                logger.debug("Installing from local project path...")

                self.manager = PipManager(active_dir, venv)
                if os.name == 'nt':
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[2], f"{project_dir}"]
                    )
                else:
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
        if os.name == 'nt':
            active_dir = active_dir.replace('/', '\\')
        venv = self.get_selected_item()
        if os.name == 'nt':
            venv_bin = os.path.join(active_dir, venv, "Scripts", "python.exe")
        else:
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
                logger.debug(f"Installing {project_name}...")

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

    def finish_info_2(self):
        """
        Show an info message when bootstrap installing pip has finished successfully.
        """
        msg_txt = (
            "Successfully installed pip, setuptools, and wheel.\n"
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
                logger.debug(f"Saving '{save_path}'...")

                # write 'pip freeze' output to selected file
                self.manager = PipManager(active_dir, venv)
                self.manager.run_pip(creator.cmds[2], [">", save_path])

                # show an info message
                message_txt = (f"Saved requirements in \n{save_path}")
                QMessageBox.information(self, "Saved", message_txt)


    def generate_scripts(self, event):
        """
        Generates an activate and deactive script in the chosen
        project directory for the venv selected in the table.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if os.name == 'nt':
            ext = ".bat"
            fs_sep = "\\"
            scripts_dir = 'Scripts'
            prefix = ""
            eol = "\r\n"
        else:
            ext = ""
            fs_sep = "/"
            scripts_dir = 'bin'
            prefix = "source "
            
            eol = "\n"

        project_dir = os.getenv("PYTHON_DEV_PROJECTS")
        if not project_dir:
            project_dir = os.path.expanduser("~/")

        script_file_1 = f"start_venv{ext}"
        script_file_2 = f"stop_venv{ext}"
        script_file_1_contents = f"{prefix}{venv_dir}{fs_sep}{scripts_dir}{fs_sep}activate{ext}{eol}"
        if os.name == 'nt':
            script_file_2_contents = f"{prefix}{venv_dir}{fs_sep}{scripts_dir}{fs_sep}deactivate{ext}{eol}"
        else:
            script_file_2_contents = f"deactivate{eol}"

        scripts = list()
        scripts.append((script_file_1, script_file_1_contents))
        scripts.append((script_file_2, script_file_2_contents))

        dialog = QFileDialog(self, 'Choose a Project Directory to Generate Venv Access Files', project_dir, filter=None)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec_():
            project_dir = dialog.selectedFiles()[0]
            logger.debug(f"Project Dir: {project_dir}")

            if os.path.exists(project_dir):
                for script_file, script_file_contents in scripts:
                    script_file = os.path.join(project_dir, script_file)
                    logger.debug(f"Script File to write: {script_file}")
                    with open(script_file, "w") as sf:
                        sf.write(script_file_contents)
                        logger.debug(f"Script contents: {script_file_contents}")

                # Update the venvi config
                vcm = VenvConfigMgr(active_dir, venv)
                if vcm.read():
                    logger.debug(f"Dev Project dir written to venvi cfg file: '{project_dir}'")
                    # Only append if project_dir is not in the projects directory list
                    check_set = set(vcm.vc.projects)
                    if project_dir in check_set:
                        logger.info(f"Project Dir: '{project_dir}' already in Project Directory List...")
                    else:
                        vcm.vc.projects.append(project_dir)
                    vcm.write()
                else:
                    logger.debug("No valid venvi config file found")

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

            if os.name == 'nt':
                self.manager = PipManager(active_dir, f"{venv}")
            else:
                self.manager = PipManager(active_dir, f"'{venv}'")
            
            # We have to do the connect BEFORE we run_pip on Windows 10,
            # else the console never is displayed. However, this works
            # fine as originally coded on Ubuntu.
            #self.manager.run_pip(creator.cmds[style])

            #self.manager.started.connect(self.console.exec_)
            self.manager.started.connect(self.raise_console_dialog)

            self.manager.run_pip(creator.cmds[style])

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.console_window.clear()

    def list_projects(self, event, style):
        """
        Open console dialog and list the development projects that have
        had venv access scripts created in their project root dir. The argument
        `style` controls which style the output should have: `style=1` for
        `pip list`, `style=2` for `pip freeze` and style=3 for a dependency
        output via `pipdeptree`.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()

        self.projects = ProjectsDialog(venv, self)

        vcm = VenvConfigMgr(active_dir, venv)
        if vcm.read():
            logger.debug("Read a valid venvipy cfg file")
            for projdir in vcm.vc.projects:
                logger.debug(f"Proj Dir: '{projdir}'")
                self.projects.update(projdir)
        else:
            logger.debug("No valid venvipy cfg file to read")
            self.projects.update(f"There are no dev project references to venv {venv}")

        self.projects.exec_()

    def raise_console_dialog(self):
        """
        On Windows 10, if we raise the console via self.console.exec_ as originally
        coded (and which does work on Ubuntu), the self.manager.textChanged.connect() 
        slots are not called eventhough the corresponding emits are happening in the 
        self.manager object. This method should work on both Windows & Ubuntu since
        it is doing essentially what the exec_ call does interms of displaying a modal
        dialog while not inhibiting the textChanged connect slots from being invoked.
        """
        self.console.setModal(True)
        self.console.show()

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
        if os.name == 'nt':
            pipdeptree_loc = "Scripts"
            pipdeptree_exe = "pipdeptree.exe"
        else:
            pipdeptree_loc = "bin"
            pipdeptree_exe = "pipdeptree"
        pipdeptree_binary = os.path.join(active_dir, venv, pipdeptree_loc, pipdeptree_exe)
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
                    logger.debug("Installing pipdeptree...")

                    self.manager = PipManager(active_dir, venv)
                    self.manager.started.connect(self.progress_bar.exec_)
                    self.manager.finished.connect(self.progress_bar.close)
                    self.manager.run_pip(
                        creator.cmds[0], [creator.opts[0], "pipdeptree"]
                    )
                    #self.manager.started.connect(self.progress_bar.exec_)
                    #self.manager.finished.connect(self.progress_bar.close)
                    self.manager.process_stop()
                    self.list_packages(event, style)


    def open_venv_dir(self, event):
        """Open the selected venv directory.
        """
        active_dir = get_data.get_active_dir_str()
        venv = self.get_selected_item()
        venv_dir = os.path.join(active_dir, venv)

        if os.path.isdir(venv_dir):
            if os.name == 'nt':
                starting_dir = f"{venv_dir}"
                _ = QFileDialog.getOpenFileName(
                    self,
                    f"Virtual Env Directory for {venv}",
                    starting_dir
                )
            else:
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
                logger.debug(f"Successfully deleted '{venv_path}'")
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

            logger.debug(f"Removed '{item}' from database")
            self.drop_item.emit()
