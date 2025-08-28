__all__ = (
    'QUOTA_EXCEEDED_ERROR',
    'BMLLError',
    'ConnectivityError',
    'AuthenticationError',
    'LoginError',
    'MarketDataError',
    'RequestTooLarge',
    'QuotaReachedError',
    'InvalidArgumentError',
)


QUOTA_EXCEEDED_ERROR = 'Limit Exceeded'


class BMLLError(Exception):
    pass


class ConnectivityError(BMLLError):
    """The user was unable to reach the BMLL services"""
    pass


class AuthenticationError(BMLLError):
    """The service was unable to authenticate."""
    pass


class LoginError(BMLLError):
    """An error has occurred when attempting to login to the BMLL Services."""
    pass


class MarketDataError(BMLLError):
    """Failed to retrieve market data."""
    pass


class RequestTooLarge(BMLLError):
    """Request content length is too large, the size of the query should be reduced."""


class QuotaReachedError(BMLLError):
    """User has reached their quota and got a 429 status code."""


class BaseError(BMLLError):
    """ Base class for all BMLL object related errors.
    """


class InvalidArgumentError(ValueError):
    """Return a given Exception if a parameter is not in the expected values."""

    def __init__(self, var, var_name, valid_options):
        super().__init__(self._get_msg(var, var_name, valid_options))

    @staticmethod
    def _get_msg(var, var_name, valid_options):
        valid_options = list(valid_options)

        if len(valid_options) <= 2:
            valid_option_str = " or ".join(f'"{nt}"' for nt in valid_options)
        else:
            valid_option_str = ", ".join(f'"{nt}"' for nt in valid_options[:-1])
            valid_option_str += f', or "{valid_options[-1]}"'

        msg = f'"{var_name}" must be {valid_option_str}, not "{var}".'

        return msg
