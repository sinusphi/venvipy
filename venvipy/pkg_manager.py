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

from PyQt5.QtGui import (
    QIcon,
    QCursor,
    QPixmap,
    QStandardItem,
    QStandardItemModel
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QFileDialog,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDesktopWidget,
    QPushButton,
    QGridLayout,
    QMessageBox,
    QAbstractItemView,
    QStyle,
    QAction,
    QTableView,
    QMenu,
    QFrame
)

import venvipy_rc  # pylint: disable=unused-import
import get_data
import creator
from manage_pip import PipManager
from dialogs import ConsoleDialog

logger = logging.getLogger(__name__)



class PackagesTable(QTableView):
    """Contains the Packages installed in the selected venv.
    """
    context_triggered = pyqtSignal()
    refresh_packages = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.delete_icon = QIcon(
            self.style().standardIcon(QStyle.SP_TrashIcon)
        )
        self.info_icon = QIcon(
            self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        )

        self.console = ConsoleDialog()


    def get_selected_item(self):
        """
        Return `str` from `name` column of the selected row.
        """
        listed_items = self.selectionModel().selectedRows()
        for index in listed_items:
            selected_item = index.data()
            return selected_item


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # pop up only if clicking on a row
        if self.indexAt(event.pos()).isValid():
            context_menu.popup(QCursor.pos())

        update_action = QAction(
            QIcon.fromTheme("software-install"),
            "&Update package",
            self,
            statusTip="Update package via pip"
        )
        context_menu.addAction(update_action)
        # connect to install_package() in InstallPackages() in wizard
        update_action.triggered.connect(
            lambda: self.update_package(event)
        )

        open_pypi_action = QAction(
            self.info_icon,
            "&Open on PyPI",
            self,
            statusTip="Open on Python Package Index"
        )
        context_menu.addAction(open_pypi_action)
        open_pypi_action.triggered.connect(
            lambda: self.open_on_pypi(event)
        )


    def open_on_pypi(self, event):
        """
        Open pypi.org and show the project page
        of the selected package.
        """
        url = "https://pypi.org/project"
        package = self.get_selected_item()
        webbrowser.open("/".join([url, package]))


    def update_package(self, event):
        """Run pip --update 'package'.
        """
        self.setEnabled(False)

        # get the venv path
        with open(get_data.ACTIVE_VENV, "r", encoding="utf-8") as f:
            venv_path = f.read()

        split_venv_path = os.path.split(venv_path)
        self.venv_location = split_venv_path[0]
        self.venv_name = os.path.basename(venv_path)
        self.pkg = self.get_selected_item()

        msg_box_question = QMessageBox.question(self,
            "Confirm", f"Are you sure you want to update '{self.pkg}'?      ",
            QMessageBox.Cancel | QMessageBox.Yes
        )

        if msg_box_question == QMessageBox.Yes:
            self.console.setWindowTitle(f"Updating {self.pkg}")

            self.manager = PipManager(
                self.venv_location,
                f"'{self.venv_name}'"
            )
            # open the console when recieving signal from manager
            self.manager.started.connect(self.console.exec_)

            # start installing the selected package
            logger.debug(f"Updating '{self.pkg}'...")
            self.manager.run_pip(creator.cmds[0], [creator.opts[0], self.pkg])

            # display the updated output
            self.manager.text_changed.connect(self.console.update_status)

            # clear the content when closing console
            if self.console.close:
                self.console.console_window.clear()

        self.setEnabled(True)



class PackageManager(QDialog):
    """
    The package manager dialog.
    """
    refresh_packages = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Package Manager")
        self.resize(975, 650)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))

        reload_icon = QIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload)
        )

        # get the venv path from file
        try:
            with open(get_data.ACTIVE_VENV, "r", encoding="utf-8") as f:
                venv_path = f.read()
        except FileNotFoundError:
            venv_path = ""

        split_venv_path = os.path.split(venv_path)
        self.venv_location = split_venv_path[0]
        self.venv_name = os.path.basename(venv_path)


        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        horizontal_layout = QHBoxLayout(self)
        horizontal_layout.setContentsMargins(25, 18, 25, 22)

        grid_layout = QGridLayout()

        title_label = QLabel(
            '<p><span style="font-size:12.5pt;">\
                <b>Package Manager</b>\
            </span></p>'
        )

        logo = QLabel()
        pixmap = QPixmap(":/img/pypi.png")
        logo_scaled = pixmap.scaled(92, 92, Qt.KeepAspectRatio)
        logo.setPixmap(logo_scaled)

        venv_name_colored = (
            f'<b><span style="font-size: 13pt; color: #0059ff;">\
                {self.venv_name}\
            </span></B>'
        )

        subtitle_label_1 = QLabel(
            f"Listet below are the Python packages installed in {venv_name_colored} "
        )
        subtitle_label_1.setContentsMargins(22, 0, 0, 0)

        subtitle_label_2 = QLabel(
            "Select one and right-click for available options. "
        )
        subtitle_label_2.setContentsMargins(22, 0, 0, 0)

        line_1 = QFrame(self)
        line_1.setFixedHeight(15)
        line_1.setFrameShape(QFrame.HLine)
        line_1.setFrameShadow(QFrame.Sunken)

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
            selectionBehavior=QAbstractItemView.SelectRows,
            editTriggers=QAbstractItemView.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            #refresh_packages=self.pop_packages_table
            #context_triggered=self.install_package
            ### TODO: add signal
        )

        # hide vertical header
        self.packages_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header = self.packages_table.horizontalHeader()
        h_header.setDefaultAlignment(Qt.AlignLeft)
        h_header.setStretchLastSection(True)

        # set table view model
        self.packages_table_model = QStandardItemModel(0, 3, self)
        self.packages_table.setModel(self.packages_table_model)

        line_2 = QFrame(self)
        line_2.setFixedHeight(8)
        line_2.setFrameShape(QFrame.HLine)
        line_2.setFrameShadow(QFrame.Sunken)

        grid_layout.addWidget(title_label, 0, 0, 1, 2)
        grid_layout.addWidget(logo, 0, 2, 1, 1)
        grid_layout.addWidget(subtitle_label_1, 1, 0, 1, 2)
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
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def on_close(self):
        """Close window if no changes made, else ask to save a requirements.
        """
        self.close()


    def launch(self):
        """Launches the manager.
        """
        # count whether changes has been made to venv
        #self.venv_modified = 0

        # clear input
        self.packages_table_model.clear()
        self.pkg_name_line.clear()
        self.pkg_name_line.setFocus(True)

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

        # connect to pop_packages_table method and call it
        self.refresh_packages.connect(self.pop_packages_table)
        self.refresh_packages.emit()

        # launch the dialog via exec_() method
        self.exec_()


    def pop_packages_table(self):
        """Fill (refresh) the packages table content.
        """
        self.packages_table_model.setRowCount(0)

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
