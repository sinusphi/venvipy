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
This module provides several necessary data.
"""
import re
import os
import sys
import csv
import time
import json
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from subprocess import PIPE, STDOUT, run
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests

from platforms import get_platform

__version__ = "0.4.4"

CFG_DIR = Path.home() / ".venvipy"
DB_FILE = Path.home() / ".venvipy" / "py-installs"
ACTIVE_DIR = Path.home() / ".venvipy" / "selected-dir"
ACTIVE_VENV = Path.home() / ".venvipy" / "active-venv"
TABS_STATE = Path.home() / ".venvipy" / "tabs-state.json"
LAUNCHER_STATE = Path.home() / ".venvipy" / "launcher-state.json"
PYPI_SIMPLE_URL = "https://pypi.org/simple/"
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"
PACKAGE_DB_PATH = Path.home() / ".venvipy" / "pypi_index.sqlite3"
DB_TABLE = "projects"
DB_COL = "name"

logger = logging.getLogger(__name__)


#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    """
    Info about Python installs.
    """
    py_version: str
    py_path: str


def to_version(value):
    """Convert a value to a readable version string.
    """
    return f"Python {value}"


def to_path(bin_path, version):
    """Return the absolute path to a python binary.
    """
    platform = get_platform()
    base_path = Path(bin_path)
    if platform.is_windows():
        return str(base_path / platform.python_exe_name())
    return str(base_path / f"{platform.python_exe_name()}{version}")


def is_writable(target_dir):
    """Test whether a directory is writable.
    """
    if os.path.exists(target_dir):
        test_file = os.path.join(target_dir, "test_file")

        try:
            logger.debug("Testing whether filesystem is writable...")
            with open(test_file, "w+", encoding="utf-8") as f:
                f.write("test")

            os.remove(test_file)
            logger.debug("Filesystem is writable")
            return True

        except OSError as e:
            logger.debug(f"Filesystem is read-only\n{e}")
            return False

    else:
        logger.debug(f"No such file or directory: {target_dir}")
        return False

    return False


def ensure_confdir():
    """Create `~/.venvipy` config directory.
    """
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)


def ensure_dbfile():
    """Create the database in `~/.venvipy/py-installs`.
    """
    if not os.path.exists(DB_FILE):
        get_python_installs()


def ensure_active_dir():
    """Create the file that holds the selected path to venvs.
    """
    ensure_confdir()
    if not os.path.exists(ACTIVE_DIR):
        with open(ACTIVE_DIR, "w+", encoding="utf-8") as f:
            f.write("")


def ensure_active_venv():
    """Create the file that holds the selected path to venvs.
    """
    ensure_confdir()
    if not os.path.exists(ACTIVE_VENV):
        with open(ACTIVE_VENV, "w+", encoding="utf-8") as f:
            f.write("")


def default_tabs_state() -> Dict[str, Any]:
    """Return the default structure for stored tabs.
    """
    return {
        "tabs": [],
        "active_index": 0,
        "always_save_tabs": False,
        "ask_before_saving_tabs": True
    }


def load_tabs_state() -> Dict[str, Any]:
    """Load persisted tab information if present.
    """
    ensure_confdir()

    if not os.path.exists(TABS_STATE):
        return default_tabs_state()

    try:
        with open(TABS_STATE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        logger.warning("Could not read tabs state file; starting fresh")

    return default_tabs_state()


def save_tabs_state(state: Dict[str, Any]) -> None:
    """Persist tab information to disk.
    """
    ensure_confdir()

    try:
        with open(TABS_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        logger.warning(f"Failed to save tabs state: {e}")


def default_launcher_state() -> Dict[str, Any]:
    """Return the default structure for launcher preferences.
    """
    return {
        "prompt_shown": False,
        "desktop_venvipy": False,
        "desktop_wizard": False,
        "startmenu_venvipy": False,
        "startmenu_wizard": False
    }


def normalize_launcher_state(state: Any) -> Dict[str, Any]:
    """Normalize persisted launcher state to the expected schema.
    """
    defaults = default_launcher_state()
    if not isinstance(state, dict):
        return defaults

    normalized = defaults.copy()
    normalized["prompt_shown"] = bool(state.get("prompt_shown", False))

    for key in (
            "desktop_venvipy",
            "desktop_wizard",
            "startmenu_venvipy",
            "startmenu_wizard"
        ):
        normalized[key] = bool(state.get(key, False))

    return normalized


def load_launcher_state() -> Dict[str, Any]:
    """Load persisted launcher settings if present.
    """
    ensure_confdir()

    if not os.path.exists(LAUNCHER_STATE):
        return default_launcher_state()

    try:
        with open(LAUNCHER_STATE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        logger.warning("Could not read launcher state file; using defaults")
        return default_launcher_state()

    return normalize_launcher_state(data)


def save_launcher_state(state: Dict[str, Any]) -> None:
    """Persist launcher settings to disk.
    """
    ensure_confdir()

    try:
        with open(LAUNCHER_STATE, "w", encoding="utf-8") as f:
            json.dump(normalize_launcher_state(state), f, indent=2)
    except OSError as e:
        logger.warning(f"Failed to save launcher state: {e}")


def get_python_version(py_path):
    """Return Python version.
    """
    res = run(
        [py_path, "-V"],
        stdout=PIPE,
        stderr=STDOUT,
        encoding="utf-8",
        errors="replace",
        text=True,
        check=False,
    )

    python_version = (res.stdout or "").strip()
    return python_version


def get_python_installs(relaunching=False):
    """
    Write the found Python versions to `py-installs`. Create
    a new database if `relaunching=True`.
    """
    LATEST = 15
    versions = [f"3.{v}" for v in range(LATEST, 2, -1)]
    py_info_list = []
    platform = get_platform()

    ensure_confdir()

    if not os.path.exists(DB_FILE) or relaunching:
        with open(DB_FILE, "w", newline="", encoding="utf-8") as cf:
            fields = ["PYTHON_VERSION", "PYTHON_PATH"]
            writer = csv.DictWriter(
                cf,
                delimiter=",",
                quoting=csv.QUOTE_ALL,
                fieldnames=fields
            )
            writer.writeheader()

            if platform.is_windows():
                python_paths = _get_windows_python_paths()
                for python_path in python_paths:
                    if _is_venv_interpreter(python_path):
                        continue
                    python_version = get_python_version(python_path)
                    py_info = PythonInfo(python_version, python_path)
                    py_info_list.append(py_info)
                    writer.writerow({
                        "PYTHON_VERSION": py_info.py_version,
                        "PYTHON_PATH": py_info.py_path
                    })
            else:
                for version in versions:
                    python_path = shutil.which(f"python{version}")
                    if python_path is not None:
                        if _is_venv_interpreter(python_path):
                            continue
                        python_version = get_python_version(python_path)
                        py_info = PythonInfo(python_version, python_path)
                        py_info_list.append(py_info)
                        writer.writerow({
                            "PYTHON_VERSION": py_info.py_version,
                            "PYTHON_PATH": py_info.py_path
                        })
            cf.close()

            # add the system's Python manually if running in a virtual env
            if "VIRTUAL_ENV" in os.environ:
                system_python = os.path.realpath(sys.executable)
                add_python(system_python)

        return py_info_list[::-1]
    return False


def _get_windows_python_paths():
    paths = []
    py_launcher = run(
        ["py", "-0p"],
        stdout=PIPE,
        stderr=STDOUT,
        encoding="utf-8",
        errors="replace",
        text=True,
        check=False,
    )
    if py_launcher.returncode == 0:
        for line in py_launcher.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            candidate = parts[-1] if parts else ""
            if candidate and os.path.exists(candidate):
                paths.append(candidate)

    if not paths:
        where_python = run(
            ["where", "python"],
            stdout=PIPE,
            stderr=STDOUT,
            encoding="utf-8",
            errors="replace",
            text=True,
            check=False,
        )
        if where_python.returncode == 0:
            for line in where_python.stdout.splitlines():
                candidate = line.strip()
                if candidate and os.path.exists(candidate):
                    paths.append(candidate)

    unique_paths = []
    for path in paths:
        if path not in unique_paths:
            unique_paths.append(path)
    return unique_paths


def add_python(py_path):
    """
    Write (append) Python version and path to `py-installs`.
    """
    ensure_dbfile()

    with open(DB_FILE, "a", newline="", encoding="utf-8") as cf:
        fields = ["PYTHON_VERSION", "PYTHON_PATH"]
        writer = csv.DictWriter(
            cf,
            delimiter=",",
            quoting=csv.QUOTE_ALL,
            fieldnames=fields
        )
        writer.writerow({
            "PYTHON_VERSION": get_python_version(py_path),
            "PYTHON_PATH": py_path
        })
        cf.close()

    # remove the interpreter if running in a virtual env
    if "VIRTUAL_ENV" in os.environ:
        remove_env()

def _is_venv_interpreter(py_path):
    """
    Return True if py_path points to the active venv interpreter.
    """
    venv_root = os.environ.get("VIRTUAL_ENV")
    if not venv_root:
        return False

    venv_root = os.path.realpath(venv_root)
    candidate = os.path.realpath(py_path)
    candidate_raw = os.path.abspath(py_path)

    def _within(root, path):
        try:
            return os.path.commonpath([root, path]) == root
        except ValueError:
            return False

    return _within(venv_root, candidate) or _within(venv_root, candidate_raw)



def remove_env():
    """
    Remove interpreters that belong to the active virtual environment.
    """
    if "VIRTUAL_ENV" not in os.environ:
        return

    with open(DB_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter=","))

    with open(DB_FILE, "w", newline="", encoding="utf-8") as f:
        fields = ["PYTHON_VERSION", "PYTHON_PATH"]
        writer = csv.DictWriter(
            f,
            delimiter=",",
            quoting=csv.QUOTE_ALL,
            fieldnames=fields
        )
        writer.writeheader()
        for row in rows:
            python_path = row.get("PYTHON_PATH", "")
            if python_path and _is_venv_interpreter(python_path):
                continue
            writer.writerow({
                "PYTHON_VERSION": row.get("PYTHON_VERSION", ""),
                "PYTHON_PATH": python_path,
            })








#]===========================================================================[#
#] GET VENVS [#==============================================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    """_"""
    venv_name: str
    venv_version: str
    site_packages: str
    is_installed: str
    venv_comment: str


def get_venvs(path):
    """
    Get the available virtual environments
    from the specified folder.
    """
    # return an emtpty list if directory doesn't exist
    if not os.path.isdir(path):
        return []

    venv_info_list = []

    for i, venv in enumerate(os.listdir(path)):
        # build path to venv directory
        valid_venv = os.path.join(path, venv)

        # only look for dirs
        if not os.path.isdir(valid_venv):
            continue

        # build path to pyvenv.cfg file
        cfg_file = os.path.join(valid_venv, "pyvenv.cfg")
        if not os.path.isfile(cfg_file):
            continue

        # build path to venvipy.cfg file
        venvipy_cfg_file = os.path.join(valid_venv, "venvipy.cfg")

        venv_name = os.path.basename(valid_venv)
        venv_version = get_config(cfg_file, "version")
        site_packages = get_config(cfg_file, "site_packages")
        is_installed = get_config(cfg_file, "installed")
        venv_comment = get_comment(venvipy_cfg_file)

        venv_info = VenvInfo(
            venv_name,
            venv_version,
            site_packages,
            is_installed,
            venv_comment
        )
        venv_info_list.append(venv_info)

    return venv_info_list[::-1]


def get_config(cfg_file, cfg):
    """
    Return the values as string from a `pyvenv.cfg` file.
    Values for `cfg` can be: `version`, `py_path`,
    `site_packages`, `installed`, `comment`.
    """
    with open(cfg_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    config = {}

    for line in lines:
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        config[key.strip().lower()] = value.strip()


    def normalized_version(value):
        numbers = re.findall(r"\d+", value)

        if len(numbers) >= 3:
            return ".".join(numbers[:3])

        if len(numbers) >= 2:
            return ".".join(numbers[:2])

        return value.strip()


    def major_minor(value):
        numbers = re.findall(r"\d+", value)
        if len(numbers) >= 2:
            return f"{numbers[0]}.{numbers[1]}"
        return value.strip()


    raw_version = config.get("version") or config.get("version_info", "")
    version_value = normalized_version(raw_version) if raw_version else "N/A"
    version_str = to_version(version_value) if raw_version else "N/A"

    home = config.get("home", "")
    base_executable = config.get("base-executable", "")
    version_suffix = major_minor(version_value) if raw_version else ""
    binary_path = base_executable or to_path(home, version_suffix)

    site_packages = config.get("include-system-site-packages", "N/A")

    if cfg == "version":
        return version_str

    if cfg == "py_path":
        return binary_path

    if cfg == "site_packages":
        if site_packages == "true":
            return "global"
        if site_packages == "false":
            return "isolated"
        return "N/A"

    if cfg == "installed":
        ensure_dbfile()
        with open(DB_FILE, newline="", encoding="utf-8") as cf:
            reader = csv.DictReader(cf, delimiter=",")
            for info in reader:
                if binary_path == info["PYTHON_PATH"]:
                    return "yes"
            return "no"

    return "N/A"


def get_active_dir_str():
    """Return path to selected directory.
    """
    ensure_active_dir()
    with open(ACTIVE_DIR, "r", encoding="utf-8") as f:
        selected_dir = f.read()
        return selected_dir
    return ""


def get_selected_dir():
    """
    Get the selected directory path from `selected-dir`
    file. Return `get_venvs()`.
    """
    selected_dir = get_active_dir_str()
    return get_venvs(selected_dir)


def get_comment(cfg_file):
    """Get the comment string from `venvipy_cfg` file.
    """
    if os.path.exists(cfg_file):
        with open(cfg_file, "r", encoding="utf-8") as f:
            venv_comment = f.read()

        return venv_comment
    return ""



#]===========================================================================[#
#] GET INFOS FROM PYTHON PACKAGE INDEX [#====================================[#
#]===========================================================================[#

@dataclass
class PackageInfo:
    """
    Info about a PyPI package.
    """
    pkg_name: str
    pkg_version: str
    pkg_info_2: str
    pkg_summary: str



def ensure_pypi_db() -> None:
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("CREATE TABLE IF NOT EXISTS projects (name TEXT PRIMARY KEY)")
        con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_projects_name_nocase ON projects(name COLLATE NOCASE)")

        # cache table: version/author/summary + timestamp
        # if older schema exists -> drop & recreate once (simple, no ALTER-mess)
        cols = {r[1] for r in con.execute("PRAGMA table_info(pkg_meta)").fetchall()}
        if cols and not {"name", "version", "info_2", "summary", "fetched_at"}.issubset(cols):
            con.execute("DROP TABLE IF EXISTS pkg_meta")

        con.execute("""
            CREATE TABLE IF NOT EXISTS pkg_meta (
                name TEXT PRIMARY KEY,
                version TEXT NOT NULL DEFAULT '',
                info_2  TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                fetched_at INTEGER NOT NULL DEFAULT 0
            )
        """)

def update_pypi_index(force: bool = False, timeout: int = 60) -> bool:
    """
    Returns True if DB was updated, False if unchanged.
    """
    ensure_pypi_db()

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT value FROM meta WHERE key='last_serial'")
        row = cur.fetchone()
        stored_serial = row[0] if row else None

    with requests.Session() as s:
        r = s.get(
            PYPI_SIMPLE_URL,
            headers={
                "Accept": "application/vnd.pypi.simple.v1+json, application/json;q=0.9, text/html;q=0.1",
                "User-Agent": "venvipy",
            },
            timeout=timeout,
        )
        r.raise_for_status()

        last_serial = r.headers.get("X-PyPI-Last-Serial")

        if (not force) and last_serial and stored_serial == last_serial:
            return False

        ctype = (r.headers.get("content-type") or "").lower()
        if "json" in ctype:
            data = r.json()
            projects = [p["name"] for p in data.get("projects", []) if isinstance(p, dict) and p.get("name")]
        else:
            soup = BeautifulSoup(r.text, "html.parser")
            projects = [a.get_text(strip=True) for a in soup.select("a") if a.get_text(strip=True)]

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute("BEGIN")
        con.execute("DELETE FROM projects")
        con.executemany("INSERT INTO projects(name) VALUES (?)", [(n,) for n in projects])
        con.execute(
            """
            INSERT INTO meta(key, value) VALUES ('last_serial', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (last_serial or "",),
        )
        con.commit()

    return True


