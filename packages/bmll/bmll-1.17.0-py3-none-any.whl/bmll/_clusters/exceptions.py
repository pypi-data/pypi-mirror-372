""" Exceptions that can be raised when working with _clusters.
"""

__all__ = (
    "ClusterException",
    "InvalidDateTime",
)


from bmll.exceptions import BMLLError


class BaseBmllClusterError(BMLLError):
    """ Base class for all cluster-related errors.
    """


class ClusterException(BaseBmllClusterError):
    """ Raised when an error occurs when working with _clusters.
    """


class InvalidDateTime(BaseBmllClusterError):
    """ Raised when an error occurs when working with timestamps
    """
