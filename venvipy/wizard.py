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
This module contains the wizard for creating
and setting up virtual environments.
"""
import sys
import os
import csv
import logging
from functools import partial
from pathlib import Path

# need to set the correct cwd
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
os.chdir(CURRENT_DIR)

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import (
    QIcon,
    QStandardItemModel,
    QStandardItem,
    QPixmap,
    QFont
)
from PyQt5.QtWidgets import (
    QStyle,
    QApplication,
    QGridLayout,
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWizard,
    QWizardPage,
    QToolButton,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QGroupBox,
    QAbstractItemView,
    QPushButton,
    QMessageBox,
    QDesktopWidget
)

import venvipy_rc  # pylint: disable=unused-import
import get_data
import creator
from dialogs import ProgBarDialog, ConsoleDialog
from pkg_installer import ResultsTable
from creator import CreationWorker
from manage_pip import PipManager


logger = logging.getLogger(__name__)



#]===========================================================================[#
#] WIZARD [#=================================================================[#
#]===========================================================================[#

class VenvWizard(QWizard):
    """
    Wizard for creating and setting up a virtual environment.
    """
    refresh = pyqtSignal()
    update_table = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VenviPy - Venv Wizard")
        self.resize(850, 625)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))

        self.setStyleSheet(
            """
            QMenu {
                background-color: rgb(47, 52, 63);
                color: rgb(210, 210, 210)
            }

            QMenu::item::selected {
                background-color: rgb(72, 72, 82)
            }

            QToolTip {
                background-color: rgb(47, 52, 63);
                border: rgb(47, 52, 63);
                color: rgb(210, 210, 210);
                padding: 1px;
                opacity: 325
            }

            QTableView {
                gridline-color: rgb(230, 230, 230)
            }

            QTableView::item {
                selection-background-color: rgb(120, 120, 130);
                selection-color: rgb(255, 255, 255)
            }
            """
        )

        self.basic_settings = BasicSettings()
        self.basic_settings_id = self.addPage(self.basic_settings)

        self.install_packages = InstallPackages()
        self.install_packages_id = self.addPage(self.install_packages)

        self.final_page = FinalPage()
        self.final_page_id = self.addPage(self.final_page)

        self.cancel_button = self.button(self.CancelButton)
        self.cancel_button.clicked.connect(self.force_exit)


    def nextId(self):
        # process the flow only if the current page is BasicSettings()
        if self.currentId() != self.basic_settings_id:
            return super().nextId()

        # go to InstallPackages() page only if pip has been selected
        if self.basic_settings.with_pip_check_box.isChecked():
            return self.install_packages_id

        return self.final_page_id


    def center(self):
        """Center window.
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def force_exit(self):
        """
        Stop the thread, then close the wizard.
        """
        if self.basic_settings.thread.isRunning():
            self.basic_settings.thread.quit()
            self.basic_settings.thread.wait()