def _get_db_names(name: str, following: int) -> List[str]:
    """
    Returns anchor match + `following` subsequent package names (alphabetical).
    If nothing found, returns [].
    """
    if not name or following < 0:
        return []

    def q1(cur, sql, params) -> Optional[str]:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else None

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        cur = con.cursor()

        # 1) exact (case-insensitive)
        anchor = q1(
            cur,
            f"SELECT {DB_COL} FROM {DB_TABLE} WHERE lower({DB_COL}) = lower(?) LIMIT 1",
            (name,),
        )

        # 2) prefix (case-insensitive)
        if anchor is None:
            anchor = q1(
                cur,
                f"""
                SELECT {DB_COL}
                FROM {DB_TABLE}
                WHERE {DB_COL} LIKE ? ESCAPE '\\' COLLATE NOCASE
                ORDER BY {DB_COL} COLLATE NOCASE
                LIMIT 1
                """,
                (f"{name}%",),
            )

        # 3) contains (case-insensitive), prefer earlier occurrence + shorter names
        if anchor is None:
            anchor = q1(
                cur,
                f"""
                SELECT {DB_COL}
                FROM {DB_TABLE}
                WHERE {DB_COL} LIKE ? COLLATE NOCASE
                ORDER BY instr(lower({DB_COL}), lower(?)) ASC, length({DB_COL}) ASC, {DB_COL} COLLATE NOCASE
                LIMIT 1
                """,
                (f"%{name}%", name),
            )

        # 4) fallback: next alphabetical position
        if anchor is None:
            anchor = q1(
                cur,
                f"""
                SELECT {DB_COL}
                FROM {DB_TABLE}
                WHERE {DB_COL} >= ? COLLATE NOCASE
                ORDER BY {DB_COL} COLLATE NOCASE
                LIMIT 1
                """,
                (name,),
            )

        if anchor is None:
            return []

        # anchor + following subsequent
        limit = following + 1
        cur.execute(
            f"""
            SELECT {DB_COL}
            FROM {DB_TABLE}
            WHERE {DB_COL} >= ? COLLATE NOCASE
            ORDER BY {DB_COL} COLLATE NOCASE
            LIMIT ?
            """,
            (anchor, limit),
        )
        return [r[0] for r in cur.fetchall()]


