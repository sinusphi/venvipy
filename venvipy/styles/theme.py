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
Themes
"""

# Base palette for the entire project (dark-focused).
COLORS = {
    "bg": "#0f1218",
    "surface": "#151a24",
    "surface_alt": "#1a2130",
    "panel": "#202938",
    "panel_alt": "#263144",
    "border": "#2c3850",
    "border_strong": "#35435f",
    "text": "#e6e9ef",
    "text_muted": "#a8b0bf",
    "accent": "#4ea3ff",
    "accent_soft": "#1b3556",
    "accent_strong": "#2f7be5",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "tooltip": "#1f2634",
    "tooltip_text": "#e6e9ef",
    "hover": "#2a3a55",
    "shadow": "#0b0d12",
}

dark = f"""
    QMainWindow {{
        background-color: {COLORS["bg"]};
        border: 1px solid {COLORS["border"]};
        margin: 1px;
        border-radius: 6px;
    }}

    QWidget#centralwidget {{
        background-color: {COLORS["surface"]};
        border-radius: 6px;
    }}

    QMenuBar {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
    }}

    QMenuBar::item {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
    }}

    QMenuBar::item::selected {{
        background-color: {COLORS["panel_alt"]};
    }}

    QMenu {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
    }}

    QMenu::item::selected {{
        background-color: {COLORS["panel_alt"]};
    }}

    QToolTip {{
        background-color: {COLORS["tooltip"]};
        border: 1px solid {COLORS["border"]};
        color: {COLORS["tooltip_text"]};
        padding: 4px 6px;
        opacity: 220;
    }}
    
    QListWidget {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
        padding: 6px;
    }}

    QListWidget::item {{
        border-radius: 6px;
        padding: 12px;
    }}

    QListWidget::item:hover {{
        background-color: {COLORS["hover"]};
    }}

    QListWidget::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text"]};
    }}

    QTabWidget {{
        background-color: {COLORS["surface"]};
        border-radius: 6px;
    }}

    QTabWidget::pane {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
    }}

    QTabBar::tab {{
        background: {COLORS["panel"]};
        padding: 8px 12px;
        color: {COLORS["text_muted"]};
        border: 1px solid {COLORS["border"]};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border-color: {COLORS["border_strong"]};
    }}

    QPushButton {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS["text"]};
        font: 600 13px;
    }}

    QPushButton:hover {{
        background-color: {COLORS["hover"]};
        border-color: {COLORS["border_strong"]};
    }}

    QPushButton:pressed {{
        background-color: {COLORS["panel_alt"]};
    }}

    QTableView {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        gridline-color: {COLORS["border"]};
        border-radius: 6px;
    }}

    QHeaderView::section {{
        background-color: {COLORS["panel"]};
        color: {COLORS["text"]};
        padding: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QTableView::item {{
        background-color: {COLORS["surface_alt"]};
        padding: 8px;
        color: {COLORS["text"]};
    }}

    QTableView::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text"]};
    }}

    QScrollBar:vertical {{
        background-color: {COLORS["surface"]};
        width: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS["panel_alt"]};
        min-height: 20px;
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QScrollBar:horizontal {{
        background-color: {COLORS["surface"]};
        height: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {COLORS["panel_alt"]};
        min-width: 20px;
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QTableView QTableCornerButton::section {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
    }}

    QTableView QHeaderView {{
        background-color: {COLORS["panel"]};
    }}
"""


light = f"""
    QMainWindow {{
        background-color: {COLORS["bg"]};
        border: 1px solid {COLORS["border"]};
        margin: 1px;
        border-radius: 6px;
    }}

    QWidget#centralwidget {{
        background-color: {COLORS["surface"]};
        border-radius: 6px;
    }}

    QListWidget {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        padding: 6px;
        border-radius: 6px;
    }}

    QListWidget::item {{
        padding: 12px;
    }}

    QListWidget::item:hover {{
        background-color: {COLORS["hover"]};
    }}

    QListWidget::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text"]};
    }}

    QTabWidget::pane {{
        background-color: {COLORS["surface"]};
        border-top: 1px solid {COLORS["border"]};
        border-radius: 6px;
    }}

    QTabBar::tab {{
        background: {COLORS["panel"]};
        padding: 8px 12px;
        color: {COLORS["text_muted"]};
        border: 1px solid {COLORS["border"]};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border-color: {COLORS["border_strong"]};
    }}
                    
    QPushButton {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS["text"]};
        font: 600 13px;
    }}
                    
    QPushButton:hover {{
        background-color: {COLORS["hover"]};
        border-color: {COLORS["border_strong"]};
    }}
                    
    QTableView {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        gridline-color: {COLORS["border"]};
        border-radius: 6px;
    }}

    QHeaderView::section {{
        background-color: {COLORS["panel"]};
        color: {COLORS["text"]};
        padding: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QTableView::item {{
        padding: 8px;
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
    }}

    QTableView::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text"]};
    }}

    QScrollBar:vertical {{
        background-color: {COLORS["surface"]};
        width: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS["panel_alt"]};
        min-height: 20px;
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QScrollBar:horizontal {{
        background-color: {COLORS["surface"]};
        height: 12px;
        margin: 0px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {COLORS["panel_alt"]};
        min-width: 20px;
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QTableView QTableCornerButton::section {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
    }}

    QTableView QHeaderView {{
        background-color: {COLORS["panel"]};
    }}
"""

WIZARD_QSS = f"""
    QWizard {{
        background-color: {COLORS["bg"]};
        color: {COLORS["text"]};
    }}

    QWizardPage {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
    }}

    QLabel {{
        color: {COLORS["text"]};
    }}

    QLineEdit,
    QComboBox {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        padding: 6px 8px;
    }}

    QLineEdit:focus,
    QComboBox:focus {{
        border-color: {COLORS["accent"]};
    }}

    QToolButton {{
        background-color: {COLORS["panel"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        padding: 4px;
    }}

    QToolButton:hover {{
        background-color: {COLORS["hover"]};
        border-color: {COLORS["border_strong"]};
    }}

    QGroupBox {{
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        margin-top: 10px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 6px;
        color: {COLORS["text_muted"]};
    }}

    QCheckBox {{
        color: {COLORS["text"]};
    }}

    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border-radius: 4px;
        border: 1px solid {COLORS["border"]};
        background-color: {COLORS["surface_alt"]};
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLORS["accent"]};
        border-color: {COLORS["accent"]};
    }}

    QMenu {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
    }}

    QMenu::item::selected {{
        background-color: {COLORS["panel_alt"]};
    }}

    QToolTip {{
        background-color: {COLORS["tooltip"]};
        border: 1px solid {COLORS["border"]};
        color: {COLORS["tooltip_text"]};
        padding: 4px 6px;
        opacity: 220;
    }}

    QTableView {{
        gridline-color: {COLORS["border"]};
    }}

    QTableView::item:selected {{
        selection-background-color: {COLORS["accent_soft"]};
        selection-color: {COLORS["text"]};
    }}
"""

PACKAGE_DIALOG_QSS = f"""
    QDialog {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
    }}

    QLabel {{
        color: {COLORS["text"]};
    }}

    QLineEdit {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        padding: 6px 8px;
    }}

    QLineEdit:focus {{
        border-color: {COLORS["accent"]};
    }}

    QFrame[frameShape="4"] {{
        color: {COLORS["border"]};
        border: 1px solid {COLORS["border"]};
    }}

    QTableView {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        gridline-color: {COLORS["border"]};
        border-radius: 6px;
    }}

    QHeaderView::section {{
        background-color: {COLORS["panel"]};
        color: {COLORS["text"]};
        padding: 6px;
        border: 1px solid {COLORS["border"]};
    }}

    QTableView::item:selected {{
        background-color: {COLORS["accent_soft"]};
        color: {COLORS["text"]};
    }}

    QMenu {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
    }}

    QMenu::item:selected {{
        background-color: {COLORS["panel_alt"]};
    }}
"""
