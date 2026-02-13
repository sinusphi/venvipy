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
from typing import Any, Dict

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
    QGridLayout,
    QGroupBox,
    QCheckBox,
    QMessageBox
)

import venvipy_rc  # pylint: disable=unused-import
from get_data import __version__
from styles.theme import DIALOG_QSS


logger = logging.getLogger(__name__)

WINDOW_ICON_PATH = ":/img/profile.png"
ABOUT_LOGO_PATH = ":/img/default.png"
CONSOLE_DIALOG_WIDTH = 1375
CONSOLE_DIALOG_HEIGHT = 775
LAUNCHER_LABELS = {
    "desktop_venvipy": "Desktop / VenviPy",
    "desktop_wizard": "Desktop / Wizard only",
    "startmenu_venvipy": "Startmenu / VenviPy",
    "startmenu_wizard": "Startmenu / Wizard only",
}


def _launcher_apply_result_payload(result: Dict[str, Any]) -> Dict[str, str]:
    """Build message payload for launcher apply result dialogs.
    """
    changed = list(result.get("changed") or [])
    failed = dict(result.get("failed") or {})

    if failed:
        details = []
        for key, err in failed.items():
            label = LAUNCHER_LABELS.get(key, key)
            details.append(f"{label}: {err}")
        return {
            "type": "error",
            "title": "Launcher update failed",
            "text": "Some launcher changes could not be applied.",
            "info": (
                f"{len(changed) - len(failed)} of {len(changed)} change(s) "
                "were applied."
            ),
            "details": "\n".join(details),
        }

    if changed:
        return {
            "type": "success",
            "title": "Launchers updated",
            "text": "Launcher changes were applied successfully.",
            "info": f"{len(changed)} change(s) were applied.",
            "details": "",
        }

    return {
        "type": "success",
        "title": "No launcher changes",
        "text": "No launcher changes were required.",
        "info": "",
        "details": "",
    }


def show_launcher_apply_result(
    result: Dict[str, Any],
    parent=None
) -> Dict[str, str]:
    """Show a result dialog after launcher apply operations.
    """
    payload = _launcher_apply_result_payload(result)

    msg_box = QMessageBox(parent)
    msg_box.setWindowIcon(QIcon(WINDOW_ICON_PATH))
    msg_box.setWindowTitle(payload["title"])
    msg_box.setText(payload["text"])
    if payload["info"]:
        msg_box.setInformativeText(payload["info"])
    if payload["details"]:
        msg_box.setDetailedText(payload["details"])
    msg_box.setIcon(
        QMessageBox.Icon.Critical
        if payload["type"] == "error"
        else QMessageBox.Icon.Information
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

    return payload


def center_window(dialog):
    """Center dialog on parent window if available, else on current screen.
    """
    qr = dialog.frameGeometry()
    parent = dialog.parentWidget()
    if parent:
        anchor = parent.window()
        if anchor:
            qr.moveCenter(anchor.frameGeometry().center())
            dialog.move(qr.topLeft())
            return

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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.resize(CONSOLE_DIALOG_WIDTH, CONSOLE_DIALOG_HEIGHT)
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
            QPlainTextEdit.LineWrapMode.WidgetWidth
        )
        self.console_window.setMaximumBlockCount(5000)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.console_window)
        self.center_console()

    def showEvent(self, event):
        """Re-center on each show to avoid platform-specific drift."""
        super().showEvent(event)
        self.center_console()

    def center_console(self):
        """Center console consistently relative to parent/main window."""
        self.center()


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