def get_db_name(name: str, following: int) -> str:
    """
    Returns a newline-separated string of suggested package names.
    If nothing found, returns "".
    """
    names = _get_db_names(name, following)
    return "\n".join(names) if names else ""


def get_pkg_info_2(name: str, ttl_sec: int = 24 * 3600) -> str:
    """
    Return author (pkg_info_2) for `name`,
    cached in ~/.venvipy/pypi_index.sqlite3.
    """
    if not name:
        return ""

    now = int(time.time())

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS pkg_meta (
                name TEXT PRIMARY KEY,
                version TEXT NOT NULL DEFAULT '',
                info_2  TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                fetched_at INTEGER NOT NULL
            )
        """)

        row = con.execute(
            "SELECT info_2, fetched_at FROM pkg_meta WHERE name = ?",
            (name,),
        ).fetchone()

        if row:
            cached_info_2, fetched_at = row
            if cached_info_2 and (now - int(fetched_at) < ttl_sec):
                return cached_info_2

    # fetch fresh
    try:
        r = requests.get(PYPI_JSON_URL.format(name=name), timeout=10)
        if r.status_code == 404:
            return ""
        r.raise_for_status()
        info = r.json().get("info", {}) or {}
        author = (info.get("author") or "").strip()
        author_email = (info.get("author_email") or "").strip()

        # keep it short but useful
        info_2 = author
        if author_email and author_email not in info_2:
            info_2 = f"{author} <{author_email}>".strip() if author else author_email
    except Exception:
        if row:
            return row[0] or ""
        return ""

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute(
            """
            INSERT INTO pkg_meta(name, info_2, fetched_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                info_2 = excluded.info_2,
                fetched_at = excluded.fetched_at
            """,
            (name, info_2, now),
        )

    return info_2


def get_pkg_summary(name: str, ttl_sec: int = 24 * 3600) -> str:
    """
    Return short description (PyPI 'summary')
    for `name`, cached in pkg_meta.summary.
    """
    if not name:
        return ""

    now = int(time.time())

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        row = con.execute(
            "SELECT summary, fetched_at FROM pkg_meta WHERE name = ?",
            (name,),
        ).fetchone()

    if row:
        cached_summary, fetched_at = row
        if cached_summary and (now - int(fetched_at) < ttl_sec):
            return cached_summary
    else:
        cached_summary = ""

    try:
        r = requests.get(PYPI_JSON_URL.format(name=name), timeout=10)
        if r.status_code == 404:
            return ""
        r.raise_for_status()
        info = r.json().get("info", {}) or {}

        summary = (info.get("summary") or "").strip()
        if not summary:
            # fallback: derive a short line from long description
            desc = (info.get("description") or "").strip()
            summary = re.sub(r"\s+", " ", desc).strip()[:160] if desc else ""
    except Exception:
        return cached_summary or ""

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute(
            """
            INSERT INTO pkg_meta(name, summary, fetched_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                summary = excluded.summary,
                fetched_at = excluded.fetched_at
            """,
            (name, summary, now),
        )

    return summary


def get_pkg_version(name: str, ttl_sec: int = 24 * 3600) -> str:
    """
    Return latest version for `name`, cached
    in ~/.venvipy/pypi_index.sqlite3.
    """
    if not name:
        return ""

    now = int(time.time())

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS pkg_meta (
                name TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                fetched_at INTEGER NOT NULL
            )
        """)

        row = con.execute(
            "SELECT version, fetched_at FROM pkg_meta WHERE name = ?",
            (name,),
        ).fetchone()

        if row:
            cached_version, fetched_at = row
            if cached_version and (now - int(fetched_at) < ttl_sec):
                return cached_version

    # fetch fresh
    try:
        r = requests.get(PYPI_JSON_URL.format(name=name), timeout=10)
        if r.status_code == 404:
            return ""
        r.raise_for_status()
        version = (r.json().get("info", {}) or {}).get("version", "") or ""
    except Exception:
        # fallback to cached if available
        if row:
            return row[0] or ""
        return ""

    with sqlite3.connect(PACKAGE_DB_PATH) as con:
        con.execute(
            """
            INSERT INTO pkg_meta(name, version, fetched_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                version = excluded.version,
                fetched_at = excluded.fetched_at
            """,
            (name, version, now),
        )

    return version


def get_package_infos(pkg: str) -> list[PackageInfo]:
    """Get package infos from PyPI (pkg_name from DB for now).
    """
    package_info_list: list[PackageInfo] = []

    # e.g. show 15 suggestions; adjust as needed
    for pkg_name in _get_db_names(pkg, following=15):
        pkg_version = get_pkg_version(pkg_name)
        pkg_info_2 = get_pkg_info_2(pkg_name)
        pkg_summary = get_pkg_summary(pkg_name)

        pkg_info = PackageInfo(
            pkg_name,
            pkg_version,
            pkg_info_2,
            pkg_summary
        )
        package_info_list.append(pkg_info)

    return package_info_list[::-1]


def get_installed_packages(venv_location, venv_name) -> list:
    """Get infos about installed packages.
    """
    platform = get_platform()
    venv_path = Path(venv_location) / venv_name
    site_packages_dir = platform.site_packages_path(venv_path)

    # get list of installed packages
    package_info_list = []
    if not site_packages_dir.exists():
        return package_info_list
    site_packages = os.listdir(site_packages_dir)

    for pkg in site_packages:
        if ".dist-info" in pkg:
            meta_file = site_packages_dir / pkg / "METADATA"

            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta_data = f.readlines()
            except FileNotFoundError:
                logger.debug(f"File '{meta_file}' not found.")
                continue

            pkg_name = ""
            pkg_version = ""
            pkg_info_2 = ""
            pkg_summary = ""

            # search for each str
            for line in meta_data:
                if "Name: " in line:
                    pkg_name = line[5:].strip()

                if "Version: " in line:
                    pkg_version = line[8:].strip()

                if "Author: " in line:
                    pkg_info_2 = line[7:].strip()

                if "Summary: " in line:
                    pkg_summary = line[8:].strip()

            if pkg_name:
                pkg_info = PackageInfo(
                    pkg_name,
                    pkg_version,
                    pkg_info_2,
                    pkg_summary
                )
                package_info_list.append(pkg_info)

    return package_info_list[::-1]






if __name__ == "__main__":

    update_pypi_index(True)
    
    print(get_package_infos("venvipy"))
