# -*- coding: utf-8 -*-
"""
The main module of VenviPy.
"""
from subprocess import Popen, PIPE
import shutil
import os

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (
    QIcon, QPixmap, QStandardItemModel, QStandardItem, QCursor
)
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QFileDialog, QLabel, QToolButton,
    QWidget, QGridLayout, QVBoxLayout, QPushButton, QSpacerItem, QDialog,
    QSizePolicy, QTableView, QMenuBar, QMenu, QStatusBar, QAbstractItemView,
    QMessageBox, QDesktopWidget, QHBoxLayout, QLineEdit
)
import resources.venvipy_rc

from get_data import get_python_installs, get_active_dir, get_active_dir_str
from dialogs import AppInfoDialog, ConsoleDialog
from manage_pip import PipManager
from creator import cmds, opts
import wizard


__version__ = '0.11.7'


class VenvTable(QTableView):
    """
    The table that lists the virtual environments
    found in the specified default folder.
    """
    refresh = pyqtSignal()

    def contextMenuEvent(self, event):
        self.contextMenu = QMenu(self)
        self.detailsSubMenu = QMenu("Det&ails", self)

        upgradePipAction = QAction(
            QIcon.fromTheme("upload"),
            "Upgrade Pip to latest",
            self,
            statusTip="&Upgrade Pip to latest"
        )
        self.contextMenu.addAction(upgradePipAction)
        upgradePipAction.triggered.connect(lambda: self.upgrade_pip(event))

        addModulesAction = QAction(
            QIcon.fromTheme("add"),
            "&Install additional modules",
            self,
            statusTip="Install additional modules"
        )
        self.contextMenu.addAction(addModulesAction)
        addModulesAction.triggered.connect(lambda: self.add_modules(event))

        self.contextMenu.addSeparator()
        self.contextMenu.addMenu(self.detailsSubMenu)

        listModulesAction = QAction(
            QIcon.fromTheme("dialog-information"),
            "&List installed modules",
            self,
            statusTip="List installed modules"
        )
        self.detailsSubMenu.addAction(listModulesAction)
        listModulesAction.triggered.connect(
            lambda: self.list_modules(event, style=1)
        )

        freezeAction = QAction(
            QIcon.fromTheme("dialog-information"),
            "&Freeze output",
            self,
            statusTip="Show output in 'pip freeze' format"
        )
        self.detailsSubMenu.addAction(freezeAction)
        freezeAction.triggered.connect(
            lambda: self.freeze_output(event, style=2)
        )

        deleteAction = QAction(
            QIcon.fromTheme("delete"),
            "&Delete environment",
            self,
            statusTip="Delete environment"
        )
        self.contextMenu.addAction(deleteAction)
        deleteAction.triggered.connect(lambda: self.delete_venv(event))

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            self.contextMenu.popup(QCursor.pos())


    def get_selected_item(self):
        """
        Get the venv name of the selected row.
        """
        listed_venvs = self.selectionModel().selectedRows()
        for index in listed_venvs:
            selected_venv = index.data()
            return selected_venv


    def upgrade_pip(self, event):
        default_dir = get_active_dir_str()
        venv = self.get_selected_item()

        self.console = ConsoleDialog()
        self.console.setWindowTitle("Updating Pip")

        #print("[PROCESS]: Updating Pip to the latest version...")
        self.manager = PipManager(default_dir, venv)
        self.manager.run_pip(cmds[0], [opts[0], "pip"])
        self.manager.started.connect(self.console.exec_)

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # clear the content on window close
        if self.console.close:
            self.console.consoleWindow.clear()


    def add_modules(self, event):
        """
        Install additional modules into the selected environment.
        """
        pass


    def list_modules(self, event, style):
        """
        Open console dialog and list the installed modules.
        """
        default_dir = get_active_dir_str()
        venv = self.get_selected_item()

        self.console = ConsoleDialog()
        self.console.setWindowTitle(f"Modules installed in:  {venv}")

        #print("[PROCESS]: Listing modules...")
        self.manager = PipManager(default_dir, f"'{venv}'")
        self.manager.run_pip(cmds[style])
        self.manager.started.connect(self.console.exec_)

        # display the updated output
        self.manager.textChanged.connect(self.console.update_status)

        # clear the content on window close
        if self.console.close:
            self.console.consoleWindow.clear()


    def freeze_output(self, event, style):
        """
        Show `pip freeze` output in console window.
        """
        self.list_modules(event, style=2)


    def delete_venv(self, event):
        """
        Delete the selected virtual environment by clicking
        delete from the context menu in venv table.
        """
        venv = self.get_selected_item()

        if venv is not None:
            messageBoxConfirm = QMessageBox.critical(self,
                "Confirm", f"Are you sure you want to delete '{venv}'?",
                QMessageBox.Yes | QMessageBox.Cancel
            )

            if messageBoxConfirm == QMessageBox.Yes:
                default_dir = get_active_dir_str()

                venv_to_delete = os.path.join(default_dir, venv)
                shutil.rmtree(venv_to_delete)
                #print(
                    #f"[PROCESS]: Successfully deleted '{default_dir}/{venv}'"
                #)

                self.refresh.emit()



