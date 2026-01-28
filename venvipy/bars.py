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
Custom bars for VenviPy.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QStyle,
    QLabel,
    QToolButton,
    QWidget,
    QHBoxLayout
)



class TitleBar(QWidget):
    """
    Custom title bar widget.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._window = parent
        self._drag_pos = None

        self.setObjectName("titleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 8, 2, 3)
        layout.setSpacing(8)

        self.win_min_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMinButton
            )
        self.win_max_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMaxButton
            )
        self.win_normal_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarNormalButton
            )
        self.win_close_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarCloseButton
            )

        icon_label = QLabel(self)
        icon_pixmap = QPixmap(":/img/profile.png").scaled(
            24,
            22,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(icon_pixmap)

        title_label = QLabel("VenviPy", self)
        title_label.setStyleSheet("""
            font-family: 'DejaVu Sans';
            font-size: 15px;
            font-weight: bold;
        """)
        title_label.setObjectName("titleLabel")

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch(1)

        self.min_button = QToolButton(self)
        self.min_button.setIcon(self.win_min_icon)
        self.min_button.setObjectName("titleButton")
        self.min_button.clicked.connect(self._window.showMinimized)

        self.max_button = QToolButton(self)
        self.max_button.setObjectName("titleButton")
        self.max_button.clicked.connect(self.toggle_max_restore)
        self.update_maximize_icon()

        self.close_button = QToolButton(self)
        self.close_button.setIcon(self.win_close_icon)
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self._window.on_close)

        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)


    def update_maximize_icon(self):
        """Update maximize/restore icon.
        """
        if self._window.isMaximized():
            icon = self.win_normal_icon
        else:
            icon = self.win_max_icon
        self.max_button.setIcon(icon)


    def toggle_max_restore(self):
        """Toggle maximize/restore.
        """
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.update_maximize_icon()


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window_handle = self._window.windowHandle()
            if window_handle is not None and window_handle.startSystemMove():
                event.accept()
                return
            self._drag_pos = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self._drag_pos is not None
            and not self._window.isMaximized()
        ):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_max_restore()
