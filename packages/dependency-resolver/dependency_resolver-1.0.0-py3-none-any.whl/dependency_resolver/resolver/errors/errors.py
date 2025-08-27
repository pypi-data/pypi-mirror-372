from ..utilities.errors_util import ProjectError

class ProtocolError(ProjectError) :
    """Wraps underlying exceptions to make handling them easier for calling code."""


class FetchError(ProtocolError) :
    """Raised when fetching dependency sources fails. Wraps underlying exceptions when fetching a source using the specified protocol."""


class ResolveError(ProjectError) :
    """Raised when resolving dependencies fails. Wraps underlying exceptions to make handling them easier for calling code."""
