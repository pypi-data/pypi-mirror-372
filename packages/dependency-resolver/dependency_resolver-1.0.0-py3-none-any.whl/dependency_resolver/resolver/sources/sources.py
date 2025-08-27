from .source import Source

class Sources :

    def __init__(self) :
        self._sources:dict = {}


    def addSource(self, name:str, source:Source) :
        """
        Adds a source to the sources collection.

        Args:
            name (str): The unique name of the source.
            source (Source): The source object to add.
        """
        self._sources[name] = source


    def getSource(self, name:str) -> Source :
        """
        Retrieves a source by its name.

        Args:
            name (str): The name of the source to retrieve.

        Returns:
            Source: The source object associated with the given name.
        """
        return self._sources[name]


    def getAllSourceName(self) -> list[str]:
        """
        Returns a list of all source names.

        Returns:
            list[str]: A list of names of all sources.
        """
        return [*self._sources]
