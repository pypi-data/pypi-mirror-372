import logging
from sys import executable
from typing import Any
from . import run_util

_logger:logging.Logger = logging.getLogger(__name__)

def installPackages(packages:list[str]) :
    """
    Installs a list of Python packages using pip.

    Args:
        packages (list[str]): A list of package names to install.
    """
    for package in packages :
        try:
            if len(packages) > 0:
                parameters:list[Any] = [executable, "-m", "pip", "install", package]
                run_util.runExternalArgs(parameters, False)
                print(f"Installed package: {package}")
                _logger.info(f"Installed package: {package}")

        except Exception as e:
            print(f"Failed to install package {package}")
            _logger.error(f"Failed to install package {package} :", e)