class LauncherDialog(BaseDialog):
    """
    Dialog for managing Desktop and Startmenu launchers.
    """
    STATE_KEYS = (
        "desktop_venvipy",
        "desktop_wizard",
        "startmenu_venvipy",
        "startmenu_wizard",
    )

    def __init__(self, initial_state=None, parent=None):
        super().__init__(parent)
        self._initial_state = self.default_state()
        self._updating = False
        self._build_ui()
        self.set_state(initial_state or self.default_state())


    def _build_ui(self):
        self.setWindowTitle("Create launcher")
        self.setFixedSize(520, 330)
        self.center()
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.disable_window_buttons(close=False, minimize=True)
        self.setContentsMargins(10, 0, 10, 5)

        self.setStyleSheet(
            DIALOG_QSS + """
            QLabel#launcherHeader {
                font: 500 12px;
                color: #c7d2e3;
            }
            QGroupBox#launcherGroup {
                font: 600 13.5px;
                border: 1px solid #3b465c;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox#launcherGroup::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QCheckBox {
                font: 500 13px;
                spacing: 8px;
            }
            QPushButton#launcherCancelButton,
            QPushButton#launcherApplyButton {
                min-width: 68px;
                min-height: 22px;
            }
            QPushButton#launcherApplyButton[inactive="true"] {
                background-color: #243042;
                border: 1px solid #3b465c;
                color: #8f9ab0;
            }
            QPushButton#launcherApplyButton[inactive="true"]:hover {
                background-color: #2b3850;
                border: 1px solid #52617d;
                color: #a5b1c9;
            }
            """
        )

        header_label = QLabel(""" You  can  create  a  desktop  shortcut  and/or  a  startmenu  shortcut.  
 Select  the  launchers  you  want  to  create.  
 Click  Apply  to  confirm  your selection."""
        )
        header_label.setObjectName("launcherHeader")
        header_label.setWordWrap(True)

        desktop_group = QGroupBox("Desktop launcher", self)
        desktop_group.setObjectName("launcherGroup")
        desktop_layout = QGridLayout(desktop_group)
        desktop_layout.setContentsMargins(14, 10, 14, 12)
        desktop_layout.setVerticalSpacing(10)
        self.desktop_venvipy_cb = QCheckBox("VenviPy", desktop_group)
        self.desktop_wizard_cb = QCheckBox("Wizard only", desktop_group)
        desktop_layout.addWidget(self.desktop_venvipy_cb, 0, 0)
        desktop_layout.addWidget(self.desktop_wizard_cb, 1, 0)

        startmenu_group = QGroupBox("Startmenu shortcut", self)
        startmenu_group.setObjectName("launcherGroup")
        startmenu_layout = QGridLayout(startmenu_group)
        startmenu_layout.setContentsMargins(14, 10, 14, 12)
        startmenu_layout.setVerticalSpacing(10)
        self.startmenu_venvipy_cb = QCheckBox("VenviPy", startmenu_group)
        self.startmenu_wizard_cb = QCheckBox("Wizard only", startmenu_group)
        startmenu_layout.addWidget(self.startmenu_venvipy_cb, 0, 0)
        startmenu_layout.addWidget(self.startmenu_wizard_cb, 1, 0)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setObjectName("launcherCancelButton")
        #self.cancel_button.setFixedSize(96, 30)
        self.cancel_button.clicked.connect(self.reject)

        self.apply_button = QPushButton("Apply", self)
        self.apply_button.setObjectName("launcherApplyButton")
        #self.apply_button.setFixedSize(96, 30)
        self.apply_button.setProperty("inactive", True)
        self.apply_button.clicked.connect(self._on_apply_clicked)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch(1)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        layout.addWidget(header_label)
        layout.addWidget(desktop_group)
        layout.addWidget(startmenu_group)
        layout.addStretch(1)
        layout.addLayout(button_layout)

        for checkbox in self._checkboxes():
            checkbox.toggled.connect(self._on_checkbox_toggled)

    def _checkboxes(self):
        return (
            self.desktop_venvipy_cb,
            self.desktop_wizard_cb,
            self.startmenu_venvipy_cb,
            self.startmenu_wizard_cb,
        )

    def default_state(self) -> Dict[str, bool]:
        """Return a default launcher state with all flags disabled.
        """
        return {key: False for key in self.STATE_KEYS}

    def normalize_state(self, state: Any) -> Dict[str, bool]:
        """Normalize input state to the dialog schema.
        """
        normalized = self.default_state()
        if not isinstance(state, dict):
            return normalized

        for key in self.STATE_KEYS:
            normalized[key] = bool(state.get(key, False))

        return normalized

    def state(self) -> Dict[str, bool]:
        """Return the currently selected launcher state.
        """
        return {
            "desktop_venvipy": self.desktop_venvipy_cb.isChecked(),
            "desktop_wizard": self.desktop_wizard_cb.isChecked(),
            "startmenu_venvipy": self.startmenu_venvipy_cb.isChecked(),
            "startmenu_wizard": self.startmenu_wizard_cb.isChecked(),
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set dialog state and reset change tracking baseline.
        """
        normalized = self.normalize_state(state)
        self._updating = True
        self.desktop_venvipy_cb.setChecked(normalized["desktop_venvipy"])
        self.desktop_wizard_cb.setChecked(normalized["desktop_wizard"])
        self.startmenu_venvipy_cb.setChecked(normalized["startmenu_venvipy"])
        self.startmenu_wizard_cb.setChecked(normalized["startmenu_wizard"])
        self._updating = False

        self._initial_state = normalized.copy()
        self._update_apply_button_state()

    def has_changes(self) -> bool:
        """Return whether current selection differs from the baseline.
        """
        return self.state() != self._initial_state

    def _on_checkbox_toggled(self, _checked):
        if self._updating:
            return
        self._update_apply_button_state()

    def _update_apply_button_state(self):
        inactive = not self.has_changes()
        self.apply_button.setProperty("inactive", inactive)
        self.apply_button.setCursor(
            Qt.CursorShape.ArrowCursor
            if inactive
            else Qt.CursorShape.PointingHandCursor
        )
        self.apply_button.style().unpolish(self.apply_button)
        self.apply_button.style().polish(self.apply_button)
        self.apply_button.update()

    def _on_apply_clicked(self):
        if not self.has_changes():
            return
        self.accept()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    print(f"{'-'*20}\nTesting dialogs...\n")

    #progress_dialog = ProgBarDialog()
    #progress_dialog.show()

    #console_dialog = ConsoleDialog()
    #console_dialog.show()

    #info_about_venvipy = InfoAboutVenviPy()
    #info_about_venvipy.show()

    launcher_dialog = LauncherDialog("desktop_venvipy")
    launcher_dialog.exec()

    #sys.exit(app.exec())
