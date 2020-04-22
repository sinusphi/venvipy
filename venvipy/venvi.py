# -*- coding: utf-8 -*-
"""
The main module of VenviPy.
"""
from subprocess import Popen, PIPE
import sys
import os

from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QStandardItemModel,
    QStandardItem
)
from PyQt5.QtWidgets import (
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
    QTableView,
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

from get_data import get_python_installs, get_active_dir
from dialogs import AppInfoDialog
from tables import VenvTable
import wizard



class MainWindow(QMainWindow):
    """
    The main window.
    """
    def __init__(self):
        super().__init__()

        self.init_ui()


    def init_ui(self):
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

        self.app_info_dialog = AppInfoDialog()
        self.venv_wizard = wizard.VenvWizard()

        # refresh venv table when wizard closed
        self.venv_wizard.refresh.connect(self.pop_venv_table)


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

        self.search_pypi_button = QPushButton(
            "&Search PyPI",
            centralwidget,
            statusTip="Search the Python Package Index",
            clicked=self.search_pypi
        )

        self.exit_button = QPushButton(
            "Quit", centralwidget,
            statusTip="Quit Application",
            clicked=self.on_close
        )

        self.change_dir_button = QToolButton(
            icon=folder_icon,
            toolTip="Switch directory",
            statusTip="Select another directory",
            clicked=self.select_folder
        )
        self.change_dir_button.setFixedSize(30, 30)

        # use line edit to store the str
        self.directory_line = QLineEdit()

        #]===================================================================[#
        # spacer between manage button and exit button
        spacer_item_1 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        #]===================================================================[#

        v_layout_2.addWidget(self.logo)
        v_layout_2.addWidget(self.add_interpreter_button)
        v_layout_2.addWidget(self.new_venv_button)
        v_layout_2.addWidget(self.search_pypi_button)
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
        interpreter_table = QTableView(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True
        )

        # adjust vertical headers
        v_header_interpreter_table = interpreter_table.verticalHeader()
        v_header_interpreter_table.setDefaultSectionSize(27)
        v_header_interpreter_table.hide()

        # adjust (horizontal) headers
        h_header_interpreter_table = interpreter_table.horizontalHeader()
        h_header_interpreter_table.setDefaultAlignment(Qt.AlignLeft)
        h_header_interpreter_table.setDefaultSectionSize(180)
        h_header_interpreter_table.setStretchLastSection(True)

        # set table view model
        self.model_interpreter_table = QStandardItemModel(0, 2, centralwidget)
        self.model_interpreter_table.setHorizontalHeaderLabels(
            ["Version", "Path"]
        )
        interpreter_table.setModel(self.model_interpreter_table)

        #]===================================================================[#
        # spacer between interpreter table and venv table title
        spacer_item_2 = QSpacerItem(
            20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed
        )
        #]===================================================================[#

        # venv table header
        venv_table_label = QLabel(
            '<span style="font-size: 13pt;">\
                <b>Available virtual environments</b>\
            </span>',
            centralwidget
        )

        # venv table
        venv_table = VenvTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            refresh=self.pop_venv_table  # signal
        )

        # adjust vertical headers
        v_header_venv_table = venv_table.verticalHeader()
        v_header_venv_table.setDefaultSectionSize(27)
        v_header_venv_table.hide()

        # adjust (horizontal) headers
        h_header_venv_table = venv_table.horizontalHeader()
        h_header_venv_table.setDefaultAlignment(Qt.AlignLeft)
        h_header_venv_table.setDefaultSectionSize(180)
        h_header_venv_table.setStretchLastSection(True)

        # set table view model
        self.model_venv_table = QStandardItemModel(0, 2, centralwidget)
        self.model_venv_table.setHorizontalHeaderLabels(
            ["Venv Name", "Version"]
        )
        venv_table.setModel(self.model_venv_table)

        # add widgets to layout
        v_layout_1.addWidget(interpreter_table_label)
        v_layout_1.addWidget(interpreter_table)
        v_layout_1.addItem(spacer_item_2)
        v_layout_1.addLayout(h_layout_1)
        h_layout_1.addWidget(venv_table_label)
        h_layout_1.addWidget(self.change_dir_button)
        v_layout_1.addWidget(venv_table)

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

        self.action_search_pypi = QAction(
            manage_icon,
            "&Search PyPI",
            self,
            statusTip="Search the Python Package Index",
            shortcut="Ctrl+S",
            triggered=self.search_pypi
        )

        self.action_select_active_dir = QAction(
            settings_icon, "Change active &directory", self,
            statusTip="Change active directory",
            shortcut="Ctrl+D", triggered=self.select_folder
        )

        self.action_exit = QAction(
            exit_icon,
            "&Quit",
            self,
            statusTip="Quit application",
            shortcut="Ctrl+Q",
            triggered=self.on_close
        )

        self.action_about = QAction(
            info_icon,
            "&About",
            self,
            statusTip="About VenviPy",
            shortcut="Ctrl+B",
            triggered=self.app_info_dialog.exec_
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

        menu_extras = QMenu("&Extras", menu_bar)
        menu_extras.addAction(self.action_search_pypi)
        menu_bar.addAction(menu_extras.menuAction())

        menu_help = QMenu("&Help", menu_bar)
        menu_help.addAction(self.action_about)
        menu_bar.addAction(menu_help.menuAction())


        #]===================================================================[#
        #] MESSAGE BOX [#====================================================[#
        #]===================================================================[#

        # display a message box if no Python installation is found at all
        msg_txt = (
            "No suitable Python installation found!\n\n"
            "Please specify the path to a Python (>=3.3) \n"
            "installation or click Continue to go on anyway.\n\n"
        )

        self.msg_box = QMessageBox(
            QMessageBox.Critical, "VenviPy Launcher",
            msg_txt, QMessageBox.NoButton, self
        )

        self.msg_box.addButton("&Search", QMessageBox.AcceptRole)
        self.msg_box.addButton("&Continue", QMessageBox.RejectRole)

        if not get_python_installs():
            print("[WARNING]: No suitable Python installation found!")

            if self.msg_box.exec_() == QMessageBox.AcceptRole:
                # let user specify path to an interpreter
                self.add_interpreter()


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def on_close(self):
        """
        Stop the thread, then close the application.
        """
        self.venv_wizard.basic_settings.thread.exit()
        self.close()


    def add_interpreter(self):
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
            self.model_interpreter_table.insertRow(0)
            self.model_interpreter_table.setItem(0, 0, QStandardItem(version))
            self.model_interpreter_table.setItem(0, 1, QStandardItem(path))

            # pass the selected interpreter to the wizard's QComboBox
            self.venv_wizard.basic_settings.interpreter_combo_box.addItem(
                f"{version}  ->  {path}", path
            )


    def pop_interpreter_table(self):
        """
        Populate the interpreter table view.
        """
        if get_python_installs():
            self.model_interpreter_table.setRowCount(0)

            for info in get_python_installs():
                self.model_interpreter_table.insertRow(0)

                for i, text in enumerate((info.py_version, info.py_path)):
                    self.model_interpreter_table.setItem(0, i, QStandardItem(text))

                print(f"[PYTHON]: {info}")


    def pop_venv_table(self):
        """
        Populate the venv table view.
        """
        self.model_venv_table.setRowCount(0)

        for info in get_active_dir():
            self.model_venv_table.insertRow(0)

            for i, text in enumerate((info.venv_name, info.venv_version)):
                self.model_venv_table.setItem(0, i, QStandardItem(text))

            print(f"[VENV]: {info}")


    def select_folder(self):
        """
        Select the active directory of which the content
        should be shown in venv table.
        """
        directory = QFileDialog.getExistingDirectory(
            self, "Open directory containing virtual environments"
        )
        self.directory_line.setText(directory)

        current_dir = os.path.dirname(sys.argv[0])
        active_file = os.path.join(current_dir, "active")
        active_dir = self.directory_line.text()

        if active_dir != "":
            with open(active_file, "w") as f:
                f.write(active_dir)
                print(
                    "[INFO]: Setting active dir to "
                    f"'{active_dir}'"
                )
            self.pop_venv_table()


    def search_pypi(self):
        """
        Search the Python Package Index.
        """
        pass



if __name__ == "__main__":

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.pop_interpreter_table()
    main_window.pop_venv_table()
    main_window.show()

    sys.exit(app.exec_())
