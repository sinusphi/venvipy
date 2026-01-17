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
Windows platform implementation.
"""
from pathlib import Path
from typing import Optional, Dict
import subprocess
import shutil

from .base import Platform


class WindowsPlatform(Platform):
    name = "windows"

    def is_windows(self):
        return True

    def venv_bin_dir_name(self):
        return "Scripts"

    def python_exe_name(self):
        return "python.exe"

    def pip_exe_name(self):
        return "pip.exe"

    def activate_script_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / "activate.bat"

    def default_python_search_path(self) -> str:
        return str(Path.home())

    def site_packages_path(self, venv_dir: Path) -> Path:
        return venv_dir / "Lib" / "site-packages"

    def open_activated_terminal(
        self,
        venv_dir: Path,
        workdir: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        banner: bool = False,
    ) -> None:
        if workdir is None:
            workdir = Path.home()

        scripts = venv_dir / self.venv_bin_dir_name()
        activate_ps1 = scripts / "Activate.ps1"
        activate_bat = scripts / "activate.bat"

        # prefer PowerShell (better UX), fallback to cmd
        if activate_ps1.exists() and shutil.which("powershell"):
            def psq(s: str) -> str:
                # single-quote for PowerShell, escape embedded quotes
                return "'" + s.replace("'", "''") + "'"

            parts = [
                f"& {psq(str(activate_ps1))}",
                f"Set-Location -LiteralPath {psq(str(workdir))}",
            ]
            if banner:
                parts += [
                    'Write-Host ("Active environment: " + $env:VIRTUAL_ENV)',
                    'Write-Host ("Python interpreter: " + (Get-Command python).Source)',
                ]
            cmdline = "; ".join(parts)

            if shutil.which("wt"):
                cmd = ["wt", "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", cmdline]
            else:
                cmd = ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", cmdline]

            subprocess.Popen(cmd, env=env)
            return

        # cmd.exe fallback
        if activate_bat.exists():
            # /d allows drive change
            inner = f'cd /d "{workdir}" & call "{activate_bat}"'
            if banner:
                inner += ' & echo Active environment: %VIRTUAL_ENV% & where python'
            cmd = ["cmd.exe", "/K", inner]
            subprocess.Popen(cmd, env=env)
            return

        raise FileNotFoundError("No activation script found in venv Scripts/ directory.")
