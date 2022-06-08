#    VenviPy - A Virtual Environment Manager for Python.
#    Copyright (C) 2021 - Youssef Serestou - sinusphi.sq@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License or any
#    later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License version 3 named LICENSE is
#    in the root directory of VenviPy.
#    If not, see <https://www.gnu.org/licenses/licenses.en.html#GPL>.

# -*- coding: utf-8 -*-
"""
The main module of VenviPy.
"""
import sys
import os
import csv
import getopt
import logging
from pathlib import Path

# need to set the correct cwd
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
os.chdir(CURRENT_DIR)

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSlot
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QStandardItemModel,
    QStandardItem
)
from PyQt5.QtWidgets import (
    QStyle,
    QMainWindow,
    QApplication,
    QAction,
    QFileDialog,
    QLabel,
    QToolButton,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QMenuBar,
    QMenu,
    QStatusBar,
    QAbstractItemView,
    QMessageBox,
    QDesktopWidget,
    QHBoxLayout,
    QLineEdit
)

import venvipy_rc  # pylint: disable=unused-import
import get_data
import wizard
from pkg_installer import PackageInstaller
from dialogs import InfoAboutVenviPy
from tables import VenvTable, InterpreterTable

LOG_FORMAT = "[%(levelname)s] - { %(name)s }: %(message)s"
logger = logging.getLogger()



