import logging
import subprocess
from subprocess import CompletedProcess
from typing import Any


_logger:logging.Logger = logging.getLogger(__name__)


def runExternal(command:str, verifySuccess:bool = True) -> str :
    """
    Runs an external command using the shell.

    Args:
        command (str): The command to execute, as a string. paces in the command need /" escaping.
        verifySuccess (bool, optional): If True, checks the return code of the command and raises an exception if it indicates failure. Defaults to True.

    Returns:
        str: The standard output of the command.

    Raises:
        subprocess.CalledProcessError: If the command fails (returns a non-zero exit code) and verifySuccess is True.
    """
    _logger.debug(f"Executing command: {command}")
    result:CompletedProcess = subprocess.run(command, shell=True, capture_output=True, text=True)

    if _logger.isEnabledFor(logging.DEBUG) :
        if result.stdout is not None and len(result.stdout) > 0 :
            _logger.debug(f"stdout: {result.stdout}")
        if result.stderr is not None and len(result.stderr) > 0 :
            _logger.debug(f"stderr: {result.stderr}")

    if verifySuccess :
        result.check_returncode()  # checks the return code and exits if failure indicated.

    return result.stdout


def runExternalArgs(parameters:list[Any], verifySuccess:bool = True) -> str :
    """
    Runs an external command with the given parameters.

    Args:
        parameters (list[Any]): A list of command-line arguments to pass to the command.
        verifySuccess (bool, optional): If True, checks the return code of the command and raises an exception if it indicates failure. Defaults to True.

    Returns:
        str: The standard output of the command.

    Raises:
        subprocess.CalledProcessError: If the command fails (returns a non-zero exit code) and verifySuccess is True.
    """
    result:CompletedProcess = subprocess.run(parameters, capture_output=True, text=True)

    if _logger.isEnabledFor(logging.DEBUG) :
        if result.stdout is not None and len(result.stdout) > 0 :
            _logger.debug(f"stdout: {result.stdout}")
        if result.stderr is not None and len(result.stderr) > 0 :
            _logger.debug(f"stderr: {result.stderr}")

    if verifySuccess :
        result.check_returncode()  # checks the return code and exits if failure indicated.

    return result.stdout
