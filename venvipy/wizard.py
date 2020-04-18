# -*- coding: utf-8 -*-
"""
This module contains the wizard for creating
and setting up virtual environments.
"""
from functools import partial
import shutil
import sys
import os

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt5.QtGui import (
    QIcon, QStandardItemModel, QStandardItem, QFontMetrics, QPixmap, QFont
)
from PyQt5.QtWidgets import (
    QApplication, QProgressBar, QGridLayout, QLabel, QFileDialog, QHBoxLayout,
    QVBoxLayout, QDialog, QWizard, QWizardPage, QToolButton, QComboBox,
    QCheckBox, QLineEdit, QGroupBox, QTableView, QAbstractItemView,
    QPushButton, QTextEdit, QMessageBox, QHeaderView, QDesktopWidget
)
import venvipy_rc

from dialogs import ProgBarDialog, ConsoleDialog
from manage_pip import PipManager
from tables import ResultsTable
from get_data import (
    get_module_infos,
    get_active_dir,
    get_active_dir_str,
    get_python_installs
)
from creator import (
    CreationWorker,
    create_venv,
    create_requirements,
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

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Venv Wizard")
        self.resize(680, 510)
        self.center()
        self.setWindowIcon(QIcon(":/img/python.png"))

        self.setStyleSheet(
            """
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

        self.basicSettings = BasicSettings()
        self.basicSettingsId = self.addPage(self.basicSettings)

        self.installModules = InstallModules()
        self.installModulesId = self.addPage(self.installModules)

        self.finalPage = FinalPage()
        self.finalPageId = self.addPage(self.finalPage)

        self.cancel_button = self.button(self.CancelButton)
        self.cancel_button.clicked.connect(self.force_exit)


    def nextId(self):
        # process the flow only if the current page is BasicSettings()
        if self.currentId() != self.basicSettingsId:
            return super().nextId()

        if self.basicSettings.withPipCBox.isChecked():
            return self.installModulesId

        return self.finalPageId


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
        if self.basicSettings.thread.isRunning():
            self.basicSettings.thread.exit()



class BasicSettings(QWizardPage):
    """
    Basic settings of the virtual environment to create.
    """
    def __init__(self):
        super().__init__()

        folder_icon = QIcon.fromTheme("folder")

        self.setTitle("Basic Settings")
        self.setSubTitle("This wizard will help you to create and set up "
                         "a virtual environment for Python. ")


        #]===================================================================[#
        #] THREADS  [#=======================================================[#
        #]===================================================================[#

        self.thread = QThread(self)
        self.thread.start()

        self.progressBar = ProgBarDialog()

        self.m_install_venv_worker = CreationWorker()
        self.m_install_venv_worker.moveToThread(self.thread)

        # started
        self.m_install_venv_worker.started.connect(self.progressBar.exec_)

        # updated
        self.m_install_venv_worker.updatePipMsg.connect(self.update_pip_msg)

        # finished
        self.m_install_venv_worker.finished.connect(self.progressBar.close)
        self.m_install_venv_worker.finished.connect(self.finish_info)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        interpreterLabel = QLabel("&Interpreter:")
        self.interprComboBox = QComboBox()
        interpreterLabel.setBuddy(self.interprComboBox)

        # add the found Python versions to combobox
        self.interprComboBox.addItem("---")
        for info in get_python_installs():
            self.interprComboBox.addItem(
                f"{info.py_version}  ->  {info.py_path}", info.py_path
            )

        venvNameLabel = QLabel("Venv &name:")
        self.venvNameLineEdit = QLineEdit()
        venvNameLabel.setBuddy(self.venvNameLineEdit)

        venvLocationLabel = QLabel("&Location:")
        self.venvLocationLineEdit = QLineEdit()
        venvLocationLabel.setBuddy(self.venvLocationLineEdit)

        self.selectDirToolButton = QToolButton(
            icon=folder_icon,
            toolTip="Browse",
            clicked=self.select_dir
        )
        self.selectDirToolButton.setFixedSize(26, 27)

        requirementsLabel = QLabel("Requirements &fiile:")
        self.requirementsLineEdit = QLineEdit()
        requirementsLabel.setBuddy(self.requirementsLineEdit)

        self.selectFileToolButton = QToolButton(
            icon=folder_icon,
            toolTip="Browse",
            clicked=self.select_file
        )
        self.selectFileToolButton.setFixedSize(26, 27)

        placeHolder = QLabel()

        # options groupbox
        groupBox = QGroupBox("Options")

        self.withPipCBox = QCheckBox(
            "Install and update &Pip",
            checked=True,
            stateChanged=self.with_pip
        )
        self.sitePackagesCBox = QCheckBox(
            "&Make system (global) site-packages dir available to venv"
        )
        self.symlinksCBox = QCheckBox(
            "Attempt to &symlink rather than copy files into venv"
        )

        # register fields
        self.registerField("interprComboBox*", self.interprComboBox)
        self.registerField("pythonVers", self.interprComboBox, "currentText")
        self.registerField("pythonPath", self.interprComboBox, "currentData")
        self.registerField("venvName*", self.venvNameLineEdit)
        self.registerField("venvLocation*", self.venvLocationLineEdit)
        self.registerField("withPip", self.withPipCBox)
        self.registerField("sitePackages", self.sitePackagesCBox)
        self.registerField("symlinks", self.symlinksCBox)
        self.registerField("requirements", self.requirementsLineEdit)

        # grid layout
        gridLayout = QGridLayout()
        gridLayout.addWidget(interpreterLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.interprComboBox, 0, 1, 1, 2)

        gridLayout.addWidget(venvNameLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.venvNameLineEdit, 1, 1, 1, 2)

        gridLayout.addWidget(venvLocationLabel, 2, 0, 1, 1)
        gridLayout.addWidget(self.venvLocationLineEdit, 2, 1, 1, 1)
        gridLayout.addWidget(self.selectDirToolButton, 2, 2, 1, 1)

        gridLayout.addWidget(requirementsLabel, 3, 0, 1, 1)
        gridLayout.addWidget(self.requirementsLineEdit, 3, 1, 1, 1)
        gridLayout.addWidget(self.selectFileToolButton, 3, 2, 1, 1)

        gridLayout.addWidget(placeHolder, 4, 0, 1, 2)
        gridLayout.addWidget(groupBox, 5, 0, 1, 3)
        self.setLayout(gridLayout)

        # options groupbox
        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(self.withPipCBox)
        groupBoxLayout.addWidget(self.sitePackagesCBox)
        groupBoxLayout.addWidget(self.symlinksCBox)
        groupBox.setLayout(groupBoxLayout)


    def initializePage(self):
        # connect 'next' button to self.execute_venv_create()
        next_button = self.wizard().button(QWizard.NextButton)
        next_button.disconnect()
        next_button.clicked.connect(self.execute_venv_create)


    def select_dir(self):
        """
        Specify path where to create the virtual environment.
        """
        folderName = QFileDialog.getExistingDirectory()
        self.venvLocationLineEdit.setText(folderName)


    def select_file(self):
        """
        Specify the requirements file to use
        to clone the virtual environment.
        """
        fileName = QFileDialog.getOpenFileName()
        self.requirementsLineEdit.setText(fileName[0])


    def with_pip(self, state):
        """
        Enable input line for specifying a requirements file
        only if `self.withPipCBox` is checked, else disable it.
        """
        if self.withPipCBox.isChecked():
            self.requirementsLineEdit.setEnabled(True)
            self.selectFileToolButton.setEnabled(True)
        else:
            self.requirementsLineEdit.setEnabled(False)
            self.selectFileToolButton.setEnabled(False)


    def execute_venv_create(self):
        """
        Execute the creation process.
        """
        self.combobox = self.field("interprComboBox")
        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")
        self.withPip = self.field("withPip")
        self.sitePackages = self.field("sitePackages")
        self.symlinks = self.field("symlinks")
        self.requirements = self.field("requirements")

        if self.combobox and self.venvName and self.venvLocation:
            # format the text shown in progress bar window title
            if self.pythonVers[12] == " ":
                version = self.pythonVers[:12]  # stable releases
            else:
                version = self.pythonVers[:16]  # pre-releases

            # show python version in progress bar window title
            self.progressBar.setWindowTitle(f"Using {version}")
            self.progressBar.statusLabel.setText(
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
            self.pythonPath,
            self.venvName,
            self.venvLocation,
            self.withPip,
            self.sitePackages,
            self.symlinks
        )

        wrapper = partial(self.m_install_venv_worker.install_venv, args)
        QTimer.singleShot(0, wrapper)


    def update_pip_msg(self):
        """
        Set the text in status label to show that Pip is being updated.
        """
        self.progressBar.statusLabel.setText("Updating Pip...")


    def finish_info(self):
        """
        Show info message when the creation process has finished successfully.
        """
        default_msg = (
            f"Virtual environment created \nsuccessfully. \n\n"
            f"New Python {self.pythonVers[7:10]} executable in \n"
            f"'{self.venvLocation}/{self.venvName}/bin'. \n"
        )
        with_pip_msg = ("Installed Pip and Setuptools.\n")

        #print(
            #"[PROCESS]: Successfully created new virtual environment: "
            #f"'{self.venvLocation}/{self.venvName}'"
        #)

        if self.withPipCBox.isChecked():
            message_txt = default_msg + with_pip_msg
            #print("[PROCESS]: Installed pip, setuptools.")
        else:
            message_txt = default_msg

        QMessageBox.information(self, "Done", message_txt)

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

        gridLayout = QGridLayout(self)

        pkgNameLabel = QLabel("Module &name:")
        self.pkgNameLineEdit = QLineEdit()
        pkgNameLabel.setBuddy(self.pkgNameLineEdit)

        self.searchButton = QPushButton(
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
            contextTriggered=self.install_module  # signal
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

        gridLayout.addWidget(pkgNameLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.pkgNameLineEdit, 0, 1, 1, 1)
        gridLayout.addWidget(self.searchButton, 0, 2, 1, 1)
        gridLayout.addWidget(resultsTable, 1, 0, 1, 3)


    def initializePage(self):
        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")
        self.requirements = self.field("requirements")

        # clear all inputs and contents
        self.resultsModel.clear()
        self.pkgNameLineEdit.clear()
        self.pkgNameLineEdit.setFocus(True)

        # set text in column headers
        self.resultsModel.setHorizontalHeaderLabels(
            ["Name", "Version", "Description"]
        )

        # reconnect 'next' button to self.wizard().next()
        self.next_button = self.wizard().button(QWizard.NextButton)
        self.next_button.disconnect()
        self.next_button.clicked.connect(self.wizard().next)

        # remove focus from 'next' button
        QTimer.singleShot(0, lambda: self.next_button.setDefault(False))

        # set focus on 'search' button
        QTimer.singleShot(0, lambda: self.searchButton.setDefault(True))

        # disable 'back' button
        back_button = self.wizard().button(QWizard.BackButton)
        QTimer.singleShot(0, lambda: back_button.setEnabled(False))

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

        self.manager = PipManager(self.venvLocation, f"'{self.venvName}'")
        self.console = ConsoleDialog()

        self.console.setWindowTitle("Cloning environment")

        # open the console when recieving signal from manager
        self.manager.started.connect(self.console.exec_)

        # start installing modules from requirements file
        #print("[PROCESS]: Installing Modules from requirements...")
        #print(f"[PROCESS]: Using file '{self.requirements}'")
        self.manager.run_pip(cmds[0], [opts[1], f"'{self.requirements}'"])

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # show info dialog
        #print("[ERROR]: Could not install from requirements")
        self.manager.failed.connect(self.console.finish_fail)
        self.manager.failed.connect(self.console.close)

        #print("[PROCESS]: Environment cloned successfully")
        #self.manager.success.connect(self.console.finish_success)
        #self.manager.success.connect(self.console.close)

        # clear the contents when closing console
        if self.console.close:
            self.console.consoleWindow.clear()

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
            #print(f"[PIP]: No matches for '{search_item}'")

            QMessageBox.information(self,
                "No result",
                f"No result matching '{search_item}'.\n"
            )


    def install_module(self):
        """
        Get the name of the double-clicked item from the results table
        view and ask user for confirmation before installing. If confirmed
        install the selected module into the created virtual environment,
        else abort.
        """
        indexes = self.selectionModel.selectedRows()
        for index in sorted(indexes):
            self.pkg = index.data()

        messageBoxConfirm = QMessageBox.question(self,
            "Confirm", f"Are you sure you want to install '{self.pkg}'?",
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if messageBoxConfirm == QMessageBox.Yes:
            self.manager = PipManager(self.venvLocation, f"'{self.venvName}'")
            self.console = ConsoleDialog()

            self.console.setWindowTitle("Installing")

            # open the console when recieving signal from manager
            self.manager.started.connect(self.console.exec_)

            #]===============================================================[#
            # TODO: provide some options here:
            #       * let the user decide whether to install packages with
            #         the "--upgrade" flag or not
            #       * let user specify a particular version to install
            #]===============================================================[#
            # start installing the selected module
            #print(f"[PROCESS]: Installing module '{self.pkg}'...")
            self.manager.run_pip(cmds[0], [opts[0], self.pkg])

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content when closing console
            if self.console.close:
                self.console.consoleWindow.clear()

                # clear search input line
                self.pkgNameLineEdit.clear()
                self.pkgNameLineEdit.setFocus(True)

                # connect 'next' button to self.save_requirements()
                self.next_button.disconnect()
                self.next_button.clicked.connect(self.save_requirements)


    def save_requirements(self):
        """
        Ask if they want to save the requirements of the
        created virtual environment.
        """
        self.setEnabled(False)

        messageBoxConfirm = QMessageBox.question(
            self,
            "Save requirements",
            "Do you want to generate a requirements?",
            QMessageBox.Yes | QMessageBox.No
        )

        if messageBoxConfirm == QMessageBox.Yes:
            active_dir = get_active_dir_str()
            save_file = QFileDialog.getSaveFileName(self, "Save requirements")
            save_path = save_file[0]

            if save_path != "":
                #print(f"[PROCESS]: Generating '{save_path}'...")
                manager = PipManager(active_dir, self.venvName)
                manager.run_pip(cmds[2], [">", save_path])

                message_txt = (f"Saved requirements in: \n{save_path}")
                QMessageBox.information(self, "Saved", message_txt)
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



if __name__ == "__main__":

    app = QApplication(sys.argv)
    wizard = VenvWizard()
    wizard.show()

    sys.exit(app.exec_())