class MainWindow(QMainWindow):
    """
    The main window.
    """
    def __init__(self):
        super().__init__()

        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("VenviPy")
        self.resize(1150, 770)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))

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

        self.info_about_venvipy = InfoAboutVenviPy()
        self.venv_wizard = wizard.VenvWizard()

        # refresh venv table on wizard close
        self.venv_wizard.refresh.connect(self.pop_venv_table)

        # refresh interpreter table if 'py-installs' changes
        self.venv_wizard.update_table.connect(self.pop_interpreter_table)

        self.pkg_installer = PackageInstaller()

        #]===================================================================[#
        #] ICONS [#==========================================================[#
        #]===================================================================[#

        python_icon = QIcon(":/img/python.png")
        find_icon = QIcon.fromTheme("edit-find")
        manage_icon = QIcon.fromTheme("insert-object")
        settings_icon = QIcon.fromTheme("preferences-system")

        new_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogNewFolder)
        )
        exit_icon = QIcon(
            self.style().standardIcon(QStyle.SP_BrowserStop)
        )
        reload_icon = QIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload)
        )
        delete_icon = QIcon(
            self.style().standardIcon(QStyle.SP_TrashIcon)
        )
        folder_icon = QIcon(
            self.style().standardIcon(QStyle.SP_DirOpenIcon)
        )
        qt_icon = QIcon(
            self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        )
        info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )

        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        centralwidget = QWidget(self)
        grid_layout = QGridLayout(centralwidget)

        v_layout_1 = QVBoxLayout()
        v_layout_2 = QVBoxLayout()
        h_layout_1 = QHBoxLayout()

        v_layout_1.setContentsMargins(12, 19, 5, -1)
        v_layout_2.setContentsMargins(-1, 4, 6, -1)

        # python logo
        self.logo = QLabel(centralwidget)
        self.logo.setPixmap(QPixmap(":/img/pypower.png"))
        self.logo.setAlignment(Qt.AlignRight)


        #]===================================================================[#
        #] BUTTONS [#========================================================[#
        #]===================================================================[#

        self.add_interpreter_button = QPushButton(
            "Add &Interpreter",
            centralwidget,
            statusTip="Add an Interpreter",
            clicked=self.add_interpreter
        )
        self.add_interpreter_button.setMinimumSize(QSize(150, 0))

        self.new_venv_button = QPushButton(
            "&New Venv",
            centralwidget,
            statusTip="Create a new virtual environment",
            clicked=self.venv_wizard.exec_
        )
        self.new_venv_button.setMinimumSize(QSize(135, 0))

        #self.search_pypi_button = QPushButton(
            #"&Search PyPI",
            #centralwidget,
            #statusTip="Search the Python Package Index",
            #clicked=self.search_pypi
        #)

        self.exit_button = QPushButton(
            "Quit",
            centralwidget,
            statusTip="Quit Application",
            clicked=self.on_close
        )

        self.active_dir_button = QToolButton(
            icon=folder_icon,
            toolTip="Switch directory",
            statusTip="Select another directory",
            clicked=self.select_active_dir
        )
        self.active_dir_button.setFixedSize(30, 30)

        # use line edit to store the str
        self.directory_line = QLineEdit()

        self.reload_button = QToolButton(
            icon=reload_icon,
            toolTip="Reload",
            statusTip="Reload venv table content",
            clicked=self.pop_venv_table
        )
        self.reload_button.setFixedSize(30, 30)

        #]===================================================================[#
        # spacer between manage button and exit button
        spacer_item_1 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        #]===================================================================[#

        v_layout_2.addWidget(self.logo)
        v_layout_2.addWidget(self.add_interpreter_button)
        v_layout_2.addWidget(self.new_venv_button)
        #v_layout_2.addWidget(self.search_pypi_button)
        v_layout_2.addItem(spacer_item_1)
        v_layout_2.addWidget(self.exit_button)

        grid_layout.addLayout(v_layout_2, 0, 1, 1, 1)


        #]===================================================================[#
        #] TABLES [#=========================================================[#
        #]===================================================================[#

        # interpreter table header
        interpreter_table_label = QLabel(
            '<span style="font-size: 13pt;">\
                <b>Available Interpreters</b>\
            </span>',
            centralwidget
        )

        # interpreter table
        self.interpreter_table = InterpreterTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            drop_item=self.pop_interpreter_table
        )

        # hide vertical header
        self.interpreter_table.verticalHeader().hide()

        # adjust (horizontal) headers
        h_header_interpreter_table = self.interpreter_table.horizontalHeader()
        h_header_interpreter_table.setDefaultAlignment(Qt.AlignLeft)
        h_header_interpreter_table.setDefaultSectionSize(180)
        h_header_interpreter_table.setStretchLastSection(True)

        # set table view model
        self.model_interpreter_table = QStandardItemModel(0, 2, centralwidget)
        self.model_interpreter_table.setHorizontalHeaderLabels(
            ["Version", "Path"]
        )
        self.interpreter_table.setModel(self.model_interpreter_table)

        #]===================================================================[#
        # spacer between interpreter table and venv table title
        spacer_item_2 = QSpacerItem(
            20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed
        )
        #]===================================================================[#

        # venv table header
        self.venv_table_label = QLabel(centralwidget)

        # venv table
        self.venv_table = VenvTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            refresh=self.pop_venv_table,
            start_installer=self.pkg_installer.launch
        )

        # hide vertical header
        self.venv_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header_venv_table = self.venv_table.horizontalHeader()
        h_header_venv_table.setDefaultAlignment(Qt.AlignLeft)
        h_header_venv_table.setStretchLastSection(True)

        # set table view model
        self.model_venv_table = QStandardItemModel(0, 4, centralwidget)
        self.model_venv_table.setHorizontalHeaderLabels([
            "Venv",
            "Version",
            "Packages",
            "Installed",
            "Description"
        ])
        self.venv_table.setModel(self.model_venv_table)

        # adjust column width
        self.venv_table.setColumnWidth(0, 225)
        self.venv_table.setColumnWidth(1, 120)
        self.venv_table.setColumnWidth(2, 100)
        self.venv_table.setColumnWidth(3, 80)

        # add widgets to layout
        v_layout_1.addWidget(interpreter_table_label)
        v_layout_1.addWidget(self.interpreter_table)
        v_layout_1.addItem(spacer_item_2)
        v_layout_1.addLayout(h_layout_1)
        h_layout_1.addWidget(self.venv_table_label)
        h_layout_1.addWidget(self.reload_button)
        h_layout_1.addWidget(self.active_dir_button)
        v_layout_1.addWidget(self.venv_table)

        grid_layout.addLayout(v_layout_1, 0, 0, 1, 1)

        self.setCentralWidget(centralwidget)


        #]===================================================================[#
        #] ACTIONS [#========================================================[#
        #]===================================================================[#

        # create actions
        self.action_add_interpreter = QAction(
            find_icon,
            "Add &Interpreter",
            self,
            statusTip="Add an Interpreter",
            shortcut="Ctrl+I",
            triggered=self.add_interpreter
        )

        self.action_new_venv = QAction(
            new_icon,
            "&New Venv",
            self,
            statusTip="Create a new virtual environment",
            shortcut="Ctrl+N",
            triggered=self.venv_wizard.exec_
        )

        #self.action_search_pypi = QAction(
            #manage_icon,
            #"&Search PyPI",
            #self,
            #statusTip="Search the Python Package Index",
            #shortcut="Ctrl+S",
            #triggered=self.search_pypi
        #)

        self.action_select_active_dir = QAction(
            folder_icon,
            "Change active &directory",
            self,
            statusTip="Change active directory",
            shortcut="Ctrl+D",
            triggered=self.select_active_dir
        )

        self.action_exit = QAction(
            exit_icon,
            "&Quit",
            self,
            statusTip="Quit application",
            shortcut="Ctrl+Q",
            triggered=self.on_close
        )

        self.action_about_venvipy = QAction(
            info_icon,
            "&About VenviPy",
            self,
            statusTip="About VenviPy",
            shortcut="Ctrl+A",
            triggered=self.info_about_venvipy.exec_
        )

        self.action_about_qt = QAction(
            qt_icon,
            "About &Qt",
            self,
            statusTip="About Qt",
            shortcut="Ctrl+Q",
            triggered=self.info_about_qt
        )

        #]===================================================================[#
        #] MENUS [#==========================================================[#
        #]===================================================================[#

        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        menu_bar = QMenuBar(self)
        menu_bar.setGeometry(QRect(0, 0, 740, 24))
        self.setMenuBar(menu_bar)

        menu_venv = QMenu("&Venv", menu_bar)
        menu_venv.addAction(self.action_add_interpreter)
        menu_venv.addSeparator()
        menu_venv.addAction(self.action_new_venv)
        menu_venv.addAction(self.action_select_active_dir)
        menu_venv.addSeparator()
        menu_venv.addAction(self.action_exit)
        menu_bar.addAction(menu_venv.menuAction())

        menu_help = QMenu("&Help", menu_bar)
        menu_help.addAction(self.action_about_qt)
        menu_help.addAction(self.action_about_venvipy)
        menu_bar.addAction(menu_help.menuAction())

        # check if any Python is installed
        if os.path.exists(get_data.DB_FILE):
            with open(get_data.DB_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) < 2:
                self.launching_without_python()


    def launching_without_python(self):
        """If no Python was found run with features disabled.
        """
        logger.warning("No suitable Python interpreter found")
        msg_txt = (
            "No suitable Python interpreter found!\n\n"
            "Please specify the path to a Python (>=3.6) \n"
            "interpreter or click 'Continue' to go on anyway.\n\n"
        )
        self.msg_box = QMessageBox(
            QMessageBox.Critical,
            "VenviPy",
            msg_txt, QMessageBox.NoButton,
            self
        )
        self.msg_box.addButton("&Select", QMessageBox.AcceptRole)
        self.msg_box.addButton("&Continue", QMessageBox.RejectRole)

        if self.msg_box.exec_() == QMessageBox.AcceptRole:
            # let user specify path to an interpreter
            self.add_interpreter()
        else:
            self.enable_features(False)


    def center(self):
        """Center window.
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def on_close(self):
        """Stop all threads, then close the application.
        """
        self.venv_wizard.basic_settings.thread.exit()
        self.venv_table.thread.exit()
        self.close()


    def info_about_qt(self):
        """Open the "About Qt" dialog.
        """
        QMessageBox.aboutQt(self)


    def add_interpreter(self):
        """Add a custom interpreter.
        """
        if self.venv_wizard.basic_settings.select_python() != "":
            self.enable_features(True)


    def enable_features(self, state):
        """Enable or disable features.
        """
        self.venv_table.setEnabled(state)
        #self.search_pypi_button.setEnabled(state)
        #self.action_search_pypi.setEnabled(state)


    @pyqtSlot()
    def pop_interpreter_table(self):
        """Populate the interpreter table view.
        """
        get_data.ensure_dbfile()

        with open(get_data.DB_FILE, newline="", encoding="utf-8") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            self.model_interpreter_table.setRowCount(0)
            for info in reader:
                self.model_interpreter_table.insertRow(0)
                for i, text in enumerate(
                        (info["PYTHON_VERSION"], info["PYTHON_PATH"])
                    ):
                    self.model_interpreter_table.setItem(
                        0, i, QStandardItem(text)
                    )
        # also populate the combo box in wizard
        self.venv_wizard.basic_settings.pop_combo_box()


    def pop_venv_table(self):
        """Populate the venv table view.
        """
        self.model_venv_table.setRowCount(0)

        for info in get_data.get_selected_dir():
            self.model_venv_table.insertRow(0)
            for i, text in enumerate((
                    info.venv_name,
                    info.venv_version,
                    info.site_packages,
                    info.is_installed,
                    info.venv_comment
            )):
                self.model_venv_table.setItem(0, i, QStandardItem(text))

        self.model_venv_table.sort(0, QtCore.Qt.AscendingOrder)


    def update_label(self):
        """
        Show the currently selected folder containing
        virtual environments.
        """
        head = (
            '<span style="font-size: 13pt;">\
                    <b>Virtual environments:</b>\
                </span>'
        )
        no_folder = (
            '<span style="font-size: 13pt; color: #ff0000;">\
                <i> --- please select a folder containing virtual environments</i>\
            </span>'
        )
        with_folder = (
            f'<span style="font-size: 13pt; color: #0059ff;">\
                {get_data.get_active_dir_str()}\
            </span>'
        )

        if get_data.get_active_dir_str() != "":
            self.venv_table_label.setText(f"{head}{with_folder}")
        else:
            self.venv_table_label.setText(f"{head}{no_folder}")


    def select_active_dir(self):
        """
        Select the active directory of which the content
        should be shown in venv table.
        """
        directory = QFileDialog.getExistingDirectory(
            self,
            "Open a folder containing virtual environments"
        )
        self.directory_line.setText(directory)
        active_dir = self.directory_line.text()

        if active_dir != "":
            if os.path.exists(get_data.ACTIVE_DIR):
                with open(get_data.ACTIVE_DIR, "w", encoding="utf-8") as f:
                    f.write(active_dir)
                self.pop_venv_table()
                self.update_label()


    def search_pypi(self):
        """Search the Python Package Index.
        """
        pass


def with_args():
    """Execute with command-line arguments.
    """
    # get full command-line arguments
    full_cmd_arguments = sys.argv

    # ignore the first
    argument_list = full_cmd_arguments[1:]

    # tell getopts() the parameters
    short_options = "Vdh"
    long_options = ["version", "debug", "help"]

    # use try-except to cover errors
    try:
        arguments, values = getopt.getopt(
            argument_list, short_options, long_options
        )
    except getopt.error as e:
        # print error message and return error code
        err_msg = str(e)
        print(f"O{err_msg[1:]}")
        sys.exit(2)

    for arg, val in arguments:
        if arg in ("-h", "--help"):
            # show help message, then exit
            print(
                f"VenviPy {get_data.__version__}  "
                "( https://github.com/sinusphi/venvipy )\n\n"
                "    -h --help           Show this help message and exit\n"
                "    -d --debug          Print debugging output\n"
                "    -v --version        Print version and exit\n"
            )
            sys.exit(0)

        if arg in ("-d", "--debug"):
            # verbose output for debugging
            logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

        if arg in ("-V", "--version"):
            # print version, then exit
            print(f"VenviPy {get_data.__version__}")
            sys.exit(0)



def main():
    with_args()

    app = QApplication(sys.argv)
    os.system("clear")

    main_window = MainWindow()
    get_data.get_python_installs(True)
    main_window.pop_interpreter_table()
    main_window.venv_wizard.basic_settings.pop_combo_box()
    main_window.pop_venv_table()
    main_window.update_label()
    main_window.show()

    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
