import sys
import codecs
import ast
import re
from pathlib import Path
from setuptools import setup, find_packages


CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta

try:
    with codecs.open(CURRENT_DIR / "README.rst", encoding="utf-8") as f:
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
    "PyQt5==5.15.4",
    "PyQt5-Qt5==5.15.2",
    "PyQt5-sip==12.10.1",
    "requests",
    "beautifulsoup4",
    "dataclasses ; python_version<'3.7'"
]

setup(
    name="venvipy",
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    version=version,
    license="GPLv3+",
    description="A GUI for managing Python virtual environments.",
    long_description=long_desc,
    long_description_content_type="text/x-rst",
    author="Youssef Serestou",
    author_email="sinusphi.sq@gmail.com",
    url="https://github.com/sinusphi/venvipy",
    download_url="https://github.com/sinusphi/venvipy/archive/v0.3.6.tar.gz",
    keywords=[
        "python",
        "python3",
        "venv",
        "virtualenvironment",
        "virtual-environment",
        "pyqt",
        "pyqt5",
        "pyqt5-desktop-application",
        "gui"
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "venvipy=venvipy.venvi:main",
            "venvipy-wizard=venvipy.wizard:main"
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
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython"
    ]
)
