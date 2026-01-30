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
This module contains some dialogs.
"""
import sys
import logging
from datetime import date

from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QApplication,
    QGridLayout
)

import venvipy_rc  # pylint: disable=unused-import
from get_data import __version__
from styles.theme import DIALOG_QSS


logger = logging.getLogger(__name__)

WINDOW_ICON_PATH = ":/img/profile.png"
ABOUT_LOGO_PATH = ":/img/default.png"


def center_window(dialog):
    """Center dialog on the active screen.
    """
    qr = dialog.frameGeometry()
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen:
        cp = screen.availableGeometry().center()
        qr.moveCenter(cp)
        dialog.move(qr.topLeft())


def disable_window_buttons(dialog, *, close=True, minimize=True):
    """
    Disable specific window buttons without resetting other flags.
    """
    flags = dialog.windowFlags()
    if close:
        flags &= ~Qt.WindowType.WindowCloseButtonHint
    if minimize:
        flags &= ~Qt.WindowType.WindowMinimizeButtonHint
    dialog.setWindowFlags(flags)


class BaseDialog(QDialog):
    """Base dialog with shared helpers.
    """
    def center(self):
        """Center window."""
        center_window(self)

    def disable_window_buttons(self, *, close=True, minimize=True):
        disable_window_buttons(self, close=close, minimize=minimize)



#]===========================================================================[#
#] PROGRESS BAR DIALOG [#====================================================[#
#]===========================================================================[#

class ProgBarDialog(BaseDialog):
    """
    Dialog showing a progress bar during processes.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setFixedSize(420, 85)
        self.center()
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.disable_window_buttons(close=True, minimize=True)
        self.setStyleSheet(DIALOG_QSS)

        self.status_label = QLabel(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedSize(395, 23)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.status_label)
        v_layout.addWidget(self.progress_bar)
        v_layout.addStretch(1)

        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(0, 15, 0, 0)
        h_layout.addLayout(v_layout)

        self.setLayout(h_layout)




#]===========================================================================[#
#] CONSOLE DIALOG [#=========================================================[#
#]===========================================================================[#

class ConsoleDialog(BaseDialog):
    """
    Dialog box printing the output to a console-like 
    widget when running commands.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.resize(1115, 705)
        self.center()
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.disable_window_buttons(close=True, minimize=True)

        self.setStyleSheet(
            DIALOG_QSS + """
            QPlainTextEdit {
                background-color: black;
                color: lightgrey;
                selection-background-color: rgb(50, 50, 60);
                selection-color: rgb(0, 255, 0)
            }
            """
        )

        self.console_window = QPlainTextEdit()
        self.console_window.setReadOnly(True)
        self.console_window.setFont(QFont("Monospace", 11))
        self.console_window.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.console_window.setMaximumBlockCount(5000)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.console_window)


    @pyqtSlot(str)
    def update_status(self, message):
        """
        Print the output from stdin/ stderr to `console_window`.
        """
        if message.endswith("\n"):
            message = message[:-1]
        self.console_window.appendPlainText(message)



#]===========================================================================[#
#] APPLICATION INFO DIALOG [#================================================[#
#]===========================================================================[#

class InfoAboutVenviPy(BaseDialog):
    """
    The "Info about VenviPy" dialog.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle("About VenviPy")
        self.setFixedSize(500, 405)
        self.center()
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.disable_window_buttons(close=False, minimize=True)
        self.setStyleSheet(DIALOG_QSS)

        # logo
        logo = QLabel()
        pixmap = QPixmap(ABOUT_LOGO_PATH)
        logo_scaled = pixmap.scaled(
            156, 156, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(logo_scaled)

        # title
        title_label = QLabel(
            '<p><span style="font-size:12pt;"><b>VenviPy</b></span></p>'
        )

        # version
        version_label = QLabel(
            f'<p><span style="font-size:11pt;">{__version__}</span></p>'
        )

        # subtitle
        subtitle_label = QLabel(
            "<p><span style=\"font-size:11pt;\">"
            "Virtual Environment Manager for Python"
            "</span></p>"
        )

        # link to repository
        repo_label = QLabel(
            "<p><span style=\"font-size:11pt;\">"
            "<a href=\"https://github.com/sinusphi/venvipy\">"
            "Website"
            "</a></span></p>",
            openExternalLinks=True
        )
        repo_label.setToolTip("https://github.com/sinusphi/venvipy")

        # copyright
        current_year = str(date.today().year)
        copyright_label = QLabel(
            f"<p><span style=\"font-size:10pt;\">"
            f"Copyright © 2019-{current_year} - Youssef Serestou "
            "</span></p>"
        )

        # close button
        close_button = QPushButton("Close", clicked=self.close)
        close_button.setFixedWidth(135)
        close_button.setFixedHeight(30)

        # layout
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(15, 15, 10, 15)

        grid_layout.addWidget(logo, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        grid_layout.addWidget(title_label, 2, 0, Qt.AlignmentFlag.AlignHCenter)
        grid_layout.addWidget(
            version_label, 3, 0, Qt.AlignmentFlag.AlignHCenter
        )
        grid_layout.addWidget(
            subtitle_label, 4, 0, Qt.AlignmentFlag.AlignHCenter
        )
        grid_layout.addWidget(repo_label, 5, 0, Qt.AlignmentFlag.AlignHCenter)
        grid_layout.addWidget(
            copyright_label, 6, 0, Qt.AlignmentFlag.AlignHCenter
        )
        grid_layout.addWidget(close_button, 8, 0, Qt.AlignmentFlag.AlignRight)
        grid_layout.setRowMinimumHeight(1, 1)
        grid_layout.setRowMinimumHeight(7, 5)
        self.setLayout(grid_layout)



if __name__ == "__main__":

    app = QApplication(sys.argv)

    #progress_dialog = ProgBarDialog()
    #progress_dialog.show()

    #console_dialog = ConsoleDialog()
    #console_dialog.show()

    info_about_venvipy = InfoAboutVenviPy()
    info_about_venvipy.show()

    sys.exit(app.exec())
