# -*- coding: utf-8 -*-
"""Wizard for creating and setting up virtual environments."""
from venv import create as create_venv
from functools import partial
import shutil
import sys
import os

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread,
                          QProcess)
from PyQt5.QtWidgets import (QApplication, QProgressBar, QGridLayout, QLabel,
                             QFileDialog, QHBoxLayout, QVBoxLayout, QDialog,
                             QWizard, QWizardPage, QToolButton, QComboBox,
                             QCheckBox, QLineEdit, QGroupBox, QTableView,
                             QAbstractItemView, QPushButton, QFrame, QTextEdit,
                             QMessageBox, QHeaderView, QDesktopWidget)

from organize import get_package_infos, get_venvs_default, get_python_installs
from managepip import PipManager

PIP = "pip"


# pip commands and options
cmd = ["install", "list", "show"]
opt = ["--upgrade"]


#]===========================================================================[#
#] PROGRESS BAR DIALOG [#====================================================[#
#]===========================================================================[#

class ProgBarDialog(QDialog):
    """
    Dialog showing a progress bar during the create process.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(350, 85)
        self.center()
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        h_Layout = QHBoxLayout(self)
        v_Layout = QVBoxLayout()
        h_Layout.setContentsMargins(0, 15, 0, 0)

        self.statusLabel = QLabel(self)
        self.placeHolder = QLabel(self)

        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedSize(325, 23)
        self.progressBar.setRange(0, 0)

        v_Layout.addWidget(self.statusLabel)
        v_Layout.addWidget(self.progressBar)
        v_Layout.addWidget(self.placeHolder)

        h_Layout.addLayout(v_Layout)
        self.setLayout(h_Layout)

    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


#]===========================================================================[#
#] CONSOLE DIALOG [#=========================================================[#
#]===========================================================================[#

class ConsoleDialog(QDialog):
    """
    Dialog box displaying the output inside a console-like widget during the
    installation process.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Installing")
        self.resize(880, 510)
        self.center()
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        self.setStyleSheet(
            """
            QTextEdit {
                background-color: black;
                color: lightgrey;
                selection-background-color: rgb(50, 50, 60);
                selection-color: rgb(0, 255, 0)
            }
            """
        )

        self.consoleWindow = QTextEdit()
        self.consoleWindow.setReadOnly(True)
        self.consoleWindow.setFontFamily("Monospace")
        self.consoleWindow.setFontPointSize(10)

        v_Layout = QVBoxLayout(self)
        v_Layout.addWidget(self.consoleWindow)

    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot(str)
    def update_status(self, status):
        """
        Set the content to be shown in the console dialog.
        """
        metrix = QFontMetrics(self.consoleWindow.font())
        clippedText = metrix.elidedText(
            status, Qt.ElideRight, self.consoleWindow.width()
        )
        self.consoleWindow.append(clippedText)


#]===========================================================================[#
#] WORKER (CREATE VIRTUAL ENVIRONMENT) [#====================================[#
#]===========================================================================[#

class CreationWorker(QObject):
    """
    Worker informing about start and end of the create process.
    """
    started = pyqtSignal()
    textChanged = pyqtSignal()
    finished = pyqtSignal()

    @pyqtSlot(tuple)
    def install_venv(self, args):
        self.started.emit()

        name, location, with_pip, site_packages, symlinks = args

        create_venv(
            os.path.join(location, name),
            with_pip=with_pip,
            system_site_packages=site_packages,
            symlinks=symlinks,
        )

        self.manager = PipManager(location, name)

        if with_pip:
            self.textChanged.emit()
            self.manager.run_command(cmd[0], [opt[0], PIP])

        self.finished.emit()


#]===========================================================================[#
#] WIZARD [#=================================================================[#
#]===========================================================================[#

