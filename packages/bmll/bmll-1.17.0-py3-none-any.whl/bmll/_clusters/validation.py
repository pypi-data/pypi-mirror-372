""" Functions and classes for validating inputs.
"""

import datetime
import warnings

import numpy as np
import pandas as pd

from bmll.exceptions import InvalidArgumentError
from bmll._clusters import exceptions
from bmll._core.enum import Area


__all__ = (
    "argument_check",
    "validate_datetime",
    "check_bootstrap_format",
)


def argument_check(value, name, expected_values):
    """Checks that the argument 'value' is contained in the permitted values, if not then
    it will raise an bmll.exceptions.InvalidArgumentError.

    Args:
        value:
            Variable to be checked
        name: str
            Name of the variable being checked
        expected_values: List, Enum
            An iterable that we are checking if `value` is contained in.

    Raises:
        ParameterError
            If `value` is not contained in `expected_values`.
    """
    if value not in expected_values:
        raise InvalidArgumentError(value, name, expected_values)


def validate_datetime(datetime_value):
    """Converts the user given datetime to pd.Timestamp, as long as it is an
    instance of datetime.datetime. pandas.Timestamp, numpy.datetime64
    or an ISO string (yyyy-MM-ddTHH:mm:ss.fffffff).

    Args:
        datetime_value: datetime.datetime. pandas.Timestamp, numpy.datetime64
                or an ISO string (yyyy-MM-ddTHH:mm:ss.fffffff)
                The datetime given by the user

    Returns:
        pd.Timestamp

    Raises:
        warnings if
            * date_value is not a valid datetime
            * date_value is not of valid format
    """
    datetime_warning_message = ('{} is not a valid datetime format.\n'
                                'Please choose between: isoformat str '
                                '(yyyy-MM-ddTHH:mm:ss.fffffff), '
                                'datetime.datetime, pandas.Timestamp, '
                                'or numpy.datetime64')
    if isinstance(datetime_value, str):
        try:
            datetime_value = pd.Timestamp(datetime_value)
            return datetime_value
        except ValueError:
            warnings.warn(datetime_warning_message.format(datetime_value))
            raise exceptions.InvalidDateTime()

    elif isinstance(datetime_value, (datetime.datetime, datetime.date)):
        return pd.to_datetime(datetime_value, unit='ns')

    elif isinstance(datetime_value, np.datetime64):
        return pd.to_datetime(datetime_value)

    elif isinstance(datetime_value, pd.Timestamp):
        return datetime_value

    else:
        warnings.warn(datetime_warning_message.format(datetime_value))
        raise exceptions.InvalidDateTime()


def check_bootstrap_format(cluster_bootstraps):
    """Check that the format of the cluster_bootstrap argument passed to
    `create_cluster` is formatted correctly.

    Args:
        cluster_bootstraps: list
            The argument users pass with `bmll.compute.create_cluster`
    """
    for bootstrap in cluster_bootstraps:

        error_string = f'{bootstrap} is invalid'

        if not isinstance(bootstrap, dict):
            raise exceptions.ClusterException(
                'cluster_bootstraps should be a list of dictionaries.'
            )

        # Check that the specified keys are a subset of {area, args, name, path}.
        diff_keys = set(bootstrap) - {'area', 'args', 'name', 'path'}
        if diff_keys != set():
            raise exceptions.ClusterException(
                f'{error_string}. cluster_bootstraps should '
                f'only specify path, name, area, and args, not {diff_keys}.'
            )

        if 'path' not in bootstrap:
            raise exceptions.ClusterException(
                f'{error_string}. The path must be specified for each bootstrap.'
            )

        if 'area' in bootstrap:
            if bootstrap['area'] not in Area:
                raise InvalidArgumentError(
                    bootstrap['area'], f'{error_string}. `area`', Area
                )

        check_instance_type('args', bootstrap, list, error_string)
        check_instance_type('name', bootstrap, str, error_string)


def check_instance_type(keyword, dictionary, expected_type, error_string=None):
    """Check the type of a value in a dictionary.  Raise if the type does not match
    the expected type.

    Args:
        keyword: str
            The keyword to look up in the dictionary.
        dictionary: dict
            A dictionary.
        expected_type: Type
            The expected type of the value from the dictionary with key=keyword.
        error_string: str, optional
            String to prefix the error message.
    """
    if keyword in dictionary:
        if not isinstance(dictionary[keyword], expected_type):
            raise exceptions.ClusterException(
                f"{error_string}. `{keyword}` specified must be of "
                f"type {expected_type} not {type(dictionary[keyword])}"
            )
