import logging
from pathlib import Path
import zipfile
from zipfile import ZipFile
from . import file_util
from .errors_util import UtilityError


_logger:logging.Logger = logging.getLogger(__name__)


def zip(sourceDir:str, zipDir:str, zipName:str) -> str :
    """
    Zips the specified directory to the specified target directory.

    Args:
        sourceDir (str): The directory to zip.
        zipDir (str): The directory to place the zip file in.
        zipName (str): The name of the zip file.

    Returns:
        str: The path to the zip file.

    Raises:
        ZipError: If an error is encountered.
    """
    _logger.debug(f"Zipping {sourceDir} -> {zipDir}/{zipName}")

    # Validate the source and target directories
    _validateSourceDirectory(sourceDir)
    _validateTargetDirectory(zipDir)

    # Create the path to the zip file
    zip_path:str = f"{zipDir}/{zipName}"

    # delete the zip file if it already exists
    file_util.delete(zip_path)

    # Convert to Path object
    dir:Path = Path(sourceDir)

    # Zip the directory
    try :
        with _createZipFileForWrite(zip_path) as zip_file:
            for entry in dir.rglob("*"):
                zip_file.write(entry, entry.relative_to(dir))
    except Exception as exc :
        _logger.error(f"Unable to zip {sourceDir} -> {zip_path}", exc_info=True)
        raise ZipError(f"Unable to zip {sourceDir} -> {zip_path}") from exc

    _logger.debug(f"Zipped {sourceDir} -> {zip_path}")

    # Return the path to the zip file
    return zip_path


def unzip(zipPath:str, targetDir:str) :
    """
    Unzip (extracts all from) the specified zip file to the specified directory.

    Parameters:
        zipPath - the path to the zip file to extract.
        targetDir - the directory to zip into.

    Raises:
        ZipError if an error is encountered.
    """
    _logger.debug(f"Unzipping {zipPath} -> {targetDir}")

    # Validate the zip file and target directory
    _validateZipPath(zipPath)
    _validateTargetDirectory(targetDir)

    # Make the target directory in case it doesn't exist.
    file_util.mkdir(targetDir, mode=0o744)  # make target directory in case it doesn't exist.
    try :
        with _createZipFileForRead(zipPath) as zip :
            zip.extractall(targetDir)
    except Exception as exc :
        _logger.error(f"Unable to extract zip file at {zipPath}", exc_info=True)
        raise ZipError(f"Unable to extract zip file at {zipPath}") from exc

    _logger.debug(f"Unzipped {zipPath} -> {targetDir}")


def isValidZipPath(zipPath:str) -> bool :
    """
    Returns true if the file at the specified path is a zip file.

    Args:
        zipPath (str): The path to the zip file to check.

    Returns:
        bool: True if the path is a valid zip file, False otherwise.
    """
    try :
        _validateZipPath(zipPath)
        return True
    except ZipError :
        return False


def _validateZipPath(zipPath:str) :
    """
    Validates the specified zip file path.

    Args:
        zipPath (str): the path to the zip file to validate.

    Raises:
        ZipError: if the path is not specified, does not exist, or is not a valid zip file.
    """
    if zipPath :
        if file_util.exists(zipPath) :
            if not zipfile.is_zipfile(zipPath) :
                _logger.error(f"{zipPath} is not a zip file.")
                raise ZipError(f"{zipPath} is not a zip file.")
        else :
            _logger.error(f"Specified zip file {zipPath} does not exist.")
            raise ZipError(f"Specified zip file {zipPath} does not exist.")
    else :
        _logger.error("Path to the zip file has not been specified.")
        raise ZipError("Path to the zip file has not been specified.")


def _validateTargetDirectory(targetDir:str) :
    """
    Validates the specified target directory.

    Args:
        targetDir (str): the target directory to validate.

    Raises:
        ZipError: if the target directory is not specified or is not a directory.
    """
    if targetDir :
        if file_util.exists(targetDir) and not file_util.isDir(targetDir) :
            _logger.error(f"The target directory {targetDir} is actually a file (at least its not a directory).")
            raise ZipError(f"The target directory {targetDir} already exists but is a file.")
    else :
        _logger.error("The target directory has not been specified.")
        raise ZipError("The target directory has not been specified.")


def _validateSourceDirectory(sourceDir:str) :
    """
    Validates the specified source directory.

    Args:
        sourceDir (str): the source directory to validate.

    Raises:
        ZipError: if the source directory is not specified or does not exist, or is not a directory.
    """
    if sourceDir :
        if file_util.exists(sourceDir) :
            if not file_util.isDir(sourceDir) :
                _logger.error(f"The source directory {sourceDir} is actually a file (at least its not a directory).")
                raise ZipError(f"The source directory {sourceDir} is not a file.")
        else :
            _logger.error(f"The source directory {sourceDir} does not exist.")
            raise ZipError(f"The source directory {sourceDir} does not exist.")
    else :
        _logger.error("The source directory has not been specified.")
        raise ZipError("The source directory has not been specified.")


def _createZipFileForRead(path:str) -> ZipFile :
    return ZipFile(path, "r")


def _createZipFileForWrite(path:str) -> ZipFile :
    return ZipFile(path, "w", zipfile.ZIP_DEFLATED)


class ZipError(UtilityError) :
    """Raised by the zip utility functions to indicate some issue."""
