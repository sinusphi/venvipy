# -*- coding: utf-8 -*-
"""Collect and serve data."""
from subprocess import Popen, PIPE
from dataclasses import dataclass
import xmlrpc.client
import shlex
import os



#]===========================================================================[#
#] FIND PYTHON 3 INSTALLATIONS [#============================================[#
#]===========================================================================[#

@dataclass
class PythonInfo:
    version: str
    path: str


def get_python_installs():
    """
    Determine if Python 3 installations exist and where they are.
    """
    versions = ['3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3']

    infos = []

    for i, vers in enumerate(versions):
        try:
            # get python versions
            res1 = Popen(
                ["python" + vers, "-V"],
                stdout=PIPE,
                universal_newlines=True
            )
            out1, _ = res1.communicate()
            version = out1.strip()

            # get paths to the python binaries
            res2 = Popen(
                ["which", "python" + vers],
                stdout=PIPE,
                universal_newlines=True
            )
            out2, _ = res2.communicate()
            path = out2.strip()

            info = PythonInfo(version, path)
            infos.append(info)

        except FileNotFoundError as err:
            #print(f"[INFO]: {err.args[1]}")
            pass  # no need to show which Python versions were not found

    return infos


#]===========================================================================[#
#] GET VENVS FROM DEFAULT DIRECTORY [#=======================================[#
#]===========================================================================[#

@dataclass
class VenvInfo:
    name: str
    directory: str
    version: str


def get_venvs(path):
    """
    Get the venv directories from default directory.
    """
    if not os.path.isdir(path):
        return []

    infos = []

    for i, _dir in enumerate(os.listdir(path)):

        bin_folder = os.path.join(path, _dir, "bin")
        if not os.path.isdir(bin_folder):
            continue

        python_binary = os.path.join(bin_folder, "python")
        if not os.path.isfile(python_binary):
            continue

        try:
            res = Popen(
                [python_binary, "-V"],
                stdout=PIPE,
                universal_newlines=True
            )
            out, _ = res.communicate()
            version = out.strip()

            info = VenvInfo(_dir, path, version)
            infos.append(info)

        except OSError as err:
            print(f"{err.args[1]}: {python_binary}")

    return infos


def get_venvs_default():
    """
    Get the default venv directory string from file.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_file = os.path.join(current_dir, "def", "default")

    if os.path.isfile(default_file):
        with open(default_file, "r") as f:
            default_dir = f.read()
            return get_venvs(default_dir)

    return []


#]===========================================================================[#
#] GET INFOS FROM PYTHON PACKAGE INDEX [#====================================[#
#]===========================================================================[#

@dataclass
class PackageInfo:
    pkg_name: str
    pkg_vers: str
    pkg_sum: str


def get_package_infos(name):
    """
    Get package name, version and description from https://pypi.org/pypi.
    """
    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    res = client.search({"name": name})

    infos = []

    for i, proj in enumerate(res):
        pkg_name = proj["name"]
        pkg_vers = proj["version"]
        pkg_sum = proj["summary"]

        info = PackageInfo(pkg_name, pkg_vers, pkg_sum)
        infos.append(info)

    return infos


#]===========================================================================[#
#] INSTALL SELECTED PACKAGES [#==============================================[#
#]===========================================================================[#

def has_bash():
    """
    Test if bash is available. If present the string `/bin/bash` is returned,
    an empty string otherwise.
    """
    res = Popen(
        ["which", "bash"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True
    )
    out, _ = res.communicate()
    shell = out.strip()

    return shell


def run_script(command):
    """
    Run the subprocess and catch the realtime output.
    """
    process = Popen(command, stdout=PIPE, text="utf-8")
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc


def run_pip(cmd, opt, target, venv_dir, venv_name):
    """
    Activate the created virtual environment and run pip commands.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    pipup_script = os.path.join(current_dir, "scripts", "update_pip.sh")
    install_script = os.path.join(current_dir, "scripts", "install_pkgs.sh")

    if target == "pip":
        script = os.path.join(current_dir, "scripts", "update_pip.sh")
    else:
        script = os.path.join(current_dir, "scripts", "install_pkgs.sh")

    if has_bash():
        # create install script and make it executable
        with open(script, "w") as f:
            f.write(
                "#!/bin/bash\n"
                f"source {venv_dir}/{venv_name}/bin/activate\n"
                f"pip {cmd}{opt}{target}\n"
                "deactivate\n"
            )
            os.system(f"chmod +x {script}")

        # run the script
        command = ["/bin/bash", script]
        run_script(command)



if __name__ == "__main__":
    '''
    for python in get_python_installs():
        print(python.version, python.path)

    #]=======================================================================[#

    for venv in get_venvs_default():
        print(venv.name, venv.version, venv.directory)

    #]=======================================================================[#

    test_pkg = "test"

    for pkg in get_package_infos(test_pkg):
        print(pkg.pkg_name, pkg.pkg_vers, pkg.pkg_sum)

    if not get_package_infos(test_pkg):
        print("No packages found!")

    #]=======================================================================[#
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_file = os.path.join(current_dir, "def", "default")

    if os.path.isfile(default_file):
        with open(default_file, "r") as f:
            default_dir = f.read()

    cmd = ["install ", "list ", "show "]
    opt = ["--upgrade "]
    PIP = "pip"
    package = "mist"  # returned by 'self.selectionModel.selectedRows().data()'
    venv_dir = default_dir  # returned by 'location'
    venv_name = "asdf"  # returned by 'name'

    run_pip(cmd[0], opt[0], package, venv_dir, venv_name)
