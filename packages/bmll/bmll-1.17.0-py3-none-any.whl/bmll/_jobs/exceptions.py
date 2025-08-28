""" Exceptions that can be raised when working with _jobs.
"""

__all__ = (
    "JobException",
    "JobRunException",
)


from bmll.exceptions import BMLLError


class JobException(BMLLError):
    """ Raised when an error occurs when working with _jobs.
    """


class JobRunException(BMLLError):
    """ Raised when an error occurs when working with _jobs.
    """
