import logging
from enum import Enum
from ..errors.errors import FetchError
from ..configuration.attributes import ConfigAttributes
from ..utilities import helpers, file_util, https_util


_logger = logging.getLogger(__name__)  # module name


# How the source fetched - each method of getting a source file requires its own protocol.
class SourceProtocol(Enum) :
    HTTPS = ConfigAttributes.PROTOCOL_HTTPS
    FILESYSTEM = ConfigAttributes.PROTOCOL_FS

    def __init__(self, value) :
        self._value_ = value


    @staticmethod
    def determine(type: str) :
        """
        Construct a SourceProtocol enum from a string representation.
        Defaults to SourceProtocol.HTTPS

        Parameters:
            type - the string representation of the protocol
        """
        if helpers.isEmpty(type) :
            return SourceProtocol.HTTPS

        match type.lower() :
            case "http" :
                return SourceProtocol.HTTPS
            case ConfigAttributes.PROTOCOL_HTTPS :
                return SourceProtocol.HTTPS
            case ConfigAttributes.PROTOCOL_FS :
                return SourceProtocol.FILESYSTEM
            case "fs" :
                return SourceProtocol.FILESYSTEM
            case _ :
                _logger.debug(f"Cannot determine SourceProtocol for {type}. Assuming SourceProtocol.HTTPS.")
                return SourceProtocol.HTTPS  # if its unknown then lets assume https


    def fetch(self, source:str, destinationDir:str, destinationName:str) :
        """
        Fetch the specified source an put it in the destination, using the appropriate method for this protocol.

        Parameters:
            source - the absolute location of the source file
            destinationDir - the absolute directory to put this file.
            destinationName - the filename for the fetched resource

        Raises:
            FetchError if fetch fails.
        """
        helpers.assertSet(_logger, "Cannot fetch - the source path was not specified.", source)
        helpers.assertSet(_logger, "Cannot fetch - the destination directory was not specified.", destinationDir)
        helpers.assertSet(_logger, "Cannot fetch - the destination file was not specified.", destinationName)

        file_util.mkdir(destinationDir, mode=0o744)  # Try to make the target destination
        if file_util.ensurePathExists(destinationDir) and file_util.isDir(destinationDir) :  # make sure all is ok with the destination.
            destination:str = file_util.buildPath(destinationDir, destinationName)
            match self :
                case SourceProtocol.HTTPS :
                    self._fetchHttps(source, destination)
                case SourceProtocol.FILESYSTEM:
                    self._fetchFileSystem(source, destination)
        else :
            raise FetchError(f"Unable to fetch {source}, as the specified destination ({destinationDir}) exists but is not a directory")


    def _fetchFileSystem(self, source:str, destination:str) :
        """
        Copy the source path to the destination path.

        Parameters:
            source - the absolute location of the source file
            destination - the absolute path to put this file. Can be a file (source will be renamed) or a directory.

        Throws:
            FetchError if copy fails.
        """
        if not file_util.copy(source, destination) :
            raise FetchError(f"Failed to fetch {source} -> {destination}.")


    def _fetchHttps(self, source:str, destination:str) :
        """
        Perform a http(s) get to stream the source to the specified location.

        Parameters:
            source - the absolute location of the source file
            destination - the absolute path to put this file. Must include destination file name.

        Throws:
            FetchError if copy fails.
        """
        try :
            https_util.download(source, destination)
        except https_util.HttpError as http :
            raise FetchError(f"Failed to fetch {source} -> {destination}.") from http
