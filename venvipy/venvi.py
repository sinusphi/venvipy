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
from functools import partial
from pathlib import Path

# need to set the correct cwd
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
os.chdir(CURRENT_DIR)

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSlot
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QStandardItemModel,
    QStandardItem,
    QAction
)
from PyQt6.QtWidgets import (
    QStyle,
    QMainWindow,
    QApplication,
    QDialog,
    QFileDialog,
    QLabel,
    QToolButton,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QInputDialog,
    QCheckBox,
    QMenuBar,
    QMenu,
    QStatusBar,
    QAbstractItemView,
    QMessageBox,
    QHBoxLayout,
    QLineEdit,
    QTabWidget,
    QWidgetAction
)

import venvipy_rc  # pylint: disable=unused-import
import get_data
import wizard
import bars
from styles import theme
from styles import custom
from pkg_installer import PackageInstaller
from pkg_manager import PackageManager
from dialogs import (
    InfoAboutVenviPy,
    LauncherDialog,
    show_launcher_apply_result
)
from platforms import get_platform
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
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("VenviPy")
        self.resize(1600, 880)
        self.setContentsMargins(4, 0, 4, 0)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))
        self.setStyleSheet(theme.dark)

        self.info_about_venvipy = InfoAboutVenviPy()
        self.venv_wizard = wizard.VenvWizard()
        self._wizard_refresh_tab = None

        # refresh venv table on wizard close
        self.venv_wizard.refresh.connect(self.refresh_wizard_tab)

        # refresh interpreter table if 'py-installs' changes
        self.venv_wizard.update_table.connect(self.pop_interpreter_table)

        self.pkg_installer = PackageInstaller()
        self.pkg_manager = PackageManager()


        #]===================================================================[#
        #] ICONS [#==========================================================[#
        #]===================================================================[#

        find_icon = QIcon.fromTheme("edit-find")
        #python_icon = QIcon(":/img/python.png")
        #manage_icon = QIcon.fromTheme("insert-object")
        #settings_icon = QIcon.fromTheme("preferences-system")

        new_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        )
        exit_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop)
        )
        folder_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        )
        qt_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton)
        )
        info_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        )
        self.new_folder_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        )
        self.reload_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.dir_open_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        )
        #delete_icon = QIcon(
        #    self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        #)


        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        centralwidget = QWidget(self)
        grid_layout = QGridLayout(centralwidget)

        v_layout_1 = QVBoxLayout()
        v_layout_2 = QVBoxLayout()
        v_layout_1.setContentsMargins(12, 19, 5, -1)
        v_layout_2.setContentsMargins(-1, 4, 6, -1)

        # python logo
        self.logo = QLabel(centralwidget)
        self.logo.setPixmap(QPixmap(":/img/pypower.png"))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignRight)


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
            clicked=self.launch_venv_wizard
        )
        self.new_venv_button.setMinimumSize(QSize(135, 0))

        self.exit_button = QPushButton(
            "Quit",
            centralwidget,
            statusTip="Quit Application",
            clicked=self.on_close
        )

        # use line edit to store the str
        self.directory_line = QLineEdit()
        self.venv_tab_map = {}
        self.venv_tabs_data = []
        self.tab_save_pref = {
            "always_save_tabs": False,
            "ask_before_saving_tabs": True
        }

        #]===================================================================[#
        # spacer between manage button and exit button
        spacer_item_1 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        #]===================================================================[#

        v_layout_2.addWidget(self.logo)
        v_layout_2.addWidget(self.add_interpreter_button)
        v_layout_2.addWidget(self.new_venv_button)
        v_layout_2.addItem(spacer_item_1)
        v_layout_2.addWidget(self.exit_button)

        grid_layout.addLayout(v_layout_2, 0, 1, 1, 1)


        #]===================================================================[#
        #] TABLES [#=========================================================[#
        #]===================================================================[#

        # interpreter table header
        interpreter_table_title = QLabel(
            custom.interpreter_table_title_text,
            centralwidget
        )

        # interpreter table
        self.interpreter_table = InterpreterTable(
            centralwidget,
            selectionBehavior=QAbstractItemView.SelectionBehavior.SelectRows,
            editTriggers=QAbstractItemView.EditTrigger.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            drop_item=self.pop_interpreter_table
        )

        # hide vertical header
        self.interpreter_table.verticalHeader().hide()

        # adjust (horizontal) headers
        h_header_interpreter_table = self.interpreter_table.horizontalHeader()
        h_header_interpreter_table.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
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
            20, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        #]===================================================================[#

        self.venv_tabs = QTabWidget(centralwidget)
        self.venv_tabs.currentChanged.connect(self.on_venv_tab_changed)
        self.venv_tabs.setTabsClosable(True)
        self.venv_tabs.tabCloseRequested.connect(self.close_venv_tab)
        self.venv_tabs.tabBarDoubleClicked.connect(self.rename_venv_tab)
        tab_bar = self.venv_tabs.tabBar()
        tab_bar.setMovable(True)
        tab_bar.tabMoved.connect(self.on_venv_tab_moved)

        # add widgets to layout
        v_layout_1.addWidget(interpreter_table_title)
        v_layout_1.addWidget(self.interpreter_table)
        v_layout_1.addItem(spacer_item_2)
        v_layout_1.addWidget(self.venv_tabs)

        grid_layout.addLayout(v_layout_1, 0, 0, 1, 1)

        self.setCentralWidget(centralwidget)
        restored = self.restore_tabs_from_state()
        if not restored:
            initial_dir = get_data.get_active_dir_str()
            initial_title = self.next_venv_tab_title(initial_dir)
            self.create_venv_tab(initial_title, initial_dir)

        self.on_venv_tab_changed(self.venv_tabs.currentIndex())


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
            triggered=self.launch_venv_wizard
        )

        self.action_select_active_dir = QAction(
            folder_icon,
            "Change active &directory",
            self,
            statusTip="Change active directory",
            shortcut="Ctrl+D",
            triggered=self.select_active_dir
        )

        self.action_create_launcher = QAction(
            folder_icon,
            "Create launcher",
            self,
            statusTip="Create or remove launcher shortcuts",
            triggered=self.open_launcher_dialog
        )

        self.always_save_tabs_checkbox = QCheckBox("Always save tabs", self)
        self.always_save_tabs_checkbox.setChecked(
            self.tab_save_pref.get("always_save_tabs", False)
        )
        self.always_save_tabs_checkbox.toggled.connect(
            self.toggle_always_save_tabs
        )
        self.action_always_save_tabs = QWidgetAction(self)
        self.action_always_save_tabs.setDefaultWidget(
            self.always_save_tabs_checkbox
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
            triggered=self.info_about_venvipy.exec
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

        self.title_bar = bars.TitleBar(self)
        menu_container = QWidget(self)
        menu_container.setObjectName("menuContainer")

        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(2, 0, 2, 0)
        menu_layout.setSpacing(2)

        title_separator = QWidget(self)
        title_separator.setObjectName("titleSeparator")
        title_separator.setFixedHeight(1)

        menu_layout.addWidget(self.title_bar)
        menu_layout.addWidget(title_separator)
        menu_layout.addWidget(menu_bar)

        self.setMenuWidget(menu_container)

        menu_venv = QMenu("&Venv", menu_bar)
        menu_venv.addAction(self.action_add_interpreter)
        menu_venv.addSeparator()
        menu_venv.addAction(self.action_new_venv)
        menu_venv.addAction(self.action_select_active_dir)
        menu_venv.addAction(self.action_create_launcher)
        menu_venv.addAction(self.action_always_save_tabs)
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

        QtCore.QTimer.singleShot(
            0,
            self.maybe_show_first_launch_launcher_dialog
        )


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
            QMessageBox.Icon.Critical,
            "VenviPy",
            msg_txt, QMessageBox.StandardButton.NoButton,
            self
        )
        select_button = self.msg_box.addButton(
            "&Select", QMessageBox.ButtonRole.AcceptRole
        )
        self.msg_box.addButton("&Continue", QMessageBox.ButtonRole.RejectRole)

        self.msg_box.exec()
        if self.msg_box.clickedButton() == select_button:
            # let user specify path to an interpreter
            self.add_interpreter()
        else:
            self.enable_features(False)


    def center(self):
        """Center window.
        """
        qr = self.frameGeometry()
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            cp = screen.availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())


    def on_close(self):
        """Request application shutdown.
        """
        self.close()


    def closeEvent(self, event):
        """Handle persistence and shutdown when the window closes.
        """
        if not self.handle_tab_persistence_on_close():
            event.ignore()
            return

        self.shutdown_threads()
        event.accept()
        super().closeEvent(event)


    def shutdown_threads(self):
        """Stop background threads gracefully.
        """
        if hasattr(self.venv_wizard, "basic_settings"):
            thread = getattr(self.venv_wizard.basic_settings, "thread", None)
            if thread is not None:
                thread.exit()

        for tab_data in self.venv_tabs_data:
            table = tab_data.get("table")
            if table is not None and hasattr(table, "thread"):
                table.thread.exit()


    def handle_tab_persistence_on_close(self):
        """Ask whether to save tabs (or auto-save) when closing.
        """
        tab_count = self.venv_tabs.count()

        if self.tab_save_pref.get("always_save_tabs"):
            self.save_tabs_state()
            return True

        if not self.tab_save_pref.get("ask_before_saving_tabs", True):
            # Safety net: default to saving when prompting is disabled.
            self.save_tabs_state()
            return True

        # Only prompt if there is at least one tab open.
        if tab_count == 0:
            return True
        # Skip prompt when no tab has a directory loaded.
        any_dir_loaded = False
        for i in range(tab_count):
            tab_widget = self.venv_tabs.widget(i)
            tab_data = self.get_tab_data(tab_widget)
            if tab_data and tab_data.get("path"):
                any_dir_loaded = True
                break
        if not any_dir_loaded:
            return True

        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Save tabs?",
            (
                f"There {'is' if tab_count == 1 else 'are'} "
                f"{tab_count} open tab{'s' if tab_count != 1 else ''}.\n"
                "Save them for the next start?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            self
        )

        dont_ask_checkbox = QCheckBox("Don't ask again. Always save tabs.")
        msg_box.setCheckBox(dont_ask_checkbox)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Cancel:
            return False

        if result == QMessageBox.StandardButton.No:
            state = self.collect_tabs_state()
            state["tabs"] = []
            state["active_index"] = 0
            get_data.save_tabs_state(state)
            self.set_active_dir("")
            return True

        if dont_ask_checkbox.isChecked():
            self.tab_save_pref["always_save_tabs"] = True
            self.tab_save_pref["ask_before_saving_tabs"] = False

        if result == QMessageBox.StandardButton.Yes:
            self.save_tabs_state()

        return True


    def toggle_always_save_tabs(self, enabled):
        """Toggle automatic tab persistence on app close.
        """
        self.tab_save_pref["always_save_tabs"] = bool(enabled)
        self.tab_save_pref["ask_before_saving_tabs"] = not bool(enabled)
        self.save_tabs_state()


    def apply_launcher_state_with_feedback(self, desired_state):
        """Apply launcher changes and show success/error feedback dialog.
        """
        platform = get_platform()
        result = platform.apply_launcher_state(desired_state)
        show_launcher_apply_result(result, parent=self)
        return result

    def _save_launcher_state_preferences(
        self,
        launcher_state=None,
        prompt_shown=None
    ):
        """Persist launcher preferences and first-launch prompt state.
        """
        state = get_data.load_launcher_state()

        if isinstance(launcher_state, dict):
            for key in (
                "desktop_venvipy",
                "desktop_wizard",
                "startmenu_venvipy",
                "startmenu_wizard",
            ):
                state[key] = bool(launcher_state.get(key, False))

        if prompt_shown is not None:
            state["prompt_shown"] = bool(prompt_shown)

        get_data.save_launcher_state(state)

    def maybe_show_first_launch_launcher_dialog(self):
        """Show launcher dialog once on first application launch.
        """
        launcher_state = get_data.load_launcher_state()
        if launcher_state.get("prompt_shown", False):
            return
        self.open_launcher_dialog(mark_prompt_shown=True)

    def open_launcher_dialog(self, mark_prompt_shown=False):
        """Open launcher management dialog with current launcher state.
        """
        platform = get_platform()
        current_state = platform.get_launcher_state()
        launcher_dialog = LauncherDialog(initial_state=current_state, parent=self)
        if launcher_dialog.exec() != QDialog.DialogCode.Accepted:
            if mark_prompt_shown:
                self._save_launcher_state_preferences(
                    launcher_state=current_state,
                    prompt_shown=True
                )
            return None

        desired_state = launcher_dialog.state()
        result = self.apply_launcher_state_with_feedback(desired_state)
        self._save_launcher_state_preferences(
            launcher_state=result.get("after", desired_state),
            prompt_shown=True if mark_prompt_shown else None
        )
        return result


    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if hasattr(self, "title_bar"):
                self.title_bar.update_maximize_icon()


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
        for tab_data in self.venv_tabs_data:
            tab_data["table"].setEnabled(state)


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


    def pop_venv_table(self, tab_widget=None):
        """Populate the venv table view.
        """
        tab_data = self.get_tab_data(tab_widget)
        if tab_data is None:
            return

        model = tab_data["model"]
        model.setRowCount(0)

        for info in get_data.get_venvs(tab_data["path"]):
            model.insertRow(0)
            for i, text in enumerate((
                    info.venv_name,
                    info.venv_version,
                    info.site_packages,
                    info.is_installed,
                    info.venv_comment
            )):
                model.setItem(0, i, QStandardItem(text))

        model.sort(0, Qt.SortOrder.AscendingOrder)


    def update_label(self, tab_data=None):
        """
        Show the currently selected folder containing
        virtual environments.
        """
        tab_data = self.get_tab_data(tab_data)
        if tab_data is None:
            return

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
                {tab_data["path"]}\
            </span>'
        )

        if tab_data["path"] != "":
            tab_data["label"].setText(f"{head}{with_folder}")
        else:
            tab_data["label"].setText(f"{head}{no_folder}")


    def select_active_dir(self, tab_widget=None):
        """
        Select the active directory of which the content
        should be shown in venv table.
        """
        tab_data = self.get_tab_data(tab_widget)
        if tab_data is None:
            return

        current_dir = tab_data["path"] or get_data.get_active_dir_str()

        directory = QFileDialog.getExistingDirectory(
            self,
            "Open a folder containing virtual environments",
            directory=current_dir
        )
        self.directory_line.setText(directory)
        active_dir = self.directory_line.text()

        if active_dir != "":
            tab_data["path"] = active_dir
            self.set_active_dir(active_dir)
            self.pop_venv_table(tab_data["widget"])
            self.update_label(tab_data)


    def add_venv_tab(self):
        """Create a new venv tab for another directory.
        """
        current_dir = get_data.get_active_dir_str()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Open a folder containing virtual environments",
            directory=current_dir
        )
        if directory != "":
            if self.venv_tabs.count() == 1:
                current_data = self.get_tab_data()
                if current_data and not current_data.get("path"):
                    title = self.next_venv_tab_title(directory)
                    current_data["path"] = directory
                    current_data["title"] = title
                    current_index = self.venv_tabs.currentIndex()
                    if current_index >= 0:
                        self.venv_tabs.setTabText(current_index, title)
                    self.set_active_dir(directory)
                    self.pop_venv_table(current_data["widget"])
                    self.update_label(current_data)
                    return

            title = self.next_venv_tab_title(directory)
            tab_data = self.create_venv_tab(title, directory)
            self.venv_tabs.setCurrentWidget(tab_data["widget"])
            self.set_active_dir(directory)


    def create_venv_tab(self, title, active_dir):
        """Create a new venv tab.
        """
        tab_widget = QWidget(self)
        tab_layout = QVBoxLayout(tab_widget)
        header_layout = QHBoxLayout()

        label = QLabel(tab_widget)
        new_venv_button = QToolButton(
            text="+",
            toolTip="New venv",
            statusTip="Create a new virtual environment",
            clicked=self.launch_venv_wizard
        )
        new_venv_button.setFixedSize(30, 30)

        add_tab_button = QToolButton(
            icon=self.new_folder_icon,
            toolTip="Add a venv tab",
            statusTip="Open a new venv tab",
            clicked=self.add_venv_tab
        )
        add_tab_button.setFixedSize(30, 30)

        reload_button = QToolButton(
            icon=self.reload_icon,
            toolTip="Reload",
            statusTip="Reload venv table content",
            clicked=partial(self.pop_venv_table, tab_widget)
        )
        reload_button.setFixedSize(30, 30)

        active_dir_button = QToolButton(
            icon=self.dir_open_icon,
            toolTip="Switch directory",
            statusTip="Select another directory",
            clicked=partial(self.select_active_dir, tab_widget)
        )
        active_dir_button.setFixedSize(30, 30)

        header_layout.addWidget(label)
        header_layout.addStretch(1)
        header_layout.addWidget(new_venv_button)
        header_layout.addWidget(add_tab_button)
        header_layout.addWidget(reload_button)
        header_layout.addWidget(active_dir_button)

        venv_table = VenvTable(
            tab_widget,
            selectionBehavior=QAbstractItemView.SelectionBehavior.SelectRows,
            editTriggers=QAbstractItemView.EditTrigger.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            refresh=partial(self.pop_venv_table, tab_widget),
            start_installer=self.pkg_installer.launch,
            start_pkg_manager=self.pkg_manager.launch
        )

        # hide vertical header
        venv_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header_venv_table = venv_table.horizontalHeader()
        h_header_venv_table.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        h_header_venv_table.setStretchLastSection(True)

        # set table view model
        model_venv_table = QStandardItemModel(0, 4, tab_widget)
        model_venv_table.setHorizontalHeaderLabels([
            "Venv",
            "Version",
            "Packages",
            "Installed",
            "Description"
        ])
        venv_table.setModel(model_venv_table)

        # adjust column width
        venv_table.setColumnWidth(0, 225)
        venv_table.setColumnWidth(1, 120)
        venv_table.setColumnWidth(2, 100)
        venv_table.setColumnWidth(3, 80)

        tab_layout.addLayout(header_layout)
        tab_layout.addWidget(venv_table)

        self.venv_tabs.addTab(tab_widget, title)
        tab_data = {
            "widget": tab_widget,
            "label": label,
            "table": venv_table,
            "model": model_venv_table,
            "path": active_dir,
            "title": title
        }
        self.venv_tabs_data.append(tab_data)
        self.venv_tab_map[tab_widget] = tab_data

        self.update_label(tab_data)
        self.pop_venv_table(tab_widget)

        return tab_data


    def restore_tabs_from_state(self):
        """Recreate tabs based on the last saved state, if any.
        """
        state = get_data.load_tabs_state() or {}

        self.tab_save_pref["always_save_tabs"] = bool(
            state.get("always_save_tabs", False)
        )
        self.tab_save_pref["ask_before_saving_tabs"] = bool(
            state.get("ask_before_saving_tabs", True)
        )
        if not self.tab_save_pref["ask_before_saving_tabs"]:
            self.tab_save_pref["always_save_tabs"] = True

        tabs = state.get("tabs") or []
        if not tabs:
            return False

        for tab in tabs:
            path = tab.get("path", "")
            title = tab.get("title") or self.next_venv_tab_title(path)
            self.create_venv_tab(title, path)

        active_index = state.get("active_index", 0)
        if 0 <= active_index < self.venv_tabs.count():
            self.venv_tabs.setCurrentIndex(active_index)

        return True


    def collect_tabs_state(self):
        """Gather current tab information for persistence.
        """
        tabs = []
        for i in range(self.venv_tabs.count()):
            tab_widget = self.venv_tabs.widget(i)
            tab_data = self.get_tab_data(tab_widget)
            if tab_data is None:
                continue
            tabs.append({
                "title": self.venv_tabs.tabText(i),
                "path": tab_data.get("path", "")
            })

        active_index = self.venv_tabs.currentIndex()
        if active_index < 0:
            active_index = 0

        return {
            "tabs": tabs,
            "active_index": active_index,
            "always_save_tabs": self.tab_save_pref.get("always_save_tabs", False),
            "ask_before_saving_tabs": self.tab_save_pref.get("ask_before_saving_tabs", True)
        }


    def save_tabs_state(self):
        """Persist current tabs and preferences.
        """
        state = self.collect_tabs_state()
        get_data.save_tabs_state(state)


    def rename_venv_tab(self, index):
        """Rename a venv tab via double-click.
        """
        if index < 0:
            return

        current_title = self.venv_tabs.tabText(index)
        new_title, ok = QInputDialog.getText(
            self,
            "Rename tab",
            "Tab name:",
            text=current_title
        )

        if not ok:
            return

        new_title = new_title.strip()
        if new_title == "":
            return

        self.venv_tabs.setTabText(index, new_title)

        tab_widget = self.venv_tabs.widget(index)
        tab_data = self.get_tab_data(tab_widget)
        if tab_data is not None:
            tab_data["title"] = new_title


    def on_venv_tab_moved(self, _from, _to):
        """Keep internal tab order in sync with the UI order.
        """
        new_order = []
        for i in range(self.venv_tabs.count()):
            tab_widget = self.venv_tabs.widget(i)
            tab_data = self.get_tab_data(tab_widget)
            if tab_data is not None:
                new_order.append(tab_data)

        self.venv_tabs_data = new_order


    def next_venv_tab_title(self, directory=None):
        """Return the default title for a new venv tab.
        """
        if directory:
            folder_name = Path(directory).name
            if folder_name:
                return folder_name
        return f"venv #{len(self.venv_tabs_data) + 1:02d}"


    def get_tab_data(self, tab_widget=None):
        """Return tab data for a widget (or the current tab).
        """
        if isinstance(tab_widget, dict):
            return tab_widget

        if tab_widget is None:
            tab_widget = self.venv_tabs.currentWidget()

        return self.venv_tab_map.get(tab_widget)


    def set_active_dir(self, active_dir):
        """Persist the active directory to disk.
        """
        get_data.ensure_active_dir()
        with open(get_data.ACTIVE_DIR, "w", encoding="utf-8") as f:
            f.write(active_dir)


    def on_venv_tab_changed(self, index):
        """Update active directory when switching tabs.
        """
        tab_widget = self.venv_tabs.widget(index)
        tab_data = self.get_tab_data(tab_widget)

        if tab_data is None:
            return

        self.set_active_dir(tab_data["path"])
        self.update_label(tab_data)


    def launch_venv_wizard(self):
        """Launch the venv wizard and remember the active tab.
        """
        tab_data = self.get_tab_data()
        self._wizard_refresh_tab = tab_data["widget"] if tab_data else None
        self.venv_wizard.exec()


    def refresh_wizard_tab(self):
        """Refresh the tab captured when launching the wizard.
        """
        tab_widget = self._wizard_refresh_tab

        if tab_widget is not None and tab_widget in self.venv_tab_map:
            self.pop_venv_table(tab_widget)
        else:
            self.pop_venv_table()

        self._wizard_refresh_tab = None


    def close_venv_tab(self, index):
        """Close a venv tab without confirmation.
        """
        if self.venv_tabs.count() <= 1:
            return

        tab_widget = self.venv_tabs.widget(index)

        if tab_widget is None:
            return

        tab_data = self.venv_tab_map.pop(tab_widget, None)

        if tab_data and tab_data in self.venv_tabs_data:
            self.venv_tabs_data.remove(tab_data)

        if tab_data:
            table = tab_data.get("table")

            if table and hasattr(table, "thread"):
                table.thread.quit()
                table.thread.wait()

            tab_widget.deleteLater()

        self.venv_tabs.removeTab(index)

        if self._wizard_refresh_tab == tab_widget:
            self._wizard_refresh_tab = None

        current_data = self.get_tab_data()

        if current_data:
            self.set_active_dir(current_data["path"])
            self.update_label(current_data)



