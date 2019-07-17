# -*- coding: utf-8 -*-
"""The main menu of VenviPy."""
from subprocess import Popen, PIPE
import os

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (Qt, QRect, QSize, QMetaObject, pyqtSignal, pyqtSlot,
                          QObject, QTimer, QThread)
from PyQt5.QtGui import (QIcon, QFont, QPixmap, QStandardItemModel,
                         QStandardItem)
from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, QProgressBar,
                             QFileDialog, QWidget, QGridLayout, QVBoxLayout,
                             QLabel, QPushButton, QSpacerItem, QSizePolicy,
                             QTableView, QAbstractItemView, QMenuBar, QMenu,
                             QStatusBar, QMessageBox, QWizard, QWizardPage,
                             QCheckBox, QLineEdit, QGroupBox, QHBoxLayout,
                             QComboBox, QToolButton, QDialog)

import venvipy_rc
import settings
import creator
import info




class Ui_MainWindow(QMainWindow):
    """
    The main window.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        #]===================================================================[#
        #] WINDOW SETTINGS [#================================================[#
        #]===================================================================[#

        self.setWindowTitle("VenviPy")
        self.setGeometry(430, 150, 830, 525)

        self.setStyleSheet(
            """
            QMenuBar {
                background-color: rgb(47, 52, 63);
                color: rgb(210, 210, 210)
            }

            QMenuBar::item {
                background-color: rgb(47, 52, 63);
                color: rgb(210, 210, 210)
            }

            QMenuBar::item::selected {
                background-color: rgb(72, 72, 82)
            }

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


        #]===================================================================[#
        #] INSTANCES [#======================================================[#
        #]===================================================================[#

        self.wizard = creator.VenvWizard()
        self.setDefaultDir = settings.SetDefaultDirectory()
        self.appInfo = info.AppInfo()


        #]===================================================================[#
        #] ICONS [#==========================================================[#
        #]===================================================================[#

        #del_icon = QIcon.fromTheme("edit-delete")
        #copy_icon = QIcon.fromTheme("edit-copy")
        #paste_icon = QIcon.fromTheme("edit-paste")
        #folder_icon = QIcon.fromTheme("folder")
        find_icon = QIcon.fromTheme("edit-find")
        manage_icon = QIcon.fromTheme("insert-object")
        about_icon = QIcon.fromTheme("dialog-information")
        new_icon = QIcon.fromTheme("list-add")
        settings_icon = QIcon.fromTheme("preferences-system")
        exit_icon = QIcon.fromTheme("exit")


        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        centralwidget = QWidget(self)
        gridLayout = QGridLayout(centralwidget)

        v_Layout1 = QVBoxLayout()
        v_Layout2 = QVBoxLayout()

        v_Layout1.setContentsMargins(12, 19, 5, -1)
        v_Layout2.setContentsMargins(-1, 0, 6, -1)

        # python logo
        self.logo = QLabel(centralwidget)
        self.logo.setPixmap(QPixmap(":/img/pypower.png"))
        self.logo.setAlignment(Qt.AlignRight)


        #]===================================================================[#
        #] BUTTONS [#========================================================[#
        #]===================================================================[#

        self.addButton = QPushButton(
            "Add Interpreter", centralwidget,
            statusTip="Add an Interpreter",
            clicked=self.selectInterpreter
        )
        self.addButton.setMinimumSize(QSize(150, 0))

        self.newVenvButton = QPushButton(
            "New Venv", centralwidget,
            statusTip="Create a new virtual environment",
            clicked=self.openWizard
        )

        self.manageVenvButton = QPushButton(
            "Manage Venvs", centralwidget,
            statusTip="Manage your virtual environments",
            clicked=self.openManager
        )

        self.exitButton = QPushButton(
            "Quit", centralwidget,
            statusTip="Quit Application",
            clicked=self.close
        )


        #]===================================================================[#

        # spacer manage button and exit button
        spacerItem1 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        #]===================================================================[#


        # add widgets to layout
        v_Layout2.addWidget(self.logo)
        v_Layout2.addWidget(self.addButton)
        v_Layout2.addWidget(self.newVenvButton)
        v_Layout2.addWidget(self.manageVenvButton)
        v_Layout2.addItem(spacerItem1)
        v_Layout2.addWidget(self.exitButton)

        gridLayout.addLayout(v_Layout2, 0, 1, 1, 1)


        #]===================================================================[#
        #] TABLES [#=========================================================[#
        #]===================================================================[#

        # interpreter table header
        self.interprTableLabel = QLabel(
            "<b>Available Interpreters</b>", centralwidget
        )

        # interpreter table
        interprTable = QTableView(centralwidget)
        interprTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        interprTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        interprTable.setAlternatingRowColors(True)

        # adjust vertical headers
        v_HeaderTV1 = interprTable.verticalHeader()
        v_HeaderTV1.setVisible(False)
        v_HeaderTV1.setDefaultSectionSize(27.5)

        # adjust (horizontal) headers
        h_HeaderTV1 = interprTable.horizontalHeader()
        h_HeaderTV1.setDefaultAlignment(Qt.AlignLeft)
        h_HeaderTV1.setDefaultSectionSize(180)
        h_HeaderTV1.setStretchLastSection(True)

        # set table view model
        self.modelTV1 = QStandardItemModel(centralwidget)
        self.modelTV1.setColumnCount(2)
        self.modelTV1.setHorizontalHeaderLabels(["Version", "Path"])
        interprTable.setModel(self.modelTV1)

        # fill the cells
        for i in range(len(creator.versFound)):
            self.modelTV1.insertRow(0)
            self.modelTV1.setItem(0, 0, QStandardItem(creator.versFound[i]))
            self.modelTV1.setItem(0, 1, QStandardItem(creator.pathFound[i]))

        #]===================================================================[#

        # spacer between interpreter table and venv table title
        spacerItem2 = QSpacerItem(
            20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed
        )

        #]===================================================================[#

        # venv table header
        self.venvTableLabel = QLabel(
            "<b>Available virtual environments</b>", centralwidget
        )

        # venv table
        venvTable = QTableView(centralwidget)
        venvTable.verticalHeader().setVisible(False)
        venvTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        venvTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        venvTable.setAlternatingRowColors(True)

        # adjust vertical headers
        v_HeaderTV2 = venvTable.verticalHeader()
        v_HeaderTV2.setVisible(False)
        v_HeaderTV2.setDefaultSectionSize(27.5)

        # adjust (horizontal) headers
        h_HeaderTV2 = venvTable.horizontalHeader()
        h_HeaderTV2.setDefaultAlignment(Qt.AlignLeft)
        h_HeaderTV2.setDefaultSectionSize(180)
        h_HeaderTV2.setStretchLastSection(True)

        # set table view model
        self.modelTV2 = QStandardItemModel(centralwidget)
        self.modelTV2.setColumnCount(3)
        self.modelTV2.setHorizontalHeaderLabels(
            ["Venv Name", "Version", "Path"]
        )
        venvTable.setModel(self.modelTV2)

        # get the path (str) to the default dir from file
        with open("def/default", 'r') as default:
            defDir = default.read()
            default.close()

        # get all folders inside the selected default dir
        subDirs = os.listdir(defDir)

        # loop over the subdirs of the selected default dir
        for i, _dir in enumerate(subDirs):
            # if there's a 'bin' folder inside the subdir, and it contains a
            # file named 'python', then try to get the version
            if ("bin" in os.listdir('/'.join([defDir, _dir]))
            and "python" in os.listdir('/'.join([defDir, _dir, "bin"]))):

                try:
                    getVers = Popen(
                        ['/'.join([defDir, _dir, "bin", "python"]), "-V"],
                        stdout=PIPE, universal_newlines=True
                    )
                    version = getVers.communicate()[0].strip()

                except Exception as err:
                    print(err)
                    continue

                # fill the cells
                self.modelTV2.insertRow(0)
                self.modelTV2.setItem(0, 0, QStandardItem(_dir))
                self.modelTV2.setItem(0, 1, QStandardItem(version))
                self.modelTV2.setItem(0, 2, QStandardItem(defDir))


        # add widgets to layout
        v_Layout1.addWidget(self.interprTableLabel)
        v_Layout1.addWidget(interprTable)
        v_Layout1.addItem(spacerItem2)
        v_Layout1.addWidget(self.venvTableLabel)
        v_Layout1.addWidget(venvTable)

        gridLayout.addLayout(v_Layout1, 0, 0, 1, 1)

        self.setCentralWidget(centralwidget)


        #]===================================================================[#
        #] MENUS [#==========================================================[#
        #]===================================================================[#

        statusBar = QStatusBar(self)

        menuBar = QMenuBar(self)
        menuBar.setGeometry(QRect(0, 0, 740, 24))

        self.menuVenv = QMenu("&Venv", menuBar)
        self.menuHelp = QMenu("&Help", menuBar)

        self.setMenuBar(menuBar)
        self.setStatusBar(statusBar)


        #]===================================================================[#
        #] ACTIONS [#========================================================[#
        #]===================================================================[#

        # create actions
        self.actAddInterpreter = QAction(
            find_icon, "Add &Interpreter", self,
            statusTip="Add an Interpreter", shortcut="Ctrl+I",
            triggered=self.selectInterpreter
        )

        self.actNewVenv = QAction(
            new_icon, "&New Venv", self,
            statusTip="Create a new virtual environment",
            shortcut="Ctrl+N", triggered=self.openWizard
        )

        self.actManageVenvs = QAction(
            manage_icon, "&Manage Venvs", self,
            statusTip="Manage your virtual environments",
            shortcut="Ctrl+M", triggered=self.openManager
        )

        self.actSetDefaultDir = QAction(
            settings_icon, "Set &default venv directory", self,
            statusTip="Set default venv directory",
            shortcut="Ctrl+D", triggered=self.openSetDefaultDir
        )

        self.actExit = QAction(
            exit_icon, "&Quit", self,
            statusTip="Quit application",
            shortcut="Ctrl+Q", triggered=self.close
        )

        self.actAbout = QAction(
            about_icon, "&About", self,
            statusTip="About VenviPy",
            shortcut="Ctrl+B", triggered=self.openInfo
        )

        # add actions to menus
        self.menuVenv.addAction(self.actAddInterpreter)
        self.menuVenv.addSeparator()
        self.menuVenv.addAction(self.actNewVenv)
        self.menuVenv.addAction(self.actManageVenvs)
        self.menuVenv.addAction(self.actSetDefaultDir)
        self.menuVenv.addSeparator()
        self.menuVenv.addAction(self.actExit)
        self.menuHelp.addAction(self.actAbout)

        menuBar.addAction(self.menuVenv.menuAction())
        menuBar.addAction(self.menuHelp.menuAction())


        #]===================================================================[#
        #] MESSAGE BOX [#====================================================[#
        #]===================================================================[#

        # display a message box if no Python installation is found at all
        messageText = "No Python 3 installation found!\n\n" \
                      "Please specify the path to a Python 3 " \
                      "installation or click Continue to go on " \
                      "anyway.\n\n"

        self.messageBox = QMessageBox(
            QMessageBox.Critical, "VenviPy Launcher",
            messageText, QMessageBox.NoButton, self
        )

        self.messageBox.addButton("&Search", QMessageBox.AcceptRole)
        self.messageBox.addButton("&Continue", QMessageBox.RejectRole)

        # if the notFound list is full (none of the versions is found), then
        #  there's no Python install in the common paths -> display message
        if len(creator.notFound) == 8:
            print("WARNING: No Python 3 installation found!")

            if self.messageBox.exec_() == QMessageBox.AcceptRole:
                # let user specify the path to an interpreter
                self.selectInterpreter()


    #]=======================================================================[#
    #] SELECT A CUSTOM INTERPRETER [#========================================[#
    #]=======================================================================[#

    def selectInterpreter(self):
        """
        Specify path to a python executable and add it to list.
        """
        fileDiag = QFileDialog()

        fileName = fileDiag.getOpenFileName(
            self,
            "Select Python Interpreter",
            "~",
            "Python executable (python3 python3.3 python3.4 \
                                python3.5 python3.6 python3.7 \
                                python3.8 python3.9 python4.0)"
        )

        binFile = fileName[0]

        if binFile != "":
            # get version info and path of selected interpreter
            getVersInf = Popen(
                [binFile, "-V"], stdout=PIPE, universal_newlines=True
            )

            versInf = getVersInf.communicate()[0].strip()

            pathInf = fileName[0]

            # fill cells with the returned values
            self.modelTV1.insertRow(0)
            self.modelTV1.setItem(0, 0, QStandardItem(versInf))
            self.modelTV1.setItem(0, 1, QStandardItem(pathInf))


    #]=======================================================================[#
    #] OPEN WIDGETS / WINDOWS [#=============================================[#
    #]=======================================================================[#

    def openWizard(self):
        """
        Open the wizard that creates the virtual environment.
        """
        self.wizard.exec_()


    def openInfo(self):
        """
        Open the application info window.
        """
        self.appInfo.exec_()


    def openSetDefaultDir(self):
        """
        Open the set-default-directory window.
        """
        self.setDefaultDir.exec_()


    def openManager(self):
        """
        Open the window for managing venvs.
        """
        # TODO: add the manage menu





if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    mainUI = Ui_MainWindow()
    mainUI.show()

    sys.exit(app.exec_())
