# -*- coding: utf-8 -*-
"""
This module contains the wizard for creating
and setting up virtual environments.
"""
from functools import partial
import shutil
import sys
import os

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt5.QtWidgets import (
    QApplication, QProgressBar, QGridLayout, QLabel, QFileDialog, QHBoxLayout,
    QVBoxLayout, QDialog, QWizard, QWizardPage, QToolButton, QComboBox,
    QCheckBox, QLineEdit, QGroupBox, QTableView, QAbstractItemView,
    QPushButton, QTextEdit, QMessageBox, QHeaderView, QDesktopWidget
)
import resources.venvipy_rc

from get_data import get_module_infos, get_venvs_default, get_python_installs
from dialogs import ProgBarDialog, ConsoleDialog
from manage_pip import PipManager
from creator import (
    CreationWorker, create_venv, create_requirements, cmds, opts
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

        self.summaryPage = SummaryPage()
        self.summaryPageId = self.addPage(self.summaryPage)


    def nextId(self):
        # process the flow only if the current page is BasicSettings()
        if self.currentId() != self.basicSettingsId:
            return super().nextId()

        if self.basicSettings.withPipCBox.isChecked():
            return self.installModulesId

        return self.summaryPageId


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



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

        thread = QThread(self)
        thread.start()

        self.progressBar = ProgBarDialog()

        self.m_install_venv_worker = CreationWorker()
        self.m_install_venv_worker.moveToThread(thread)

        # started
        self.m_install_venv_worker.started.connect(self.progressBar.exec_)

        # updated
        self.m_install_venv_worker.updatePipMsg.connect(self.update_pip_msg)

        # finished
        self.m_install_venv_worker.finished.connect(self.progressBar.close)
        self.m_install_venv_worker.finished.connect(self.show_finished_msg)


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

        placeHolder = QLabel()

        # options groupbox
        groupBox = QGroupBox("Options")

        self.withPipCBox = QCheckBox(
            "Install and update &Pip"
        )
        self.sitePackagesCBox = QCheckBox(
            "&Make system (global) site-packages dir available to venv"
        )
        self.symlinksCBox = QCheckBox(
            "Attempt to &symlink rather than copy files into venv"
        )
        #self.launchVenvCBox = QCheckBox(
            #"Launch a &terminal with activated venv after installation"
        #)

        # register fields
        self.registerField("interprComboBox*", self.interprComboBox)
        self.registerField("pythonVers", self.interprComboBox, "currentText")
        self.registerField("pythonPath", self.interprComboBox, "currentData")
        self.registerField("venvName*", self.venvNameLineEdit)
        self.registerField("venvLocation*", self.venvLocationLineEdit)
        self.registerField("withPip", self.withPipCBox)
        self.registerField("sitePackages", self.sitePackagesCBox)
        self.registerField("symlinks", self.symlinksCBox)
        #self.registerField("launchVenv", self.launchVenvCBox)

        # grid layout
        gridLayout = QGridLayout()
        gridLayout.addWidget(interpreterLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.interprComboBox, 0, 1, 1, 2)
        gridLayout.addWidget(venvNameLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.venvNameLineEdit, 1, 1, 1, 2)
        gridLayout.addWidget(venvLocationLabel, 2, 0, 1, 1)
        gridLayout.addWidget(self.venvLocationLineEdit, 2, 1, 1, 1)
        gridLayout.addWidget(self.selectDirToolButton, 2, 2, 1, 1)
        gridLayout.addWidget(placeHolder, 3, 0, 1, 2)
        gridLayout.addWidget(groupBox, 4, 0, 1, 3)
        self.setLayout(gridLayout)

        # options groupbox
        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(self.withPipCBox)
        groupBoxLayout.addWidget(self.sitePackagesCBox)
        groupBoxLayout.addWidget(self.symlinksCBox)
        #groupBoxLayout.addWidget(self.launchVenvCBox)
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
        #self.launchVenv = self.field("launchVenv")

        if self.combobox and self.venvName and self.venvLocation:
            if self.pythonVers[12] == " ":
                version = self.pythonVers[:12]  # stable releases
            else:
                version = self.pythonVers[:16]  # pre-releases

            # show python version in window title
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


    def show_finished_msg(self):
        """
        Show info message when the creation process has finished successfully.
        """
        default_msg = (
            f"Virtual environment created \nsuccessfully. \n\n"
            f"New Python {self.pythonVers[7:10]} executable in \n"
            f"'{self.venvLocation}/{self.venvName}/bin'. \n"
        )
        with_pip_msg = ("Installed Pip and Setuptools.\n")

        print(
            "[PROCESS]: Successfully created new virtual environment: "
            f"'{self.venvLocation}/{self.venvName}'"
        )

        if self.withPipCBox.isChecked():
            message_txt = default_msg + with_pip_msg
            print("[PROCESS]: Installed pip, setuptools.")
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
            "environment. Double-click the item you want to install. "
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


        #]===================================================================[#
        #] RESULTS TABLE VIEW [#=============================================[#
        #]===================================================================[#

        resultsTable = QTableView(
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            doubleClicked=self.install_module
        )
        resultsTable.setSortingEnabled(True)

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
        # clear the search input line and the results table
        self.pkgNameLineEdit.clear()
        self.resultsModel.clear()

        # set header labels
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

        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")


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
            self.manager = PipManager(self.venvLocation, self.venvName)
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
            print(f"[PROCESS]: Installing module '{self.pkg}'...")
            self.manager.run_pip(cmds[0], [opts[0], self.pkg])

            # display the updated output
            self.manager.textChanged.connect(self.console.update_status)

            # clear the content on window close
            if self.console.close:
                self.console.consoleWindow.clear()

                # connect 'next' button to self.save_requirements()
                self.next_button.disconnect()
                self.next_button.clicked.connect(self.save_requirements)


    def save_requirements(self):
        """
        Ask user for saving a requirements.txt in the
        created virtual environment.
        """
        self.setEnabled(False)

        messageBoxConfirm = QMessageBox.question(self,
            "Confirm", "Do you want to generate a requirements.txt file?",
            QMessageBox.Yes | QMessageBox.No
        )

        if messageBoxConfirm == QMessageBox.Yes:
            create_requirements(self.venvLocation, self.venvName)
            print(
                "[PROCESS]: Generating "
                f"'{self.venvLocation}/{self.venvName}/requirements.txt'..."
            )
            message_txt = (
                "The requirements.txt file has been saved in:\n"
                f"'{self.venvLocation}/{self.venvName}'"
            )
            QMessageBox.information(self, "Done", message_txt)

            self.wizard().next()

        else:
            self.wizard().next()

        self.setEnabled(True)



class SummaryPage(QWizardPage):
    """
    The last page.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Finished")
        self.setSubTitle("All Tasks have been completed successfully.")

        #]===================================================================[#
        # TODO: create the summary page
        #]===================================================================[#


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

        self.wizard().refresh.emit()



if __name__ == "__main__":

    app = QApplication(sys.argv)
    wizard = VenvWizard()
    wizard.show()

    sys.exit(app.exec_())
