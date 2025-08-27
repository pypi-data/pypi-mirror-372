#!/usr/bin/env python3

import argparse
import logging
import traceback
import constants
from resolver.utilities import dependencies_util, log_util
from collections.abc import Sequence


_logger:logging.Logger = logging.getLogger(__name__)


# Sets up the whole shebang
def _init() :
    log_util.setupRootLogging(constants.LOG_TO_FILE)


# Deals with all the command-line interface
def _commandRunner() :
    parser = argparse.ArgumentParser(description="Setup the python environment to see for the resolver.")
    subparsers = parser.add_subparsers()
    _installRequiredPackages(subparsers)
    args = parser.parse_args()
    args.func(args)


def _installRequiredPackages(subparsers) :
    """
    Install any required python libraries.
    This is a separate executable to limit its dependencies to avoid the 'I can't run this because I haven't got the right dependencies' situation.
    """
    runner = subparsers.add_parser("install_python_dependencies", help="Install any extra non-default python library dependencies using pip.")
    runner.set_defaults(func=_installRequiredPackagesCommand)


def _installRequiredPackagesCommand(args:Sequence[str]) :
    # StrEnum is available by default in python version >=3.11 onwards.
    requiredPackages:list[str] = ["requests", "StrEnum"]  # todo - could externalize this list at some point (note: there is a requirements.txt now).
    dependencies_util.installPackages(requiredPackages)


# the entry point
try :
    if __name__ == "__main__" :
        _init()
        _commandRunner()
except Exception :
    _logger.error(f"Command caught the exception (may not be harmful): {traceback.format_exc()}")
    raise
