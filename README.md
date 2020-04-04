# _VenviPy_

### A GUI for managing multiple Python virtual environments

<a href="https://python.org"><img alt="Python version: 3.3+" src="https://img.shields.io/badge/python-3.3+-blue"></a>
<a href="https://pypi.org/project/PyQt5"><img alt="PyQt: 5.11+" src="https://img.shields.io/badge/pyqt-5.13+-blue.svg"></a>
<a href="https://www.linux.org/pages/download"><img alt="Platform: Linux" src="https://img.shields.io/badge/platform-linux-darkblue.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/sinusphi/venvipy/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-darkviolet.svg"></a>

---

### **Introduction**

_VenviPy_ is a user friendly graphical interface for creating customized virtual environments quick and easy. It provides a number of useful features like a wizard, that guides the user through the creation process, modify an existing environment in different ways nd much more. 

This is an overwiew:
- Create virtual environments from any Python version (3.3+) which is properly build or installed on your system
- Install and update Pip with one click
- Search, select and install packages from [Python Package Index (PyPI)](https://pypi.org/) or use a requirements.txt
- Generate and/ or modifiy requirements.txt files


### **Prerequisits**

To be able to use _VenviPy_ you'll need the `python3-pip` package to be present on your system. You can install it by using your operating system's package manager (for example `apt` if you're on a debian based distro).

Then install [PyQt5](https://pypi.org/project/PyQt5) by running the following command in a terminal:
```
$ python3 -m pip install PyQt5
```

Or create a virtual environment, activate it and install the `PyQt5` package into it by running the following commands:
```
$ python3 -m venv [your_env_name]
$ source [your_env_name]/bin/activate

$ (your_env_name) pip install PyQt5
```


### **Installation**

At the moment _VenviPy_ is not yet available from [PyPI](https://pypi.org/) and can only be obtained by cloning or downloading the source repository. After cloned or downloaded open a terminal and cd into the directory and run the _VenviPy_ main module:
```
$ cd venvipy/
$ python3 venvi.py
```

**NOTE** :
If you want to run _VenviPy_ inside a virtual environment, don't forget to activate the environment first by running:
```
$ source [your_env_name]/bin/activate
```
and then simply do:
```
$ (your_env_name) python venvi.py
```


### **Contributing**

Contributions are welcomed, as well as [Pull requests](https://github.com/sinusphi/venvipy/pulls), [bug reports](https://github.com/sinusphi/venvipy/issues), and [feature requests](https://github.com/sinusphi/venvipy/issues).

