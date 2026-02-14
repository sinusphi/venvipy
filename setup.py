import sys
import ast
import re
from pathlib import Path
from setuptools import setup, find_packages


CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta

try:
    with open(CURRENT_DIR / "README.rst", "r", encoding="utf-8") as f:
        long_desc = f.read()
except FileNotFoundError:
    long_desc = ""

_version_re = re.compile(r"__version__\s+=\s+(.*)")
try:
    with open(CURRENT_DIR / "venvipy/get_data.py", "rb") as f:
        version = str(ast.literal_eval(
            _version_re.search(
                f.read().decode("utf-8")).group(1)
            )
        )
except FileNotFoundError:
    version = "latest"

install_requires = [
    "PyQt6==6.10.2",
    "requests",
    "beautifulsoup4",
]

setup(
    name="venvipy",
    python_requires=">=3.7",
    packages=["venvipy", "venvipy.platforms", "venvipy.styles"],
    include_package_data=True,
    package_data={
        "venvipy": ["icons/*.png", "icons/*.ico"],
    },
    version=version,
    license="GPLv3+",
    description="A GUI for managing Python virtual environments.",
    long_description=long_desc,
    long_description_content_type="text/x-rst",
    author="Youssef Serestou",
    author_email="sinusphi.sq@gmail.com",
    url="https://github.com/sinusphi/venvipy",
    download_url=f"https://github.com/sinusphi/venvipy/archive/v{version}.tar.gz",
    keywords=[
        "python",
        "python3",
        "venv",
        "virtualenvironment",
        "virtual-environment",
        "pyqt",
        "pyqt6",
        "pyqt6-desktop-application",
        "gui"
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "venvipy=venvipy.venvi:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Other Audience",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython"
    ]
)
