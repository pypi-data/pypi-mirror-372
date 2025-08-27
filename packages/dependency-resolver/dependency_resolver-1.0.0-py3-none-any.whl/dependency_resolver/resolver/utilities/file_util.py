import logging
import shutil
import os
import glob
from pathlib import Path
from typing import Optional
from . import helpers, time_util, errors_util

_logger:logging.Logger = logging.getLogger(__name__)


def mkdir(dir:str, parents:bool = True, exist_ok:bool = True, mode:int = 511, user:Optional[str] = None, group:Optional[str] = None) :
    """
    Create a directory (and parent structure if required) if it doesn't already exist.

    Args:
        dir (str): The directory to create.
        parents (bool, optional): If True, will create parent directories as needed. Defaults to True.
        exist_ok (bool, optional): If True, will not raise an error if the directory already exists. Defaults to True.
        mode (int, optional): The mode to set for the directory (default is 0o777, which is 511 in decimal). Defaults to 511.
        user (Optional[str], optional): The user to set as the owner of the directory. Defaults to None.
        group (Optional[str], optional): The group to set as the owner of the directory. Defaults to None.
    """
    if helpers.hasValue(dir) :
        Path(dir).mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

        if user is not None and group is not None :
            chown(dir, user, group)
    else :
        _logger.warning("Directory not specified - cannot create it.")


