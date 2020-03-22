# -*- coding: utf-8 -*-
"""
This module ...
"""
from subprocess import Popen, PIPE



#]===========================================================================[#
#] CREATE A VIRTUAL ENVIRONMENT [#===========================================[#
#]===========================================================================[#

def create_venv(py_vers, env_dir, with_pip=False,
                system_site_packages=False, symlinks=False):
    """
    Create a virtual environment in a directory.
    """
    pip = "" if with_pip else " --without-pip"
    ssp = " --system-site-packages" if system_site_packages else ""
    sym = " --symlinks" if symlinks else ""

    script = f"{py_vers} -m venv {env_dir}{pip}{ssp}{sym};"

    res = Popen(
            ["bash", "-c", script],
            stdout=PIPE,
            text="utf-8"
        )

    out, _ = res.communicate()
    output = out.strip()

    return output


#]===========================================================================[#
#] GENERATE A REQUIREMENTS [#================================================[#
#]===========================================================================[#

def create_requirements(venv_dir, venv_name):
    """
    Generate a requirements.txt file and save in the root directory
    of the virtual environment.
    """
    script = (
        f"source {venv_dir}/{venv_name}/bin/activate;" \
        f"pip freeze > {venv_dir}/{venv_name}/requirements.txt;" \
        "deactivate;"
    )

    res = Popen(
            ["bash", "-c", script],
            stdout=PIPE,
            text="utf-8"
        )

    out, _ = res.communicate()
    output = out.strip()

    return output



if __name__ == "__main__":

    python_version = "/usr/local/bin/python3.8"
    env_directory = "/mnt/SQ-Core/coding/.virtualenvs/DEV/"
    with_pip_opt = None
    with_sys_site_pkgs = None
    with_symlinks = None

    create_venv(python_version, env_directory)
