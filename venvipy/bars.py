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
    Reusable custom title bar widget.
    """
    def __init__(
        self,
        parent,
        *,
        window=None,
        title="",
        icon_path=None,
        icon_pixmap=None,
        icon_size=(24, 22),
        on_close=None,
        show_minimize=True,
        show_maximize=True,
        show_close=True,
    ):
        super().__init__(parent)
        self._window = window or parent
        self._drag_pos = None
        self._on_close = on_close

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

        self.icon_label = QLabel(self)
        self.icon_label.setObjectName("titleIcon")
        self.set_icon(
            icon_pixmap=icon_pixmap,
            icon_path=icon_path,
            icon_size=icon_size
        )
        if self.icon_label.pixmap() is None:
            self.icon_label.hide()

        self.title_label = QLabel(title, self)
        self.title_label.setStyleSheet("""
            font-family: 'DejaVu Sans';
            font-size: 15px;
            font-weight: bold;
            """
        )
        self.title_label.setObjectName("titleLabel")
        if not title:
            self.title_label.hide()

        layout.addWidget(self.icon_label)
        layout.addStretch(1)
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.min_button = None
        self.max_button = None
        self.close_button = None

        if show_minimize:
            self.min_button = QToolButton(self)
            self.min_button.setIcon(self.win_min_icon)
            self.min_button.setObjectName("titleButton")

            if hasattr(self._window, "showMinimized"):
                self.min_button.clicked.connect(self._window.showMinimized)

            layout.addWidget(self.min_button)

        if show_maximize:
            self.max_button = QToolButton(self)
            self.max_button.setObjectName("titleButton")
            self.max_button.clicked.connect(self.toggle_max_restore)
            self.update_maximize_icon()
            layout.addWidget(self.max_button)

        if show_close:
            self.close_button = QToolButton(self)
            self.close_button.setIcon(self.win_close_icon)
            self.close_button.setObjectName("closeButton")
            self.close_button.clicked.connect(self._handle_close)
            layout.addWidget(self.close_button)


    def set_title(self, title):
        """Update title label text and visibility.
        """
        self.title_label.setText(title)
        self.title_label.setVisible(bool(title))


    def set_icon(self, *, icon_pixmap=None, icon_path=None, icon_size=(24, 22)):
        """Update the icon label.
        """
        pixmap = None
        if icon_pixmap is not None:
            pixmap = icon_pixmap
        elif icon_path:
            pixmap = QPixmap(icon_path)
        if pixmap is not None and not pixmap.isNull():
            scaled = pixmap.scaled(
                icon_size[0],
                icon_size[1],
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
            self.icon_label.setPixmap(scaled)
            self.icon_label.setVisible(True)
        else:
            self.icon_label.clear()
            self.icon_label.setVisible(False)


    def _handle_close(self):
        if self._on_close is not None:
            self._on_close()
            return
        if hasattr(self._window, "close"):
            self._window.close()


    def update_maximize_icon(self):
        """Update maximize/restore icon.
        """
        if not self.max_button:
            return
        if self._window and self._window.isMaximized():
            icon = self.win_normal_icon
        else:
            icon = self.win_max_icon
        self.max_button.setIcon(icon)


    def toggle_max_restore(self):
        """Toggle maximize/restore.
        """
        if not self._window:
            return
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.update_maximize_icon()


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._window:
                window_handle = self._window.windowHandle()
                if window_handle is not None and window_handle.startSystemMove():
                    event.accept()
                    return
                self._drag_pos = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self._drag_pos is not None
            and self._window
            and not self._window.isMaximized()
        ):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_max_restore()
