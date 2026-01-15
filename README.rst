.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/cover_slim.png
   :alt: VenviPy cover

VenviPy
=======

**A GUI for managing multiple Python virtual environments**

.. image:: https://img.shields.io/pypi/v/venvipy?logo=pypi&logoColor=gold
    :target: https://pypi.org/project/venvipy/

.. image:: https://img.shields.io/badge/python-3.7%2B-blue?logo=python&logoColor=gold
    :target: https://www.python.org/downloads/

.. image:: https://img.shields.io/badge/pyqt-5.15.9-darkgreen?logo=qt&logoColor=green
    :target: https://pypi.org/project/PyQt5/5.15.9/

.. image:: https://pepy.tech/badge/venvipy
    :target: https://pepy.tech/project/venvipy

.. image:: https://img.shields.io/badge/platform-linux-orange?logo=linux&logoColor=FFE873
    :target: https://www.linux.org/pages/download/

.. image:: https://img.shields.io/badge/code%20style-black-000000
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/license-GPL%203.0-darkviolet
    :target: https://github.com/sinusphi/venvipy/blob/main/LICENSE

.. image:: https://img.shields.io/badge/donations-paypal-darkblue?logo=paypal&logoColor=darkblue
    :target: https://paypal.me/yserestou

|

Introduction
------------

*VenviPy* is a desktop GUI to create, manage, and maintain many Python virtual
environments from one place. It focuses on a fast workflow:

* create environments via a wizard (Python version, name, location, packages)
* keep an overview table of all environments in a directory
* install / update / inspect packages with context-menu actions

VenviPy was originally built for \*NIX systems. Windows support exists via a
platform abstraction layer, but should be considered experimental unless stated otherwise.

|

Screenshots
-----------

**Main menu**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-1.png
   :alt: Main menu screenshot

|

**Wizard**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-2.png
   :alt: Wizard screenshot

|

**Pip output**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-3.png
   :alt: Pip output screenshot

|

Key Features
------------

Environment management
~~~~~~~~~~~~~~~~~~~~~~

* Create virtual environments with a selectable Python version (3.3+)
* Clone an environment from a requirements file
* Generate requirements from an existing environment
* Add a description to an environment

Package management
~~~~~~~~~~~~~~~~~~

* Install and update Pip and Wheel with one click
* Search and install packages from `PyPI <https://pypi.org/>`__
* Install from requirements files
* Install from local project directories
* Install from a VCS URL *(currently git only)*
* Install from local or remote source archives

Inspection & tooling
~~~~~~~~~~~~~~~~~~~~

* List detailed information about installed packages
* Show dependency tree *(via* `pipdeptree <https://pypi.org/project/pipdeptree/>`__ *)*
* Open a project's PyPI page in your browser

|

Prerequisites
-------------

* Python **3.7+** (PyQt5 5.15.9 requires Python >= 3.7)
* A working ``venv`` module for the Python versions you want to use

Linux (Debian/Ubuntu)
~~~~~~~~~~~~~~~~~~~~~

Install the basics:

.. code-block:: bash

    sudo apt update
    sudo apt install python3-pip python3-venv

If you want to create venvs for a specific Python version, install its ``-venv`` package as well
(example for Python 3.10):

.. code-block:: bash

    sudo apt install python3.10-venv

Windows
~~~~~~~

Install Python from python.org and make sure it is on ``PATH``. No additional system packages are required.

|

Installation
------------

Installing into the system Python is discouraged. Use a dedicated venv (recommended) or ``pipx``.

Recommended: install into a venv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m venv .venv

    # on Linux/macOS:
    source .venv/bin/activate

    # on Windows (PowerShell):
    # .venv\\Scripts\\Activate.ps1

    pip install -U pip
    pip install venvipy

Development version (GitHub):

.. code-block:: bash

    pip install -U pip
    pip install git+https://github.com/sinusphi/venvipy.git

Alternative: install with pipx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pipx install venvipy

|

Usage
-----

After installation you get the entry point:

.. code-block:: bash

    venvipy

For command line options run:

.. code-block:: bash

    venvipy --help

|

Running from source
-------------------

Clone and install dependencies:

.. code-block:: bash

    git clone --depth 50 https://github.com/sinusphi/venvipy.git
    cd venvipy
    python -m venv .venv

    # on Linux/macOS:
    source .venv/bin/activate

    # on Windows (PowerShell):
    # .venv\\Scripts\\Activate.ps1

    pip install -U pip
    pip install -r requirements.txt

If you prefer a minimal manual install:

.. code-block:: bash

    pip install requests beautifulsoup4 PyQt5==5.15.9

Run:

.. code-block:: bash

    python venvipy/venvi.py

|

Contributing
------------

Contributions are welcome:

* `Pull requests <https://github.com/sinusphi/venvipy/pulls>`__
* `Bug reports <https://github.com/sinusphi/venvipy/issues>`__
* `Feature requests <https://github.com/sinusphi/venvipy/issues>`__
