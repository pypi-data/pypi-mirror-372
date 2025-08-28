from collections import defaultdict
from datetime import datetime
import pandas as pd
from typing import Optional

from bmll._core.collections import BMLLCollection
from bmll._clusters.components import _get_clusters
from bmll._tasks.core import (get_tasks, get_task, disable_task,
                              enable_task, execute_task, get_logs)
from bmll._tasks.exceptions import TaskException, TaskFetchException, TaskUpdateException


TASK_FIELDS = {
    'ID': 'id',
    'Name': 'name',
    'Type': 'task_type',
    'Schedule': 'schedule',
    'Triggers': 'triggers',
    'Enabled': 'enabled'
}

TASK_FIELDS_DETAILED = {
    **TASK_FIELDS,
    'Environment': 'conda_env',
    'Node_Count':  'node_count',
    'Log': 'logging_details',
    'Status': 'last_run_status'
}

VALID_TRIGGERS = ['l3']


__all__ = ('Task',
           'TaskCollection')


class Task:
    """
    Encapsulates a BMLL Data Lab scheduled task.

    This object can be used to:
        * execute a task.
        * access the invocation history of the task.
        * access the execution logs of the task.
        * view the metadata associated with the task.
        * disable the task.

    See also
        * :class:`TaskCollection <bmll._tasks.TaskCollection>`

    """

    def __init__(self, task_id, task_type='cluster', schedule=None, enabled=False,
                 latest_modified=None, triggers=None, payload={}):

        self._task_id = task_id
        self._type = task_type
        self._schedule = schedule
        self._triggers = triggers
        self._enabled = enabled
        self._latest_modified = latest_modified
        self._payload = payload

    @property
    def id(self):
        return self._task_id

    @property
    def task_type(self):
        """
        The type of the task.
        """
        return self._type

    @property
    def schedule(self):
        """
        The cron schedule associated with the task
        (if any).
        None if the task is not configured to run on a schedule.
        """
        return self._schedule

    @property
    def triggers(self):
        """
        The mic based trigger associated with the task.
        None, if the task is not configured based on mic availability.
        """
        return self._triggers

    @property
    def enabled(self):
        """
        Indicating if the task is enabled or not.
        """
        return self._enabled

    @property
    def latest_modified(self):
        """
        The latest_modified timestamp associated with the task.
        """
        return self._latest_modified

    @property
    def node_count(self):
        """
        The node count field associated with the task,
        obtained from the task payload.
        """
        return self._payload.get('node_count')

    @property
    def conda_env(self):
        """
        The conda environment in which the task will be executed.
        """
        return self._payload.get('conda_env')

    @property
    def name(self):
        """
        The name of the task.
        """
        return self._payload.get('name')

    @property
    def jobs(self):
        """
        Returns jobs as a list of dicts.
        """
        return self._payload.get('jobs')

    @property
    def bootstrap_actions(self):
        """
        The bootstrap actions associated with the task if any.
        """
        return self._payload.get('bootstrap_actions')

    @property
    def logging_details(self):
        """
        The details of the log area and log path associated with the task.

        The older tasks had a different payload structure in which the log_path
        and log_area fields were present in another dictionary object called location.

        In newer tasks, the log_path and log_area are directly present in the
        task payload itself.
        """
        logging_details = self._payload.get('logging', {}).get('location')
        if not logging_details:
            log_area = self._payload.get('log_area')
            log_path = self._payload.get('log_path')
            logging_details = {'area': log_area, 'path': log_path}
        return logging_details

    @property
    def last_run_status(self):
        return self._payload.get('lastRunStatus', {}).get('text', 'Unknown')

    def __repr__(self):
        return "{}(id={}, name={}, type={})".format(
            self.__class__.__name__,
            self.id,
            self.name,
            self.task_type
        )

    def reload(self):
        """
        method to re-fetch the task metadata
        and update the internal variables.
        """
        try:
            task_metadata = get_task(self._task_id)
        except Exception as e:
            raise TaskFetchException(f'encountered {e} when attempting to fetch task data')
        self._type = task_metadata['task_type']
        self._enabled = task_metadata['enabled']
        self._schedule = task_metadata['schedule']
        self._triggers = task_metadata['triggers']
        self._payload = task_metadata['payload']
        self._latest_modified = task_metadata['latest_modified']

    def disable(self):
        """
        Disables the specific task
        """
        try:
            disable_task(self._task_id)
        except Exception as e:
            raise TaskUpdateException(f'encountered {e} when attempting to disable task')
        self.reload()

    def enable(self):
        """
        Enables the specific task
        """
        try:
            enable_task(self._task_id)
        except Exception as e:
            raise TaskUpdateException(f'encountered {e} when attempting to enable task')
        self.reload()

    def execute(self):
        """
        Triggeres the execution of the specific task
        """
        if not self.enabled:
            raise TaskException(f'Task {self.id} is disabled, unable to execute')
        try:
            execute_task(self._task_id)
        except Exception as e:
            raise TaskException(f'unable to execute task {self.id}, exception: {e}')

    def get_logs(self, start_time: datetime, end_time: datetime):
        """
        Returns the logs for the task.

        Parameters
        ----------
            start_time: datetime
                Start time for the logs to be fetched.
            end_time: datetime
                End time for the logs to be fetched.
        Raises
        ------
            TaskFetchException
                If there is an error while fetching the logs.

        Returns
        -------
            Log lines of the task as a list of dicts in the specified
            time interval.
        """
        try:
            return get_logs(self.id, start_time.isoformat(), end_time.isoformat())
        except Exception as e:
            raise TaskFetchException(f'Encountered {e} while attempting to fetch logs associated with {self.id}')

    def get_invocations(self, max_num_rows=10):
        """
        Returns the cluster runs associated with the task.

        parameters
        ----------
            max_num_rows: maximum number of clusters to be included
            in the output.

        Raises
        ------
            TaskFetchException
                If there is an error while fetching the invocations.

        Returns
        -------
            ClusterCollection of clusters associated with the particular task.

        See Also:
            * :class:`bmll._clusters.ClusterCollection`
        """
        try:
            return _get_clusters(active_only=False, max_n_clusters=max_num_rows,
                                 tags={'task_id': str(self.id)})
        except Exception as e:
            raise TaskFetchException(f'Encountered {e} while attempting to fetch history of {self.id}')

    def to_dict(self, full_details=False):
        """
        Helper method to retrieve the metadata of a task in a dictionary format.
        """
        fields = TASK_FIELDS_DETAILED if full_details else TASK_FIELDS
        res = {}
        for key, attr in fields.items():
            res[key] = getattr(self, attr)
        return res


