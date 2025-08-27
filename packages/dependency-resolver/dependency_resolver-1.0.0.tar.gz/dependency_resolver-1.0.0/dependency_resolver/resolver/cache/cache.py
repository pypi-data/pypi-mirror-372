import logging
from ..utilities import file_util, helpers
from ..dependencies.dependency import Dependency
from ..errors.errors import FetchError, ResolveError

_logger:logging.Logger = logging.getLogger(__name__)


class Cache() :
    # When we download something in the cache we have to give it a file name.
    #  This may the the target name of the dependency, but if not specified then we use this default.
    #  This is a possible clash, but it needs to be something deterministic for a dependency.
    defaultDownloadName:str = "downloadedSource"


    def __init__(self, cacheRoot:str, cacheName:str) :
        """
        Construct the cache.
            Parameters:
                cacheRoot - the home/root directory of the cache. All downloaded sources will be added somewhere in this directory.
                cacheName - the name of the cache. This is used to separate different caches from each other. If not specified, defaults to "default".
        """
        self.init(cacheRoot=cacheRoot, cacheName=cacheName)


    def clean(self) :
        """Empty the cache."""
        if file_util.exists(self._getCachePath()) :
            _logger.info(f"Cleaning cache: {self._getCachePath()}")
            file_util.deleteContents(self._getCachePath())


    def init(self, cacheRoot:str, cacheName:str) :
        """
        Initializes the cache.
        Must be called before it is used.

        Parameters:
            cacheRoot - Set the root of the cache.
            cacheName - Can give this cache a specific name. All sources will be downloaded under this name, separating the from the rest of the cache.
        """
        helpers.assertSet(_logger, "init:cacheRoot not set", cacheRoot)
        helpers.assertSet(_logger, "init:cacheName not set", cacheName)

        self._setCacheRoot(cacheRoot)
        self._setCacheName(cacheName)
        self._setCachePath(cacheRoot=cacheRoot, cacheName=cacheName)

        # make sure the cache directory exists
        file_util.mkdir(self._getCachePath(), mode=0o755)


    def fetchDependency(self, dependency:Dependency, alwaysFetch:bool = False) :
        """
        Fetches a dependency's source into the cache.

        Parameters:
            dependency - the dependency to fetch.
            alwaysFetch - will always fetch the dependency's source, even if it is already in the cache.
        """
        _logger.debug(f"Downloading dependency {dependency.getName()}...")

        if dependency.alwaysUpdate() or (alwaysFetch or not self._isCached(dependency)) :
            targetDir:str = self._generateCacheLocation(dependency)
            if targetDir and not file_util.exists(targetDir) :
                _logger.debug(f"Trying to create cache location: {targetDir}")
                file_util.mkdir(targetDir, mode=0o755)

            targetName:str = self._generateCachedFileName(dependency)
            if targetDir and file_util.isDir(targetDir) :
                cacheDownloadPath:str = self._generateCacheDownloadPath(dependency)
                if file_util.exists(cacheDownloadPath) :
                    file_util.delete(cacheDownloadPath)

                dependency.fetchSource(targetDir, targetName)
                _logger.debug(f"...successfully cached dependency {dependency.getName()}: source {dependency.getSource().getName()}::{dependency.getSourcePath()} -> {targetDir}/{targetName}.")
            else :
                _logger.debug(f"...failed to cache dependency {dependency.getName()} - the cache already has a file (not a directory) at the target download location in the cache ({targetDir}): source {dependency.getSource().getName()}::{dependency.getSourcePath()} -> {targetDir}/{targetName}.")
                raise FetchError(f"Failed to cache dependency {dependency.getName()} - the cache already has a file (not a directory) at the target download location in the cache ({targetDir}).")
        else :
            _logger.debug(f"...dependency {dependency.getName()} already in cache.")


    def resolveDependency(self, dependency:Dependency, targetHomeDir:str, onlyMissing:bool = False) :
        """
        Resolves a dependency by performing its Resolve action from the fetched source in the cache into the target location.

        Parameters:
            dependency - the dependency to resolve.
            targetHome - Each dependency is relative the configuration that defines it. This is the path to that directory.
            onlyMissing - only resolve missing dependencies. Non filesystem copies (for example unzipping) resolve actions are always completed.
        """
        _logger.debug(f"Resolving dependency {dependency.getName()}...")
        if self._isCached(dependency) :
            dependency.resolve(self._generateCacheDownloadPath(dependency), targetHomeDir)
            _logger.debug(f"...successfully resolved dependency {dependency.getName()}.")
        else :
            _logger.debug(f"...dependency {dependency.getName()} not in cache.")
            raise ResolveError(f"Failed to resolve dependency {dependency.getName()} - the source has not been fetched to the cache.")


    def _generateCacheLocation(self, dependency:Dependency) -> str :
        """
        Generates the path to the directory (inside the cache) that the source of the dependency is fetched to.

        Args:
            dependency (Dependency): the dependency to generate the cache location for.

        Returns:
            str: the path to the cache directory for the dependency's source.
        """
        # cache location is based on the source name and the source path
        return file_util.buildPath(self._getCachePath(), dependency.getSource().getName(), dependency.getSourcePath())


    def _generateCachedFileName(self, dependency:Dependency) -> str :
        """
        Generates the name of the file that the dependency's source will be downloaded to in the cache.
        This is usually the target name of the dependency, but if not specified then it will use the end of the source path or a default name.

        Args:
            dependency (Dependency): the dependency to generate the cached file name for.

        Returns:
            str: the name of the file in the cache that the dependency's source will be downloaded to.
        """
        cacheName:str = dependency.getTargetName()
        if not cacheName and dependency.getSourcePath() :  # use the end of the source path if specified.
            cacheName = file_util.returnLastPartOfPath(dependency.getSourcePath())
        if not cacheName :  # just use a default name
            cacheName = self.defaultDownloadName
        return cacheName


    def _generateCacheDownloadPath(self, dependency:Dependency) -> str :
        """
        Generates the full path to the file in the cache where the dependency's source is downloaded to.

        Args:
            dependency (Dependency): the dependency to generate the cache download path for.

        Returns:
            str: the full path to the file in the cache where the dependency's source is downloaded to.
        """
        return file_util.buildPath(self._generateCacheLocation(dependency), self._generateCachedFileName(dependency))


    def _setCacheRoot(self, cacheRoot:str) :
        """
        Sets the root of the cache. This is where all the cache files will be stored.

        Args:
            cacheRoot (str): the root directory for the cache. If not specified, defaults to the user's home directory.
        """
        helpers.assertSet(_logger, "_setCacheRoot:cacheRoot not set", cacheRoot)

        if not file_util.exists(cacheRoot) or (file_util.exists(cacheRoot) and file_util.isDir(cacheRoot)) :
            self._cacheRoot:str = cacheRoot
        else :
            _logger.error(f"Unable to create cache with a root of {cacheRoot} - a file already exists at this location (at least its not a directory - could be a permission thing also).")
            exit(1)


    def _getCacheRoot(self) -> str :
        """
        Returns the root path of the cache.

        Returns:
            str: the root path of the cache.
        """
        return self._cacheRoot


    def _setCacheName(self, cacheName:str) :
        """
        Sets the name of the cache. This is used to separate different caches from each other.

        Args:
            cacheName (str): the name of the cache. If not specified, defaults to "default".
        """
        self._cacheName:str = cacheName


    def _getCacheName(self) -> str :
        """
        Returns the name of the cache.

        Returns:
            str: the name of the cache.
        """
        return self._cacheName


    def _setCachePath(self, cacheRoot:str, cacheName:str) :
        """
        Sets the path for the cache. This is where all the cache files will be stored.

        Args:
            cacheRoot (str): the root directory for the cache.
            cacheName (str): the name of the cache. This is used to separate different caches from each other.
        """
        helpers.assertSet(_logger, "_setCachePath:cacheRoot not set", cacheRoot)
        helpers.assertSet(_logger, "_setCachePath:cacheName not set", cacheName)

        self._cachePath:str = file_util.buildPath(cacheRoot, cacheName)
        _logger.debug(f"Caching to {self._getCachePath()}")


    def _getCachePath(self) -> str :
        """
        Returns the path for this cache. This is where all the cache files will be stored.

        Returns:
            str: the path for this cache.
        """
        return self._cachePath


    def _isCached(self, dependency:Dependency) -> bool :
        """
        Checks if the dependency's source is already cached.

        Args:
            dependency (Dependency): the dependency to check.

        Returns:
            bool: True if the dependency's source is already cached, False otherwise.
        """
        return file_util.exists(self._generateCacheDownloadPath(dependency))