class VenvWizard(QWizard):
    """
    Wizard for creating and setting up a virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Venv Wizard")
        self.resize(680, 510)
        self.center()

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

        self.installId = self.addPage(InstallPackages())
        self.summaryId = self.addPage(Summary())

    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def nextId(self):
        # process the flow only if the current page is BasicSettings()
        if self.currentId() != self.basicSettingsId:
            return super().nextId()

        if self.basicSettings.withPipCBox.isChecked():
            return self.installId
        return self.summaryId


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

        self.progressBar = ProgBarDialog()

        #]===================================================================[#
        #] THREADS  [#=======================================================[#
        #]===================================================================[#

        thread = QThread(self)
        thread.start()

        self.m_install_venv_worker = CreationWorker()
        self.m_install_venv_worker.moveToThread(thread)

        self.m_install_venv_worker.started.connect(self.progressBar.exec_)
        self.m_install_venv_worker.textChanged.connect(self.set_progbar_label)
        self.m_install_venv_worker.finished.connect(self.progressBar.close)
        self.m_install_venv_worker.finished.connect(self.post_install_venv)
        self.m_install_venv_worker.finished.connect(self.show_finished_msg)
        self.m_install_venv_worker.finished.connect(self.re_enable_page)

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
                f"{info.version} - {info.path}", info.path
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

        #]===================================================================[#
        # TODO: remove placeholder and add a spacer instead
        placeHolder = QLabel()
        #]===================================================================[#

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
        self.launchVenvCBox = QCheckBox(
            "Launch a &terminal with activated venv after installation"
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
        self.registerField("launchVenv", self.launchVenvCBox)

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
        groupBoxLayout.addWidget(self.launchVenvCBox)
        groupBox.setLayout(groupBoxLayout)

    def initializePage(self):
        next_button = self.wizard().button(QWizard.NextButton)
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
        self.launchVenv = self.field("launchVenv")

        if self.combobox and self.venvName and self.venvLocation:
            # display which python version is used to create the virt. env
            self.progressBar.setWindowTitle(f"Using {self.pythonVers[:12]}")
            self.progressBar.statusLabel.setText("Creating virtual environment...")

            # overwrite executable with the python version selected
            sys.executable = self.pythonPath

            # run the create process
            self.create_process()

            # disable page during create process
            self.setEnabled(False)

    def create_process(self):
        """
        Create the virtual environment.
        """
        args = (
            self.venvName,
            self.venvLocation,
            self.withPip,
            self.sitePackages,
            self.symlinks
        )

        wrapper = partial(self.m_install_venv_worker.install_venv, args)
        QTimer.singleShot(0, wrapper)

    def set_progbar_label(self):
        """
        Set the text in status label to show that Pip is being updated.
        """
        self.progressBar.statusLabel.setText("Updating Pip...")

    def show_finished_msg(self):
        """
        Show info message when the creation process has finished successfully.
        """
        print(
            f"[VENVIPY]: Successfully created virtual environment "
            f"'{self.venvName}' in '{self.venvLocation}'"
        )

        default_msg = (
            f"Virtual environment created \nsuccessfully. \n\n"
            f"New Python{self.pythonVers[7:10]} executable in \n"
            f"'{self.venvLocation}/{self.venvName}/bin'. \n"
        )

        withpip_msg = ("Installed pip, setuptools.\n")

        if self.withPipCBox.isChecked():
            #print("[INFO]: Installed pip, setuptools")
            message_txt = default_msg + withpip_msg
        else:
            message_txt = default_msg

        QMessageBox.information(self, "Done", message_txt)

        next_button = self.wizard().button(QWizard.NextButton)
        next_button.disconnect()
        next_button.clicked.connect(self.wizard().next)


    def clean_venv_dir(self):
        """
        Remove unnecessarily created dirs from `lib` dir.
        """
        lib_dir = os.path.join(self.venvLocation, self.venvName, "lib")
        valid_dir_name = f"python{self.pythonVers[7:10]}"

        valid_dir = os.path.join(
            self.venvLocation,
            self.venvName,
            "lib",
            valid_dir_name
        )

        for fn in os.listdir(lib_dir):
            fn = os.path.join(lib_dir, fn)

            if os.path.islink(fn) or os.path.isfile(fn):
                os.remove(fn)
                print(f"[VENVIPY]: Removed file or directory: '{fn}'")

            elif os.path.isdir(fn) and fn != valid_dir:
                shutil.rmtree(fn)
                print(f"[VENVIPY]: Removed file or directory: '{fn}'")


    def post_install_venv(self):
        """
        Create the configuration file and remove unnecessary dirs.
        """
        cfg_path = os.path.join(self.venvLocation, self.venvName, "pyvenv.cfg")
        bin_path = os.path.split(self.pythonPath)[0]

        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(f"home = {bin_path}\n")

            if self.sitePackages:
                include = "true"
            else:
                include = "false"

            f.write(f"include-system-site-packages = {include}\n")
            f.write(f"version = {self.pythonVers[7:12]}\n")

        self.clean_venv_dir()


    def re_enable_page(self):
        """
        Re-enable wizard page when create process has finished.
        """
        self.setEnabled(True)


class InstallPackages(QWizardPage):
    """
    Install packages via `pip` into the created virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Install Packages")
        self.setSubTitle(
            "Specify the packages you want to install into the virtual "
            "environment. Double-click the item you want to install and "
            "click next when finished."
        )

        self.console = ConsoleDialog()

        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        verticalLayout = QVBoxLayout()
        gridLayout = QGridLayout(self)

        pkgNameLabel = QLabel("Package:")
        self.pkgNameLineEdit = QLineEdit()
        pkgNameLabel.setBuddy(self.pkgNameLineEdit)

        self.searchButton = QPushButton(
            "&Search",
            clicked=self.pop_results_table
        )

        #]===================================================================[#
        #] RESULTS TABLE VIEW [#=============================================[#
        #]===================================================================[#

        self.resultsTable = QTableView(
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            doubleClicked=self.install_package
        )
        self.resultsTable.setSortingEnabled(True)

        # adjust vertical headers
        v_Header = self.resultsTable.verticalHeader()
        v_Header.setDefaultSectionSize(27.5)
        v_Header.hide()

        # adjust horizontal headers
        self.h_Header = self.resultsTable.horizontalHeader()
        self.h_Header.setDefaultAlignment(Qt.AlignLeft)
        self.h_Header.setDefaultSectionSize(120)
        self.h_Header.setStretchLastSection(True)
        self.h_Header.setSectionResizeMode(QHeaderView.ResizeToContents)

        # item model
        self.resultsModel = QStandardItemModel(0, 2, self)
        self.resultsModel.setHorizontalHeaderLabels(
            ["Name", "Version", "Description"]
        )
        self.resultsTable.setModel(self.resultsModel)

        # selection model
        self.selectionModel = self.resultsTable.selectionModel()

        gridLayout.addWidget(pkgNameLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.pkgNameLineEdit, 0, 1, 1, 1)
        gridLayout.addWidget(self.searchButton, 0, 2, 1, 1)
        gridLayout.addWidget(self.resultsTable, 1, 0, 1, 3)

        verticalLayout.addLayout(gridLayout)


    def initializePage(self):
        next_button = self.wizard().button(QWizard.NextButton)

        # disable focus on 'next' button and set 'search' button to default
        QTimer.singleShot(0, lambda: next_button.setDefault(False))
        QTimer.singleShot(0, lambda: self.searchButton.setDefault(True))

        # disable 'back' button to prevent returning back to first page
        back_button = self.wizard().button(QWizard.BackButton)
        QTimer.singleShot(0, lambda: back_button.setEnabled(False))

        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")


    def pop_results_table(self):
        """
        Populate the results table view.
        """
        search_item = self.pkgNameLineEdit.text()

        self.resultsModel.setRowCount(0)

        for info in get_package_infos(search_item):
            self.resultsModel.insertRow(0)

            for i, text in enumerate(
                (info.pkg_name, info.pkg_vers, info.pkg_sum)
            ):
                self.resultsModel.setItem(0, i, QStandardItem(text))

        if not get_package_infos(search_item):
            print(f"[PIP]: No matches for '{search_item}'")
            QMessageBox.information(self,
                "No results",
                f"No packages matching '{search_item}'.\n"
            )


    def install_package(self):
        """
        Get the name of the double-clicked item from the results table
        view and ask user for confirmation before installing. If confirmed
        install the selected package into the created virtual environment,
        else abort.
        """
        indexes = self.selectionModel.selectedRows()
        for index in sorted(indexes):
            self.pkg = index.data()

        self.messageBoxConfirm = QMessageBox.question(self,
            "Confirm", f"Are you sure you want to install '{self.pkg}'?",
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if self.messageBoxConfirm == QMessageBox.Yes:
            print(f"[VENVIPY]: Installing '{self.pkg}'")
            self.manager = PipManager(self.venvLocation, self.venvName)
            self.manager.textChanged.connect(self.console.update_status)
            self.manager.started.connect(self.console.exec_)
            self.manager.run_command(cmd[0], [opt[0], self.pkg])
            #self.manager.finished.connect(self.console.close)

            #]===============================================================[#
            # TODO: don't autoclose the console window on finish,
            #       add a button instead
            #]===============================================================[#


    def launch_terminal(self):
        """
        Launch a terminal with the created virtual environment activated.
        """
        #]===================================================================[#
        # TODO: launch a terminal and activate the created virt. env
        #       (not yet sure if this is easy to realize)
        #]===================================================================[#


class Summary(QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Summary")
        self.setSubTitle("..........................."
                         "...........................")

        #]===================================================================[#
        # TODO: create the summary page
        #]===================================================================[#


    def initializePage(self):
        back_button = self.wizard().button(QWizard.BackButton)
        finish_button = self.wizard().button(QWizard.FinishButton)

        # disable 'back' button to prevent returning back to previous pages
        QTimer.singleShot(0, lambda: back_button.setEnabled(False))

        # reset wizard
        finish_button.clicked.connect(self.wizard().restart)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    wiz = VenvWizard()
    wiz.show()

    sys.exit(app.exec_())
