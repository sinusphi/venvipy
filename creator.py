# -*- coding: utf-8 -*-
"""Wizard for creating and setting up virtual environments."""
from venv import create as create_venv
from functools import partial
import shutil
import sys
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt5.QtWidgets import (QApplication, QProgressBar, QGridLayout, QLabel,
                             QFileDialog, QHBoxLayout, QVBoxLayout, QDialog,
                             QWizard, QWizardPage, QToolButton, QComboBox,
                             QCheckBox, QLineEdit, QGroupBox)

from organize import get_python_installs



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
        self.setGeometry(684, 365, 325, 80)
        self.setFixedSize(325, 80)
        self.setWindowTitle("Creating")
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        h_Layout = QHBoxLayout(self)
        v_Layout = QVBoxLayout()

        self.statusLabel = QLabel(self)

        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedSize(300, 23)
        self.progressBar.setRange(0, 0)

        v_Layout.addWidget(self.statusLabel)
        v_Layout.addWidget(self.progressBar)

        h_Layout.addLayout(v_Layout)
        self.setLayout(h_Layout)



#]===========================================================================[#
#] WIZARD [#=================================================================[#
#]===========================================================================[#

class VenvWizard(QWizard):
    """
    Wizard for creating and setting up virtual environments.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Venv Wizard")
        self.resize(535, 430)
        self.move(578, 183)

        self.setStyleSheet(
            """
            QToolTip {
                background-color: rgb(47, 52, 63);
                border: rgb(47, 52, 63);
                color: rgb(210, 210, 210);
                padding: 2px;
                opacity: 325
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
                f"{info.version} ~ {info.path}", info.path
            )

        venvNameLabel = QLabel("Venv &name:")
        self.venvNameLineEdit = QLineEdit()
        venvNameLabel.setBuddy(self.venvNameLineEdit)

        venvLocationLabel = QLabel("&Location:")
        self.venvLocationLineEdit = QLineEdit()
        venvLocationLabel.setBuddy(self.venvLocationLineEdit)

        selectDirToolButton = QToolButton(
            toolTip="Browse",
            clicked=self.selectDir
        )
        selectDirToolButton.setFixedSize(26, 27)
        selectDirToolButton.setIcon(folder_icon)

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


    def selectDir(self):
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
    finished = pyqtSignal()

    @pyqtSlot(tuple)
    def install(self, args):
        self.started.emit()

        name, location, with_pip, site_packages, symlinks = args

        create_venv(
            os.path.join(location, name),
            with_pip=with_pip,
            system_site_packages=site_packages,
            symlinks=symlinks,
        )

        self.finished.emit()


class InstallPackages(QWizardPage):
    """
    Install packages via `pip` into the created virtual environment.
    """
    def __init__(self):
        super().__init__()

        self.setTitle("Install Packages")
        self.setSubTitle("Specify the packages which you want Pip to "
                         "install into the virtual environment.")

        self.progressBar = ProgBarDialog()


        #]===================================================================[#
        #] THREAD (CREATE PROCESS) [#========================================[#
        #]===================================================================[#

        thread = QThread(self)
        thread.start()

        self.m_install_worker = CreationWorker()
        self.m_install_worker.moveToThread(thread)

        self.m_install_worker.started.connect(self.progressBar.exec_)
        self.m_install_worker.finished.connect(self.progressBar.close)
        self.m_install_worker.finished.connect(self.post_install_venv)
        self.m_install_worker.finished.connect(self.reEnablePage)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        # content for tests
        TestLabel1 = QLabel("This is a test label:", self)
        TestLineEdit1 = QLineEdit(self)
        TestLabel1.setBuddy(TestLineEdit1)

        TestLabel2 = QLabel("This is a test label:", self)
        TestLineEdit2 = QLineEdit(self)
        TestLabel2.setBuddy(TestLineEdit2)


        v_layout = QVBoxLayout(self)
        v_layout.addWidget(TestLabel1)
        v_layout.addWidget(TestLineEdit1)
        v_layout.addWidget(TestLabel2)
        v_layout.addWidget(TestLineEdit2)

        self.setLayout(v_layout)


    def initializePage(self):
        self.pythonVers = self.field("pythonVers")
        self.pythonPath = self.field("pythonPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")
        self.withPip = self.field("withPip")
        self.sitePackages = self.field("sitePackages")
        self.launchVenv = self.field("launchVenv")
        self.symlinks = self.field("symlinks")

        # display which python version is used to create the virt. env
        self.progressBar.statusLabel.setText(
            f"Creating venv using {self.pythonVers[:12]}"
        )

        # overwrite executable with the python version selected
        sys.executable = self.pythonPath

        # run the create process
        self.createProcess()

        # disable the next wizard page during create process
        self.setEnabled(False)


    def createProcess(self):
        """
        Create the virtual environment.
        """
        args = (
            self.venvName,
            self.venvLocation,
            self.withPip,
            self.sitePackages,
            self.symlinks,
        )

        wrapper = partial(self.m_install_worker.install, args)
        QTimer.singleShot(0, wrapper)


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


    def reEnablePage(self):
        """
        Re-enable wizard page when create process has finished.
        """
        self.setEnabled(True)


    def launchTerminal(self):
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
