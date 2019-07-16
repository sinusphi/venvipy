# -*- coding: utf-8 -*-
"""
Show infos about VenviPy.
"""
from platform import system, release

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QPushButton, QApplication,
                             QSpacerItem, QSizePolicy, QDialog)




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

        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)


        #]===================================================================[#
        #] LAYOUTS [#========================================================[#
        #]===================================================================[#

        self.horizontalLayout_0 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.formLayout = QtWidgets.QFormLayout()


        self.horizontalLayout_0.setContentsMargins(257, 8, 0, 25)
        self.horizontalLayout_1.setContentsMargins(0, 0, 75, 25)
        self.horizontalLayout_3.setContentsMargins(0, 75, 6, 0)
        self.formLayout.setContentsMargins(37, -1, 20, -1)


        self.gridLayout.addLayout(self.horizontalLayout_0, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.horizontalLayout_1, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 0)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)


        #]===================================================================[#
        #] LABELS [#=========================================================[#
        #]===================================================================[#

        # python logo
        self.logo = QtWidgets.QLabel(self)
        self.logo.setPixmap(QPixmap(":/img/pylogo.png"))
        self.logo.setAlignment(Qt.AlignVCenter)
        self.horizontalLayout_0.addWidget(self.logo)


        # title
        self.labelTitle = QtWidgets.QLabel(self)
        self.labelTitle.setFont(QFont("FreeSerif", italic=True))
        self.horizontalLayout_1.addWidget(
            self.labelTitle, 0, QtCore.Qt.AlignVCenter
        )


        # subtitle
        self.labelSubtitle = QtWidgets.QLabel(self)
        self.labelSubtitle.setFont(QFont("FreeSerif", italic=True))
        self.horizontalLayout_3.addWidget(self.labelSubtitle, 0, QtCore.Qt.AlignVCenter)


        # spacer below subtitle
        spacer1 = QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.formLayout.addItem(spacer1)


        # version
        self.labelVersion = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.labelVersion
        )

        self.label_outVersion = QtWidgets.QLabel(self)
        self.label_outVersion.setText("0.1.0")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.label_outVersion
        )


        # OS
        self.labelOS = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.labelOS
        )

        self.label_outOS = QtWidgets.QLabel(self)
        self.label_outOS.setText(system() + ' ' + release())
        self.formLayout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.label_outOS
        )


        # author
        self.labelAuthor = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            3, QtWidgets.QFormLayout.LabelRole, self.labelAuthor
        )

        self.label_outAuthor = QtWidgets.QLabel(self)
        self.label_outAuthor.setText("Youssef Serestou")
        self.formLayout.setWidget(
            3, QtWidgets.QFormLayout.FieldRole, self.label_outAuthor
        )


        # email
        self.labelEmail = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            4, QtWidgets.QFormLayout.LabelRole, self.labelEmail
        )

        self.label_outEmail = QtWidgets.QLabel(self)
        self.label_outEmail.setText("youssef.serestou.83@gmail.com")
        self.formLayout.setWidget(
            4, QtWidgets.QFormLayout.FieldRole, self.label_outEmail
        )


        # link to repository
        self.labelRepo = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            5, QtWidgets.QFormLayout.LabelRole, self.labelRepo
        )

        self.label_outRepo = QtWidgets.QLabel(self)
        self.label_outRepo.setText(
            "<a href='https://github.com/sinusphi/venvipy'>\
                www.github.com/sinusphi/venvipy\
            </a>"
        )
        self.label_outRepo.setOpenExternalLinks(True)
        self.formLayout.setWidget(
            5, QtWidgets.QFormLayout.FieldRole, self.label_outRepo
        )


        # link to python
        self.labelPython = QtWidgets.QLabel(self)
        self.formLayout.setWidget(
            6, QtWidgets.QFormLayout.LabelRole, self.labelPython
        )

        self.label_outPython = QtWidgets.QLabel(self)
        self.label_outPython.setText(
            "<a href='https://python.org'>\
                www.python.org\
            </a>"
        )
        self.label_outPython.setOpenExternalLinks(True)
        self.formLayout.setWidget(
            6, QtWidgets.QFormLayout.FieldRole, self.label_outPython
        )


        #]===================================================================[#
        #] BUTTON [#=========================================================[#
        #]===================================================================[#

        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setMinimumSize(QtCore.QSize(110, 0))
        self.closeButton.clicked.connect(self.close)
        self.horizontalLayout_2.addWidget(
            self.closeButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom
        )

        self.retranslateUi()


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "App Info"))

        self.labelTitle.setText(_translate(
            "Form", "<p align=\"center\"><span style=\" font-size:35pt;\">\
            <b>VenviPy</b></span></p>"
        ))

        self.labelSubtitle.setText(_translate(
            "Form", "<p align=\"center\"><span style=\" font-size:13.5pt;\">\
            Virtual Environment Manager for Python</span></p>"
        ))

        self.labelVersion.setText(_translate("Form", "<b>Version:</b>"))
        self.labelOS.setText(_translate("Form", "<b>OS:</b>"))
        self.labelAuthor.setText(_translate("Form", "<b>Author:</b>"))
        self.labelEmail.setText(_translate("Form", "<b>E-Mail:</b>"))
        self.labelRepo.setText(_translate("Form", "<b>Repository:</b>"))
        self.labelPython.setText(_translate("Form", "<b>Python:</b>"))
        self.closeButton.setText(_translate("Form", "Close"))





if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    appInfo = AppInfo()
    appInfo.show()

    sys.exit(app.exec_())
