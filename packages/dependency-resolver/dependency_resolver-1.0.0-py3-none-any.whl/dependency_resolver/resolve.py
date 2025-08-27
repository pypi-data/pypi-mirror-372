#!/usr/bin/env python3

import argparse
import logging
import traceback

from typing import Optional

from . import constants
from .resolver.utilities import file_util, helpers, log_util
from .resolver.configuration.configuration import Configuration
from .resolver.project.project import Project
from .resolver.cache.cache import Cache

_logger:logging.Logger = logging.getLogger(__name__)


# Sets up the whole shebang
def _init() :
    log_util.setupRootLogging(constants.LOG_TO_FILE)


# Deals with all the command-line interface
def _commandRunner() :
    parser = argparse.ArgumentParser(description="Fetch and resolve external dependencies for a project.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()
    _printConfig(subparsers)
    _validateConfig(subparsers)
    _printDependencyTargetPath(subparsers)
    _updateSourceCache(subparsers)
    _resolveFromCacheDependencies(subparsers)
    _resolveDependencies(subparsers)
    args:argparse.Namespace = parser.parse_args()
    args.func(args)


# Print the configuration at the specified path.
def _printConfig(subparsers) :
    runner = subparsers.add_parser("print_config", help="Print the target JSON configuration.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.set_defaults(func=_printCommand)


def _printCommand(args:argparse.Namespace) :
    _createConfiguration(args).printConfiguration()


# Validate (check for missing required attributes) the configuration at the specified path.
def _validateConfig(subparsers) :
    runner = subparsers.add_parser("validate_config", help="Validate (find any missing required attributes) in the target JSON configuration.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.set_defaults(func=_validateCommand)


def _validateCommand(args:argparse.Namespace) :
    _createConfiguration(args).validateConfiguration()


# Print the configuration at the specified path.
def _printDependencyTargetPath(subparsers) :
    runner = subparsers.add_parser("print_dependency_target", help="Prints the target full path for a given dependency name. Do not infer that the dependency has been fetched.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--name", "-n", help='The name of the dependency', required=True)
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', default=constants.CACHE_DIR, required=False)
    runner.set_defaults(func=_printDependencyTargetPathCommand)


def _printDependencyTargetPathCommand(args:argparse.Namespace) :
    _createProject(args).printDependencyTarget(name=args.name)


# Update every dependencies source in the cache.
def _updateSourceCache(subparsers) :
    runner = subparsers.add_parser("update_cache", help="Download sources and cache them.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--clean", action="store_true", help='Clean the cache and logs before downloading Sources. Essentially rebuilds the cache for the given configuration.')
    runner.add_argument("--force", action="store_true", help='Force the update of any source for this project.')
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', default=constants.CACHE_DIR, required=False)
    runner.set_defaults(func=_updateSourceCacheCommand)


def _updateSourceCacheCommand(args:argparse.Namespace) :
    project:Project = _createProject(args)

    # delete the current log file.
    if args.clean :
        _clean(project=project)

    project.fetchDependencies(alwaysFetch=args.force)


# Update every dependencies source in the cache.
def _resolveFromCacheDependencies(subparsers) :
    runner = subparsers.add_parser("resolve_from_cache", help="Resolve all dependencies. Must have performed an update_cache to fetch the sources first.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', default=constants.CACHE_DIR, required=False)
    runner.set_defaults(func=_resolveFromCacheDependenciesCommand)


def _resolveFromCacheDependenciesCommand(args:argparse.Namespace) :
    _createProject(args).resolveFetchedDependencies()


# Update every dependencies source in the cache.
def _resolveDependencies(subparsers) :
    runner = subparsers.add_parser("resolve", help="Fetch and Resolve all dependencies.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--clean", action="store_true", help='Clean the cache and logs before downloading Sources. Essentially rebuilds the cache for the given configuration.')
    runner.add_argument("--force", action="store_true", help='Always fetch of the source even if already previously fetched.')
    runner.add_argument("--configPath", "-c", help='The path to the configuration file', required=True)
    runner.add_argument("--cacheRoot", "-R", help='The root of the cache to use for the downloads.', default=constants.CACHE_DIR, required=False)
    runner.set_defaults(func=_resolveDependenciesCommand)


def _resolveDependenciesCommand(args:argparse.Namespace) :
    _createProject(args).resolveDependencies(alwaysFetch=args.force)


# Cleans the log and cache
def _clean(project:Optional[Project]) :
    _resetLogFile()
    _logger.debug("Cleaned log file")
    if project is not None :
        project.clean()


# Empties the existing contents of the log file.
#  Helpful when testing.
def _resetLogFile() :
    file_util.emptyFileContents(constants.LOG_TO_FILE)


# Instantiate the Dependencies class from the supplied command-line arguments.
def _createConfiguration(args:argparse.Namespace) -> Configuration :
    if args and helpers.hasValue(args.configPath) :
        return Configuration(configurationPath=args.configPath)

    return Configuration("config.json")  # todo - allow some default.


# Creates and checks the config for errors.
def _loadConfiguration(args:argparse.Namespace) -> Configuration :
    config:Configuration = _createConfiguration(args)
    if config.numberOfErrors() < 0 :
        message:str = "Errors detected in the configuration - please run validate_config command for details."
        print(message)
        _logger.error(message)
        exit(1)

    return config


# Instantiate the Project with the specified configuration.
def _createProject(args:argparse.Namespace) -> Project :
    project:Project = Project(_loadConfiguration(args))
    project.setCache(_createCache(args.cacheRoot, project.getProjectName()))
    return project


# Instantiate the Cache. A cacheName can be used to specify a separate cache to use.
def _createCache(cacheRoot:str, projectName:str) -> Cache :
    helpers.assertSet(_logger, "_createCache::cacheRoot not set", cacheRoot)
    helpers.assertSet(_logger, "_createCache::projectName not set", projectName)
    # initialise the cache with a default name - we don't know what is is until the configuration is loaded.
    return Cache(cacheRoot=cacheRoot, cacheName=projectName)


def main() -> None:
    """
    The main entry point for the dependency resolver.
    """
    try:
        _init()
        _commandRunner()
    except Exception:
        _logger.error(f"Command caught the exception (may not be harmful): {traceback.format_exc()}")
        raise


# the entry point
if __name__ == "__main__" :
    main()
