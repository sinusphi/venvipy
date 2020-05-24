# -*- coding: utf-8 -*-
"""
This module contains some dialogs.
"""
import sys
import logging

from PyQt5.QtGui import QIcon, QPixmap, QFontMetrics
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QDesktopWidget,
    QTextEdit,
    QProgressBar,
    QPushButton,
    QApplication,
    QGridLayout,
    QMessageBox
)

import venvipy_rc  # pylint: disable=unused-import
from get_data import __version__


logger = logging.getLogger(__name__)



#]===========================================================================[#
#] PROGRESS BAR DIALOG [#====================================================[#
#]===========================================================================[#

class ProgBarDialog(QDialog):
    """
    Dialog showing a progress bar during the create process.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setFixedSize(350, 85)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        self.status_label = QLabel(self)
        self.place_holder = QLabel(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedSize(325, 23)
        self.progress_bar.setRange(0, 0)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.status_label)
        v_layout.addWidget(self.progress_bar)
        v_layout.addWidget(self.place_holder)

        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(0, 15, 0, 0)
        h_layout.addLayout(v_layout)

        self.setLayout(h_layout)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



#]===========================================================================[#
#] CONSOLE DIALOG [#=========================================================[#
#]===========================================================================[#

class ConsoleDialog(QDialog):
    """
    Dialog box printing the output to a console-like widget during the
    installation process.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.resize(880, 510)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        self.setStyleSheet(
            """
            QTextEdit {
                background-color: black;
                color: lightgrey;
                selection-background-color: rgb(50, 50, 60);
                selection-color: rgb(0, 255, 0)
            }
            """
        )

        self.console_window = QTextEdit()
        self.console_window.setReadOnly(True)
        self.console_window.setFontFamily("Monospace")
        self.console_window.setFontPointSize(11)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.console_window)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    @pyqtSlot(str)
    def update_status(self, message):
        """
        Print the output from stdin/ stderr to `console_window`.
        """
        metrix = QFontMetrics(self.console_window.font())
        formatted_text = metrix.elidedText(
            message, Qt.ElideNone, self.console_window.width()
        )
        self.console_window.append(formatted_text)


    def finish_fail(self):
        """
        Show info message when the installation process failed.
        """
        message_txt = (
            "Could not install from requirements.\n\n"
            "File not found.\n"
        )
        logger.error("Could not install from requirements")
        QMessageBox.critical(self, "Error", message_txt)



#]===========================================================================[#
#] APPLICATION INFO DIALOG [#================================================[#
#]===========================================================================[#

class InfoAboutVenviPy(QDialog):
    """
    The "Info about VenviPy" dialog.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle("About VenviPy")
        self.setFixedSize(420, 350)
        self.center()
        self.setWindowIcon(QIcon(":/img/profile.png"))
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

        # logo
        logo = QLabel()
        pixmap = QPixmap(":/img/default.png")
        logo_scaled = pixmap.scaled(136, 136, Qt.KeepAspectRatio)
        logo.setPixmap(logo_scaled)

        place_holder = QLabel(maximumHeight=1)

        # title
        title_label = QLabel(
            '<p><span style="font-size:12pt;">\
                <b>VenviPy</b>\
            </span></p>'
        )
        #title_label.setFont(QFont("FreeSerif", italic=True))

        # version
        version_label = QLabel(
            f'<p><span style="font-size:11pt;">\
                {__version__}\
            </span></p>'
        )

        # subtitle
        subtitle_label = QLabel(
            '<p><span style="font-size:11pt;">\
                Virtual Environment Manager for Python\
            </span></p>'
        )

        repo_label = QLabel(
            '<p><span style="font-size:11pt;">\
            <a href="https://github.com/sinusphi/venvipy">\
                Website\
            </a></span></p>',
            openExternalLinks=True
        )

        # copyright
        copyright_label = QLabel(
            '<p><span style="font-size:10pt;">\
                Copyright © 2019-2020 Youssef Serestou\
            </span></p>'
        )

        # close button
        close_button = QPushButton("Close", clicked=self.close)
        close_button.setMinimumSize(QSize(110, 15))


        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(15, 15, 10, 15)

        grid_layout.addWidget(logo, 0, 0, Qt.AlignHCenter)
        grid_layout.addWidget(place_holder, 1, 0, Qt.AlignHCenter)
        grid_layout.addWidget(title_label, 2, 0, Qt.AlignHCenter)
        grid_layout.addWidget(version_label, 3, 0, Qt.AlignHCenter)
        grid_layout.addWidget(subtitle_label, 4, 0, Qt.AlignHCenter)
        grid_layout.addWidget(repo_label, 5, 0, Qt.AlignHCenter)
        grid_layout.addWidget(copyright_label, 6, 0, Qt.AlignHCenter)
        grid_layout.addWidget(close_button, 7, 0, Qt.AlignRight)
        self.setLayout(grid_layout)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



if __name__ == "__main__":

    app = QApplication(sys.argv)

    #progress_dialog = ProgBarDialog()
    #progress_dialog.show()

    #console_dialog = ConsoleDialog()
    #console_dialog.show()

    info_about_venvipy = InfoAboutVenviPy()
    info_about_venvipy.show()

    sys.exit(app.exec_())
