import logging
from enum import Enum
from ..utilities import helpers, file_util, zip_util, tar_util
from ..configuration.attributes import ConfigAttributes
from ..errors.errors import ResolveError

_logger:logging.Logger = logging.getLogger(__name__)


class ResolveAction(Enum) :
    COPY = ConfigAttributes.RESOLVE_COPY
    UNZIP = ConfigAttributes.RESOLVE_UNZIP
    UNTAR = ConfigAttributes.RESOLVE_UNTAR


    def __init__(self, value) :
        self._value_ = value


    @staticmethod
    def determine(type: str) :
        """
        Construct a ResolveAction enum from a string representation.
        Defaults to ResolveAction.COPY

        Parameters:
            type - the string representation of the action.
        """
        if helpers.isEmpty(type) :
            return ResolveAction.COPY

        match type.lower() :
            case ConfigAttributes.RESOLVE_COPY :
                return ResolveAction.COPY
            case ConfigAttributes.RESOLVE_UNZIP :
                return ResolveAction.UNZIP
            case ConfigAttributes.RESOLVE_UNTAR :
                return ResolveAction.UNTAR
            case _ :
                return ResolveAction.COPY  # if its unknown then lets assume copy


    def resolve(self, sourcePath:str, destinationDir:str) :
        """
        Resolve the specified sourcePath file as appropriate for this action, e.g. copy to destination dir or unzip to destination dir.

        Parameters:
            source - the absolute location of the source file
            destinationDir - the absolute directory to put this source file.

        Raises:
            ResolveError if fails to resolve the action.
        """
        helpers.assertSet(_logger, "Cannot fetch - the source path was not specified.", sourcePath)
        helpers.assertSet(_logger, "Cannot fetch - the destination directory was not specified.", destinationDir)
        match self :
            case ResolveAction.COPY :
                self._copy(sourcePath, destinationDir)
            case ResolveAction.UNZIP:
                self._unzip(sourcePath, destinationDir)
            case ResolveAction.UNTAR:
                self._untar(sourcePath, destinationDir)


    def _copy(self, sourcePath:str, destinationDir:str):
        if not file_util.copy(sourcePath, destinationDir) :
            raise ResolveError(f"Failed to copy {sourcePath} -> {destinationDir}.")


    def _unzip(self, sourcePath:str, destinationDir:str) :
        try :
            zip_util.unzip(sourcePath, destinationDir)
        except zip_util.ZipError as zipError :
            raise ResolveError(f"Failed to unzip {sourcePath} -> {destinationDir}") from zipError


    def _untar(self, sourcePath:str, destinationDir:str) :
        try :
            tar_util.untar(sourcePath, destinationDir)
        except tar_util.TarError as tarError :
            raise ResolveError(f"Failed to untar {sourcePath} -> {destinationDir}") from tarError
