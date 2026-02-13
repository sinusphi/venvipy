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
Linux platform implementation.
"""
from pathlib import Path
import os
import shlex
import shutil
import stat
import sys

from .base import Platform


class LinuxPlatform(Platform):
    name = "linux"


    def is_linux(self):
        return True


    def default_python_search_path(self) -> str:
        return "/usr/local/bin"


    def site_packages_path(self, venv_dir):
        lib_dir = venv_dir / "lib"
        if not lib_dir.exists():
            return lib_dir / "site-packages"
        python_dirs = [p for p in lib_dir.iterdir() if p.is_dir()]
        if not python_dirs:
            return lib_dir / "site-packages"
        return python_dirs[0] / "site-packages"


    def _desktop_dir(self) -> Path:
        """Resolve desktop folder from XDG config with sensible fallbacks.
        """
        user_dirs = Path.home() / ".config" / "user-dirs.dirs"
        if user_dirs.exists():
            try:
                lines = user_dirs.read_text(encoding="utf-8").splitlines()
            except OSError:
                lines = []

            for line in lines:
                line = line.strip()
                if not line.startswith("XDG_DESKTOP_DIR="):
                    continue
                raw = line.split("=", 1)[1].strip().strip('"')
                raw = raw.replace("$HOME", str(Path.home()))
                desktop_dir = Path(os.path.expanduser(raw))
                return desktop_dir

        for name in ("Desktop", "Schreibtisch"):
            candidate = Path.home() / name
            if candidate.exists():
                return candidate

        return Path.home() / "Desktop"


    def launcher_path(self, launcher_key: str) -> Path:
        """Return launcher file path for Linux desktop entries.
        """
        file_names = {
            "desktop_venvipy": "VenviPy.desktop",
            "desktop_wizard": "VenviPy-Wizard.desktop",
            "startmenu_venvipy": "venvipy.desktop",
            "startmenu_wizard": "venvipy-wizard.desktop",
        }
        if launcher_key not in file_names:
            raise ValueError(f"Unsupported launcher key: {launcher_key}")

        if launcher_key.startswith("desktop_"):
            base_dir = self._desktop_dir()
        else:
            base_dir = Path.home() / ".local" / "share" / "applications"

        return base_dir / file_names[launcher_key]


    def create_launcher(self, launcher_key: str) -> None:
        """Create Linux .desktop launchers for VenviPy and Wizard.
        """
        launcher_file = self.launcher_path(launcher_key)
        launcher_file.parent.mkdir(parents=True, exist_ok=True)

        is_wizard = launcher_key.endswith("_wizard")
        entry_name = "VenviPy Wizard" if is_wizard else "VenviPy"
        entry_comment = (
            "Launch VenviPy setup wizard only"
            if is_wizard
            else "Virtual Environment Manager for Python"
        )

        launcher_cmd = self._launcher_command(is_wizard)
        icon_file = self._launcher_icon_path(is_wizard)

        lines = [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            f"Name={entry_name}",
            f"Comment={entry_comment}",
            f"Exec={launcher_cmd}",
            "Terminal=false",
            "Categories=Development;Utility;",
        ]
        if icon_file:
            lines.append(f"Icon={icon_file}")

        launcher_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        launcher_file.chmod(
            launcher_file.stat().st_mode
            | stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH
        )


    def _launcher_command(self, wizard_only: bool) -> str:
        """Build the command executed by the .desktop launcher.
        """
        launcher_exe = shutil.which("venvipy")
        if launcher_exe:
            parts = [launcher_exe]
        else:
            parts = [sys.executable, "-m", "venvipy.venvi"]

        if wizard_only:
            parts.append("--wizard")

        return " ".join(shlex.quote(part) for part in parts)


    def _launcher_icon_path(self, wizard_only: bool) -> str:
        """Resolve icon path from repository image assets.
        """
        img_dir = Path(__file__).resolve().parents[2] / "img"
        icon_name = "default.png" if wizard_only else "profile.png"
        icon_path = img_dir / icon_name
        if icon_path.exists():
            return str(icon_path)

        fallback = img_dir / "profile.png"
        if fallback.exists():
            return str(fallback)
        return ""
