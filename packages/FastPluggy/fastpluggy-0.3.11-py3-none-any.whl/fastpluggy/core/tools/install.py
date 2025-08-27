import logging
import os
import importlib.util
import sys


def install_requirements(requirements_file: str, force: bool = False) -> bool:
    import subprocess

    if not os.path.exists(requirements_file):
        logging.warning(f"No requirements file found: '{requirements_file}'")
        return False

    cmd = [sys.executable,"-m", "pip", "install", "-r", requirements_file]
    if force:
        cmd.insert(4, "--force-reinstall")

    logging.info(f"Installing dependencies from '{requirements_file}'...")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        logging.info(line.strip())

    return_code = process.wait()
    if return_code != 0:
        logging.error(f"pip install failed with exit code {return_code}")
        raise subprocess.CalledProcessError(return_code, cmd)

    logging.info(f"Dependencies from '{requirements_file}' installed successfully!")
    return True


def is_installed(pkg_name: str) -> bool:
    data= importlib.util.find_spec(pkg_name) is not None
    logging.info(f"is_installed : {data} for {pkg_name}")
    return data