class BasicSettings(QWizardPage):
    """
    Basic settings of the virtual environment to create.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Basic Settings")
        self.setSubTitle("This wizard will help you to create and set up "
                         "a virtual environment for Python. ")

        folder_icon = QIcon(
            self.style().standardIcon(QStyle.SP_DirOpenIcon)
        )
        file_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogContentsView)
        )

        #]===================================================================[#
        #] THREAD [#=========================================================[#
        #]===================================================================[#

        self.thread = QThread(self)
        self.thread.start()

        self.progress_bar = ProgBarDialog()

        self.m_install_venv_worker = CreationWorker()
        self.m_install_venv_worker.moveToThread(self.thread)

        # started
        self.m_install_venv_worker.started.connect(self.progress_bar.exec_)

        # updated
        self.m_install_venv_worker.updating_pip.connect(self.update_pip_msg)
        self.m_install_venv_worker.updating_pip.connect(
            lambda: logger.debug("Updating pip...")
        )
        self.m_install_venv_worker.installing_wheel.connect(
            self.install_wheel_msg
        )
        self.m_install_venv_worker.installing_wheel.connect(
            lambda: logger.debug("Installing wheel...")
        )

        # finished
        self.m_install_venv_worker.finished.connect(self.progress_bar.close)
        self.m_install_venv_worker.finished.connect(self.finish_info)

        # perform a proper stop using quit() and wait()
        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.wait)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        interpreter_label = QLabel("&Interpreter:")
        self.interpreter_combo_box = QComboBox()
        self.interpreter_combo_box.addItem("---")
        interpreter_label.setBuddy(self.interpreter_combo_box)

        self.select_python_button = QToolButton(
            icon=QIcon(":/img/python.png"),
            toolTip="Add custom interpreter",
            clicked=self.select_python
        )
        self.select_python_button.setFixedSize(26, 27)

        venv_name_label = QLabel("Venv &name:")
        self.venv_name_line = QLineEdit()
        venv_name_label.setBuddy(self.venv_name_line)

        comment_label = QLabel("&Description:")
        self.comment_line = QLineEdit()
        comment_label.setBuddy(self.comment_line)

        venv_location_label = QLabel("&Location:")
        self.venv_location_line = QLineEdit()
        venv_location_label.setBuddy(self.venv_location_line)

        self.select_dir_button = QToolButton(
            icon=folder_icon,
            toolTip="Select venv directory",
            clicked=self.select_dir
        )
        self.select_dir_button.setFixedSize(26, 27)

        requirements_label = QLabel("Requirements &file:")
        self.requirements_line = QLineEdit()
        requirements_label.setBuddy(self.requirements_line)

        self.select_file_button = QToolButton(
            icon=file_icon,
            toolTip="Select requirements",
            clicked=self.select_file
        )
        self.select_file_button.setFixedSize(26, 27)

        place_holder = QLabel()

        # options group box
        group_box = QGroupBox("Options")

        self.with_pip_check_box = QCheckBox(
            "Install and update &Pip",
            checked=True,
            stateChanged=self.pip_enabled
        )
        self.with_wheel_check_box = QCheckBox(
            "Install &Wheel",
            checked=True
        )
        self.site_pkgs_check_box = QCheckBox(
            "&Make system (global) site-packages available to venv"
        )

        # register fields
        self.registerField(
            "interpreter_combo_box*",
            self.interpreter_combo_box
        )
        self.registerField(
            "python_version",
            self.interpreter_combo_box,
            "currentText"
        )
        self.registerField(
            "python_path",
            self.interpreter_combo_box,
            "currentData"
        )
        self.registerField(
            "venv_name*",
            self.venv_name_line
        )
        self.registerField(
            "venv_location*",
            self.venv_location_line
        )
        self.registerField(
            "with_pip",
            self.with_pip_check_box
        )
        self.registerField(
            "with_wheel",
            self.with_wheel_check_box
        )
        self.registerField(
            "site_pkgs",
            self.site_pkgs_check_box
        )
        self.registerField(
            "requirements",
            self.requirements_line
        )

        # grid layout
        grid_layout = QGridLayout()
        grid_layout.addWidget(interpreter_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.interpreter_combo_box, 0, 1, 1, 1)
        grid_layout.addWidget(self.select_python_button, 0, 2, 1, 1)

        grid_layout.addWidget(venv_name_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.venv_name_line, 1, 1, 1, 1)

        grid_layout.addWidget(comment_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.comment_line, 2, 1, 1, 1)

        grid_layout.addWidget(venv_location_label, 3, 0, 1, 1)
        grid_layout.addWidget(self.venv_location_line, 3, 1, 1, 1)
        grid_layout.addWidget(self.select_dir_button, 3, 2, 1, 1)

        grid_layout.addWidget(requirements_label, 4, 0, 1, 1)
        grid_layout.addWidget(self.requirements_line, 4, 1, 1, 1)
        grid_layout.addWidget(self.select_file_button, 4, 2, 1, 1)

        grid_layout.addWidget(place_holder, 5, 0, 1, 2)
        grid_layout.addWidget(group_box, 6, 0, 1, 3)
        self.setLayout(grid_layout)

        # options group box
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.with_pip_check_box)
        group_box_layout.addWidget(self.with_wheel_check_box)
        group_box_layout.addWidget(self.site_pkgs_check_box)
        group_box.setLayout(group_box_layout)


    def initializePage(self):
        # connect 'next' button to self.execute_venv_create()
        next_button = self.wizard().button(QWizard.NextButton)
        next_button.disconnect()
        next_button.clicked.connect(self.execute_venv_create)

        # clear comment line
        self.comment_line.clear()


    def pop_combo_box(self):
        """Add the selected Python version to combo box.
        """
        get_data.ensure_dbfile()

        # clear combo box content
        self.interpreter_combo_box.clear()
        self.interpreter_combo_box.addItem("---")

        with open(get_data.DB_FILE, newline="", encoding="utf-8") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            for info in reader:
                self.interpreter_combo_box.addItem(
                    f'{info["PYTHON_VERSION"]}  ->  {info["PYTHON_PATH"]}',
                    info["PYTHON_PATH"]
                )


    def select_python(self):
        """Specify path to a custom interpreter.
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Select a Python interpreter",
            "/usr/local/bin",
            "Python 3.3+ binary (\
                python3.3 python3.4 python3.5 \
                python3.6 python3.7 python3.8 \
                python3.9 python3.10 python3.11 \
            )"
        )
        bin_file = file_name[0]

        if bin_file != "":
            get_data.add_python(bin_file)
            self.pop_combo_box()
            # also call pop_interpreter_table() method in venvi.MainWindow()
            self.wizard().update_table.emit()
            return bin_file
        return ""


    def select_dir(self):
        """Specify path where to create the virtual environment.
        """
        folder_name = QFileDialog.getExistingDirectory(
            self,
            "Select venv location",
            directory=get_data.get_active_dir_str()
        )
        self.venv_location_line.setText(folder_name)


    def select_file(self):
        """
        Specify the requirements file to install from.
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Select a requirements file"
        )
        self.requirements_line.setText(file_name[0])


    def pip_enabled(self):
        """
        Enable or disable input line for requirements
        and checkbox for installing wheel.
        """
        if self.with_pip_check_box.isChecked():
            self.requirements_line.setEnabled(True)
            self.select_file_button.setEnabled(True)
            self.with_wheel_check_box.setEnabled(True)
        else:
            self.requirements_line.setEnabled(False)
            self.select_file_button.setEnabled(False)
            self.with_wheel_check_box.setEnabled(False)


    def execute_venv_create(self):
        """Execute the creation process.
        """
        self.combo_box = self.field("interpreter_combo_box")
        self.python_version = self.field("python_version")
        self.python_path = self.field("python_path")
        self.venv_name = self.field("venv_name")
        self.venv_location = self.field("venv_location")
        self.with_pip = self.field("with_pip")
        self.with_wheel = self.field("with_wheel")
        self.site_pkgs = self.field("site_pkgs")
        self.requirements = self.field("requirements")

        if self.combo_box and self.venv_name and self.venv_location:
            # format the text shown in progress bar window title
            if self.python_version[12] == " ":
                version = self.python_version[:12]  # stable releases
            else:
                version = self.python_version[:16]  # pre-releases

            # show python version in progress bar window title
            self.progress_bar.setWindowTitle(f"Using {version}")
            self.progress_bar.status_label.setText(
                "Creating virtual environment..."
            )
            # run the create process
            self.create_process()
            self.setEnabled(False)


    def create_process(self):
        """
        Create the virtual environment.
        """
        args = (
            self.python_path,
            self.venv_name,
            self.venv_location,
            self.with_pip,
            self.with_wheel,
            self.site_pkgs
        )

        wrapper = partial(self.m_install_venv_worker.install_venv, args)
        QTimer.singleShot(0, wrapper)


    def update_pip_msg(self):
        """
        Set the text in status label to show that Pip is being updated.
        """
        self.progress_bar.status_label.setText("Updating Pip...")


    def install_wheel_msg(self):
        """
        Set the text in status label to show that Pip is being updated
        and Wheel is being installed.
        """
        self.progress_bar.status_label.setText(
            "Updating Pip and installing Wheel..."
        )


    def finish_info(self):
        """
        Save the description text and show an info message on finish.
        """
        comment = self.comment_line.text()
        venvipy_cfg = os.path.join(
            self.venv_location,
            self.venv_name,
            "venvipy.cfg"
        )
        creator.save_comment(venvipy_cfg, comment)

        cfg_file = os.path.join(
            self.venv_location, self.venv_name, "pyvenv.cfg"
        )
        binary_path = os.path.join(self.venv_location, self.venv_name, "bin")
        version = get_data.get_config(cfg_file, cfg="version")
        default_msg = (
            f"Virtual environment created \nsuccessfully. \n\n"
            f"New {version[:-2]} executable in \n"
            f"'{binary_path}'.         \n"
        )
        with_pip_msg = ("Installed Pip and Setuptools.\n")
        with_wheel_msg = ("Installed Pip, Setuptools and Wheel.\n")

        if self.with_wheel_check_box.isChecked():
            msg_txt = default_msg + with_wheel_msg
        elif self.with_pip_check_box.isChecked():
            msg_txt = default_msg + with_pip_msg
        else:
            msg_txt = default_msg

        QMessageBox.information(self, "Done", msg_txt)
        self.wizard().refresh.emit()  # refresh venv table in main menu
        self.wizard().next()
        self.setEnabled(True)



class InstallPackages(QWizardPage):
    """
    Install packages via Pip into the created virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Install Packages")
        self.setSubTitle(
            "Specify the packages you want to install into the virtual "
            "environment. For more options right-click on the item you "
            "want to install. "
            "You can install multiple packages. When finished "
            "click next."
        )

        self.console = ConsoleDialog()

        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        grid_layout = QGridLayout(self)

        pkg_name_label = QLabel("Package &name:")
        self.pkg_name_line = QLineEdit()
        pkg_name_label.setBuddy(self.pkg_name_line)

        self.search_button = QPushButton(
            "&Search",
            clicked=self.pop_results_table
        )

        # results table
        self.results_table = ResultsTable(
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            doubleClicked=self.install_package,
            context_triggered=self.install_package  # signal
        )

        # hide vertical header
        self.results_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header = self.results_table.horizontalHeader()
        h_header.setDefaultAlignment(Qt.AlignLeft)
        h_header.setStretchLastSection(True)

        # set table view model
        self.results_table_model = QStandardItemModel(0, 3, self)
        self.results_table.setModel(self.results_table_model)

        grid_layout.addWidget(pkg_name_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.pkg_name_line, 0, 1, 1, 1)
        grid_layout.addWidget(self.search_button, 0, 2, 1, 1)
        grid_layout.addWidget(self.results_table, 1, 0, 1, 3)


    def initializePage(self):
        self.python_version = self.field("python_version")
        self.python_path = self.field("python_path")
        self.venv_name = self.field("venv_name")
        self.venv_location = self.field("venv_location")
        self.requirements = self.field("requirements")

        # run the installer if self.requirements holds a str
        if len(self.requirements) > 0:
            try:
                creator.fix_requirements(self.requirements)
            except FileNotFoundError:
                pass  # the gui will show an error message
            self.install_requirements()

        # clear all inputs and contents
        self.results_table_model.clear()
        self.pkg_name_line.clear()
        self.pkg_name_line.setFocus(True)

        # set text in column headers
        self.results_table_model.setHorizontalHeaderLabels([
            "Name",
            "Version",
            "Release",
            "Description"
        ])

        # remove focus from 'next' button
        QTimer.singleShot(0, lambda: self.next_button.setDefault(False))

        # set focus on 'search' button
        QTimer.singleShot(0, lambda: self.search_button.setDefault(True))

        # disable 'back' button
        back_button = self.wizard().button(QWizard.BackButton)
        QTimer.singleShot(0, lambda: back_button.setEnabled(False))

        if self.wizard().basic_settings.with_pip_check_box.isChecked():
            # connect 'next' button to self.save_requirements()
            self.next_button = self.wizard().button(QWizard.NextButton)
            self.next_button.disconnect()
            self.next_button.clicked.connect(self.save_requirements)


    def install_requirements(self):
        """Install the packages from the specified requirements file.
        """
        self.setEnabled(False)

        self.console.setWindowTitle("Installing packages")
        logger.debug("Installing from requirements...")

        # open the console when recieving signal from manager
        self.manager = PipManager(self.venv_location, f"'{self.venv_name}'")
        self.manager.started.connect(self.console.exec_)

        # start installing packages from requirements file
        self.manager.run_pip(
            creator.cmds[0], [creator.opts[1], f"'{self.requirements}'"]
        )

        # display the updated output
        self.manager.text_changed.connect(self.console.update_status)

        # clear the contents when closing console
        if self.console.close:
            self.console.console_window.clear()

        self.setEnabled(True)


    def pop_results_table(self):
        """Refresh the results table.
        """
        # adjust column width
        self.results_table.setColumnWidth(0, 200)  # name
        self.results_table.setColumnWidth(1, 80)  # version
        self.results_table.setColumnWidth(2, 110)  # release date

        self.results_table_model.setRowCount(0)
        search_item = self.pkg_name_line.text()

        if len(search_item) >= 1:
            for info in get_data.get_package_infos(search_item):
                self.results_table_model.insertRow(0)

                for i, text in enumerate((
                    info.pkg_name,
                    info.pkg_version,
                    info.pkg_release_date,
                    info.pkg_summary
                )):
                    self.results_table_model.setItem(0, i, QStandardItem(text))

            if not get_data.get_package_infos(search_item):
                logger.debug(f"No matches for '{search_item}'")
                QMessageBox.information(
                    self,
                    "No results",
                    f"No results matching '{search_item}'.\n"
                )


    def install_package(self):
        """
        Get the name of the selected item from the results table. Then install
        the selected package into the created virtual environment.
        """
        indexes = self.results_table.selectionModel().selectedRows()
        for index in sorted(indexes):
            self.pkg = index.data()

        msg_box_question = QMessageBox.question(self,
            "Confirm", f"Are you sure you want to install '{self.pkg}'?",
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if msg_box_question == QMessageBox.Yes:
            self.console.setWindowTitle(f"Installing {self.pkg}")

            self.manager = PipManager(
                self.venv_location,
                f"'{self.venv_name}'"
            )
            # open the console when recieving signal from manager
            self.manager.started.connect(self.console.exec_)

            # start installing the selected package
            logger.debug(f"Installing '{self.pkg}'...")
            self.manager.run_pip(creator.cmds[0], [creator.opts[0], self.pkg])

            # display the updated output
            self.manager.text_changed.connect(self.console.update_status)

            # clear the content when closing console
            if self.console.close:
                self.console.console_window.clear()

                # clear search input line
                self.pkg_name_line.clear()
                self.pkg_name_line.setFocus(True)


    def save_requirements(self):
        """
        Ask if user want to save a requirements of the
        created virtual environment.
        """
        self.setEnabled(False)

        self.msg_box = QMessageBox(
            QMessageBox.Question,
            "Save requirements",
            "Do you want to generate a requirements?          ",
            QMessageBox.NoButton,
            self
        )
        yes_button = self.msg_box.addButton("&Yes", QMessageBox.YesRole)
        no_button = self.msg_box.addButton("&No", QMessageBox.NoRole)
        cancel_button = self.msg_box.addButton("&Cancel", QMessageBox.RejectRole)

        self.msg_box.exec_()

        if self.msg_box.clickedButton() == yes_button:
            venv_dir = os.path.join(self.venv_location, self.venv_name)
            save_file = QFileDialog.getSaveFileName(
                self,
                "Save requirements",
                directory=os.path.join(venv_dir, "requirements.txt")
            )
            save_path = save_file[0]

            if len(save_path) >= 1:
                self.manager = PipManager(self.venv_location, self.venv_name)
                self.manager.run_pip(creator.cmds[2], [">", save_path])
                logger.debug(f"Saved '{save_path}'")

                QMessageBox.information(
                    self,
                    "Saved",
                    f"Saved requirements in: \n{save_path}"
                )
                self.wizard().next()

        elif self.msg_box.clickedButton() == no_button:
            self.wizard().next()

        self.setEnabled(True)



class FinalPage(QWizardPage):
    """
    The last page. Shows a random line from
    the Zen of Python.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Finished")
        self.setSubTitle(
            "All tasks have been completed successfully. Click Finish "
            "to close the wizard."
        )

        h_layout = QHBoxLayout(self)
        v_layout = QVBoxLayout()

        logo = QLabel()
        pixmap = QPixmap(":/img/python.png")
        logo_scaled = pixmap.scaled(96, 96, Qt.KeepAspectRatio)
        logo.setPixmap(logo_scaled)

        self.zen_line = QLabel()
        self.zen_line.setFont(QFont("FreeSerif", pointSize=20))
        self.zen_line.setAlignment(Qt.AlignCenter)

        zen_author = QLabel()
        zen_author.setText(
            "From the "
            + "<a href='https://www.python.org/dev/peps/pep-0020/#the-zen-of-python'>Zen of Python</a>"
            + ", by Tim Peters"
        )
        zen_author.setFont(QFont("FreeSerif", pointSize=12, italic=True))
        zen_author.setOpenExternalLinks(True)

        v_layout.setContentsMargins(0, 20, 0, 0)

        v_layout.addWidget(logo, 1, Qt.AlignHCenter)
        v_layout.addWidget(self.zen_line, 2, Qt.AlignHCenter)
        v_layout.addWidget(zen_author, 3, Qt.AlignRight | Qt.AlignBottom)

        h_layout.addLayout(v_layout)


    def update_zen_line(self):
        """
        Set lebel text with a random line from the Zen of Python.
        """
        self.zen_line.setText(creator.random_zen_line())


    def initializePage(self):
        # reconnect 'next' button to self.wizard().next()
        next_button = self.wizard().button(QWizard.NextButton)
        next_button.disconnect()
        next_button.clicked.connect(self.wizard().next)

        # hide back button
        back_button = self.wizard().button(QWizard.BackButton)
        QTimer.singleShot(0, lambda: back_button.hide())

        # hide cancel button
        cancel_button = self.wizard().button(QWizard.CancelButton)
        QTimer.singleShot(0, lambda: cancel_button.hide())

        # reset wizard
        finish_button = self.wizard().button(QWizard.FinishButton)
        finish_button.clicked.connect(self.wizard().restart)

        if __name__ == "__main__":
            finish_button.clicked.connect(self.wizard().force_exit)

        # call update_zen_line() to get a different line on every new session
        self.wizard().refresh.connect(self.update_zen_line)
        self.wizard().refresh.emit()


def main():
    app = QApplication(sys.argv)
    os.system("clear")

    wizard = VenvWizard()
    wizard.basic_settings.pop_combo_box()
    wizard.show()

    sys.exit(app.exec_())



if __name__ == "__main__":

    LOG_FORMAT = "%(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    main()
