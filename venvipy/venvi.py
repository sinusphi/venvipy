# -*- coding: utf-8 -*-
"""
The main module of VenviPy.
"""
import sys
import os
from pathlib import Path

# need to set the correct cwd
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
os.chdir(CURRENT_DIR)

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

from get_data import (
    get_python_installs,
    get_active_dir,
    get_active_dir_str
)
from dialogs import InfoAboutVenviPy
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

        # refresh venv table when wizard closed
        self.venv_wizard.refresh.connect(self.pop_venv_table)

        # refresh interpreter table when selecting a custom one in wizard menu
        self.venv_wizard.update_table.connect(self.pop_interpreter_table)

        # populate the combo box in wizard menu
        self.venv_wizard.basic_settings.pop_combo_box()


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

        self.search_pypi_button = QPushButton(
            "&Search PyPI",
            centralwidget,
            statusTip="Search the Python Package Index",
            clicked=self.search_pypi
        )

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
        self.venv_table_label = QLabel(centralwidget)

        # venv table
        self.venv_table = VenvTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            refresh=self.pop_venv_table
        )

        # adjust vertical headers
        v_header_venv_table = self.venv_table.verticalHeader()
        v_header_venv_table.setDefaultSectionSize(27)
        v_header_venv_table.hide()

        # adjust (horizontal) headers
        h_header_venv_table = self.venv_table.horizontalHeader()
        h_header_venv_table.setDefaultAlignment(Qt.AlignLeft)
        h_header_venv_table.setDefaultSectionSize(180)
        h_header_venv_table.setStretchLastSection(True)

        # set table view model
        self.model_venv_table = QStandardItemModel(0, 2, centralwidget)
        self.model_venv_table.setHorizontalHeaderLabels(
            ["Venv Name", "Version"]
        )
        self.venv_table.setModel(self.model_venv_table)

        # add widgets to layout
        v_layout_1.addWidget(interpreter_table_label)
        v_layout_1.addWidget(interpreter_table)
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

        self.action_search_pypi = QAction(
            manage_icon,
            "&Search PyPI",
            self,
            statusTip="Search the Python Package Index",
            shortcut="Ctrl+S",
            triggered=self.search_pypi
        )

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

        menu_extras = QMenu("&Extras", menu_bar)
        menu_extras.addAction(self.action_search_pypi)
        menu_bar.addAction(menu_extras.menuAction())

        menu_help = QMenu("&Help", menu_bar)
        menu_help.addAction(self.action_about_venvipy)
        menu_help.addAction(self.action_about_qt)

        menu_bar.addAction(menu_help.menuAction())

        msg_txt = (
            "No suitable Python installation found!\n\n"
            "Please specify the path to a Python (>=3.3) \n"
            "installation or click 'Continue' to go on anyway.\n\n"
        )
        self.msg_box = QMessageBox(
            QMessageBox.Critical,
            "VenviPy",
            msg_txt, QMessageBox.NoButton,
            self
        )

        if not get_python_installs():
            self.launching_without_python()


    def info_about_qt(self):
        """Open the "About Qt" dialog."""
        QMessageBox.aboutQt(self)


    def launching_without_python(self):
        print("[WARNING]: No suitable Python installation found!")
        self.enable_features(False)
        self.msg_box.addButton("&Select", QMessageBox.AcceptRole)
        self.msg_box.addButton("&Continue", QMessageBox.RejectRole)
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
        Stop all threads, then close the application.
        """
        self.venv_wizard.basic_settings.thread.exit()
        self.venv_table.thread.exit()
        self.close()


    def add_interpreter(self):
        """
        Add a custom interpreter.
        """
        if self.venv_wizard.basic_settings.select_python() != "":
            self.enable_features(True)


    def enable_features(self, state):
        self.search_pypi_button.setEnabled(state)
        self.action_search_pypi.setEnabled(state)
        self.venv_table.setEnabled(state)


    @pyqtSlot(str)
    def pop_interpreter_table(self, custom_path):
        """
        Populate the interpreter table view.
        """
        if custom_path != "":
            if get_python_installs(custom_path):
                self.model_interpreter_table.setRowCount(0)

            for info in get_python_installs(custom_path):
                self.model_interpreter_table.insertRow(0)
                for i, text in enumerate((info.py_version, info.py_path)):
                    self.model_interpreter_table.setItem(
                        0, i, QStandardItem(text)
                    )
                print(f"[PYTHON]: {info}")
        else:
            if get_python_installs():
                self.model_interpreter_table.setRowCount(0)

            for info in get_python_installs():
                self.model_interpreter_table.insertRow(0)
                for i, text in enumerate((info.py_version, info.py_path)):
                    self.model_interpreter_table.setItem(
                        0, i, QStandardItem(text)
                    )
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


    def update_label(self):
        active_dir_str = get_active_dir_str()
        self.venv_table_label.setText(
            f'<span style="font-size: 13pt;">\
                <b>Virtual environments:</b>\
            </span>\
            <span style="font-size: 13pt; color: #0059ff;">\
                {active_dir_str}\
            </span>'
        )


    def select_active_dir(self):
        """
        Select the active directory of which the content
        should be shown in venv table.
        """
        directory = QFileDialog.getExistingDirectory(
            self,
            "Open directory containing virtual environments"
        )
        self.directory_line.setText(directory)

        active_file = os.path.expanduser("~/.venvipy/active")
        active_dir = self.directory_line.text()

        if active_dir != "":
            if os.path.exists(active_file):
                with open(active_file, "w") as f:
                    f.write(active_dir)
                    print(
                        "[INFO]: Setting active dir to "
                        f"'{active_dir}'"
                    )
                self.pop_venv_table()
                self.update_label()


    def search_pypi(self):
        """
        Search the Python Package Index.
        """
        pass


def main():
    app = QApplication(sys.argv)
    os.system("clear")

    main_window = MainWindow()
    main_window.pop_interpreter_table(None)
    main_window.pop_venv_table()
    main_window.update_label()
    main_window.show()

    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
