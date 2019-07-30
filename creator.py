# -*- coding: utf-8 -*-
"""Wizard for creating and setting up virtual environments."""
from venv import create as create_venv
from functools import partial
import shutil
import sys
import os

from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt5.QtWidgets import (QApplication, QProgressBar, QGridLayout, QLabel,
                             QFileDialog, QHBoxLayout, QVBoxLayout, QDialog,
                             QWizard, QWizardPage, QToolButton, QComboBox,
                             QCheckBox, QLineEdit, QGroupBox, QTableView,
                             QAbstractItemView, QPushButton, QFrame,
                             QMessageBox, QHeaderView)

from organize import (get_python_installs, get_package_infos, get_venvs_default,
                      run_pip)

cmd = ["install", "list", "show"]
opt = ["--upgrade"]
PIP = "pip"



#]===========================================================================[#
#] PROGRESS BAR [#===========================================================[#
#]===========================================================================[#

class ProgBarDialog(QDialog):
    """
    Dialog showing a progress bar during the create process.
    """
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setGeometry(675, 365, 325, 80)
        self.setFixedSize(350, 85)
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
        self.resize(635, 480)
        self.move(528, 153)

        self.setStyleSheet(
            """
            QToolTip {
                background-color: rgb(47, 52, 63);
                border: rgb(47, 52, 63);
                color: rgb(210, 210, 210);
                padding: 2px;
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

        self.addPage(BasicSettings())
        self.addPage(InstallPackages())
        self.addPage(Summary())


class BasicSettings(QWizardPage):
    """
    Basic settings of the virtual environment being created.
    """
    def __init__(self):
        super().__init__()

        folder_icon = QIcon.fromTheme("folder")

        self.setTitle("Basic Settings")
        self.setSubTitle("This wizard will help you to create and set up "
                         "a virtual environment for Python 3. ")


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

        selectDirToolButton = QToolButton(
            icon=folder_icon,
            toolTip="Browse",
            clicked=self.select_dir
        )
        selectDirToolButton.setFixedSize(26, 27)

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
        self.registerField("launchVenv", self.launchVenvCBox)
        self.registerField("symlinks", self.symlinksCBox)

        # grid layout
        gridLayout = QGridLayout()
        gridLayout.addWidget(interpreterLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.interprComboBox, 0, 1, 1, 2)
        gridLayout.addWidget(venvNameLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.venvNameLineEdit, 1, 1, 1, 2)
        gridLayout.addWidget(venvLocationLabel, 2, 0, 1, 1)
        gridLayout.addWidget(self.venvLocationLineEdit, 2, 1, 1, 1)
        gridLayout.addWidget(selectDirToolButton, 2, 2, 1, 1)
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


    def select_dir(self):
        """
        Specify path where to create the virtual environment.
        """
        folderName = QFileDialog.getExistingDirectory()
        self.venvLocationLineEdit.setText(folderName)


#]===========================================================================[#
#] WORKER (CREATE PROCESS) [#================================================[#
#]===========================================================================[#

class CreationWorker(QObject):
    """
    Worker informing about start and finish of the create process.
    """
    started = pyqtSignal()
    step1 = pyqtSignal()
    finished = pyqtSignal()

    @pyqtSlot(tuple)
    def install(self, args):
        self.started.emit()

        name, location, with_pip, site_packages, symlinks, pipup_script = args

        create_venv(
            os.path.join(location, name),
            with_pip=with_pip,
            system_site_packages=site_packages,
            symlinks=symlinks,
        )

        if with_pip:
            self.step1.emit()
            run_pip(cmd[0], opt[0], PIP, location, name)

        self.finished.emit()


class InstallPackages(QWizardPage):
    """
    Install packages via `pip` into the created virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Install Packages")
        self.setSubTitle(
            "Specify the packages you want to install into the virtual "
            "environment. Right-click on the item to mark it for "
            "installation and click next when ready."
            ""
        )

        self.progressBar = ProgBarDialog()


        #]===================================================================[#
        #] THREAD (CREATE PROCESS) [#========================================[#
        #]===================================================================[#

        thread = QThread(self)
        thread.start()

        self.m_install_worker = CreationWorker()
        self.m_install_worker.moveToThread(thread)

        self.m_install_worker.started.connect(self.progressBar.exec_)
        self.m_install_worker.step1.connect(self.switch_progressbar_label)
        self.m_install_worker.finished.connect(self.progressBar.close)
        self.m_install_worker.finished.connect(self.post_install_venv)
        self.m_install_worker.finished.connect(self.re_enable_page)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        verticalLayout = QVBoxLayout()
        gridLayout = QGridLayout(self)

        pkgNameLabel = QLabel("Package name:")
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
            doubleClicked=self.get_selected_row
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


        #]===================================================================[#
        #] PIP OPERATIONS [#=================================================[#
        #]===================================================================[#

        # the application directory
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # the file containing the default directory (str) if set
        default_file = os.path.join(current_dir, "def", "default")

        # script that installs the selected packages
        self.install_script = os.path.join(
            current_dir, "scripts", "install_pkgs.sh"
        )

        # script that updates pip
        self.pipup_script = os.path.join(
            current_dir, "scripts", "update_pip.sh"
        )


    def initializePage(self):
        # disable wizards next button and set search button to default
        next_button = self.wizard().button(QWizard.NextButton)
        QTimer.singleShot(0, lambda: next_button.setDefault(False))
        QTimer.singleShot(0, lambda: self.searchButton.setDefault(True))

        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")
        self.withPip = self.field("withPip")
        self.sitePackages = self.field("sitePackages")
        self.launchVenv = self.field("launchVenv")
        self.symlinks = self.field("symlinks")

        # display which python version is used to create the virt. env
        self.progressBar.setWindowTitle(f"Using {self.pythonVers[:12]}")
        self.progressBar.statusLabel.setText("Creating virtual environment...")

        # overwrite executable with the python version selected
        sys.executable = self.pythonPath

        # run the create process
        self.create_process()

        # disable the InstallPackages page during create process
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
            self.symlinks,
            self.pipup_script
        )

        wrapper = partial(self.m_install_worker.install, args)
        QTimer.singleShot(0, wrapper)


    def switch_progressbar_label(self):
        """
        Switch the progress bar label text to display when Pip is being
        updated.
        """
        self.progressBar.statusLabel.setText("Updating Pip...")


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
            elif os.path.isdir(fn) and fn != valid_dir:
                shutil.rmtree(fn)
                print(f"removed dir: '{fn}'")


    def post_install_venv(self):
        """
        Create a configuration file and remove unnecessary dirs.
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
        Re-enable wizard page when create process has finished and set focus
        on the input field.
        """
        self.setEnabled(True)
        self.pkgNameLineEdit.setFocus()


    def pop_results_table(self):
        """
        Populate the results table view.
        """
        self.resultsModel.setRowCount(0)

        for info in get_package_infos(self.pkgNameLineEdit.text()):
            self.resultsModel.insertRow(0)

            for i, text in enumerate(
                (info.pkg_name, info.pkg_vers, info.pkg_sum)
            ):
                self.resultsModel.setItem(0, i, QStandardItem(text))

        if not get_package_infos(self.pkgNameLineEdit.text()):
            self.no_results_msg()
            print("No results!")


    def no_results_msg(self):
        """
        Show info message if no packages were found.
        """
        QMessageBox.information(self,
            "No results!",
            f'No projects matching "{self.pkgNameLineEdit.text()}".\n'
        )


    def get_selected_row(self):
        """
        Get package name from the results table view.
        """
        indexes = self.selectionModel.selectedRows()
        for index in sorted(indexes):
            print(index.data())


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
        pass



if __name__ == "__main__":

    app = QApplication(sys.argv)

    wiz = VenvWizard()
    wiz.show()

    sys.exit(app.exec_())
