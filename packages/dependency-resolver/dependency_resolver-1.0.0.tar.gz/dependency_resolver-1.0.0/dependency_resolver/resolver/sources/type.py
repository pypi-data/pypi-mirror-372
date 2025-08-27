from enum import Enum
from ..utilities import helpers


# Is the source path relative to something or an absolute path?
# The default for a source is ABSOLUTE.
class SourceType(Enum) :
    ABSOLUTE = 1
    RELATIVE_PROJECT = 2

    @staticmethod
    def determine(type: str) :
        if helpers.isEmpty(type) :
            return SourceType.ABSOLUTE

        match type.lower() :
            case "absolute" :
                return SourceType.ABSOLUTE
            case "project" :
                return SourceType.RELATIVE_PROJECT
            case _ :
                return SourceType.ABSOLUTE
