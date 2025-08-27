class ProjectError(Exception) :
    """
    Base class for all raised by this project.
    Using this as a base class for all custom errors allows developers to use except ProjectException to trap these project-based custom exceptions.
    """


class UtilityError(ProjectError) :
    """Raised by utility functions."""
