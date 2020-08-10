.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/master/img/cover_slim.png

**A GUI for managing multiple Python virtual environments**

.. image:: https://img.shields.io/badge/pypi-v0.2.18-blue?logo=pypi&logoColor=FFE873
    :target: https://pypi.org/project/venvipy/0.2.18/#description

.. image:: https://img.shields.io/badge/python-3.6+-blue?logo=python&logoColor=FFE873
    :target: https://www.python.org/downloads

.. image:: https://img.shields.io/badge/pyqt-5.14.0-darkgreen
    :target: https://pypi.org/project/PyQt5

.. image:: https://pepy.tech/badge/venvipy
    :target: https://pepy.tech/project/venvipy

.. image:: https://img.shields.io/badge/platform-linux-darkblue?logo=linux&logoColor=FFE873
    :target: https://www.linux.org/pages/download

.. image:: https://img.shields.io/badge/code%20style-black-000000
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/license-GPL%203.0-darkviolet
    :target: https://github.com/sinusphi/venvipy/blob/master/LICENSE

.. image:: https://img.shields.io/travis/sinusphi/venvipy/master?label=Travis%20CI&logo=travis
    :target: https://travis-ci.org/sinusphi/venvipy


Introduction
------------

*VenviPy* is a simple graphical user interface for creating customized
virtual environments or modifing any existing Python environment (that
supports the built-in ``venv`` module) quick and easy.

It provides a set of features like a wizard, that guides the user through
the creation process, a table that shows an overview over installed
environments in a specific directory and a collection of context menu
actions like listing detailed information about an environment and much
more.

**The main menu:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/master/img/screen-1.png

**The wizard:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/master/img/screen-2.png

**Output when running pip commands:**

.. image:: https://raw.githubusercontent.com/sinusphi/venvipy/master/img/screen-3.png


Key Features
------------

*  Create virtual environments from any Python version (3.3+) which is
   properly build or installed on your system
*  Install and update Pip with one click
*  Clone an environment from a requirements file
*  Search and install packages from `PyPI <https://pypi.org/>`__
*  Generate requirements from an existing environment
*  List detailed information about installed packages
*  Show dependency tree (using
   `pipdeptree <https://pypi.org/project/pipdeptree/#description>`__ package)
*  Open a project's `PyPI <https://pypi.org/>`__ website in your browser
*  Install packages from local projects and from repository urls 
   *(currently git only)*
*  Modify any environment by adding or removing packages *(comming
   soon)*


Prerequisits
------------

Primarily *VenviPy* is aimed at \*NIX systems (maybe a Windows port could
come sometime in the future)

If you want to run *VenviPy* using your operating system's Python (3.6+)
you will have to make sure that the two packages ``python3-venv`` and
``python3-pip`` are installed, because in this case the operating system's
venv and pip will be used to perform the commands.


Installation
------------

You can install the latest version of *VenviPy* via:

.. code-block:: bash

    $ pip install venvipy

or:

.. code-block:: bash

    $ pip install git+https://github.com/sinusphi/venvipy.git

Now you can launch 

- the main menu via:

  - .. code-block:: bash

        $ venvipy

- or if you just want to quickly create a virtual environment 
  run the wizard standalone:

  - .. code-block:: bash

        $ venvipy-wizard


Running from source
-------------------

Clone the repository (use the ``--depth`` option):

.. code-block:: bash

    $ git clone --depth 1 git@github.com:sinusphi/venvipy.git


If running *VenviPy* from source the recommended way is to use a virtual
environment. 

.. code-block:: bash

    $ python3.x -m venv [your_venv]
    $ source [your_venv]/bin/activate


Cd into the repo folder and install the dependencies from 
`requirements.txt <https://github.com/sinusphi/venvipy/blob/master/requirements.txt>`__:

.. code-block:: bash

    $ (your_venv) pip install -r requirements.txt

or run:

.. code-block:: bash

    $ (your_venv) pip install PyQt5==5.14.0 PyQt5-sip

Then you can

- launch the main menu:

  - .. code-block:: bash
  
        $ (your_venv) python venvipy/venvi.py

- or run the standalone wizard to create and set up an environment:

  - .. code-block:: bash

        $ (your_venv) python venvipy/wizard.py


Known issues
------------

Sometimes it happens that when starting the creation process the wizard page 
freezes. Restarting *VenviPy* fixes this. 


Contributing
------------

Contributions are welcomed, as well as `Pull
requests <https://github.com/sinusphi/venvipy/pulls>`__, `bug
reports <https://github.com/sinusphi/venvipy/issues>`__, and `feature
requests <https://github.com/sinusphi/venvipy/issues>`__.
