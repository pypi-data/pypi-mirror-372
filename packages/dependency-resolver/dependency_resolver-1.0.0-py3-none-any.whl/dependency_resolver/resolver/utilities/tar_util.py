import logging
import tarfile
from tarfile import TarFile
from . import file_util
from .errors_util import UtilityError


_logger:logging.Logger = logging.getLogger(__name__)


def untar(tarPath:str, targetDir:str) :
    """
    Untar (extracts all from) the specified zip file to the specified directory.

    Parameters:
        tarPath - the path to the zip file to extract.
        targetDir - the directory to zip into.

    Raises:
        TarError if an error is encountered.
    """
    _logger.debug(f"Untarring {tarPath} -> {targetDir}")
    _validateTarPath(tarPath)
    _validateTargetDirectory(targetDir)
    file_util.mkdir(targetDir, mode=0o744)  # make target directory in case it doesn't exist.
    try :
        with _createTarFile(tarPath) as tar :
            tar.extractall(targetDir)
    except Exception as exc :
        _logger.error(f"Unable to extract tar file at {tarPath}", exc_info=True)
        raise TarError(f"Unable to extract tar file at {tarPath}") from exc


def isValidTarPath(tarPath:str) -> bool :
    """
    Returns true if the file at the specified path is a tar file.

    Args:
        tarPath (str): The path to the tar file to check.

    Returns:
        bool: True if the path is a valid tar file, False otherwise.
    """
    try :
        _validateTarPath(tarPath)
        return True
    except TarError :
        return False


def _validateTarPath(tarPath:str) :
    """
    Validates the specified tar file path.

    Args:
        tarPath (str): the path to the tar file to validate.

    Raises:
        TarError: if the path is not specified, does not exist, or is not a valid tar file.
    """
    if tarPath :
        if file_util.exists(tarPath) :
            if not tarfile.is_tarfile(tarPath) :
                _logger.error(f"{tarPath} is not a tar file.")
                raise TarError(f"{tarPath} is not a tar file.")
        else :
            _logger.error(f"Specified tar file {tarPath} does not exist.")
            raise TarError(f"Specified tar file {tarPath} does not exist.")
    else :
        _logger.error("Path to the tar file has not been specified.")
        raise TarError("Path to the tar file has not been specified.")


# Checks to see it the target directory is valid
def _validateTargetDirectory(targetDir:str) :
    """
    Validates the specified target directory.

    Args:
        targetDir (str): the target directory to validate.

    Raises:
        TarError: if the target directory is not specified or is not a directory.
    """
    if targetDir :
        if file_util.exists(targetDir) and not file_util.isDir(targetDir) :
            _logger.error(f"The target directory {targetDir} is actually a file (at least its not a directory).")
            raise TarError(f"The target directory {targetDir} already exists but is a file.")
    else :
        _logger.error("The target directory has not been specified.")
        raise TarError("The target directory has not been specified.")


def _createTarFile(path:str, mode:str = 'r') -> TarFile :
    return tarfile.open(path, mode=mode)  # type: ignore - mode as a string is valid for tarfile.open


class TarError(UtilityError) :
    """Raised by the zip utility functions to indicate some issue."""
