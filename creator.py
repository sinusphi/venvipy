# -*- coding: utf-8 -*-
"""Wizard for creating and setting up virtual environments."""
from subprocess import Popen, PIPE, CalledProcessError
from functools import partial
#from venv import create
import venv
import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QProgressBar, QGridLayout, QLabel,
                             QFileDialog, QHBoxLayout, QVBoxLayout, QDialog,
                             QPushButton, QSpacerItem, QSizePolicy, QWizard,
                             QWizardPage, QToolButton, QComboBox, QCheckBox,
                             QLineEdit, QGroupBox)




#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

# look for installed Python versions in common locations
versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3']

notFound = []
versFound = []
pathFound = []

for i, v in enumerate(versions):
    try:
        # get python versions
        getVers = Popen(
            ["python" + v, "-V"], stdout=PIPE, universal_newlines=True
        )

        # get paths to the python executables
        getPath = Popen(
            ["which", "python" + v], stdout=PIPE, universal_newlines=True
        )

        version = getVers.communicate()[0].strip()
        path = getPath.communicate()[0].strip()

        versFound.append(version)
        pathFound.append(path)

    except (CalledProcessError, FileNotFoundError):
        # determining the amount of the versions which were not found
        # (need this to display a message in case there's no python 3
        # installation found at all)
        notFound.append(i)



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

        # add items from versFound to combobox
        self.interprComboBox.addItem("---")
        for i in range(len(versFound)):
            self.interprComboBox.addItem(versFound[i], pathFound[i])

        venvNameLabel = QLabel("Venv &name:")
        self.venvNameLineEdit = QLineEdit(
            textChanged=self.collectData
        )
        venvNameLabel.setBuddy(self.venvNameLineEdit)

        venvLocationLabel = QLabel("&Location:")
        self.venvLocationLineEdit = QLineEdit(
            textChanged=self.collectData
        )
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

        # events
        self.interprComboBox.currentIndexChanged.connect(self.collectData)
        self.withPipCBox.toggled.connect(self.collectData)
        self.sitePackagesCBox.toggled.connect(self.collectData)
        self.symlinksCBox.toggled.connect(self.collectData)
        self.launchVenvCBox.toggled.connect(self.collectData)

        # store the collected data in line edits
        self.interprVers = QLineEdit()
        self.interprPath = QLineEdit()
        self.venvName = QLineEdit()
        self.venvLocation = QLineEdit()
        self.withPip = QLineEdit()
        self.sitePackages = QLineEdit()
        self.launchVenv = QLineEdit()
        self.symlinks = QLineEdit()

        # register fields
        self.registerField("interprComboBox*", self.interprComboBox)
        self.registerField("venvNameLineEdit*", self.venvNameLineEdit)
        self.registerField("venvLocationLineEdit*", self.venvLocationLineEdit)
        self.registerField("interprVers", self.interprVers)
        self.registerField("interprPath", self.interprPath)
        self.registerField("venvName", self.venvName)
        self.registerField("venvLocation", self.venvLocation)
        self.registerField("withPip", self.withPip)
        self.registerField("sitePackages", self.sitePackages)
        self.registerField("launchVenv", self.launchVenv)
        self.registerField("symlinks", self.symlinks)

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


    #]=======================================================================[#
    #] SELECTIONS [#=========================================================[#
    #]=======================================================================[#

    def selectDir(self):
        """
        Specify path where to create the virtual environment.
        """
        fileDiag = QFileDialog()

        folderName = fileDiag.getExistingDirectory()
        self.venvLocationLineEdit.setText(folderName)


    def collectData(self, i):
        """
        Collect all input data and create the virtual environment.
        """
        self.interprVers.setText(self.interprComboBox.currentText())
        self.interprPath.setText(self.interprComboBox.currentData())
        self.venvName.setText(self.venvNameLineEdit.text())
        self.venvLocation.setText(self.venvLocationLineEdit.text())

        # options
        self.withPip.setText(str(self.withPipCBox.isChecked()))
        self.sitePackages.setText(str(self.sitePackagesCBox.isChecked()))
        self.launchVenv.setText(str(self.launchVenvCBox.isChecked()))
        self.symlinks.setText(str(self.symlinksCBox.isChecked()))



#]===========================================================================[#
#] WORKER (CREATE PROCESS) [#================================================[#
#]===========================================================================[#

class CreationWorker(QObject):
    """
    Worker sending start and finish signal to the progress bar dialog.
    """
    started = pyqtSignal()
    finished = pyqtSignal()

    @pyqtSlot(tuple)
    def install(self, args):
        self.started.emit()

        name, location, with_pip, site_packages, symlinks = args

        # TODO: Need to determine why the create() method arguments from the
        #       venv module do not inherit the status of the corresponding
        #       checkboxes. Currently, the virtual environment is always
        #       created with default settings (with pip, ...) and ignores
        #       the args passed from the createProcess() method.

        venv.create(
            "/".join([location, name]),
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
        self.interprVers = self.field("interprVers")
        self.interprPath = self.field("interprPath")
        self.venvName = self.field("venvName")
        self.venvLocation = self.field("venvLocation")
        self.withPip = self.field("withPip")
        self.sitePackages = self.field("sitePackages")
        self.launchVenv = self.field("launchVenv")
        self.symlinks = self.field("symlinks")

        # overwrite with the interpreter selected
        sys.executable = self.interprPath

        # display which interpreter version is used
        self.progressBar.statusLabel.setText(
            "Creating venv using %s " % self.interprVers
        )

        # run the create process
        self.createProcess()

        # disable wizard page during create process
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
        # TODO: launch a terminal and activate the created venv
        #       (not yet sure if this is possible)
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
