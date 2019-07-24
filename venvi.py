# -*- coding: utf-8 -*-
"""The main menu of VenviPy."""
from subprocess import Popen, PIPE
import os

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSlot
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
import organize
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
        self.setWindowIcon(QIcon(":/img/python.png"))

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
        self.selectDefaultDir = settings.SelectDefaultDir()
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
        v_Layout2.setContentsMargins(-1, 2, 6, -1)

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
        interprTableLabel = QLabel(
            '<span style="font-size: 13pt;">\
                <b>Available Interpreters</b>\
            </span>',
            centralwidget
        )

        # interpreter table
        interprTable = QTableView(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True
        )

        # adjust vertical headers
        v_HeaderTV1 = interprTable.verticalHeader()
        v_HeaderTV1.setDefaultSectionSize(27.5)
        v_HeaderTV1.hide()

        # adjust (horizontal) headers
        h_HeaderTV1 = interprTable.horizontalHeader()
        h_HeaderTV1.setDefaultAlignment(Qt.AlignLeft)
        h_HeaderTV1.setDefaultSectionSize(180)
        h_HeaderTV1.setStretchLastSection(True)

        # set table view model
        self.modelTV1 = QStandardItemModel(0, 2, centralwidget)
        self.modelTV1.setHorizontalHeaderLabels(["Version", "Path"])
        interprTable.setModel(self.modelTV1)

        #]===================================================================[#

        # spacer between interpreter table and venv table title
        spacerItem2 = QSpacerItem(
            20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed
        )

        #]===================================================================[#

        # venv table header
        venvTableLabel = QLabel(
            '<span style="font-size: 13pt;">\
                <b>Available virtual environments</b>\
            </span>',
            centralwidget
        )

        # venv table
        venvTable = QTableView(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True
        )

        # adjust vertical headers
        v_HeaderTV2 = venvTable.verticalHeader()
        v_HeaderTV2.setDefaultSectionSize(27.5)
        v_HeaderTV2.hide()

        # adjust (horizontal) headers
        h_HeaderTV2 = venvTable.horizontalHeader()
        h_HeaderTV2.setDefaultAlignment(Qt.AlignLeft)
        h_HeaderTV2.setDefaultSectionSize(180)
        h_HeaderTV2.setStretchLastSection(True)

        # set table view model
        self.modelTV2 = QStandardItemModel(0, 3, centralwidget)
        self.modelTV2.setHorizontalHeaderLabels(
            ["Venv Name", "Version", "Path"]
        )
        venvTable.setModel(self.modelTV2)

        # add widgets to layout
        v_Layout1.addWidget(interprTableLabel)
        v_Layout1.addWidget(interprTable)
        v_Layout1.addItem(spacerItem2)
        v_Layout1.addWidget(venvTableLabel)
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

        self.actSelectDefaultDir = QAction(
            settings_icon, "Set &default venv directory", self,
            statusTip="Set default venv directory",
            shortcut="Ctrl+D", triggered=self.openSelectDefaultDir
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
        self.menuVenv.addAction(self.actSelectDefaultDir)
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


        if not organize.get_python_installs():
            print("WARNING: No Python 3 installation found!")

            if self.messageBox.exec_() == QMessageBox.AcceptRole:
                # let user specify path to an interpreter
                self.selectInterpreter()


    #]=======================================================================[#
    #] SELECT A CUSTOM INTERPRETER [#========================================[#
    #]=======================================================================[#

    def selectInterpreter(self):
        """
        Specify path to a python executable and add it to list.
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Select Python Interpreter",
            "/$HOME",
            "Python binary (python3 python3.3 python3.4 \
                            python3.5 python3.6 python3.7 \
                            python3.8 python3.9)"
        )

        bin_file = file_name[0]

        if bin_file != "":
            # get version info and path of the selected binary
            res = Popen(
                [bin_file, "-V"], stdout=PIPE, universal_newlines=True
            )
            out, _ = res.communicate()
            version = out.strip()

            path = file_name[0]

            # fill cells
            self.modelTV1.insertRow(0)
            self.modelTV1.setItem(0, 0, QStandardItem(version))
            self.modelTV1.setItem(0, 1, QStandardItem(path))


    #]=======================================================================[#
    #] POPULATE INTERPRETER TABLE VIEW [#====================================[#
    #]=======================================================================[#

    def popInterprTable(self):
        """
        Populate the interpreter table view.
        """
        if organize.get_python_installs():
            self.modelTV1.setRowCount(0)

            for info in organize.get_python_installs():
                self.modelTV1.insertRow(0)

                for i, text in enumerate((info.version, info.path)):
                    self.modelTV1.setItem(0, i, QStandardItem(text))

                print(info)


    #]=======================================================================[#
    #] POPULATE VENV TABLE VIEW [#===========================================[#
    #]=======================================================================[#

    def popVenvTable(self):
        """
        Populate the venv table view.
        """
        self.modelTV2.setRowCount(0)

        for info in organize.get_venvs_default():
            self.modelTV2.insertRow(0)

            for i, text in enumerate((info.name, info.version, info.directory)):
                self.modelTV2.setItem(0, i, QStandardItem(text))

            print(info)


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


    def openSelectDefaultDir(self):
        """
        Open the select-default-directory window.
        """
        if self.selectDefaultDir.exec_() == QDialog.Accepted:
            self.popVenvTable()


    def openManager(self):
        """
        Open the window for managing venvs.
        """
        # TODO: add the manage menu



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    mainUI = Ui_MainWindow()
    mainUI.popInterprTable()
    mainUI.popVenvTable()
    mainUI.show()

    sys.exit(app.exec_())