class TaskCollection(BMLLCollection[Task]):
    """
    Container for :class:`Task <bmll._tasks.Task>` objects.

    See Also:
        * :class:`bmll._tasks.Task`
    """

    def __init__(self, results):
        super().__init__([Task(task_id=task_dict['task_id'],
                               task_type=task_dict.get('task_type', 'cluster'),
                               enabled=task_dict.get('enabled', False),
                               latest_modified=task_dict.get('latest_modified'), 
                               triggers=task_dict.get('triggers'),
                               schedule=task_dict.get('schedule'),
                               payload=task_dict.get('payload', {})) for task_dict in results])

    def describe(self, full_details=False):
        fields = TASK_FIELDS_DETAILED.keys() if full_details else TASK_FIELDS.keys()
        data_dict = defaultdict(list)
        for task in self._values:
            task_dict = task.to_dict(full_details)
            for field in fields:
                data_dict[field].append(task_dict[field])
        df = pd.DataFrame(data_dict, columns=fields)
        return df


def _get_tasks(active_only=False, max_n_tasks=10, trigger_filter: Optional[str] = None) -> TaskCollection:
    """
    """
    if trigger_filter and trigger_filter not in VALID_TRIGGERS:
        raise TaskFetchException(f'Unknown trigger {trigger_filter} to filter tasks on')
    try:
        tasks = get_tasks(trigger_filter)
    except Exception as e:
        raise TaskFetchException(f'Exception {e} while attempting to fetch task metadata')
    if active_only:
        tasks = [t for t in tasks if t.get('enabled')]
    # Sorting such that more recent tasks appear first
    tasks.sort(key=lambda x: x['latest_modified'], reverse=True)
    return TaskCollection(tasks[:max_n_tasks])
