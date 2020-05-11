import codecs
import ast
import sys
import re
from pathlib import Path
from setuptools import setup, find_packages

assert sys.version_info >= (3, 7, 0), "VenviPy requires Python 3.7+"


CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta

try:
    fh = codecs.open(CURRENT_DIR / "README.rst", encoding="utf-8")
    long_desc = fh.read()
    fh.close()
except FileNotFoundError:
    long_desc = ""


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open(CURRENT_DIR / "venvipy/get_data.py", "rb") as f:
    version = str(ast.literal_eval(
        _version_re.search(
            f.read().decode("utf-8")).group(1)
        )
    )

install_requires = [
    "PyQt5==5.14.0",
    "PyQt5-sip",
]

setup(
    name="venvipy",
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
    version=version,
    license="MIT",
    description="A GUI for managing Python virtual environments.",
    long_description=long_desc,
    author="Youssef Serestou",
    author_email="youssef.serestou.83@gmail.com",
    url="https://github.com/sinusphi/venvipy",
    download_url="https://github.com/sinusphi/venvipy/archive/v0.2.6.tar.gz",
    keywords=[
        "python",
        "python3",
        "venv",
        "virtualenvironment",
        "pyqt",
        "pyqt5",
        "pyqt5-desktop-application",
        "gui",
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "venvipy=venvipy.venvi:main",
            "venvipy-wizard=venvipy.wizard:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
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
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
