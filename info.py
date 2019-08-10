# -*- coding: utf-8 -*-
"""Infos about VenviPy."""
from platform import system, release

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QLabel, QPushButton, QApplication, QHBoxLayout,
                             QSpacerItem, QSizePolicy, QDialog, QGridLayout,
                             QFormLayout)



class AppInfo(QDialog):
    """
    Show application infos.
    """
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        #]===================================================================[#
        #] GENERAL WINDOW PARAMETERS [#======================================[#
        #]===================================================================[#

        self.setGeometry(629, 178, 435, 425)
        self.setFixedSize(435, 410)
        self.setWindowTitle("VenviPy")
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

        horizontalLayout_0.setContentsMargins(257, 8, 0, 25)
        horizontalLayout_1.setContentsMargins(0, 0, 75, 25)
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
        fieldVersion.setText("1.0")

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



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    appInfo = AppInfo()
    appInfo.show()

    sys.exit(app.exec_())
