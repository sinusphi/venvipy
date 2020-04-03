# -*- coding: utf-8 -*-
"""
This module contains some dialogs.
"""
from platform import system, release
import sys
import os

from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QDesktopWidget, QTextEdit,
    QProgressBar, QPushButton, QSpacerItem, QApplication, QSizePolicy,
    QFormLayout, QGridLayout, QFileDialog, QToolButton, QFrame, QLineEdit
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QSize, pyqtSlot



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

        h_Layout = QHBoxLayout(self)
        v_Layout = QVBoxLayout()
        h_Layout.setContentsMargins(0, 15, 0, 0)

        self.statusLabel = QLabel(self)
        self.placeHolder = QLabel(self)

        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedSize(325, 23)
        self.progressBar.setRange(0, 0)

        v_Layout.addWidget(self.statusLabel)
        v_Layout.addWidget(self.progressBar)
        v_Layout.addWidget(self.placeHolder)

        h_Layout.addLayout(v_Layout)
        self.setLayout(h_Layout)


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
        self.setWindowTitle("Installing")
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

        self.consoleWindow = QTextEdit()
        self.consoleWindow.setReadOnly(True)
        self.consoleWindow.setFontFamily("Monospace")
        self.consoleWindow.setFontPointSize(11)

        v_Layout = QVBoxLayout(self)
        v_Layout.addWidget(self.consoleWindow)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    @pyqtSlot(str)
    def update_status(self, status):
        """
        Print the output from stdin/ stderr to `consoleWindow`.
        """
        metrix = QFontMetrics(self.consoleWindow.font())
        clippedText = metrix.elidedText(
            status, Qt.ElideNone, self.consoleWindow.width()
        )
        self.consoleWindow.append(clippedText)


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
        fieldVersion.setText("1.4")

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


#]===========================================================================[#
#] SELECT DEFAULT DIRECTORY DIALOG [#========================================[#
#]===========================================================================[#

class DefaultDirDialog(QDialog):
    """
    Set the default directory, where to look for virtual environments.
    """

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle("Set Default Directory")
        self.setGeometry(600, 365, 500, 100)
        self.setFixedSize(500, 100)
        self.center()
        self.setWindowIcon(QIcon(":/img/python.png"))

        self.setStyleSheet(
            """
            QToolTip {
                background-color: rgb(47, 52, 63);
                border: rgb(47, 52, 63);
                color: rgb(210, 210, 210);
                padding: 1px;
                opacity: 325
            }
            """
        )

        v_Layout = QVBoxLayout(self)
        h_Layout = QHBoxLayout()
        gridLayout = QGridLayout()

        defaultDirLabel = QLabel("Default Venv Directory:")
        self.defaultDirLineEdit = QLineEdit()
        defaultDirLabel.setBuddy(self.defaultDirLineEdit)

        folder_icon = QIcon.fromTheme("folder")

        browseToolButton = QToolButton(
            toolTip="Browse",
            icon=folder_icon,
            clicked=self.select_dir
        )
        browseToolButton.setFixedSize(26, 27)

        horizontalLine = QFrame(
            frameShape=QFrame.HLine,
            frameShadow=QFrame.Sunken
        )

        cancelButton = QPushButton(
            "Cancel", clicked=self.reject
        )

        okButton = QPushButton(
            "OK", clicked=self.okButton_clicked
        )

        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        gridLayout.addWidget(defaultDirLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.defaultDirLineEdit, 0, 1, 1, 1)
        gridLayout.addWidget(browseToolButton, 0, 2, 1, 1)

        h_Layout.addItem(spacerItem)
        h_Layout.addWidget(cancelButton, 0, Qt.AlignBottom)
        h_Layout.addWidget(okButton, 0, Qt.AlignBottom)

        v_Layout.addLayout(gridLayout)
        v_Layout.addWidget(horizontalLine)
        v_Layout.addLayout(h_Layout)


    def center(self):
        """Center window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def select_dir(self):
        """
        Select directory which should be set as default.
        """
        directory = QFileDialog.getExistingDirectory()
        self.defaultDirLineEdit.setText(directory)


    def okButton_clicked(self):
        """
        Store the absolute path to the selected dir in `recources/default`.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        default_file = os.path.join(current_dir, "resources", "default")
        default_path = self.defaultDirLineEdit.text()

        with open(default_file, "w") as f:
            f.write(default_path)
            print(
                f"[INFO]: Setting default venv directory to '{default_path}'"
            )

        self.accept()
