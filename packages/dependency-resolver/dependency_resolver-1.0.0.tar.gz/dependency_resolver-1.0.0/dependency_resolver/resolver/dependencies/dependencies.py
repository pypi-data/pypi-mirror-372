from typing import Optional
from .dependency import Dependency

class Dependencies() :

    def __init__(self) :
        self._dependencies:list[Dependency] = []


    def addDependency(self, dependency:Dependency) :
        """
        Adds a dependency to the list of dependencies.

        Args:
            dependency (Dependency): The dependency to add.
        """
        self._dependencies.append(dependency)


    def getDependencies(self) -> list[Dependency] :
        """
        Returns the list of dependencies.

        Returns:
            list[Dependency]: A list of Dependency objects representing all dependencies.
        """
        return self._dependencies


    def getDependency(self, name:str) -> Optional[Dependency] :
        """
        Returns the dependency with the given name, if it exists.

        Args:
            name (str): The name of the dependency to find.

        Returns:
            Optional[Dependency]: The Dependency object if found, otherwise None.
        """
        for dependency in self.getDependencies() :
            if dependency.getName() == name :
                return dependency
