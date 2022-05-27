.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/cover_slim.png

**A GUI for managing multiple Python virtual environments**

.. image:: https://img.shields.io/badge/pypi-v0.3.5-blue?logo=pypi&logoColor=FFE873
    :target: https://pypi.org/project/venvipy/0.3.5/#description

.. image:: https://img.shields.io/badge/python-3.6+-blue?logo=python&logoColor=FFE873
    :target: https://www.python.org/downloads

.. image:: https://img.shields.io/badge/pyqt-5.15.4-darkgreen
    :target: https://pypi.org/project/PyQt5

.. image:: https://pepy.tech/badge/venvipy
    :target: https://pepy.tech/project/venvipy

.. image:: https://img.shields.io/badge/platform-linux-darkblue?logo=linux&logoColor=FFE873
    :target: https://www.linux.org/pages/download

.. image:: https://img.shields.io/badge/code%20style-black-000000
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/license-GPL%203.0-darkviolet
    :target: https://github.com/sinusphi/venvipy/blob/main/LICENSE

..
    .. image:: https://img.shields.io/travis/sinusphi/venvipy/main?label=Travis%20CI&logo=travis
        :target: https://travis-ci.org/sinusphi/venvipy

|

Introduction
------------

*VenviPy* is a graphical user interface for creating or modifing customized
virtual environments quick and easy. It was developed for \*NIX systems and
has been tested on various distributions.

*VenviPy* provides a set of features like a wizard, that guides the user through
the creation process, a table that shows an overview of installed
environments in a specific directory and a collection of context menu
actions like listing detailed information about an environment and much
more.

|

**The main menu:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-1.png

|

**The wizard:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-2.png

|

**Output when running pip commands:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/main/img/screen-3.png

|

Key Features
------------

*  Create virtual environments with any Python version (3.3+)
*  Clone an environment from a requirements file
*  Generate requirements from an existing environment
*  Add a description to an environment

|

*  Install and update Pip and Wheel with one click
*  Search and install packages from `PyPI <https://pypi.org/>`__
*  Install from requirements files
*  Install from local stored project directories
*  Install from a VCS project url *(currently git only)*
*  Install from local or remote source archives

|

*  List detailed information about installed packages
*  Show dependency tree (using
   `pipdeptree <https://pypi.org/project/pipdeptree/#description>`__ package)
*  Open a project's `PyPI <https://pypi.org/>`__ website in your browser

|

Prerequisits
------------

If you don't have a Python built from source, you'll have to run *VenviPy* 
using your operating system's Python (3.6+). In this case please make sure 
that the following packages are installed on your system: 

.. code-block:: bash

    python3-pip
    python3-venv
    python3.9-venv
    python3.10-venv

|

Installation
------------

Installing packages directly into your operating system's Python is
discouraged. If you want to do it anyway, do it like this:

.. code-block:: bash

    $ python3.x -m pip install venvipy

The better way however is to create a virtual environment and install
*VenviPy* into it:

.. code-block:: bash

    $ python3.x -m venv [your_venv]
    $ source [your_venv]/bin/activate

To install the latest stable version of *VenviPy*:

.. code-block:: bash

    $ (your_venv) pip install venvipy

for the developement version:

.. code-block:: bash

    $ (your_venv) pip install git+https://github.com/sinusphi/venvipy.git

Now you can launch 

- the main menu via:

  - .. code-block:: bash

        $ (your_venv) venvipy

- or run the wizard standalone to quickly create and set up an environment:

  - .. code-block:: bash

        $ (your_venv) venvipy-wizard

|

Running from source
-------------------

Clone the repository (use the ``--depth`` option):

.. code-block:: bash

    $ (your_venv) git clone --depth 50 git@github.com:sinusphi/venvipy.git

Cd into the repo folder and install the dependencies. On Python 3.6 you will also
need to install the ``dataclasses`` package if you're not using the provided 
`requirements.txt <https://github.com/sinusphi/venvipy/blob/main/requirements.txt>`__:

.. code-block:: bash

    $ (your_venv) pip install -r requirements.txt

or: 

.. code-block:: bash

    $ (your_venv) pip install PyQt5==5.15.4 PyQt5-Qt5==5.15.2 PyQt5-sip==12.10.1 requests beautifoulsoup4

Then you can

- launch the main menu:

  - .. code-block:: bash
  
        $ (your_venv) python venvipy/venvi.py

- or run the wizard standalone to quickly create and set up an environment:

  - .. code-block:: bash

        $ (your_venv) python venvipy/wizard.py

|

Contributing
------------

Contributions are welcomed, as well as `Pull
requests <https://github.com/sinusphi/venvipy/pulls>`__, `bug
reports <https://github.com/sinusphi/venvipy/issues>`__, and `feature
requests <https://github.com/sinusphi/venvipy/issues>`__.
