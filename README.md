# _VenviPy_

### A GUI for managing multiple Python virtual environments

<a href="https://python.org"><img alt="Python version: 3.3-3.7" src="https://img.shields.io/badge/python-3.3%20--%203.9-blue"></a>
<a href="https://pypi.org/project/PyQt5"><img alt="PyQt: 5.13" src="https://img.shields.io/badge/pyqt-v5.13-blue.svg"></a>
<a href="https://www.linux.org/pages/download"><img alt="Platform: Linux" src="https://img.shields.io/badge/platform-linux-darkblue.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/sinusphi/venvipy/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-darkviolet.svg"></a>

---

### **Introduction**

_VenviPy_ is a user friendly graphical user interface for creating virtual environments very quick and easy. 

It has a wizard that provides a lot of features like selecting a specific Python version, customizing the build process, downloading and installing packages from the [Python Package Index (PyPI)](https://pypi.org/), generating requirements.txt files and more. Other features are currently in development. 


### Prerequisits

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

At the moment _VenviPy_ is not yet available from [PyPI](https://pypi.org/) and can only be obtained by cloning or downloading the source repository. 


### **Usage**

After cloned or downloaded the source repository open a terminal and cd into the directory:
```
$ cd venvipy/
```

Then run the _VenviPy_ main module:
```
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

