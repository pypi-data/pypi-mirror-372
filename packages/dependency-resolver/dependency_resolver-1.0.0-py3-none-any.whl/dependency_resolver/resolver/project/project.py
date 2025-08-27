import logging
from typing import Optional
from .creator import Creator
from ..utilities import helpers, file_util
from ..errors.errors import FetchError, ResolveError
from ..configuration.configuration import Configuration
from ..configuration.attributes import ConfigAttributes
from ..sources.sources import Sources
from ..dependencies.dependencies import Dependencies
from ..dependencies.dependency import Dependency
from ..cache.cache import Cache

_logger:logging.Logger = logging.getLogger(__name__)


class Project :
    def __init__(self, configuration: Configuration) :
        """
        Construct the Project.
        This will parse the given configuration.

        Parameters:
            configuration - the configuration to use for this project.
            cache - used as a place to store fetched sources.
        """
        helpers.assertSet(_logger, "Configuration is not set", configuration)
        if configuration.numberOfErrors() > 0 :
            print("There are syntax errors in the configuration. To view them run the validate_config command.")
            exit(1)
        self._config:Configuration = configuration
        self._creator:Creator = Creator(self._getConfiguration())
        self._parseConfig()


    def getProjectName(self) -> str :
        """Returns the name of this project."""
        return self._projectName


    def setCache(self, cache:Cache) :
        """
        Sets the cache for this project.
        The cache must be set before any dependencies are fetched or resolved.
        """
        self._cache:Cache = cache


    def printDependencyTarget(self, name:str) :
        """
        Prints the full target path of the named dependency.
        Cannot be used to infer whether the dependency has been fetched yet.

        Parameters:
            name - the name of the dependency to find.
        """
        dependency:Optional[Dependency] = self._getDependencies().getDependency(name)
        if dependency is not None :
            print(file_util.buildPath(self._determineTargetRoot(dependency), dependency.getTargetPath()))


    def _determineTargetRoot(self, dependency:Dependency) -> str :
        """
        Returns the root target of the dependency.
        This is either relative to the configuration file or may have been overridden in the configuration itself, on a dependency-by-dependency basis.
        """
        return self._getTargetRoot() if dependency.isTargetRelativeToRoot() else self._getConfiguration().getConfigurationHome()


    def fetchDependencies(self, alwaysFetch:bool = False) :
        """
        Fetch the sources of all the dependencies.
        
        Parameters:
            alwaysFetch - Fetch the dependency source even if they are already in the cache.
        """
        helpers.assertSet(_logger, "fetchDependencies:::Cache has not been configured - use setCache to set the cache for this project", self._getCache())

        _logger.debug(f"Fetching all dependencies (force download = {alwaysFetch})")

        # A map of dependencies already downloaded this fetch
        alreadyDownloaded:list[str] = []

        print(f"Fetching {len(self._getDependencies().getDependencies())} dependencies:")
        count:int = 0
        for dependency in self._getDependencies().getDependencies() :
            count += 1
            if not self._hasBeenDownloaded(alreadyDownloaded, dependency) :
                print(f"{count}-{dependency.getName()} : Fetching...")
                try :
                    self._fetchDependency(dependency, alwaysFetch)
                    self._addDownloaded(alreadyDownloaded, dependency)
                    print(f"{count}-{dependency.getName()} : Fetched.")
                except FetchError as error:
                    print(f"{count}-{dependency.getName()} : Failed :: {error}.")
            else :
                print(f"{count}-{dependency.getName()} : Already fetched.")

        _logger.debug("...fetched dependencies.")


    def _fetchDependency(self, dependency:Dependency, alwaysFetch:bool = False) :
        """
        Fetch the source of specified dependency.

        Parameters:
            alwaysFetch - Fetch the dependency source even if it is already in the cache.

        Raises:
            FetchError if an error is encountered during the fetch
        """
        _logger.debug(f"Fetching dependency {dependency.getName()} (force download = {alwaysFetch})")
        self._getCache().fetchDependency(dependency, alwaysFetch)
        _logger.debug(f"...fetched dependency {dependency.getName()}.")


    def resolveFetchedDependencies(self, onlyMissing:bool = False) :
        """
        Resolve the dependencies by moving their fetched source to the target location.

        Parameters:
            onlyMissing - Only resolve those sources that are missing at the target location. Note actions that are not file copies (e.g. unzipping) are always resolved.
        """
        helpers.assertSet(_logger, "resolveFetchedDependencies:::Cache has not been configured - use setCache to set the cache for this project", self._getCache())

        _logger.debug(f"Resolving all dependencies (only missing = {onlyMissing})")

        print(f"Resolving {len(self._getDependencies().getDependencies())} dependencies:")
        count:int = 0
        for dependency in self._getDependencies().getDependencies() :
            count += 1
            print(f"{count}-{dependency.getName()} : Resolving...")
            try :
                self._resolveDependency(dependency, onlyMissing)
                print(f"{count}-{dependency.getName()} : Resolved.")
            except ResolveError as error:
                print(f"{count}-{dependency.getName()} : Failed :: {error}.")

        _logger.debug("...resolved dependencies.")


    def _resolveDependency(self, dependency:Dependency, onlyMissing:bool = False) :
        """
        Fetch the source of specified dependency.

        Parameters:
            onlyMissing - Only resolve those sources that are missing at the target location. Note actions that are not file copies (e.g. unzipping) are always resolved.

        Raises:
            ResolveError if an error is encountered during the resolve action
        """
        _logger.debug(f"Resolving dependency {dependency.getName()} (only missing = {onlyMissing})")
        self._getCache().resolveDependency(dependency, self._determineTargetRoot(dependency), onlyMissing)
        _logger.debug(f"...resolved dependency {dependency.getName()}.")


    def resolveDependencies(self, alwaysFetch:bool = False, onlyMissing:bool = False) :
        """
        Resolve all dependencies. Fetch any sources prior to resolving them.

        Parameters:
            onlyMissing - Only resolve those sources that are missing at the target location. Note actions that are not file copies (e.g. unzipping) are always resolved.
        """
        helpers.assertSet(_logger, "resolveDependencies:::Cache has not been configured - use setCache to set the cache for this project", self._getCache())

        _logger.debug(f"Fetching and resolving dependencies (force download = {alwaysFetch})")
        self.fetchDependencies(alwaysFetch)
        self.resolveFetchedDependencies(onlyMissing)
        _logger.debug("...fetched and resolved dependencies.")


    def clean(self) :
        """
        Cleans the cache and logs for this project.
        This will delete the cache and log files.
        """
        _logger.debug(f"Cleaning project {self.getProjectName()}")
        self._getCache().clean()
        _logger.debug(f"...cleaned project {self.getProjectName()}")


    def _parseConfig(self) :
        """Uses the Creator to parse all the dependencies."""
        config:dict = self._getConfiguration().getConfiguration()
        self._parseProjectName(config)
        self._parseTargetRoot(config)
        self._sources:Sources = self._creator.createSources()
        self._dependencies:Dependencies = self._creator.createDependencies(self._getSources())


    def _parseProjectName(self, config:dict) :
        """Parses the name of this project from the configuration."""
        self._projectName:str = helpers.getKey(config, ConfigAttributes.PROJECT_NAME)
        helpers.assertSet(_logger, "Configuration must specify a Project name (attribute: project)", self.getProjectName())


    def _parseTargetRoot(self, config:dict) :
        """Parses the target root for this project from the configuration."""
        self._targetRoot:str = helpers.getKey(config, ConfigAttributes.TARGET_ROOT)


    def _getConfiguration(self) -> Configuration :
        """Returns the Configuration."""
        return self._config


    def _getTargetRoot(self) -> str :
        """Returns the target root. If not set then the configuration home is returned."""
        return self._targetRoot if self._targetRoot is not None else self._getConfiguration().getConfigurationHome()


    def _getSources(self) -> Sources :
        """Return all the Sources for this project."""
        return self._sources


    def _getDependencies(self) -> Dependencies :
        """Return all the dependencies for this project."""
        return self._dependencies


    def _getCache(self) :
        """Returns the cache."""
        helpers.assertSet(_logger, "_getCache:::Cache has not been configured - use setCache to set the cache for this project", self._cache)
        return self._cache


    def _addDownloaded(self, alreadyDownloaded:list[str], dependency:Dependency) :
        """Remember we have already downloaded this source target."""
        alreadyDownloaded.append(dependency.getAbsoluteSourcePath())


    def _hasBeenDownloaded(self, alreadyDownloaded:list[str], dependency:Dependency) :
        """Checks to we if we have already downloaded this source target."""
        return dependency.getAbsoluteSourcePath() in alreadyDownloaded
