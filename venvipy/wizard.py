# -*- coding: utf-8 -*-
"""
This module contains the wizard for creating
and setting up virtual environments.
"""
import sys
import os
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
    QHeaderView,
    QDesktopWidget
)
import venvipy_rc  # pylint: disable=unused-import

from dialogs import ProgBarDialog, ConsoleDialog
from manage_pip import PipManager
from tables import ResultsTable
from get_data import (
    get_module_infos,
    get_python_installs,
    get_python_version
)
from creator import (
    CreationWorker,
    fix_requirements,
    random_zen_line,
    cmds,
    opts
)



#]===========================================================================[#
#] WIZARD [#=================================================================[#
#]===========================================================================[#

class VenvWizard(QWizard):
    """
    Wizard for creating and setting up a virtual environment.
    """
    refresh = pyqtSignal()
    update_table = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Venv Wizard")
        self.resize(680, 510)
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

        self.install_modules = InstallModules()
        self.install_modules_id = self.addPage(self.install_modules)

        self.final_page = FinalPage()
        self.final_page_id = self.addPage(self.final_page)

        self.cancel_button = self.button(self.CancelButton)
        self.cancel_button.clicked.connect(self.force_exit)


    def nextId(self):
        # process the flow only if the current page is BasicSettings()
        if self.currentId() != self.basic_settings_id:
            return super().nextId()

        if self.basic_settings.with_pip_check_box.isChecked():
            return self.install_modules_id

        return self.final_page_id


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def force_exit(self):
        """
        Stop the thread, then close the wizard.
        """
        if self.basic_settings.thread.isRunning():
            self.basic_settings.thread.exit()



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
        self.m_install_venv_worker.updatePipMsg.connect(self.update_pip_msg)

        # finished
        self.m_install_venv_worker.finished.connect(self.progress_bar.close)
        self.m_install_venv_worker.finished.connect(self.finish_info)


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

        venv_location_label = QLabel("&Location:")
        self.venv_location_line = QLineEdit()
        venv_location_label.setBuddy(self.venv_location_line)

        self.select_dir_button = QToolButton(
            icon=folder_icon,
            toolTip="Select venv directory",
            clicked=self.select_dir
        )
        self.select_dir_button.setFixedSize(26, 27)

        requirements_label = QLabel("Requirements &fiile:")
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
        self.site_pkgs_check_box = QCheckBox(
            "&Make system (global) site-packages dir available to venv"
        )
        self.symlinks_check_box = QCheckBox(
            "Attempt to &symlink rather than copy files into venv"
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
        self.registerField("venv_name*", self.venv_name_line)
        self.registerField("venv_location*", self.venv_location_line)
        self.registerField("with_pip", self.with_pip_check_box)
        self.registerField("site_pkgs", self.site_pkgs_check_box)
        self.registerField("symlinks", self.symlinks_check_box)
        self.registerField("requirements", self.requirements_line)

        # grid layout
        grid_layout = QGridLayout()
        grid_layout.addWidget(interpreter_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.interpreter_combo_box, 0, 1, 1, 1)
        grid_layout.addWidget(self.select_python_button, 0, 2, 1, 1)

        grid_layout.addWidget(venv_name_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.venv_name_line, 1, 1, 1, 1)

        grid_layout.addWidget(venv_location_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.venv_location_line, 2, 1, 1, 1)
        grid_layout.addWidget(self.select_dir_button, 2, 2, 1, 1)

        grid_layout.addWidget(requirements_label, 3, 0, 1, 1)
        grid_layout.addWidget(self.requirements_line, 3, 1, 1, 1)
        grid_layout.addWidget(self.select_file_button, 3, 2, 1, 1)

        grid_layout.addWidget(place_holder, 4, 0, 1, 2)
        grid_layout.addWidget(group_box, 5, 0, 1, 3)
        self.setLayout(grid_layout)

        # options group box
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.with_pip_check_box)
        group_box_layout.addWidget(self.site_pkgs_check_box)
        group_box_layout.addWidget(self.symlinks_check_box)
        group_box.setLayout(group_box_layout)


    def initializePage(self):
        # connect 'next' button to self.execute_venv_create()
        next_button = self.wizard().button(QWizard.NextButton)
        next_button.disconnect()
        next_button.clicked.connect(self.execute_venv_create)


    def pop_combo_box(self):
        """
        Add the found Python versions to combo box
        """
        for info in get_python_installs():
            self.interpreter_combo_box.addItem(
                f"{info.py_version}  ->  {info.py_path}", info.py_path
            )


    def select_python(self):
        """
        Specify path to a custom interpreter.
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Select Python Interpreter",
            "/usr/local/bin",
            "Python binary (\
                python3.3 python3.4 python3.5 python3.6 \
                python3.7 python3.8 python3.9 \
            )"
        )
        bin_file = file_name[0]

        if bin_file != "":
            custom_version = get_python_version(bin_file)
            self.interpreter_combo_box.addItem(
                f"{custom_version}  ->  {bin_file}", bin_file
            )
        # transmit bin_file to pop_interpreter_table() in MainWindow
        self.wizard().update_table.emit(bin_file)
        return bin_file


    def select_dir(self):
        """
        Specify path where to create the virtual environment.
        """
        folder_name = QFileDialog.getExistingDirectory()
        self.venv_location_line.setText(folder_name)


    def select_file(self):
        """
        Specify the requirements file to use
        to clone the virtual environment.
        """
        file_name = QFileDialog.getOpenFileName()
        self.requirements_line.setText(file_name[0])


    def pip_enabled(self, state):
        """
        Enable input line for specifying a requirements file
        only if `self.with_pip_check_box` is checked, else disable it.
        """
        if self.with_pip_check_box.isChecked():
            self.requirements_line.setEnabled(True)
            self.select_file_button.setEnabled(True)
        else:
            self.requirements_line.setEnabled(False)
            self.select_file_button.setEnabled(False)


    def execute_venv_create(self):
        """
        Execute the creation process.
        """
        self.combo_box = self.field("interpreter_combo_box")
        self.python_version = self.field("python_version")
        self.python_path = self.field("python_path")
        self.venv_name = self.field("venv_name")
        self.venv_location = self.field("venv_location")
        self.with_pip = self.field("with_pip")
        self.site_pkgs = self.field("site_pkgs")
        self.symlinks = self.field("symlinks")
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

            # disable page during create process
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
            self.site_pkgs,
            self.symlinks
        )

        wrapper = partial(self.m_install_venv_worker.install_venv, args)
        QTimer.singleShot(0, wrapper)


    def update_pip_msg(self):
        """
        Set the text in status label to show that Pip is being updated.
        """
        self.progress_bar.status_label.setText("Updating Pip...")


    def finish_info(self):
        """
        Show info message when the creation process has finished successfully.
        """
        default_msg = (
            f"Virtual environment created \nsuccessfully. \n\n"
            f"New Python {self.python_version[7:10]} executable in \n"
            f"'{self.venv_location}/{self.venv_name}/bin'. \n"
        )
        with_pip_msg = ("Installed Pip and Setuptools.\n")

        print(
            "[PROCESS]: Successfully created new virtual environment: "
            f"'{self.venv_location}/{self.venv_name}'"
        )

        if self.with_pip_check_box.isChecked():
            msg_txt = default_msg + with_pip_msg
            print("[PROCESS]: Installed pip and setuptools")
        else:
            msg_txt = default_msg

        QMessageBox.information(self, "Done", msg_txt)

        self.wizard().next()
        self.setEnabled(True)



class InstallModules(QWizardPage):
    """
    Install modules via Pip into the created virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Install Modules")
        self.setSubTitle(
            "Specify the modules you want to install into the virtual "
            "environment. Right-click on the item you want to install. "
            "You can install as many modules as you need. When finished "
            "click next."
        )


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        grid_layout = QGridLayout(self)

        pkgNameLabel = QLabel("Module &name:")
        self.pkgNameLineEdit = QLineEdit()
        pkgNameLabel.setBuddy(self.pkgNameLineEdit)

        self.search_button = QPushButton(
            "&Search",
            clicked=self.pop_results_table
        )

        # results table
        resultsTable = ResultsTable(
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            doubleClicked=self.install_module,
            context_triggered=self.install_module  # signal
        )

        # adjust vertical headers
        v_Header = resultsTable.verticalHeader()
        v_Header.setDefaultSectionSize(28)
        v_Header.hide()

        # adjust horizontal headers
        h_Header = resultsTable.horizontalHeader()
        h_Header.setDefaultAlignment(Qt.AlignLeft)
        h_Header.setDefaultSectionSize(120)
        h_Header.setStretchLastSection(True)
        h_Header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # item model
        self.resultsModel = QStandardItemModel(0, 2, self)
        resultsTable.setModel(self.resultsModel)

        # selection model
        self.selectionModel = resultsTable.selectionModel()

        grid_layout.addWidget(pkgNameLabel, 0, 0, 1, 1)
        grid_layout.addWidget(self.pkgNameLineEdit, 0, 1, 1, 1)
        grid_layout.addWidget(self.search_button, 0, 2, 1, 1)
        grid_layout.addWidget(resultsTable, 1, 0, 1, 3)


    def initializePage(self):
        self.python_version = self.field("python_version")
        self.python_path = self.field("python_path")
        self.venv_name = self.field("venv_name")
        self.venv_location = self.field("venv_location")
        self.requirements = self.field("requirements")

        # clear all inputs and contents
        self.resultsModel.clear()
        self.pkgNameLineEdit.clear()
        self.pkgNameLineEdit.setFocus(True)

        # set text in column headers
        self.resultsModel.setHorizontalHeaderLabels(
            ["Name", "Version", "Description"]
        )

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

        # run the installer if self.requirements holds a str
        if len(self.requirements) > 0:
            try:
                fix_requirements(self.requirements)
            except FileNotFoundError:
                pass  # the gui will show an error message
            self.install_requirements()


    def install_requirements(self):
        """
        Install the modules from the specified requirements file.
        """
        self.setEnabled(False)

        self.manager = PipManager(self.venv_location, f"'{self.venv_name}'")
        self.console = ConsoleDialog()

        self.console.setWindowTitle("Cloning environment")

        # open the console when recieving signal from manager
        self.manager.started.connect(self.console.exec_)

        # start installing modules from requirements file
        print("[PROCESS]: Installing Modules from requirements...")
        print(f"[PROCESS]: Using file '{self.requirements}'")
        self.manager.run_pip(cmds[0], [opts[1], f"'{self.requirements}'"])

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # show info dialog
        self.manager.failed.connect(self.console.finish_fail)
        self.manager.failed.connect(self.console.close)

        # clear the contents when closing console
        if self.console.close:
            self.console.console_window.clear()

        self.setEnabled(True)


    def pop_results_table(self):
        """
        Refresh the results table.
        """
        search_item = self.pkgNameLineEdit.text()

        self.resultsModel.setRowCount(0)

        for info in get_module_infos(search_item):
            self.resultsModel.insertRow(0)

            for i, text in enumerate(
                (info.mod_name, info.mod_version, info.mod_summary)
            ):
                self.resultsModel.setItem(0, i, QStandardItem(text))

        if not get_module_infos(search_item):
            print(f"[PIP]: No matches for '{search_item}'")

            QMessageBox.information(self,
                "No result",
                f"No result matching '{search_item}'.\n"
            )


    def install_module(self):
        """
        Get the name of the selected item from the results table. Ask user
        for confirmation before installing. If user confirmes, install the
        selected module into the created virtual environment, else abort.
        """
        indexes = self.selectionModel.selectedRows()
        for index in sorted(indexes):
            self.pkg = index.data()

        msg_box_question = QMessageBox.question(self,
            "Confirm", f"Are you sure you want to install '{self.pkg}'?",
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if msg_box_question == QMessageBox.Yes:
            self.manager = PipManager(self.venv_location, f"'{self.venv_name}'")
            self.console = ConsoleDialog()

            self.console.setWindowTitle("Installing")

            # open the console when recieving signal from manager
            self.manager.started.connect(self.console.exec_)

            # start installing the selected module
            print(f"[PROCESS]: Installing module '{self.pkg}'...")
            self.manager.run_pip(cmds[0], [opts[0], self.pkg])

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content when closing console
            if self.console.close:
                self.console.console_window.clear()

                # clear search input line
                self.pkgNameLineEdit.clear()
                self.pkgNameLineEdit.setFocus(True)


    def save_requirements(self):
        """
        Ask if they want to save the requirements of the
        created virtual environment.
        """
        self.setEnabled(False)

        msg_box_question = QMessageBox.question(
            self,
            "Save requirements",
            "Do you want to generate a requirements?",
            QMessageBox.Yes | QMessageBox.No
        )

        if msg_box_question == QMessageBox.Yes:
            venv_dir = os.path.join(self.venv_location, self.venv_name)
            save_file = QFileDialog.getSaveFileName(
                self,
                "Save requirements",
                directory=f"{venv_dir}/requirements.txt"
            )
            save_path = save_file[0]

            if save_path != "":
                print(f"[PROCESS]: Generating '{save_path}'...")
                self.manager = PipManager(self.venv_location, self.venv_name)
                self.manager.run_pip(cmds[2], [">", save_path])

                msg_txt = (f"Saved requirements in: \n{save_path}")
                QMessageBox.information(self, "Saved", msg_txt)
                self.wizard().next()
        else:
            self.wizard().next()

        self.setEnabled(True)



class FinalPage(QWizardPage):
    """
    The last page.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Finished")
        self.setSubTitle(
            "All Tasks have been completed successfully. Click Finish "
            "to close the wizard and return back to the main menu."
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
        self.zen_line.setText(random_zen_line())


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

        # call update_zen_line to get a different line every new session
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
    main()
