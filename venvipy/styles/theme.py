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

dark = """
    QMainWindow {
        background-color: #181d29;  /* Dark background */
        border: 1px solid #0092af;  /* Dark border */
        margin: 1px;  /* Space between window border and content */
        border-radius: 3px;
    }

    QWidget#centralwidget {
        background-color: #0092af;
        border-radius: 3px;
    }

    QMenuBar {
        background-color: #18191e;
        color: rgb(210, 210, 210)
    }

    QMenuBar::item {
        background-color: #18191e;
        color: rgb(210, 210, 210)
    }

    QMenuBar::item::selected {
        background-color: rgb(72, 72, 82)
    }

    QMenu {
        background-color: #18191e;
        color: rgb(210, 210, 210)
    }

    QMenu::item::selected {
        background-color: rgb(72, 72, 82)
    }

    QToolTip {
        background-color: rgb(47, 52, 63);
        border: rgb(47, 52, 63);
        color: rgb(210, 210, 210);
        padding: 2px;
        opacity: 325
    }
    
    QListWidget {
        background-color: #28292f;
        color: #FFFFFF;
        border-radius: 5px;
        padding: 6px;
    }

    QListWidget::item {
        border-radius: 5px;
        padding: 15px;
    }

    QListWidget::item:hover {
        background-color: #0092af;
        transition: background-color 0.4s ease-in-out;
    }

    QListWidget::item:selected {
        background-color: #0092af;
    }

    QTabWidget {
        background-color: #18191e;
        border-radius: 5px;
    }

    QTabWidget::pane {
        background-color: #18191e;
        border: 1px solid #0092af;
    }

    QTabBar::tab {
        background: #333333;
        padding: 8px;
        color: white;
        border: none;
    }

    QTabBar::tab:selected {
        background-color: #0092af;
        color: white;
    }

    QPushButton {
        background-color: #333333;
        border-radius: 8px;
        padding: 10px;
        color: grey;
        font: bold 14px;
    }

    QPushButton:hover {
        background-color: #777777;
        color: white;
    }

    QTableView {
        background-color: #12151e;
        color: white;
        border: 1px solid #0092af;
        gridline-color: #0092af;
        border: 1px solid #0092af;
    }

    QHeaderView::section {
        background-color: #141823;
        color: white;
        padding: 5px;
        border: 1px solid #0092af;
    }

    QTableView::item {
        background-color: #181d29;
        padding: 10px;
        color: #FFFFFF;
    }

    QTableView::item:selected {
        background-color: #0092af;
        color: #FFFFFF;
    }

    QScrollBar:vertical {
        background-color: #18191e;
        width: 13px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background-color: #333333;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar:horizontal {
        background-color: #18191e;
        height: 13px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background-color: #333333;
        min-width: 20px;
        border-radius: 5px;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QHeaderView::section {
        background-color: #0092af;
        color: white;
        padding: 5px;
        border: 1px solid #444;
    }

    QTableView QTableCornerButton::section {
        background-color: #0092af;
        border: 1px solid #444;
    }

    QTableView QHeaderView {
    background-color: #0092af;  /* Set background for row header */
    }
"""


light = """
    QMainWindow {
        background-color: #18191e;
        border: 1px solid #0092af;
        margin: 1px;
        border-radius: 3px;
    }

    QWidget#centralwidget {
        background-color: #0092af;
        border-radius: 3px;
    }

    QListWidget {
        background-color: #28292f;
        color: #FFFFFF;
        border: none;
        padding: 5px;
    }

    QListWidget::item {
        padding: 15px;
    }

    QListWidget::item:hover {
        background-color: #0092af;
        transition: background-color 0.2s ease-in-out;
    }

    QListWidget::item:selected {
        background-color: #0092af;
    }

    QTabWidget::pane {
        background-color: #333333;
        border-top: 1px solid #0092af;
    }

    QTabBar::tab {
        background: #333333;
        padding: 8px;
        color: white;
        border: none;
    }

    QTabBar::tab:selected {
        background-color: #0092af;
        color: white;
    }
                    
    QPushButton {
        background-color: #333333;
        border-radius: 8px;
        padding: 10px;
        color: grey;
        font: bold 14px;
    }
                    
    QPushButton:hover {
        background-color: #0092af;
        color: white;
    }
                    
    QTableView {
        background-color: #18191e;
        color: white;
        border: 1px solid #0092af;
        gridline-color: #0092af;
    }

    QHeaderView::section {
        background-color: #333333;
        color: white;
        padding: 5px;
        border: 1px solid #444;
    }

    QTableView::item {
        padding: 10px;
        background-color: #1e1e1e;
        color: #FFFFFF;
    }

    QTableView::item:selected {
        background-color: #0092af;
        color: #FFFFFF;
    }

    QScrollBar:vertical {
        background-color: #18191e;
        width: 13px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background-color: #333333;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar:horizontal {
        background-color: #18191e;
        height: 13px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background-color: #333333;
        min-width: 20px;
        border-radius: 5px;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QHeaderView::section {
        background-color: #333333;
        color: white;
        padding: 5px;
        border: 1px solid #444;
    }

    QTableView QTableCornerButton::section {
        background-color: #0092af;
        border: 1px solid #444;
    }

    QTableView QHeaderView {
    background-color: #333333;  /* Set background for row header */
    }
"""
