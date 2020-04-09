# _VenviPy_

### A GUI for managing multiple Python virtual environments

<a href="https://python.org"><img alt="Python version: 3.3+" src="https://img.shields.io/badge/python-3.3+-blue"></a>
<a href="https://pypi.org/project/PyQt5"><img alt="PyQt: 5.11+" src="https://img.shields.io/badge/pyqt-5.13+-blue.svg"></a>
<a href="https://www.linux.org/pages/download"><img alt="Platform: Linux" src="https://img.shields.io/badge/platform-linux-darkblue.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/sinusphi/venvipy/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-darkviolet.svg"></a>

---

### **Introduction**

Basically _VenviPy_ is a user friendly graphical interface for creating customized virtual environments or modifing any existiing Python environment (that supports `venv`) quick and easy. 

It provides a number of useful features like a wizard, that guides the user through the creation process, an overview over all installed environments in a directory and a collection of context menu actions like listing detailed information about an environment and much more. 

These are the main features:
- Create virtual environments from any Python version (3.3+) which is properly build or installed on your system
- Clone the set of pre-installed packages from a requirements file
- Install and update Pip with one click
- Search and install packages from [PyPI (Python Package Index)](https://pypi.org/)
- Generate a requirements file from any existing virtual environment
- List detailed information about an environment


### **Prerequisits**

>Currently _VenviPy_ is designed to work on Linux OS only (maybe a port to `'win32'` could come somtime in the future)

**Optional** : If you want to use your operating system's Python (3.3+) to create or modify evironments from within _VenviPy_ you'll need the `python3-pip` package to be installed on your system, because in this case the operating system's Pip will be used to perform commands inside a specific environment. 

But this isn't really necessary, instead simply run _VenviPy_ itself in a virtual einvironment.

### Installation

Create a virtual environment. From a terminal run:
```
$ python3 -m venv [your_env_name]
```
Change to the created directory and run:
```
$ source bin/activate
```
Then install [PyQt5](https://pypi.org/project/PyQt5) by running the following command:
```
$ (your_env_name) pip install PyQt5
```
Then clone or download the source repository and change to `venvipy` directory. Finally run:
```
$ (your_env_name) python venvi.py
```

#### Known issues

It might be possible that when launching _VenviPy_ the first time on a machine you would have to choose the interpreter (which created the environment in which you're running _VenviPy_ in) manually to be able to use it. 

For this just open the main menu and click on the `Add Interpreter` button in the upper right corner. Then select the correct python binary file (e.g. "/usr/local/bin/python3.x") and you'll be able to use the added interpreter to perform all tasks available in _VenviPy_.


### **Contributing**

Contributions are welcomed, as well as [Pull requests](https://github.com/sinusphi/venvipy/pulls), [bug reports](https://github.com/sinusphi/venvipy/issues), and [feature requests](https://github.com/sinusphi/venvipy/issues).