def with_args():
    """Execute with command-line arguments.
    """
    # get full command-line arguments
    full_cmd_arguments = sys.argv

    # ignore the first
    argument_list = full_cmd_arguments[1:]

    # tell getopts() the parameters
    short_options = "Vdhwb"
    long_options = ["version", "debug", "help", "wizard", "wizard-debug"]

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
                f"VenviPy v{get_data.__version__}  "
                "( https://github.com/sinusphi/venvipy )\n\n"
                "    -h --help           Print this help message and exit\n"
                "    -d --debug          Print debugging output\n"
                "    -v --version        Print version and exit\n"
                "    -w --wizard         Launch venv wizard only\n"
                "    -b --wizard-debug   Launch venv wizard with debug output\n"
            )
            sys.exit(0)

        if arg in ("-d", "--debug"):
            # verbose output for debugging
            logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

        if arg in ("-V", "--version"):
            # print version, then exit
            print(f"VenviPy {get_data.__version__}")
            sys.exit(0)

        if arg in ("-w", "--wizard"):
            os.system("clear")
            app = QApplication(sys.argv)
            venv_wizard = wizard.VenvWizard()
            venv_wizard.basic_settings.pop_combo_box()
            venv_wizard.exec()
            sys.exit(0)

        if arg in ("-b", "--wizard-debug"):
            os.system("clear")
            logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
            app = QApplication(sys.argv)
            venv_wizard = wizard.VenvWizard()
            venv_wizard.basic_settings.pop_combo_box()
            venv_wizard.exec()
            sys.exit(0)


def main():
    with_args()

    app = QApplication(sys.argv)
    os.system("clear")

    main_window = MainWindow()
    get_data.update_pypi_index()
    get_data.get_python_installs(True)
    main_window.pop_interpreter_table()
    main_window.venv_wizard.basic_settings.pop_combo_box()
    main_window.pop_venv_table()
    main_window.update_label()
    main_window.show()

    sys.exit(app.exec())



if __name__ == "__main__":
    main()
