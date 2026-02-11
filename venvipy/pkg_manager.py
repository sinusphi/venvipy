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
This module contains the package manager.
"""
import os
import logging
import webbrowser

from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
    QAction
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QApplication,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QAbstractItemView,
    QStyle,
    QTableView,
    QMenu,
    QFrame
)

import venvipy_rc  # pylint: disable=unused-import
import get_data
from dialogs import ConsoleDialog
from manage_pip import PipManager
from styles.theme import PACKAGE_DIALOG_QSS
from styles.custom import (
    package_manager_title_text,
    package_manager_venv_name_text,
)

logger = logging.getLogger(__name__)



class PackagesTable(QTableView):
    """
    Contains the Packages installed in the selected venv.
    """
    remove_triggered = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.delete_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )
        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        )


    def get_selected_item(self):
        """
        Return `str` from `name` column of the selected row.
        """
        listed_items = self.selectionModel().selectedRows()
        for index in listed_items:
            selected_item = index.data()
            return selected_item


    def contextMenuEvent(self, event):

        idx = self.indexAt(event.pos())

        if not idx.isValid():
            idx = self.currentIndex()

            if not idx.isValid():
                return

        self.selectRow(idx.row())

        menu = QMenu(self)

        remove_action = QAction(self.delete_icon, "&Remove package", self)
        remove_action.triggered.connect(self.remove_triggered.emit)
        menu.addAction(remove_action)

        # Keep this as the last context action in the package manager.
        open_pypi_action = QAction(self.info_icon, "&Open on PyPI", self)
        open_pypi_action.triggered.connect(self.open_on_pypi)
        menu.addAction(open_pypi_action)

        pos = event.globalPos()
        if pos.x() == 0 and pos.y() == 0:
            pos = self.viewport().mapToGlobal(self.visualRect(idx).center())

        menu.exec(pos)


    def open_on_pypi(self):
        """
        Open pypi.org and show the project page
        of the selected package.
        """
        url = "https://pypi.org/project"
        package = self.get_selected_item()
        if not package:
            return
        webbrowser.open("/".join([url, package]))



class PackageManager(QDialog):
    """
    The package manager dialog.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Package Manager")
        self.resize(975, 650)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))

        reload_icon = QIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )

        self._load_active_venv()
        self.console = ConsoleDialog()

        self.setStyleSheet(PACKAGE_DIALOG_QSS)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        horizontal_layout = QHBoxLayout(self)
        horizontal_layout.setContentsMargins(25, 18, 25, 22)

        grid_layout = QGridLayout()

        title_label = QLabel(package_manager_title_text)

        logo = QLabel()
        pixmap = QPixmap(":/img/pypi.png")
        logo_scaled = pixmap.scaled(
            92, 92, Qt.AspectRatioMode.KeepAspectRatio
        )
        logo.setPixmap(logo_scaled)

        self.subtitle_label_1 = QLabel()
        self._set_subtitle()
        self.subtitle_label_1.setContentsMargins(22, 0, 0, 0)

        subtitle_label_2 = QLabel(
            "Select one and right-click for available options. "
        )
        subtitle_label_2.setContentsMargins(22, 0, 0, 0)

        line_1 = QFrame(self)
        line_1.setFixedHeight(15)
        line_1.setFrameShape(QFrame.Shape.HLine)
        line_1.setFrameShadow(QFrame.Shadow.Sunken)

        pkg_name_label = QLabel("Package &name:")
        self.pkg_name_line = QLineEdit()
        pkg_name_label.setBuddy(self.pkg_name_line)

        self.reload_button = QPushButton(
            reload_icon,
            "&Reload",
            clicked=self.pop_packages_table
        )

        exit_button = QPushButton(
            "&Exit",
            clicked=self.on_close
        )

        # packages table
        self.packages_table = PackagesTable(
            selectionBehavior=QAbstractItemView.SelectionBehavior.SelectRows,
            editTriggers=QAbstractItemView.EditTrigger.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
        )
        self.packages_table.remove_triggered.connect(self.remove_package)

        # hide vertical header
        self.packages_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header = self.packages_table.horizontalHeader()
        h_header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        h_header.setStretchLastSection(True)

        # set table view model
        self.packages_table_model = QStandardItemModel(0, 4, self)
        self.packages_table.setModel(self.packages_table_model)

        line_2 = QFrame(self)
        line_2.setFixedHeight(8)
        line_2.setFrameShape(QFrame.Shape.HLine)
        line_2.setFrameShadow(QFrame.Shadow.Sunken)

        grid_layout.addWidget(title_label, 0, 0, 1, 2)
        grid_layout.addWidget(logo, 0, 2, 1, 1)
        grid_layout.addWidget(self.subtitle_label_1, 1, 0, 1, 2)
        grid_layout.addWidget(subtitle_label_2, 2, 0, 1, 2)
        grid_layout.addWidget(line_1, 3, 0, 1, 3)
        grid_layout.addWidget(pkg_name_label, 4, 0, 1, 1)
        grid_layout.addWidget(self.pkg_name_line, 4, 1, 1, 1)
        grid_layout.addWidget(self.reload_button, 4, 2, 1, 1)
        grid_layout.addWidget(self.packages_table, 5, 0, 1, 3)
        grid_layout.addWidget(line_2, 6, 0, 1, 3)
        grid_layout.addWidget(exit_button, 7, 2, 1, 1)

        horizontal_layout.addLayout(grid_layout)


    def center(self):
        """Center window.
        """
        qr = self.frameGeometry()
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            cp = screen.availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())


    def _load_active_venv(self):
        """Load active venv path from file.
        """
        try:
            with open(get_data.ACTIVE_VENV, "r", encoding="utf-8") as f:
                venv_path = f.read().strip()
        except FileNotFoundError:
            venv_path = ""

        split_venv_path = os.path.split(venv_path)
        self.venv_location = split_venv_path[0]
        self.venv_name = os.path.basename(venv_path)


    def _set_subtitle(self):
        """Update subtitle with current venv name.
        """
        venv_name = self.venv_name or "(none)"
        venv_name_colored = package_manager_venv_name_text(venv_name)
        self.subtitle_label_1.setText(
            f"Listed below are the Python packages installed in {venv_name_colored} "
        )


    def on_close(self):
        """Close window if no changes made, else ask to save a requirements.
        """
        self.close()


    def launch(self):
        """Launches the manager.
        """
        self._load_active_venv()
        self._set_subtitle()

        # count whether changes has been made to venv
        #self.venv_modified = 0

        # clear input
        self.packages_table_model.clear()
        self.pkg_name_line.clear()
        self.pkg_name_line.setFocus()

        # set text in column headers
        self.packages_table_model.setHorizontalHeaderLabels([
            "Name",
            "Version",
            "Author",
            "Description"
        ])

        # adjust column width
        self.packages_table.setColumnWidth(0, 200)  # name
        self.packages_table.setColumnWidth(1, 80)  # version
        self.packages_table.setColumnWidth(2, 150)  # release

        self.pop_packages_table()

        # launch the dialog via exec_() method
        self.exec()


    def remove_package(self):
        """Uninstall selected package from the current environment."""
        package = self.packages_table.get_selected_item()
        if not package:
            return

        msg_box_warning = QMessageBox.warning(
            self,
            "Confirm",
            (
                f"Remove package '{package}' from this environment?\n\n"
                "This will run: pip uninstall --yes"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if msg_box_warning != QMessageBox.StandardButton.Yes:
            return

        venv_path = os.path.join(self.venv_location, self.venv_name)
        if not os.path.isdir(venv_path):
            QMessageBox.information(self, "Info", "No active environment selected.")
            return

        logger.debug(f"Removing package '{package}'...")
        self.console.console_window.clear()
        self.console.setWindowTitle(f"Removing {package}")

        self.manager = PipManager(self.venv_location, self.venv_name)
        self.manager.started.connect(self.console.exec)
        self.manager.text_changed.connect(self.console.update_status)
        self.manager.finished.connect(self.pop_packages_table)
        self.manager.run_pip("uninstall", ["--yes", package])


    def pop_packages_table(self):
        """Fill (refresh) the packages table content.
        """
        self.packages_table_model.setRowCount(0)
        venv_path = os.path.join(self.venv_location, self.venv_name)
        if not os.path.isdir(venv_path):
            return

        for info in get_data.get_installed_packages(
            self.venv_location,
            self.venv_name
        ):
            self.packages_table_model.insertRow(0)

            for i, text in enumerate((
                info.pkg_name,
                info.pkg_version,
                info.pkg_info_2,
                info.pkg_summary
            )):
                self.packages_table_model.setItem(0, i, QStandardItem(text))
