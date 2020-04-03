# -*- coding: utf-8 -*-
"""
This module contains all dialogs required.
"""
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QDesktopWidget, QTextEdit,
    QProgressBar
)
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtCore import Qt, pyqtSlot



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
            status, Qt.ElideRight, self.consoleWindow.width()
        )
        self.consoleWindow.append(clippedText)