class Ui_MainWindow(QMainWindow):
    """
    The main window.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle("VenviPy")
        self.resize(900, 570)
        self.center()
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

        self.appInfo = AppInfoDialog()
        self.venv_wizard = wizard.VenvWizard()

        # refresh venv table when wizard closed
        self.venv_wizard.refresh.connect(self.popVenvTable)


        #]===================================================================[#
        #] ICONS [#==========================================================[#
        #]===================================================================[#

        refresh_icon = QIcon.fromTheme("view-refresh")
        find_icon = QIcon.fromTheme("edit-find")
        manage_icon = QIcon.fromTheme("insert-object")
        info_icon = QIcon.fromTheme("dialog-information")
        new_icon = QIcon.fromTheme("list-add")
        settings_icon = QIcon.fromTheme("preferences-system")
        exit_icon = QIcon.fromTheme("exit")
        delete_icon = QIcon.fromTheme("delete")
        folder_icon = QIcon.fromTheme("folder")


        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        centralwidget = QWidget(self)
        gridLayout = QGridLayout(centralwidget)

        v_Layout1 = QVBoxLayout()
        v_Layout2 = QVBoxLayout()
        h_Layout1 = QHBoxLayout()

        v_Layout1.setContentsMargins(12, 19, 5, -1)
        v_Layout2.setContentsMargins(-1, 4, 6, -1)

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
            clicked=self.venv_wizard.exec_
        )

        #self.manageVenvButton = QPushButton(
            #"Manage Venvs", centralwidget,
            #statusTip="Manage virtual environments"
            #clicked=self.openManager
        #)

        self.exitButton = QPushButton(
            "Quit", centralwidget,
            statusTip="Quit Application",
            clicked=self.close
        )

        self.changeDirToolButton = QToolButton(
            icon=folder_icon,
            toolTip="Switch directory",
            statusTip="Select another directory",
            clicked=self.select_folder
        )
        self.changeDirToolButton.setFixedSize(30, 30)

        self.dirLineEdit = QLineEdit()

        #]===================================================================[#
        # spacer between manage button and exit button
        spacerItem1 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        #]===================================================================[#

        v_Layout2.addWidget(self.logo)
        v_Layout2.addWidget(self.addButton)
        v_Layout2.addWidget(self.newVenvButton)
        #v_Layout2.addWidget(self.manageVenvButton)
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
        v_HeaderTV1.setDefaultSectionSize(27)
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
        venvTable = VenvTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            refresh=self.popVenvTable  # signal
        )

        # adjust vertical headers
        v_HeaderTV2 = venvTable.verticalHeader()
        v_HeaderTV2.setDefaultSectionSize(27)
        v_HeaderTV2.hide()

        # adjust (horizontal) headers
        h_HeaderTV2 = venvTable.horizontalHeader()
        h_HeaderTV2.setDefaultAlignment(Qt.AlignLeft)
        h_HeaderTV2.setDefaultSectionSize(180)
        h_HeaderTV2.setStretchLastSection(True)

        # set table view model
        self.modelTV2 = QStandardItemModel(0, 2, centralwidget)
        self.modelTV2.setHorizontalHeaderLabels(
            ["Venv Name", "Version"]
        )
        venvTable.setModel(self.modelTV2)

        # add widgets to layout
        v_Layout1.addWidget(interprTableLabel)
        v_Layout1.addWidget(interprTable)
        v_Layout1.addItem(spacerItem2)
        v_Layout1.addLayout(h_Layout1)
        h_Layout1.addWidget(venvTableLabel)
        h_Layout1.addWidget(self.changeDirToolButton)
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
            shortcut="Ctrl+N", triggered=self.venv_wizard.exec_
        )

        #self.actManageVenvs = QAction(
            #manage_icon, "&Manage Venvs", self,
            #statusTip="Manage your virtual environments",
            #shortcut="Ctrl+M", #triggered=self.openManager
        #)

        self.actSelectDefaultDir = QAction(
            settings_icon, "Change active &directory", self,
            statusTip="Change active directory",
            shortcut="Ctrl+D", triggered=self.select_folder
        )

        self.actExit = QAction(
            exit_icon, "&Quit", self,
            statusTip="Quit application",
            shortcut="Ctrl+Q", triggered=self.close
        )

        self.actAbout = QAction(
            info_icon, "&About", self,
            statusTip="About VenviPy",
            shortcut="Ctrl+B", triggered=self.appInfo.exec_
        )

        # add actions to menus
        self.menuVenv.addAction(self.actAddInterpreter)
        self.menuVenv.addSeparator()
        self.menuVenv.addAction(self.actNewVenv)
        #self.menuVenv.addAction(self.actManageVenvs)
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
        messageText = (
            "No suitable Python installation found!\n\n"
            "Please specify the path to a Python (>=3.3) \n"
            "installation or click Continue to go on anyway.\n\n"
        )

        self.messageBox = QMessageBox(
            QMessageBox.Critical, "VenviPy Launcher",
            messageText, QMessageBox.NoButton, self
        )

        self.messageBox.addButton("&Search", QMessageBox.AcceptRole)
        self.messageBox.addButton("&Continue", QMessageBox.RejectRole)

        if not get_python_installs():
            #print("[WARNING]: No suitable Python installation found!")

            if self.messageBox.exec_() == QMessageBox.AcceptRole:
                # let user specify path to an interpreter
                self.selectInterpreter()


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


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
                [bin_file, "-V"],
                stdout=PIPE,
                text="utf-8"
            )

            out, _ = res.communicate()
            version = out.strip()
            path = file_name[0]

            # populate the table
            self.modelTV1.insertRow(0)
            self.modelTV1.setItem(0, 0, QStandardItem(version))
            self.modelTV1.setItem(0, 1, QStandardItem(path))

            # pass the selected interpreter to the wizard's QComboBox
            self.venv_wizard.basicSettings.interprComboBox.addItem(
                f"{version}  ->  {path}", path
            )


    def popInterprTable(self):
        """
        Populate the interpreter table view.
        """
        if get_python_installs():
            self.modelTV1.setRowCount(0)

            for info in get_python_installs():
                self.modelTV1.insertRow(0)

                for i, text in enumerate((info.py_version, info.py_path)):
                    self.modelTV1.setItem(0, i, QStandardItem(text))

                #print(f"[PYTHON]: {info}")


    def popVenvTable(self):
        """
        Populate the venv table view.
        """
        self.modelTV2.setRowCount(0)

        for info in get_active_dir():
            self.modelTV2.insertRow(0)

            for i, text in enumerate((info.venv_name, info.venv_version)):
                self.modelTV2.setItem(0, i, QStandardItem(text))

            #print(f"[VENV]: {info}")


    def select_folder(self):
        """
        Select the active folder shown in venv table.
        """
        directory = QFileDialog.getExistingDirectory()
        self.dirLineEdit.setText(directory)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        default_file = os.path.join(current_dir, "resources", "default")
        active_folder = self.dirLineEdit.text()

        if self.dirLineEdit.text() != "":
            with open(default_file, "w") as f:
                f.write(active_folder)
                #print(
                    #f"[INFO]: Setting active venv directory to '{active_folder}'"
                #)

            self.popVenvTable()



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    mainUI = Ui_MainWindow()
    mainUI.popInterprTable()
    mainUI.popVenvTable()
    mainUI.show()

    sys.exit(app.exec_())
