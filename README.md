# _VenviPy_

### A GUI for managing multiple Python virtual environments

<a href="https://python.org"><img alt="Python version: 3.3+" src="https://img.shields.io/badge/python-3.3+-blue"></a>
<a href="https://pypi.org/project/PyQt5"><img alt="PyQt: 5.11+" src="https://img.shields.io/badge/pyqt-5.13+-blue.svg"></a>
<a href="https://www.linux.org/pages/download"><img alt="Platform: Linux" src="https://img.shields.io/badge/platform-linux-darkblue.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/sinusphi/venvipy/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-darkviolet.svg"></a>

---

### **Introduction**

_VenviPy_ is a user friendly graphical interface for creating customized virtual environments or modifing any existing Python environment (that supports venv) quick and easy. 

It provides useful features like a wizard, that guides the user through the creation process, a table that shows an overview over installed environments in a specific directory and a collection of context menu actions like listing detailed information about an environment and much more. 

### **Features**

- Create virtual environments from any Python version (3.3+) which is properly build or installed on your system
- Install and update Pip with one click
- Clone an environment from a requirements file
- Modify any environment by adding or removing packages
- Search and install packages from [PyPI (Python Package Index)](https://pypi.org/)
- Generate requirements from any existing environment
- List detailed information about installed packages


### **Prerequisits**

>Currently _VenviPy_ is designed to work on Linux OS only (maybe a Windows port could come somtime in the future)

If you want to run _VenviPy_ using your operating system's Python (3.3+) make sure the packages `python3-venv` and `python3-pip` are installed, because in this case the operating system's venv and pip will be used to perform the commands.


### Installation

You can download a [ready-to-use-standalone](https://github.com/sinusphi/venvipy/blob/master/venvipy.tar.xz) from the repository. Just unpack the archive, open the unpacked folder and run the `VenviPy` executable.

Or open a terminal, navigate to your download location and run:
```
$ tar -xvf venvipy.tar.xz
```
Then cd into the unpacked `VenviPy` folder and run:
```
./VenviPy
```


### Running from source

If running _VenviPy_ from source the recommended way is to use a virtual environment. First clone or download the source repository. Then open a terminal and run:
```
$ python3.x -m venv [your_env_name]
```
Change to the created directory and run:
```
$ source bin/activate
```
The easiest to install the required packages is to use the [requirements.txt](https://github.com/sinusphi/venvipy/blob/master/requirements.txt) from the repository. Navigate to the downloaded repo and run:
```
$ (your_env_name) pip install --requirement requirements.txt
```
Or install the [PyQt5](https://pypi.org/project/PyQt5) package by running the following command:
```
$ (your_env_name) pip install PyQt5 PyQt5-sip
```
Finally inside the repo cd into the `venvipy/` folder and run:
```
$ (your_env_name) python venvi.py
```


### Known issues

It might be possible that when launching _VenviPy_ the first time on a machine you would have to choose the interpreter (the one that created the environment in which you're running _VenviPy_ ) manually to be able to use it. 

For this in the main menu click on the `Add Interpreter` button in the upper right corner. Then select the correct python binary file (e.g. "/usr/local/bin/python3.x") and you'll be able to use the added interpreter.


### **Contributing**

Contributions are welcomed, as well as [Pull requests](https://github.com/sinusphi/venvipy/pulls), [bug reports](https://github.com/sinusphi/venvipy/issues), and [feature requests](https://github.com/sinusphi/venvipy/issues).
