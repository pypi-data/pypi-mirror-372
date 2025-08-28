"""
Exceptions related to the task module
"""

from bmll.exceptions import BMLLError


__all__ = (
    "TaskException", "TaskFetchException", "TaskUpdateException"
)


class BaseBMLLTaskError(BMLLError):
    """
    Base Exception for dealing with tasks
    """


class TaskException(BaseBMLLTaskError):
    """
    Generic Task related exception
    """


class TaskFetchException(BaseBMLLTaskError):
    """
    Exception occurs while fetching task metadata
    """


class TaskUpdateException(BaseBMLLTaskError):
    """
    Exception that indicates an issue when updating
    task metadata (such as disabling a task).
    """
