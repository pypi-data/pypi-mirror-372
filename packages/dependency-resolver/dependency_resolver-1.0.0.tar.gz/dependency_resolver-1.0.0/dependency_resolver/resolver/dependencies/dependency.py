import logging
from .resolveAction import ResolveAction
from ..utilities import helpers, file_util
from ..sources.source import Source
from ..configuration.attributes import ConfigAttributes

_logger:logging.Logger = logging.getLogger(__name__)  # module name

# Models each dependency, i.e that thing needs to go here.
# An action may be defined to perform on the source file as part of resolving this dependency, for example unzip the source file.
class Dependency :

    def __init__(self, name:str, targetDir:str, targetName:str, targetRelativeRoot:bool, source:Source, sourcePath:str, resolveAction:ResolveAction, description:str, alwaysUpdate:bool) :
        """
        Parameters:
            targetDir - the path to the target location for the dependency. This path is relative to the project location (the dir containing the dependencies json configuration)
            targetName - The target file name. Can be None to represent a directory target.
            targetRelativeRoot - Should this dependency be put relative to a specified root (opposed to relative to the configuration file)
            source - Defines the base url and protocol of the dependency source. Overwrites the sourceProtocol if specified.
            sourcePath - the path to the source. Can be absolute or relative to the base attribute of the optional source parameter.
            resolveAction - Defines an action carried out when resolving this action.
            description - Can be used to describe the dependency.
            alwaysUpdate - If True, this dependency will always be fetched and resolved.
        """
        helpers.assertSet(_logger, f"The dependency have a {ConfigAttributes.DEPENDENCY_NAME} attribute in dependency: {ConfigAttributes.DEPENDENCY_TARGET_DIR}={targetDir}, {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}={sourcePath}.", source)
        helpers.assertSet(_logger, f"The {ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY} attribute must be specified in dependency: {ConfigAttributes.DEPENDENCY_TARGET_DIR}={targetDir}, {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}={sourcePath}.", source)
        helpers.assertSet(_logger, f"The {ConfigAttributes.DEPENDENCY_TARGET_DIR} attribute must be set in dependency: {ConfigAttributes.DEPENDENCY_TARGET_NAME}={targetName}, {ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY}={source.getName()}, {ConfigAttributes.DEPENDENCY_SOURCE_PATH}: {sourcePath}", targetDir)
        self._name:str = name
        self._targetDir:str = targetDir
        self._targetName:str = targetName
        self._targetRelativeRoot:bool = targetRelativeRoot
        self._source:Source = source
        self._sourcePath:str = sourcePath
        self._resolveAction:ResolveAction = resolveAction
        self._description:str = description
        self._alwaysUpdate:bool = alwaysUpdate


    def getName(self) :
        """Returns the name of this dependency"""
        return self._name


    def getTargetPath(self) -> str :
        """Returns the full target path for the dependency."""
        return file_util.buildPath(self._targetDir, self._targetName)


    def isTargetDirectory(self) -> bool :
        """Returns True if the target path is a directory (opposed to a file)."""
        return helpers.isEmpty(self._targetName)


    def getTargetDirectory(self) -> str :
        """Returns the target directory for this dependency."""
        return self._targetDir


    def getTargetName(self) -> str :
        """Returns the target file name for this dependency."""
        return self._targetName


    def isTargetRelativeToRoot(self) -> bool :
        """Should this target be  placed relative to the project's target root (opposed to the configuration file)."""
        return self._targetRelativeRoot


    def getAbsoluteSourcePath(self) -> str :
        """Returns the source complete path to this dependency's source. May include the protocol depending on how the source is fetched."""
        return self.getSource().getAbsoluteSourcePath(self.getSourcePath())


    def getSource(self) -> Source :
        """Returns the Source of this dependency."""
        return self._source


    def getSourcePath(self) -> str :
        """Returns the Source path of this dependency."""
        return self._sourcePath


    def alwaysUpdate(self) -> bool :
        """
        Returns True if this dependency should always be updated, even if it was already been fetched and resolved before.
        This is useful for dependencies that may change over time, such as the latest version of a file.
        """
        return self._alwaysUpdate


    def fetchSource(self, targetDir:str, targetName:str) :
        """
        Fetches (downloads) the source of this dependency to a specified directory. The download is saved with the given name.

        Parameters:
            targetDir  - fetch this dependency's source to the directory at this path.
            targetName - the filename to give this fetched source in the target directory.

        Raises:
            FetchError if this fails to fetch successfully.
        """
        helpers.assertSet(_logger, f"Cannot fetch the source {self.getSource().getName()} - the target destination was not specified.", targetDir)
        helpers.assertSet(_logger, f"Cannot fetch the source {self.getSource().getName()} - the target filename was not specified.", targetName)
        self.getSource().fetch(self.getSourcePath(), targetDir, targetName)


    def resolve(self, sourcePath:str, targetHomeDir:str) :
        """
        Resolves this dependency. The source must have been fetched first.

        Parameters:
            sourcePath - the path to the fetched source. Most likely points inside a cache.
            targetHomeDir - the place in the filesystem to add it.

        Raises:
            ResolveError if this fails to resolve successfully.
        """
        helpers.assertSet(_logger, f"Cannot resolve the dependency {self.getName()} - the source path wasn't set", sourcePath)
        helpers.assertSet(_logger, f"Cannot resolve the dependency {self.getName()} - the destination directory path wasn't set", targetHomeDir)
        targetDir:str = file_util.buildPath(targetHomeDir, self.getTargetDirectory())
        file_util.mkdir(targetDir, mode=0o744)  # just in case
        self._getResolveAction().resolve(sourcePath, targetDir)


    def _getResolveAction(self) -> ResolveAction :
        """
        Returns the resolve action for this dependency.

        Returns:
            ResolveAction: the resolve action for this dependency.
        """
        return self._resolveAction
