import re
import json
from functools import partial
import warnings
import datetime
from typing import Callable, Dict, Any

import pandas as pd


__all__ = (
    'chunk_call', 
    'to_pandas', 
    'paginate', 
    'to_list_of_str',
    'cc_to_snake',
    'convert_dict_keys_cc_to_snake',
    'convert_dict_keys_snake_to_cc',
    'snake_to_lcc',
    'get_available_envs',
    'validate_env',
    'get_available_instance_sizes',
    'validate_instance_size',
    'validate_script_parameters',
    )


ID_COL_TYPE = 'Int64' if pd.__version__ >= '0.24.0' else 'object'


def to_pandas(table):
    """Return a pandas DataFrame from a Table response."""
    df = pd.DataFrame(data=table['data'], columns=table['columns'])

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    if 'ObjectId' in df.columns:
        df['ObjectId'] = df['ObjectId'].astype(ID_COL_TYPE)

    return df


def _collect_notifications(container, response):
    """ Add notifications from the response JSON data to the given container if
        they are present in the response data.

        If present at the top-level of the response JSON data, a 'notifications'
        key is looked up. If present, that must have a 'message' key beneath if
        whose value is a string message to display to the user.
    """
    notifications = response.get('notifications')
    if notifications:
        container.add(notifications['message'])


def paginate(request):
    table = request()
    token = table.get('token')

    all_notifications = set()
    _collect_notifications(all_notifications, table)

    while token:
        page = request(token=token)
        _collect_notifications(all_notifications, page)

        if isinstance(table['data'], dict):
            table['data'].update(page['data'])
        else:
            table['data'].extend(page['data'])
        token = page.get('token')

    if all_notifications:
        notifications = "\n".join(all_notifications)
        warnings.warn(notifications, stacklevel=2)

    return table


def chunk_call(req_func, object_ids, chunk_size):
    """
    Retrieve data from `req_func` after splitting requests by `objects_ids`.

    This avoids a single request with an excessive request body size.

    Args:
        req_func: func
            Request function with kwargs `object_ids` and `token`.
        object_ids: list(int)
            IDs of objects for which to retrieve data.
        chunk_size: int
            Maximum number of object IDs in a single request.

    Returns:
        `pandas.DataFrame`:
            Data from the service.
    """
    if chunk_size < 1:
        raise ValueError('Chunk size must be greater than or equal to 1.')

    if object_ids is None:
        chunks = [None]
    else:
        chunks = [object_ids[i:i + chunk_size] for i in range(0, len(object_ids), chunk_size)]

    data = []
    for chunk_ids in chunks:
        chunk_func = partial(req_func, object_ids=chunk_ids)
        table = paginate(chunk_func)
        df = to_pandas(table)
        data.append(df)
    return pd.concat(data)


def to_list_of_str(x):
    """Converts variable to list. int -> list, str -> list, list -> list."""
    if hasattr(x, '__iter__') and not isinstance(x, str):
        return [str(y) for y in x]
    return [str(x)]


def create_date_range(start, end):
    """ Yield pairs of start and end dates within one year
    """
    sub_start = start
    while sub_start.year < end.year:
        start_date = sub_start
        next_year = datetime.datetime(sub_start.year, 12, 31)
        sub_start = next_year + datetime.timedelta(days=1)
        yield start_date, next_year
    yield sub_start, end


def chunk_dates(
    object_ids: dict,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    chunk_size: int,
    func: Callable,
    kwargs: dict
) -> pd.DataFrame:
    reqs = []
    for start_date, end_date in create_date_range(start_date, end_date):
        dates = {'start_date': start_date, 'end_date': end_date}
        req = partial(func, **kwargs, **dates)
        reqs.append(req)
    df = pd.concat([chunk_call(req, object_ids[mic], chunk_size) for mic in object_ids for req in reqs])
    return df


def cc_to_snake(string: str) -> str:
    """ Convert a [cC]amelCaseVariable string to snake_case_variable string.
    """
    not_at_line_start = r'(?<!^)'
    match_but_no_consume = r'(?=[A-Z])'
    return re.sub(f'{not_at_line_start}{match_but_no_consume}', '_', string).lower()


def snake_to_lcc(string: str) -> str:
    """ Convert a snake_case_variable name to a lowerCamelCaseVariable name.
    """
    lower, *rest = string.split('_')
    return ''.join([lower, *(item.title() for item in rest)])


def convert_dict_keys_cc_to_snake(d: dict) -> dict:
    """ Returns a dict with snake case keys.
    """
    return {cc_to_snake(k): v for k, v in d.items()}


def convert_dict_keys_snake_to_cc(d: dict) -> dict:
    """ Returns a dict with camel case keys.
    """
    return {snake_to_lcc(k): v for k, v in d.items()}


def get_available_envs():
    """ Return available conda environments
    """
    return ['py311-stable', 'py311-latest']


def validate_env(conda_env: str):
    """ Raise error if conda environment is not available
    """
    envs = get_available_envs()
    if conda_env not in envs:
        raise ValueError(f"Unknown conda env given {conda_env!r}. Must be one of {envs}")


def get_available_instance_sizes():
    """ Return available instance sizes (GB)
    """
    return [16, 32, 64, 128, 256, 384, 512, 768, 1024, 1536]


def validate_instance_size(instance_size: int):
    """ Raise error if instance size is not available
    """
    sizes = get_available_instance_sizes()
    if instance_size not in sizes:
        raise ValueError(f"Unknown instance size given {instance_size!r}. Must be one of {sizes}")


def validate_script_parameters(script_parameters: Dict[str, Any]):
    """ Raise error if script parameters is not serialisable
    """
    try:
        json.dumps(script_parameters)
    except Exception:
        raise ValueError("Cannot JSON serialise 'script_parameters'")
