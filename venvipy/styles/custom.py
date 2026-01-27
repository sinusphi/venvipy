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
Custom Styles
"""

from .theme import COLORS

package_installer_title_text = (
    f'<p><span style="font-size:12.5pt; color: {COLORS["text"]};">\
        <b>Package Installer</b>\
    </span></p>'
)

package_manager_title_text = (
    f'<p><span style="font-size:12.5pt; color: {COLORS["text"]};">\
        <b>Package Manager</b>\
    </span></p>'
)


def package_manager_venv_name_text(venv_name):
    return (
        f'<b><span style="font-size: 13pt; color: {COLORS["accent"]};">\
            {venv_name}\
        </span></B>'
    )

interpreter_table_title_text = (
    f'<span style="font-size: 13.5pt; color: {COLORS["text"]};">\
        <b>Interpreters available</b>\
    </span>'
)
