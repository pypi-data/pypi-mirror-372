"""
Helper functions to deal with tasks.
"""

from typing import Optional
from bmll import _rest


__all__ = ('get_tasks', 'get_task', 'disable_task',
           'execute_task', 'get_history', 'get_logs',
           'enable_task')


L3_FILTER = '?trigger={}'
NEXT_TOKEN_STR = '&nextToken={}'
PATHS = {
    'SCHEDULING': '/scheduling',
    'TASK': '/scheduling/{}',
    'EXECUTE': '/scheduling/execute/{}',
    'HISTORY': '/scheduling/history?maxHistoryRecs={}&{}',
    'LOGS': '/scheduling/{}/logs?startTime={}&endTime={}',
    'ENABLE': '/scheduling/{}/enable'
}


SESSION = _rest.DEFAULT_SESSION


def get_tasks(trigger_filter: Optional[str] = None) -> list:
    """
    Function to retrieve the tasks present in the organisation of the user.

    Parameters
    ----------
        - trigger_filter: str, default: None
            If specified, then the backend queries for the tasks configured
            based on that particular trigger.
            Supported Values
                * l3

    Returns
    -------
        list of dictionaries related to each scheduled task.

        {
            'task_id': int,
            'task_type': str,
            'schedule': str | None,
            'triggers': dict | None,
            'enabled': bool,
            'last_modified': str,
            'payload': dict
        }
    """
    uri = PATHS['SCHEDULING']
    if trigger_filter:
        uri += L3_FILTER.format(trigger_filter)

    response = SESSION.execute('get', 'compute', uri)
    return response['result']


def get_task(task_id: int) -> dict:
    """
    Return data about a specific task.

    Parameters
    ----------
        - task_id: int
            The id of the task to query for.

    Returns
    -------
        The data about a specific task as a dict.

        {
            'task_id': int,
            'task_type': str,
            'schedule': str | None,
            'triggers': dict | None,
            'enabled': bool,
            'last_modified': str,
            'payload': dict
        }
    """
    response = SESSION.execute('get', 'compute', PATHS['TASK'].format(task_id))
    return response['result']


def disable_task(task_id: int) -> None:
    """
    Disables a given task by setting the enabled field to False
    in the backend.

    Parameters
    ----------
        - task_id: int
            The id of the task to disable.

    Raises
    ------
        Exception if the task is not found or if it encounters some other error
        when attempting to disable the task.
    """
    SESSION.execute('delete', 'compute', PATHS['TASK'].format(task_id))


def enable_task(task_id: int) -> None:
    """
    Enables a given task by setting the enabled field to True
    in the backend.

    Parameters
    ----------
        - task_id: int
            The id of the task to be executed

    Raises
    ------
        Exception if the task is not found or if it encounters some other error
        when attempting execution.
    """
    SESSION.execute('post', 'compute', PATHS['ENABLE'].format(task_id))


def execute_task(task_id: int) -> None:
    """
    Triggers the execution of a given task

    Parameters
    ----------
        - task_id: int
            The id of the task to be executed

    Raises
    ------
        Exception if the task is not found or if it encounters some other error
        when attempting execution.
    """
    SESSION.execute('post', 'compute', PATHS['EXECUTE'].format(task_id))


def get_history(task_ids: list, max_num_rows: int = 10) -> list:
    """
    Obtains the invocation history of the given list of tasks.

    Parameters
    ----------
        - task_ids: list[int]
            The list of task ids whose invocation is needed.
        - max_num_rows: int
            The maximum number of entries to be obtained from the backend
            default: 10

    Returns
    -------
        list of dictionaries, detailing the invocation history of the tasks.
    """
    if not task_ids:
        return
    task_ids_query_str = '&'.join([f'taskID={x}' for x in task_ids])
    response = SESSION.execute('get', 'compute', PATHS['HISTORY'].format(max_num_rows, task_ids_query_str))
    return response['result']


def get_logs(task_id: int, start_time: str, end_time: str) -> list:
    """
    Returns the logs associated with the execution of a task in a given time
    interval.

    Parameters
    ----------
        - task_id: int
            The task_id of the task whose execution details need to be fetched.
        - start_time: str
            The start time of the time interval in which the logs are to be fetched.
        - end_time: str
            The end time of the time interval in which the logs are to be fetched.

    Returns
    -------
    List of dictionaries, each item in the list corresponds to one log entry.
    """
    uri = PATHS['LOGS'].format(task_id, start_time, end_time)
    logs = []
    response = SESSION.execute('get', 'compute', uri)
    result = response['result']
    logs.extend(result['events'])
    next_token = result.get('nextToken')
    while next_token:
        next_uri = uri
        next_uri += NEXT_TOKEN_STR.format(next_token)
        response = SESSION.execute('get', 'compute', next_uri)
        result = response['result']
        logs.extend(result['events'])
        next_token = result.get('nextToken')
    return logs
