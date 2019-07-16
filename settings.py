# -*- coding: utf-8 -*-
"""Settings."""
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QAction, QVBoxLayout, QHBoxLayout,
                             QToolButton, QPushButton, QSpacerItem, QDialog,
                             QFrame, QSizePolicy, QGridLayout, QLineEdit,
                             QLabel, QFileDialog)




class SetDefaultDirectory(QDialog):
    """
    Set the default directory, where to look for virtual environments.
    """
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        #]===================================================================[#
        #] WINDOW SETTINGS [#================================================[#
        #]===================================================================[#

        self.setWindowTitle("Set Default Directory")
        self.setGeometry(600, 365, 500, 100)
        self.setFixedSize(500, 100)

        v_Layout = QVBoxLayout(self)
        h_Layout = QHBoxLayout()
        gridLayout = QGridLayout()

        defaultDirLabel = QLabel("Default Venv Directory:")
        self.defaultDirLineEdit = QLineEdit()
        defaultDirLabel.setBuddy(self.defaultDirLineEdit)

        folder_icon = QIcon.fromTheme("folder")

        selectDirToolButton = QToolButton(
            toolTip="Browse",
            clicked=self.selectDirTButton_clicked
        )
        selectDirToolButton.setFixedSize(26, 27)
        selectDirToolButton.setIcon(folder_icon)

        horizontalLine = QFrame()
        horizontalLine.setFrameShape(QFrame.HLine)
        horizontalLine.setFrameShadow(QFrame.Sunken)

        cancelButton = QPushButton(
            "Cancel", clicked=self.close
        )

        okButton = QPushButton(
            "OK", clicked=self.okButton_clicked
        )

        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        gridLayout.addWidget(defaultDirLabel, 0, 0, 1, 1)
        gridLayout.addWidget(self.defaultDirLineEdit, 0, 1, 1, 1)
        gridLayout.addWidget(selectDirToolButton, 0, 2, 1, 1)

        h_Layout.addItem(spacerItem)
        h_Layout.addWidget(okButton, 0, Qt.AlignBottom)
        h_Layout.addWidget(cancelButton, 0, Qt.AlignBottom)

        v_Layout.addLayout(gridLayout)
        v_Layout.addWidget(horizontalLine)
        v_Layout.addLayout(h_Layout)


    def selectDirTButton_clicked(self):
        """
        Select directory which should be set as default.
        """
        fileDiag = QFileDialog()

        directory = fileDiag.getExistingDirectory()
        self.defaultDirLineEdit.setText(directory)


    def okButton_clicked(self):
        """
        Store the absolute path to the selected dir as `str` in `def/default`.
        """
        with open("def/default", 'w') as default:
            default.write(self.defaultDirLineEdit.text())
            default.close()

        self.close()





if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    settingsUI = SetDefaultDirectory()
    settingsUI.show()

    sys.exit(app.exec_())
