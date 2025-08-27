import logging
import logging.handlers
import sys
import os.path


_logger:logging.Logger = logging.getLogger(__name__)


def setupRootLogging(logToFile:str):
    """
    Sets up the root logger to log to both stdout and a file.
    This function creates a directory for the log file if it does not exist,
    and configures the logger to write debug-level messages to the file and info-level messages to stdout.

    Args:
        logToFile (str): The path to the log file where debug messages will be written.
    """
    root = logging.getLogger(None)
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s.%(funcName)s(%(lineno)d) >> %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    print(f"Setting up root logging to {logToFile}")
    os.makedirs(os.path.dirname(logToFile), 0o755, True)  # make sure the parent directory exists

    file_handler = logging.handlers.RotatingFileHandler(logToFile, "a", 10 * 1024 * 1024, 3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _logger.debug("Logging set up")
