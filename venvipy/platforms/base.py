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
Base platform abstraction.
"""
from pathlib import Path
from typing import Any, Dict


class Platform:
    """Small OS abstraction layer."""
    name = "base"
    LAUNCHER_STATE_KEYS = (
        "desktop_venvipy",
        "desktop_wizard",
        "startmenu_venvipy",
        "startmenu_wizard",
    )

    def is_windows(self):
        return False

    def is_linux(self):
        return False

    def venv_bin_dir_name(self):
        return "bin"

    def python_exe_name(self):
        return "python"

    def pip_exe_name(self):
        return "pip"

    def venv_python_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / self.python_exe_name()

    def venv_pip_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / self.pip_exe_name()

    def activate_script_path(self, venv_dir: Path) -> Path:
        return venv_dir / self.venv_bin_dir_name() / "activate"

    def default_python_search_path(self) -> str:
        return str(Path.home())

    def site_packages_path(self, venv_dir: Path) -> Path:
        lib_dir = venv_dir / "lib"
        if not lib_dir.exists():
            lib_dir = venv_dir / "Lib"
        return lib_dir / "site-packages"

    def launcher_state_keys(self):
        """Return known launcher state keys.
        """
        return self.LAUNCHER_STATE_KEYS

    def default_launcher_state(self) -> Dict[str, bool]:
        """Return a launcher state dict with all flags disabled.
        """
        return {key: False for key in self.launcher_state_keys()}

    def normalize_launcher_state(self, state: Any) -> Dict[str, bool]:
        """Normalize launcher state values to booleans.
        """
        normalized = self.default_launcher_state()
        if not isinstance(state, dict):
            return normalized

        for key in normalized:
            normalized[key] = bool(state.get(key, False))

        return normalized

    def launcher_path(self, launcher_key: str) -> Path:
        """Return the launcher file path for a launcher key.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement launcher_path()"
        )

    def get_launcher_state(self) -> Dict[str, bool]:
        """Detect current launcher state from the filesystem.
        """
        state = self.default_launcher_state()
        for key in self.launcher_state_keys():
            try:
                state[key] = self.launcher_path(key).exists()
            except (OSError, ValueError):
                state[key] = False
        return state

    def create_launcher(self, launcher_key: str) -> None:
        """Create the launcher for a launcher key.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement create_launcher()"
        )

    def remove_launcher(self, launcher_key: str) -> None:
        """Remove the launcher for a launcher key if it exists.
        """
        launcher_file = self.launcher_path(launcher_key)
        if launcher_file.exists():
            launcher_file.unlink()

    def apply_launcher_state(self, desired_state: Dict[str, bool]) -> Dict[str, Any]:
        """Apply desired launcher state and report successes/failures.
        """
        desired = self.normalize_launcher_state(desired_state)
        before = self.get_launcher_state()
        changed = []
        unchanged = []
        failed = {}

        for key in self.launcher_state_keys():
            target_enabled = desired[key]
            current_enabled = before.get(key, False)
            if target_enabled == current_enabled:
                unchanged.append(key)
                continue

            changed.append(key)
            try:
                if target_enabled:
                    self.create_launcher(key)
                else:
                    self.remove_launcher(key)
            except (OSError, ValueError) as e:
                failed[key] = str(e)
            except Exception as e:  # pragma: no cover
                failed[key] = str(e)

        after = self.get_launcher_state()
        successful = []
        for key in changed:
            if key in failed:
                continue
            if after.get(key, False) == desired[key]:
                successful.append(key)
            else:
                failed[key] = "Launcher state could not be updated."

        return {
            "requested": desired,
            "before": before,
            "after": after,
            "changed": changed,
            "unchanged": unchanged,
            "successful": successful,
            "failed": failed,
            "ok": len(failed) == 0
        }
