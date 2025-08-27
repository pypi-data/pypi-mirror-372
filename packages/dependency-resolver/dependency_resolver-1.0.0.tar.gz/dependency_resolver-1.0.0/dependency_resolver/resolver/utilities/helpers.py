import logging
from typing import Any, Optional
from sys import exit


def assertSet(logger:logging.Logger, message:str, variable:Any) :
    """
    Exits the program is the given variable is None.
    This is used to ensure that required variables are set before continuing.

    Args:
        logger (logging.Logger): uses the caller's modules' logger in a attempt to make any resulting logs more contextually relevant
        message (str): The message to log if the variable is not set.
        variable (Any): The variable to check. If it is None, the program will exit with an error message.
    """
    if not isSet(logger, message, variable) :
        exit(1)


def isSet(logger:logging.Logger, message:str, variable:Any):
    """
    Checks if the given variable is set (not None or False). If it is not set, logs an error message.

    Args:
        logger (logging.Logger): uses the caller's modules' logger in a attempt to make any resulting logs more contextually relevant
        message (str): The message to log if the variable is not set.
        variable (Any): The variable to check. If it is None or False, the function will log an error message and return False.

    Returns:
        bool: True if the variable is set (not None or False), otherwise False.
    """
    if variable :
        return True
    else :
        logger.error(message)
        return False


def isEmpty(variable:Optional[str]) -> bool :
    """
    Tests a string to see if it is empty (None, or contain no characters).

    Args:
        variable (Optional[str]): The string to test.

    Returns:
        bool: True if the string is empty (None or contains no characters), otherwise False.
    """
    return variable is None or len(variable) == 0


def hasValue(variable:Optional[str]) -> bool :
    """
    Tests a string to see if it holds a value (not None or empty string).

    Args:
        variable (Optional[str]): The string to test.

    Returns:
        bool: True if the string is not None and contains characters, otherwise False.
    """
    return not isEmpty(variable)


def addIfNotNone(strings:list[str], string:Optional[str]) :
    """
    Adds a string to a list of strings if it is not None or empty.

    Args:
        strings (list[str]): The list to which the string will be added.
        string (Optional[str]): The string to add. If it is None or empty, it will not be added.
    """
    if string :
        strings.append(string)


def getKey(config:dict, key) -> Any :
    """
    Returns the value associated with the given key in the configuration dictionary.

    Args:
        config (dict): The configuration dictionary to search.
        key (_type_): The key to look for in the configuration dictionary.

    Returns:
        Any: The value associated with the key if it exists, otherwise None.
    """
    if key not in config :
        return None
    else :
        return config[key]


def isValidUrl(url:str) -> bool:
    """
    Simply tests a string to see if it is a valid URL (starts with http).

    Args:
        url (str): The string to test.

    Returns:
        bool: True if the string is a valid URL, otherwise False.
    """
    return hasValue(url) and url.startswith("http")
