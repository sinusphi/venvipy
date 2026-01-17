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
This module contains the package installer.
"""
import os
import logging
import webbrowser
from pathlib import Path
import subprocess

from PyQt6.QtGui import (
    QIcon,
    QCursor,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
    QAction
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
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
import creator
from dialogs import ConsoleDialog
from manage_pip import PipManager

from platforms import get_platform

logger = logging.getLogger(__name__)



class ResultsTable(QTableView):
    """Contains the results from PyPI.
    """
    context_triggered = pyqtSignal()

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

        install_action = QAction(QIcon.fromTheme("software-install"), "&Install module", self)
        install_action.triggered.connect(self.context_triggered.emit)
        menu.addAction(install_action)

        open_pypi_action = QAction(self.info_icon, "&Open on PyPI", self)
        open_pypi_action.triggered.connect(lambda: self.open_on_pypi(event))
        menu.addAction(open_pypi_action)

        pos = event.globalPos()
        if pos.x() == 0 and pos.y() == 0:
            pos = self.viewport().mapToGlobal(self.visualRect(idx).center())

        menu.exec(pos)


    def open_on_pypi(self, event):
        """
        Open pypi.org and show the project page
        of the selected package.
        """
        url = "https://pypi.org/project"
        package = self.get_selected_item()
        webbrowser.open("/".join([url, package]))



class PackageInstaller(QDialog):
    """
    The package installer dialog.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Package Installer")
        self.resize(975, 650)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))

        self.console = ConsoleDialog()

        #]===================================================================[#
        #] PAGE CONTENT [#===================================================[#
        #]===================================================================[#

        horizontal_layout = QHBoxLayout(self)
        horizontal_layout.setContentsMargins(25, 18, 25, 22)

        grid_layout = QGridLayout()

        title_label = QLabel(
            '<p><span style="font-size:12.5pt;">\
                <b>Package Installer</b>\
            </span></p>'
        )

        logo = QLabel()
        pixmap = QPixmap(":/img/pypi.png")
        logo_scaled = pixmap.scaled(
            92, 92, Qt.AspectRatioMode.KeepAspectRatio
        )
        logo.setPixmap(logo_scaled)

        subtitle_label_1 = QLabel(
            "      Here you can search for Python packages on PYPI "
            "and install them into your virtual environment. "
        )
        subtitle_label_2 = QLabel(
            "      Use right-click for more info. "
        )

        line_1 = QFrame(self)
        line_1.setFixedHeight(15)
        line_1.setFrameShape(QFrame.Shape.HLine)
        line_1.setFrameShadow(QFrame.Shadow.Sunken)

        pkg_name_label = QLabel("Package &name:")
        self.pkg_name_line = QLineEdit()
        pkg_name_label.setBuddy(self.pkg_name_line)

        self.search_button = QPushButton(
            "&Search",
            clicked=self.pop_results_table
        )

        exit_button = QPushButton(
            "&Exit",
            clicked=self.on_close
        )

        # results table
        self.results_table = ResultsTable(
            selectionBehavior=QAbstractItemView.SelectionBehavior.SelectRows,
            editTriggers=QAbstractItemView.EditTrigger.NoEditTriggers,
            alternatingRowColors=True,
            sortingEnabled=True,
            doubleClicked=self.install_package,
            context_triggered=self.install_package  # signal
        )

        # hide vertical header
        self.results_table.verticalHeader().hide()

        # adjust horizontal headers
        h_header = self.results_table.horizontalHeader()
        h_header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        h_header.setStretchLastSection(True)

        # set table view model
        self.results_table_model = QStandardItemModel(0, 3, self)
        self.results_table.setModel(self.results_table_model)

        line_2 = QFrame(self)
        line_2.setFixedHeight(8)
        line_2.setFrameShape(QFrame.Shape.HLine)
        line_2.setFrameShadow(QFrame.Shadow.Sunken)

        grid_layout.addWidget(title_label, 0, 0, 1, 2)
        grid_layout.addWidget(logo, 0, 2, 1, 1)
        grid_layout.addWidget(subtitle_label_1, 1, 0, 1, 2)
        grid_layout.addWidget(subtitle_label_2, 2, 0, 1, 2)
        grid_layout.addWidget(line_1, 3, 0, 1, 3)
        grid_layout.addWidget(pkg_name_label, 4, 0, 1, 1)
        grid_layout.addWidget(self.pkg_name_line, 4, 1, 1, 1)
        grid_layout.addWidget(self.search_button, 4, 2, 1, 1)
        grid_layout.addWidget(self.results_table, 5, 0, 1, 3)
        grid_layout.addWidget(line_2, 6, 0, 1, 3)
        grid_layout.addWidget(exit_button, 7, 2, 1, 1)

        horizontal_layout.addLayout(grid_layout)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            cp = screen.availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())


    def on_close(self):
        """Close window if no changes made, else ask to save a requirements.
        """
        if self.venv_modified != 0:
            self.save_requirements()
        else:
            self.close()


    def launch(self):
        """Launches the installer dialog.
        """
        # count whether changes has been made to venv
        self.venv_modified = 0

        # get the venv path from file
        with open(get_data.ACTIVE_VENV, "r", encoding="utf-8") as f:
            venv_path = f.read()

        split_venv_path = os.path.split(venv_path)
        self.venv_location = split_venv_path[0]
        self.venv_name = os.path.basename(venv_path)

        # clear input
        self.results_table_model.clear()
        self.pkg_name_line.clear()
        self.pkg_name_line.setFocus()

        # set text in column headers
        self.results_table_model.setHorizontalHeaderLabels([
            "Name",
            "Version",
            "Author",
            "Description"
        ])

        # adjust column width
        self.results_table.setColumnWidth(0, 200)  # name
        self.results_table.setColumnWidth(1, 80)  # version
        self.results_table.setColumnWidth(2, 150)  # release

        # launch the dialog via exec_() method
        self.exec()


    def pop_results_table(self):
        """Refresh the results table.
        """
        self.results_table_model.setRowCount(0)
        search_item = self.pkg_name_line.text()

        if len(search_item) >= 1:
            for info in get_data.get_package_infos(search_item):
                self.results_table_model.insertRow(0)

                for i, text in enumerate((
                    info.pkg_name,
                    info.pkg_version,
                    info.pkg_info_2,
                    info.pkg_summary
                )):
                    self.results_table_model.setItem(0, i, QStandardItem(text))

            if not get_data.get_package_infos(search_item):
                logger.debug(f"No matches for '{search_item}'")
                QMessageBox.information(
                    self,
                    "No results",
                    f"No results matching '{search_item}'.\n"
                )
                self.pkg_name_line.setFocus()


    def install_package(self):
        """
        Get the name of the selected item from the results table. Then install
        the selected package into the created virtual environment.
        """
        indexes = self.results_table.selectionModel().selectedRows()
        for index in sorted(indexes):
            self.pkg = index.data()

        msg_box_question = QMessageBox.question(
            self,
            "Confirm", f"Are you sure you want to install '{self.pkg}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if msg_box_question == QMessageBox.StandardButton.Yes:
            self.console.setWindowTitle(f"Installing {self.pkg}")

            # changes (may) have been made to venv
            self.venv_modified += 1

            self.manager = PipManager(
                self.venv_location,
                self.venv_name
            )
            # open the console when recieving signal from manager
            self.manager.started.connect(self.console.exec)
            self.manager.text_changed.connect(self.console.update_status)

            # start installing the selected package
            logger.debug(f"Installing '{self.pkg}'...")
            self.manager.run_pip(creator.cmds[0], [creator.opts[0], self.pkg])

            # clear the content when closing console
            if self.console.close:
                self.console.console_window.clear()

                # clear input
                self.pkg_name_line.clear()
                self.pkg_name_line.setFocus()


    def save_requirements(self):
        """
        Ask if user wants to save a requirements of the
        updated environment.
        """
        self.msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Save requirements",
            "Do you want to generate a requirements?          ",
            QMessageBox.StandardButton.NoButton,
            self
        )
        yes_button = self.msg_box.addButton(
            "&Yes",
            QMessageBox.ButtonRole.YesRole
        )
        no_button = self.msg_box.addButton(
            "&No",
            QMessageBox.ButtonRole.NoRole
        )
        cancel_button = self.msg_box.addButton(
            "&Cancel",
            QMessageBox.ButtonRole.RejectRole
        )

        self.msg_box.exec()

        if self.msg_box.clickedButton() == yes_button:
            venv_dir = Path(self.venv_location) / self.venv_name
            save_file = QFileDialog.getSaveFileName(
                self,
                "Save requirements",
                directory=str(venv_dir / "requirements.txt")
            )
            save_path = save_file[0]
            logger.debug(f"Selected path: '{venv_dir}'")

            if not save_path:
                return

            platform = get_platform()
            venv_python = platform.venv_python_path(venv_dir)
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    subprocess.run([
                        str(venv_python),
                        "-m",
                        "pip",
                        "freeze"],
                        stdout=f,
                        check=False,
                    )
            except subprocess.CalledProcessError as e:
                logger.debug(f"Failed to save requirements: {e}")

            logger.debug(f"Saved '{save_path}'")

            QMessageBox.information(
                self,
                "Saved",
                f"Saved requirements in: \n{save_path}"
            )
            self.close()

        elif self.msg_box.clickedButton() == no_button:
            self.close()
