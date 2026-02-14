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
import os
import sys
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

    def launcher_path(self, launcher_key: str) -> Path:
        """Return launcher file path for Windows shortcuts.
        """
        file_names = {
            "desktop_venvipy": "VenviPy.lnk",
            "desktop_wizard": "VenviPy Wizard.lnk",
            "startmenu_venvipy": "VenviPy.lnk",
            "startmenu_wizard": "VenviPy Wizard.lnk",
        }
        if launcher_key not in file_names:
            raise ValueError(f"Unsupported launcher key: {launcher_key}")

        if launcher_key.startswith("desktop_"):
            base_dir = self._desktop_dir()
        else:
            base_dir = self._startmenu_programs_dir()

        return base_dir / file_names[launcher_key]

    def create_launcher(self, launcher_key: str) -> None:
        """Create Windows .lnk launchers for VenviPy and Wizard.
        """
        launcher_file = self.launcher_path(launcher_key)
        launcher_file.parent.mkdir(parents=True, exist_ok=True)

        is_wizard = launcher_key.endswith("_wizard")
        target_path, arguments = self._launcher_target_and_arguments(is_wizard)
        description = (
            "Launch VenviPy setup wizard only"
            if is_wizard
            else "Virtual Environment Manager for Python"
        )

        self._create_shortcut(
            shortcut_path=launcher_file,
            target_path=target_path,
            arguments=arguments,
            description=description,
            working_directory=str(Path.home()),
            icon_location=self._launcher_icon_path(),
        )

    def _desktop_dir(self) -> Path:
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            return Path(user_profile) / "Desktop"
        return Path.home() / "Desktop"

    def _startmenu_programs_dir(self) -> Path:
        app_data = os.environ.get("APPDATA")
        if app_data:
            return (
                Path(app_data)
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs"
            )
        return (
            Path.home()
            / "AppData"
            / "Roaming"
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
        )

    def _launcher_target_and_arguments(self, wizard_only: bool):
        launcher_exe = shutil.which("venvipy")
        if launcher_exe:
            suffix = Path(launcher_exe).suffix.lower()
            if suffix == ".exe":
                return launcher_exe, "--wizard" if wizard_only else ""

            if suffix in (".cmd", ".bat"):
                cmd_exe = os.environ.get(
                    "ComSpec", r"C:\Windows\System32\cmd.exe"
                )
                args = f'/c "{launcher_exe}"'
                if wizard_only:
                    args += " --wizard"
                return cmd_exe, args

            return launcher_exe, "--wizard" if wizard_only else ""

        pythonw = Path(sys.executable).with_name("pythonw.exe")
        interpreter = pythonw if pythonw.exists() else Path(sys.executable)
        args = ["-m", "venvipy.venvi"]
        if wizard_only:
            args.append("--wizard")
        return str(interpreter), subprocess.list2cmdline(args)

    def _launcher_icon_path(self) -> str:
        """Resolve icon path from packaged Windows launcher icon.
        """
        icon_path = (
            Path(__file__).resolve().parents[1] / "icons" / "icon_win.ico"
        )
        if icon_path.exists():
            return str(icon_path)
        return ""

    def _create_shortcut(
        self,
        shortcut_path: Path,
        target_path: str,
        arguments: str,
        description: str,
        working_directory: str,
        icon_location: str = "",
    ) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            raise FileNotFoundError(
                "PowerShell is required to create Windows shortcuts."
            )

        script_lines = [
            "$WScriptShell = New-Object -ComObject WScript.Shell",
            "$Shortcut = $WScriptShell.CreateShortcut("
            f"'{self._ps_quote(str(shortcut_path))}')",
            f"$Shortcut.TargetPath = '{self._ps_quote(target_path)}'",
            (
                "$Shortcut.WorkingDirectory = "
                f"'{self._ps_quote(working_directory)}'"
            ),
            f"$Shortcut.Description = '{self._ps_quote(description)}'",
            f"$Shortcut.Arguments = '{self._ps_quote(arguments)}'",
        ]

        if icon_location:
            script_lines.append(
                "$Shortcut.IconLocation = "
                f"'{self._ps_quote(icon_location)}'"
            )
        elif target_path.lower().endswith(".exe"):
            script_lines.append(
                f"$Shortcut.IconLocation = '{self._ps_quote(target_path)},0'"
            )

        script_lines.append("$Shortcut.Save()")
        script = "\n".join(script_lines)

        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            message = stderr or stdout or "Failed to create shortcut."
            raise OSError(message)

    @staticmethod
    def _ps_quote(value: str) -> str:
        return value.replace("'", "''")

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