def exists(path:str) -> bool :
    """
    Check if the specified path exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return helpers.hasValue(path) and Path(path).exists()


def isDir(path:str) -> bool :
    """
    Check if the specified path exists and is a directory.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists and is a directory, False otherwise.
    """
    return helpers.hasValue(path) and os.path.isdir(path)


def isFile(path:str) -> bool :
    """
    Check if the specified path exists and is a file.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists and is a file, False otherwise.
    """
    return helpers.hasValue(path) and os.path.isfile(path)


def ensurePathExists(path:str) -> bool :
    """
    Ensure the target path exists. Exits if the path doesn't exist.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists.

    Side Effects:
        Exits the program if the path does not exist.
    """
    if helpers.isEmpty(path) or not exists(path) :
        _logger.error(f"{path} does not exist. Exiting.")
        exit(1)
    return True


def buildPath(*paths:str) -> str:
    """
    Build up a path by joining provided parts. Separators are applied as appropriate.
    Ignores any 'None' paths.

    Args:
        *paths (str): A variable number of string arguments representing parts of the path to be built.

    Returns:
        str: The constructed path as a string. If no valid paths are provided, an empty string is returned.
    """
    result:str = ""
    for path in paths :
        if helpers.hasValue(path) :
            if result :
                # Remove leading separator from path, as a leading separator causes the thing you are joining to (result in this case) to be discarded.
                result = os.path.join(result, path.lstrip(os.path.sep))
            else :
                result = f"{path}"

    return result


def returnLastPartOfPath(fullpath:str) -> str :
    """
    Return the last part of the path, including any separators.

    Args:
        fullpath (str): The full path.

    Returns:
        str: The last part of the path.
    """
    return os.path.basename(os.path.normpath(fullpath))


def getParentDirectory(fullPath:str) -> str :
    """
    Get the parent directory of the given path.

    Args:
        fullPath (str): The full path.

    Returns:
        str: The parent directory.
    """
    return os.path.dirname(fullPath)


def getUserDirectory() -> str :
    """
    Get the user's home directory.

    Returns:
        str: The user's home directory.
    """
    return str(Path.home().absolute().resolve())


def copy(source:str, dest:str, sourceDirectoryContentsOnly:Optional[bool] = False) -> bool :
    """
    Copy files or directories.

    Args:
        source (str): The source file or directory.
        dest (str): The destination path.
        sourceDirectoryContentsOnly (bool, optional): If True, only copy the contents of a source directory (has no effect if source is a file). Defaults to False.

    Returns:
        bool: The path to the newly copied file / destination directory. Empty String indicates an error.
    """
    try :
        if Path(source).exists() :
            if Path(source).is_dir() :
                if sourceDirectoryContentsOnly :
                    return copyContents(source, dest)
                else :
                    _logger.debug(f"Copying directory from {source} -> {dest}")
                    return helpers.hasValue(shutil.copytree(source, dest, dirs_exist_ok=True))
            else :
                _logger.debug("Copying " + source + " -> " + dest)
                return helpers.hasValue(shutil.copy2(source, dest))
        else :
            _logger.error(f"Can't copy - {source} does not exist")
            return False
    except Exception :
        _logger.error(f"Failed to copy {source} -> {dest}", exc_info=True)
        return False


def copyContents(dir:str, dest:str) -> bool:
    """
    Copy the contents of a directory to a destination.

    Args:
        dir (str): The source directory.
        dest (str): The destination directory.

    Returns:
        bool: The destination directory, if successful.
    """
    if os.path.exists(dest) and os.path.isdir(dest) :
        if os.path.exists(dir) and os.path.isdir(dir) :
            _logger.error("Copying contents of %s -> %s", dir, dest)
            for name in os.listdir(dir):
                copy(os.path.join(dir, name), dest, False)  # copy files and complete directories
            return True
        else :
            _logger.error("Cannot copy contents of %s as it does not exist", dir)
            return False
    else :
        _logger.error("Cannot copy contents of %s to %s as the destination doesn't exist or is not a directory.", dir, dest)
        return False


def chown(path:str, user:str, group:str) :
    """
    Change the ownership of a file or directory (but not the contents of the directory).

    Args:
        path (str): A path.
        user (str): The user group (name, or uid).
        group (str): The group (name or group id).
    """
    _logger.debug("chown %s:%s %s", user, group, path)
    shutil.chown(path, user, group)


def chown_recursive(path:str, user:str, group:str) :
    """
    Change the ownership of a directory and its contents.

    Args:
        path (str): A path, or Path-like object.
        user (str): The user group (name, or uid).
        group (str): The group (name or group id).
    """
    _logger.debug("chown -R %s:%s %s...", user, group, path)

    # Change ownership for the top-level folder
    chown(path, user, group)

    for root, dirs, files in os.walk(path):
        # chown all sub-directories
        for dir in dirs:
            chown(os.path.join(root, dir), user, group)

        # chown all files
        for file in files:
            chown(os.path.join(root, file), user, group)

    _logger.debug("...chown %s completed", path)


def chmod(path:str, permissions:int) :
    """
    Change the permissions of a file or directory (but not the contents of the directory).

    Args:
        path (str): A path, or Path-like object.
        permissions (int): An octal string (e.g. 0o750).
    """
    _logger.debug("chmod %s %s", permissions, path)
    os.chmod(path, permissions)


def chmod_recursive(path:str, permissions:int) :
    """
    Change the permissions of a directory and its contents.

    Args:
        path (str): A path, or Path-like object.
        permissions (int): An octal string (e.g. 0o750).
    """
    _logger.debug("chmod -R %s %s...", permissions, path)

    # Change permissions for the top-level folder
    chmod(path, permissions)

    for root, dirs, files in os.walk(path):
        # chmod all sub-directories
        for dir in dirs:
            chmod(os.path.join(root, dir), permissions)

        # chmod all files
        for file in files:
            chmod(os.path.join(root, file), permissions)

    _logger.debug("...chmod %s completed", path)


def delete(path:str) :
    """
    Delete the given target path. If the path points to a symbolic link then it is unlinked.

    Args:
        path (str): The path to delete.
    """
    toDelete:Path = Path(path)
    if toDelete.exists() :
        if toDelete.is_dir() and not toDelete.is_symlink() :
            _logger.debug("rm -r %s", toDelete.absolute())
            deleteContents(str(toDelete.absolute()))
            toDelete.rmdir()
        else :
            _logger.debug("rm %s", toDelete.absolute())
            toDelete.unlink()
    else :
        _logger.debug("Not deleting non-existent path %s", toDelete.absolute())


def deleteContents(dir:str) :
    """
    Delete the contents of a directory (not the directory itself).

    Args:
        dir (str): The directory whose contents will be deleted.
    """
    toDelete:Path = Path(dir)
    if toDelete.exists() :
        for name in os.listdir(dir):
            delete(os.path.join(dir, name))


def emptyFileContents(filePath:str) :
    """
    Empty the contents of a file.

    Args:
        filePath (str): The path to the file to empty.
    """
    if helpers.isEmpty(filePath) :
        _logger.error("Cannot empty contents of 'None' filePath")
    path = Path(filePath)
    if path.exists() and path.is_file() :
        path.open("w").close()


def createFile(filePath:str, mode:int = 438) :
    """
    Create an empty file at the specified path.

    Args:
        filePath (str): The path to the file to create.
        mode (int, optional): The mode to set for the file. Defaults to 438 (0o666).
    """
    Path(filePath).touch(mode=mode, exist_ok=True)


def findNewestFileInDirectory(dir:str, filePattern:str = "*") -> Optional[str]:
    """
    Return the path of the latest file in the specified directory or None if directory doesn't exist or is empty.

    Args:
        dir (str): The target directory.
        filePattern (str, optional): A pathname pattern, for example '*.txt'. Defaults to '*'.

    Returns:
        str: The path to the newest file, or None if not found.
    """
    newestFile:Optional[str] = None
    if exists(dir) :
        list_of_files = glob.iglob(os.path.join(dir, filePattern))
        newestFile = max(list_of_files, default=None, key=os.path.getmtime)
    return newestFile


def howOldIsFile(path:str) -> Optional[time_util.timedelta] :
    """
    Get the age of the given file.

    Args:
        path (str): The path to the file.

    Returns:
        time.timedelta: The age of the file, or None if the file does not exist.
    """
    age:Optional[time_util.timedelta] = None
    if path is not None and exists(path) :
        age = time_util.howOld(os.path.getmtime(path))
    else :
        _logger.warning(f"Path: {path} does not exist, cannot determine age.")

    return age


def removeFiles(dir:str, delta:time_util.timedelta, recursive:bool = False) :
    """
    Delete files (not directories) from a given directory that are older than the specified delta.

    Args:
        dir (str): The directory to inspect.
        delta (time.timedelta): The maximum age of the file.
        recursive (bool, optional): If True, will find files in subdirectories. Defaults to False.
    """
    if exists(dir) :
        contents = glob.iglob(os.path.join(dir, "*"), recursive=recursive)
        for item in contents :
            age:Optional[time_util.timedelta] = howOldIsFile(item)
            if os.path.isfile(item) and age is not None and age > delta :
                delete(item)


def readFile(path:str, encoding:str = "utf-8") -> str :
    """
    Read the contents of a file. Should only be used for small files as it reads the entire contents.

    Args:
        path (str): The path to the file.
        encoding (str, optional): The encoding to use. Defaults to "utf-8".

    Returns:
        str: The contents of the file, or "" if the file does not exist.

    Raises:
        FileError: If the file cannot be read.
    """
    contents:str = ""
    try :
        with open(path, encoding=encoding) as file:
            contents = file.read()
        return contents
    except Exception as e :
        raise FileError(f"Failed to read file {path}: {e}")


def readListFromFile(path: str, encoding:str = "utf-8") -> list[str]:
    """
    Read a file containing patterns (one per line), ignoring comments and blank lines.

    Args:
        path (str): Path to the file containing patterns.

    Returns:
        list[str]: List of patterns (stripped, non-empty, non-comment lines).

    Raises:
        FileError: If the file cannot be read.
    """
    listFromFile: list[str] = []

    try :
        with open(path, 'r', encoding=encoding) as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                listFromFile.append(line)
        return listFromFile
    except Exception as e :
        raise FileError(f"Failed to read list from file {path}: {e}")


def removeFilesOfTypes(dir:str, types:list[str]) :
    """
    Remove files of the given types from the given directory.

    Args:
        dir (str): The directory to inspect.
        types (list[str]): The types of files to remove.

    Raises:
        errors_util.FileError: If a file cannot be deleted.
    """
    _logger.debug(f"Removing files of types {types} from {dir}")

    if exists(dir) :
        for pattern in types:
            search_pattern = os.path.join(dir, '**', pattern)
            for path in glob.iglob(search_pattern, recursive=True):
                try :
                    _logger.debug(f"Removing {path}")
                    delete(path)
                    _logger.debug(f"Removed {path}")
                except Exception as e :
                    raise FileError(f"Failed to remove file {path}: {e}")

    _logger.debug(f"Removed files of types {types} from {dir}")


class FileError(errors_util.UtilityError) :
    """Raised by the file utility functions to indicate some issue."""
