# -*- coding: utf-8 -*-
"""
This module contains some dialogs.
"""
from platform import system, release
import sys

from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QDesktopWidget,
    QTextEdit,
    QProgressBar,
    QPushButton,
    QSpacerItem,
    QApplication,
    QSizePolicy,
    QFormLayout,
    QGridLayout,
    QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QSize, pyqtSlot

from get_data import __version__



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
        self.setWindowIcon(QIcon(":/img/python.png"))
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
        self.setWindowIcon(QIcon(":/img/python.png"))
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
    def update_status(self, status):
        """
        Print the output from stdin/ stderr to `console_window`.
        """
        metrix = QFontMetrics(self.console_window.font())
        formatted_text = metrix.elidedText(
            status, Qt.ElideNone, self.console_window.width()
        )
        self.console_window.append(formatted_text)


    def finish_success(self):
        """
        Show info message when all modules installed successfully.
        """
        message_txt = (
            "Environment cloned successfully.\n\n"
            "All modules have been \ninstalled without errors.\n"
        )
        print("[PROCESS]: Environment cloned successfully")
        QMessageBox.information(self, "Done", message_txt)


    def finish_fail(self):
        """
        Show info message when the installation process failed.
        """
        message_txt = (
            "Could not install from requirements.\n\n"
            "File not found.\n"
        )
        print("[ERROR]: Could not install from requirements")
        QMessageBox.critical(self, "Error", message_txt)



#]===========================================================================[#
#] APPLICATION INFO DIALOG [#================================================[#
#]===========================================================================[#

class AppInfoDialog(QDialog):
    """
    Show application infos.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle("About VenviPy")
        self.setFixedSize(420, 390)
        self.center()
        self.setWindowIcon(QIcon(":/img/python.png"))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)


        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        gridLayout = QGridLayout(self)
        formLayout = QFormLayout()

        horizontalLayout_0 = QHBoxLayout()
        horizontalLayout_1 = QHBoxLayout()
        horizontalLayout_2 = QHBoxLayout()
        horizontalLayout_3 = QHBoxLayout()

        horizontalLayout_0.setContentsMargins(247, 8, 0, 25)
        horizontalLayout_1.setContentsMargins(0, 0, 55, 25)
        horizontalLayout_3.setContentsMargins(0, 75, 6, 0)
        formLayout.setContentsMargins(37, -1, 20, -1)

        gridLayout.addLayout(horizontalLayout_0, 0, 0, 1, 1)
        gridLayout.addLayout(horizontalLayout_1, 0, 0, 1, 1)
        gridLayout.addLayout(horizontalLayout_2, 2, 0, 1, 1)
        gridLayout.addLayout(horizontalLayout_3, 0, 0, 1, 0)
        gridLayout.addLayout(formLayout, 1, 0, 1, 1)


        #]===================================================================[#
        #] LABELS [#=========================================================[#
        #]===================================================================[#

        # python logo
        logo = QLabel()
        logo.setPixmap(QPixmap(":/img/pylogo.png"))
        logo.setAlignment(Qt.AlignVCenter)

        if sys.platform == "win32":
            # title
            labelTitle = QLabel(
                '<p align="center"><span style="font-size:31pt;">\
                    <b>VenviPy</b>\
                </span></p>'
            )
            labelTitle.setFont(QFont("Segoe Print", italic=True))

            # subtitle
            labelSubtitle = QLabel(
                '<p align="center"><span style="font-size:11pt;">\
                    Virtual Environment Manager for Python\
                </span></p>'
            )
            labelSubtitle.setFont(QFont("", italic=True))

        else:
            # title
            labelTitle = QLabel(
                '<p align="center"><span style="font-size:35pt;">\
                    <b>VenviPy</b>\
                </span></p>'
            )
            labelTitle.setFont(QFont("FreeSerif", italic=True))

            # subtitle
            labelSubtitle = QLabel(
                '<p align="center"><span style="font-size:13.5pt;">\
                    Virtual Environment Manager for Python\
                </span></p>'
            )
            labelSubtitle.setFont(QFont("FreeSerif", italic=True))

        #]===================================================================[#

        # spacer below subtitle
        spacer1 = QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        formLayout.addItem(spacer1)

        # version
        labelVersion = QLabel("<b>Version:</b>")
        fieldVersion = QLabel()
        fieldVersion.setText(__version__)

        # OS
        labelOS = QLabel("<b>OS:</b>")
        fieldOS = QLabel()
        fieldOS.setText(system() + ' ' + release())

        # author
        labelAuthor = QLabel("<b>Author:</b>")
        fieldAuthor = QLabel()
        fieldAuthor.setText("Youssef Serestou")

        # email
        labelEmail = QLabel("<b>E-Mail:</b>")
        fieldEmail = QLabel()
        fieldEmail.setText("youssef.serestou.83@gmail.com")

        # link to repository
        labelRepo = QLabel("<b>Repository:</b>")
        fieldRepo = QLabel()
        fieldRepo.setText(
            "<a href='https://github.com/sinusphi/venvipy'>\
                www.github.com/sinusphi/venvipy\
            </a>"
        )
        fieldRepo.setOpenExternalLinks(True)

        # link to python.org
        labelPython = QLabel("<b>Python:</b>")
        fieldPython = QLabel()
        fieldPython.setText(
            "<a href='https://python.org'>\
                www.python.org\
            </a>"
        )
        fieldPython.setOpenExternalLinks(True)

        # close button
        closeButton = QPushButton(
            "Close",
            clicked=self.close,
        )
        closeButton.setMinimumSize(QSize(110, 0))

        #]===================================================================[#

        horizontalLayout_0.addWidget(logo)
        horizontalLayout_1.addWidget(labelTitle, 0, Qt.AlignVCenter)
        horizontalLayout_2.addWidget(
            closeButton, 0, Qt.AlignRight | Qt.AlignBottom
        )
        horizontalLayout_3.addWidget(labelSubtitle, 0, Qt.AlignVCenter)

        formLayout.setWidget(1, QFormLayout.LabelRole, labelVersion)
        formLayout.setWidget(1, QFormLayout.FieldRole, fieldVersion)
        formLayout.setWidget(2, QFormLayout.LabelRole, labelOS)
        formLayout.setWidget(2, QFormLayout.FieldRole, fieldOS)
        formLayout.setWidget(3, QFormLayout.LabelRole, labelAuthor)
        formLayout.setWidget(3, QFormLayout.FieldRole, fieldAuthor)
        formLayout.setWidget(4, QFormLayout.LabelRole, labelEmail)
        formLayout.setWidget(4, QFormLayout.FieldRole, fieldEmail)
        formLayout.setWidget(5, QFormLayout.LabelRole, labelRepo)
        formLayout.setWidget(5, QFormLayout.FieldRole, fieldRepo)
        formLayout.setWidget(6, QFormLayout.LabelRole, labelPython)
        formLayout.setWidget(6, QFormLayout.FieldRole, fieldPython)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



if __name__ == "__main__":

    app = QApplication(sys.argv)

    progress_dialog = ProgBarDialog()
    #progress_dialog.exec()

    console_dialog = ConsoleDialog()
    #console_dialog.exec()

    info_dialog = AppInfoDialog()
    info_dialog.exec()

    sys.exit(app.exec_())
