import logging
from ..utilities import helpers
from ..configuration.configuration import Configuration
from ..configuration.attributes import ConfigAttributes
from ..sources.sources import Sources
from ..sources.source import Source
from ..sources.protocol import SourceProtocol
from ..sources.type import SourceType
from ..dependencies.dependencies import Dependencies
from ..dependencies.dependency import Dependency
from ..dependencies.resolveAction import ResolveAction

_logger:logging.Logger = logging.getLogger(__name__)

class Creator :

    def __init__(self, configuration:Configuration) :
        helpers.assertSet(_logger, "Configuration is not set", configuration)
        self._config:Configuration = configuration


    def createSources(self) -> Sources :
        """
        Create the Sources as defined in the configuration.

        Returns:
            Sources: An instance of Sources containing all the sources defined in the configuration.
        """
        sources:Sources = self._createSources()

        sourceConfig:dict = helpers.getKey(self._getConfig(), ConfigAttributes.SOURCES)
        if sourceConfig is not None :
            for source in sourceConfig :
                name:str = helpers.getKey(source, ConfigAttributes.SOURCE_NAME)
                sources.addSource(name=name, source=self._createSource(source))

        return sources


    def _createSources(self) -> Sources :
        return Sources()


    def _createSource(self, source:dict) -> Source :
        """
        Create a Source object from the given source dictionary.

        Args:
            source (dict): The source dictionary containing attributes like name, protocol, base, type, and description.

        Returns:
            Source: An instance of Source created from the provided attributes.
        """
        name:str = helpers.getKey(source, ConfigAttributes.SOURCE_NAME)
        protocol:SourceProtocol = SourceProtocol.determine(helpers.getKey(source, ConfigAttributes.SOURCE_PROTOCOL))
        base:str = helpers.getKey(source, ConfigAttributes.SOURCE_BASE)
        type:SourceType = SourceType.determine(helpers.getKey(source, ConfigAttributes.SOURCE_TYPE))
        description:str = helpers.getKey(source, ConfigAttributes.SOURCE_DESCRIPTION)
        return Source(name, protocol, type=type, base=base, description=description)


    def createDependencies(self, sources:Sources) -> Dependencies :
        """
        Create the Dependencies as defined in the configuration.

        Args:
            sources (Sources): An instance of Sources containing all the sources defined in the configuration.

        Returns:
            Dependencies: An instance of Dependencies containing all the dependencies defined in the configuration.
        """
        dependencies:Dependencies = self._createDependencies()

        dependencyConfig:dict = helpers.getKey(self._getConfig(), ConfigAttributes.DEPENDENCIES)
        if dependencyConfig is not None :
            for dependency in dependencyConfig :
                dependencies.addDependency(self._createDependency(dependency, sources))

        return dependencies


    def _createDependencies(self) -> Dependencies :
        return Dependencies()


    # Create an individual dependency
    def _createDependency(self, dependency:dict, sources:Sources) -> Dependency :
        """
        Create a Dependency object from the given dependency dictionary.

        Args:
            dependency (dict): The dependency dictionary containing attributes like name, targetDir, targetName, targetRelativeRoot, source, sourcePath, resolveAction, description, and alwaysUpdate.
            sources (Sources): An instance of Sources to resolve the source dependency.

        Returns:
            Dependency: An instance of Dependency created from the provided attributes.
        """
        name:str = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_NAME)
        targetDir:str = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_TARGET_DIR)
        targetName:str = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_TARGET_NAME)
        targetRelativeRoot:bool = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_TARGET_RELATIVE_ROOT)
        source:Source = sources.getSource(helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_SOURCE_DEPENDENCY))
        sourcePath:str = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_SOURCE_PATH)
        action:ResolveAction = ResolveAction.determine(helpers.getKey(dependency, ConfigAttributes.RESOLVE_ACTION))
        description:str = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_DESCRIPTION)
        alwaysUpdate:bool = helpers.getKey(dependency, ConfigAttributes.DEPENDENCY_ALWAYS_UPDATE)
        return Dependency(name=name, targetDir=targetDir, targetName=targetName, targetRelativeRoot=targetRelativeRoot, source=source, sourcePath=sourcePath, resolveAction=action, description=description, alwaysUpdate=alwaysUpdate)


    def _getConfiguration(self) -> Configuration :
        """
        Returns the Configuration object that this Creator was initialized with.

        Returns:
            Configuration: The Configuration object containing the project and dependencies configuration.
        """
        return self._config


    def _getConfig(self) -> dict :
        """
        Returns the underlying configuration dictionary.

        Returns:
            dict: The configuration dictionary containing all the project and dependencies settings.
        """
        return self._getConfiguration().getConfiguration()
