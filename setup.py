import codecs
import ast
import re
from setuptools import setup


try:
    fh = codecs.open("README.rst", encoding="utf-8")
    long_desc = fh.read()
    fh.close()
except FileNotFoundError:
    long_desc = ""


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("venvipy/get_data.py", "rb") as f:
    version = str(ast.literal_eval(
        _version_re.search(
            f.read().decode("utf-8")).group(1)
        )
    )

install_requires = [
    "PyQt5",
    "PyQt5-sip",
]

setup(
    name="venvipy",
    packages=["venvipy"],
    version=version,
    license="MIT",
    description="A GUI for managing Python virtual environments.",
    long_description=long_desc,
    author="Youssef Serestou",
    author_email="youssef.serestou.83@gmail.com",
    url="https://github.com/sinusphi/venvipy",
    download_url="https://github.com/sinusphi/venvipy/archive/v0.1.4.tar.gz",
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
            "venvipy=venvi:main"
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
