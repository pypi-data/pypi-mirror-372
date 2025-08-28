""" Package for _jobs functionality.
"""
import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Literal, TypedDict, Union, Callable

import pandas as pd
from typeguard import typechecked

from bmll._jobs.exceptions import JobException, JobRunException
from bmll._jobs import core
from bmll._triggers import BaseTrigger
from bmll._core.collections import BMLLCollection
from bmll._utils import (
    validate_env, validate_instance_size, validate_script_parameters
)

__all__ = (
    'Job',
    'JobCollection',
    'JobRun',
    'JobRunCollection',
    'Notification',
    '_get_jobs',
    '_get_previous_job_runs',
    '_get_job_runs',
    '_get_job_run_parameters',
    '_delete_job_run',
)


_logger = logging.getLogger(__name__)

JOB_FIELDS = {
    'Name': 'name',
    'Instance Size': 'instance_size',
    'Max Runtime Hours': 'max_runtime_hours',
    'Script Path': 'script_path',
    'Script Area': 'script_area',
    'Log Path': 'log_path',
    'Log Area': 'log_area',
    'Conda Env': 'conda_env',
    'Script Parameters': 'script_parameters',
    'Active': 'active',
    'Job Id': 'id',
    'Visibility': 'visibility',
    'Bootstraps': 'bootstraps',
    'Notifications': 'notifications',
}

JOB_RUN_FIELDS = {
    'Instance Size': 'instance_size',
    'Max Runtime Hours': 'max_runtime_hours',
    'Script Path': 'script_path',
    'Script Area': 'script_area',
    'Log Path': 'log_path',
    'Log Area': 'log_area',
    'Conda Env': 'conda_env',
    'Script Parameters': 'script_parameters',
    'States': 'states',
    'Job Run Id': 'id',
    'vCPU Hours': 'vcpu_hours',
    'Bootstraps': 'bootstraps',
}


class BootstrapRequired(TypedDict):
    area: Literal['user', 'organisation']
    path: str


class BootstrapComplete(BootstrapRequired):
    args: List[Union[str, int]]


# 'from typing_extensions import NotRequired' not fully supported in typeguard 4.4
# in py311, NotRequired is built-in
Bootstrap = Union[BootstrapRequired, BootstrapComplete]


class Notification(TypedDict):
    email: str
    on: List[Literal['start', 'success', 'error']]


@typechecked
class Job:
    def __init__(self,  data: Dict[str, Any]):
        self._data = deepcopy(data)
        self.__deleted = False

        # brand new job
        if not self._data.get('jobId'):
            try:
                response = core.create_job(self._data)
                self._data = response
                _logger.debug('Created new job (%s).', response['jobId'])

            except Exception as e:
                raise JobException(f"Failed to create job: {e}") from e

    def __repr__(self):
        updated = f', updated={self.updated_ts}' if self.updated_ts else ''
        return f'{self.__class__.__name__}(id={self.id}, active={self.active}, name={self.name}{updated})'

    # READ-ONLY

    @property
    def id(self):
        """str: Unique identifier of the job."""
        return self._data['jobId']

    @property
    def updated_ts(self):
        return self._data.get('updatedTs')

    @property
    def visibility(self):
        return self._data.get('visibility')

    @property
    def active(self):
        """bool: Whether the job is still active."""
        return self._data['active']

    @property
    def name(self):
        """str: The name of the job."""
        return self._data['name']

    @property
    def instance_size(self):
        """int: The instance size of the job."""
        return self._data['instanceSize']

    @property
    def conda_env(self):
        """str: The conda environment used by the job."""
        return self._data['condaEnv']

    @property
    def max_runtime_hours(self):
        """int: The max runtime hours of the job."""
        return self._data['maxRuntimeHours']

    @property
    def script_path(self):
        """str: The script path of the job."""
        return self._data['scriptPath']

    @property
    def script_area(self):
        """str: The script area of the job."""
        return self._data['scriptArea']

    @property
    def log_path(self):
        """str: The log path of the job."""
        return self._data['logPath']

    @property
    def log_area(self):
        """str: The log area of the job."""
        return self._data['logArea']

    @property
    def script_parameters(self):
        """dict: The parameters of the job."""
        return self._data['scriptParameters']

    @property
    def bootstraps(self):
        """List[Bootstrap]: custom bootstraps"""
        return self._data['bootstraps']

    @property
    def notifications(self):
        """List[Notification]: notifications"""
        return self._data['notifications']

    @property
    def triggers(self):
        """
        List[dict]: the triggers could be two types :class:`CronTrigger <bmll._triggers.CronTrigger>`
        or :class:`AvailabilityTrigger <bmll._triggers.AvailabilityTrigger>`
        """
        return self._data['triggers']

    @staticmethod
    def _validation(data: Dict[str, Any]):
        if 'conda_env' in data:
            validate_env(data['conda_env'])

        if 'instance_size' in data:
            validate_instance_size(data['instance_size'])

        if 'script_parameter' in data:
            validate_script_parameters(data['script_parameter'])

    def update(
        self,
        active: Optional[bool] = None,
        name: Optional[str] = None,
        instance_size: Optional[int] = None,
        conda_env: Optional[str] = None,
        max_runtime_hours: Optional[int] = None,
        script_path: Optional[str] = None,
        script_area: Optional[Literal['area', 'organisation']] = None,
        log_path: Optional[str] = None,
        log_area: Optional[Literal['area', 'organisation']] = None,
        script_parameters: Optional[Dict[str, Any]] = None,
        bootstraps: Optional[List[Bootstrap]] = None,
        notifications: Optional[List[Notification]] = None,
    ):
        """
        Update the job parameters

        Args:
            active: bool (optional)
                The active of the Job

            name: str (optional)
                The name given to the Job.

            instance_size: int (optional)
                The instance memory size of the Job. THe possible options
                are {16, 32, 64, 128, 256, 384, 512, 768, 1024, 1536}

            max_runtime_hours: int (optional)
                The max runtime hours of the Job.

            script_area: str (optional)
                The area to store the script.
                Possible values are :class:`Area <bmll._core.Area>`

            script_path: str
                The path to the script to run.

            log_path: str (optional)
                Where to put the log files.

            log_area: str (optional)
                The area to store the logs.
                Possible values are :class:`Area <bmll._core.Area>`

            conda_env: str (optional)
                Optional conda_env to run the code in. The possible options
                are {'py311-stable', 'py311-latest'}

            visibility: str (optional)
                If 'public' is given, the job is visible in org,
                if 'private' is given, the job is visible in owner only.

            script_parameters: dict (optional)
                The parameters can be used in python script by calling
                'import bmll; parameters=bmll.compute.get_job_run_parameters'

            bootstraps: dict (optional)
                :class: `Bootstrap <bmll._jobs.components.Bootstrap>`
                The bootstraps are executed before python script.
                , example:

                {'area': 'user', 'path': 'sample/test/bootstrap1.sh', args: ['arg1', 10]}

                area: str, 'user' or 'organisation'
                path: str
                args: List[str | int] (optional)

            notifications: List[Notification] (optional)
                :class:`Notification <bmll._jobs.components.Notification>`
                Notifications for the job. A notification can be set to deliver
                an email when the job starts, succeeds, or fails.

                example:

                [{'email': 'example@example.com', 'on': ['start', 'success', 'error']}]

                email: str
                on: List[str], possible values are ['start', 'success', 'error']

        Returns:
            the metadata of a job in a dictionary format
        """
        self._check_deleted()

        data = {
            'active': active,
            'name': name,
            'instanceSize': instance_size,
            'maxRuntimeHours': max_runtime_hours,
            'scriptPath': script_path,
            'scriptArea': script_area,
            'logPath': log_path,
            'logArea': log_area,
            'condaEnv': conda_env,
            'scriptParameters': script_parameters,
            'bootstraps': bootstraps,
            'notifications': notifications,
        }
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise JobException('Empty parameter to update')

        self._validation(data)

        updated_data = core.update_job(self.id, data)
        # overwrite existing data with new value
        self._data = {**self._data, **updated_data}

    def execute(
        self,
        active: Optional[bool] = None,
        name: Optional[str] = None,
        instance_size: Optional[int] = None,
        conda_env: Optional[str] = None,
        max_runtime_hours: Optional[int] = None,
        script_path: Optional[str] = None,
        script_area: Optional[Literal['area', 'organisation']] = None,
        log_path: Optional[str] = None,
        log_area: Optional[Literal['area', 'organisation']] = None,
        script_parameters: Optional[Dict[str, Any]] = None,
        bootstraps: Optional[List[Bootstrap]] = None,
    ):
        """
        Execute the job immediately

        Args:
            active: bool (optional)
                The active of the Job

            name: str (optional)
                The name given to the Job.

            instance_size: int (optional)
                The instance memory size of the Job. THe possible options
                are {16, 32, 64, 128, 256, 384, 512, 768, 1024, 1536}

            max_runtime_hours: int (optional)
                The max runtime hours of the Job.

            script_area: str (optional)
                The area to store the script.
                Possible values are :class:`Area <bmll._core.Area>`

            script_path: str
                The path to the script to run.

            log_path: str (optional)
                Where to put the log files.

            log_area: str (optional)
                The area to store the logs.
                Possible values are :class:`Area <bmll._core.Area>`

            conda_env: str (optional)
                Optional conda_env to run the code in. The possible options
                are {'py311-stable', 'py311-latest'}

            visibility: str (optional)
                If 'public' is given, the job is visible in org,
                if 'private' is given, the job is visible in owner only.

            script_parameters: dict (optional)
                The parameters can be used in python script by calling
                'import bmll; parameters=bmll.compute.get_job_run_parameters'

            bootstraps: dict (optional)
                :class: `Bootstrap <bmll._jobs.components.Bootstrap>`
                The bootstraps are executed before python script.
                , example:

                {'area': 'user', 'path': 'sample/test/bootstrap1.sh', args: ['arg1', 10]}

                area: str, 'user' or 'organisation'
                path: str
                args: List[str | int] (optional)

        Returns:
            :class:`JobRun <bmll._jobs.JobRun>`
                Object representing a collection of JobRun.
        """

        self._check_deleted()

        data = {
            'active': active,
            'name': name,
            'instanceSize': instance_size,
            'maxRuntimeHours': max_runtime_hours,
            'scriptPath': script_path,
            'scriptArea': script_area,
            'logPath': log_path,
            'logArea': log_area,
            'condaEnv': conda_env,
            'scriptParameters': script_parameters,
            'bootstraps': bootstraps,
        }
        data = {k: v for k, v in data.items() if v is not None}

        self._validation(data)

        try:
            result = core.create_job_run(
                self.id, data=data if data else None)
        except Exception as ex:
            raise JobRunException('Failed to create job run: {}'.format(ex)) from ex

        return JobRun(result)

    def _check_deleted(self):
        """Check if the instance has been deleted"""
        if self.__deleted:
            raise JobException(
                "This job has been deleted and can no longer be edited."
            )

    def previous_runs(self, max_n_job_runs: int = 10):
        """

        Args:
            * max_n_job_runs: int, default 10
                Maximum number of most recent JobRuns to retrieve.

        Returns:
            :class:`JobRun <bmll._jobs.JobRun>`
                Object representing a collection of JobRun.
        """

        return _get_previous_job_runs(self.id, max_n_job_runs)

    def delete(self):
        """
        Delete the job. No further executions of this job will occur.
        Also, the related runs will be deleted.
        """
        if not self.__deleted:
            response = core.delete_job(self.id)
            self.__deleted = True
            return response
        else:
            raise JobException("This job has already been deleted.")

    def clone(self, visibility: Optional[str] = None, name: Optional[str] = None):
        """
        Clone existing job data and can redefine the visibility and name

        Args:
            * visibility: str, default None
            * name: str, default None

        Returns:
            :class:`Job <bmll._jobs.Job>`
        """
        new_data = {
            'name': name if name else f'{self.name} - clone',
            'instanceSize': self.instance_size,
            'maxRuntimeHours': self.max_runtime_hours,
            'scriptPath': self.script_path,
            'scriptArea': self.script_area,
            'logPath': self.log_path,
            'logArea': self.log_area,
            'condaEnv': self.conda_env,
            'visibility': visibility if visibility else self.visibility,
            'scriptParameters': self.script_parameters,
            'bootstraps': self.bootstraps,
            'notifications': self.notifications,
        }

        return Job(new_data)

    def add_trigger(self, name: str, trigger: BaseTrigger):
        """
        Add trigger to Job
        """

        trigger_data = trigger._jsonify()
        data: Dict[str, Any] = {'name': name}
        data.update(trigger_data if 'cron' in trigger_data else {'availability': trigger_data})

        return core.create_job_trigger(self.id, data=data)

    def delete_trigger(self, trigger_id: str):
        """
        Delete the trigger with given ID from the Job
        """
        return core.delete_job_trigger(self.id, trigger_id)

    def update_trigger(self, trigger_id: str, name: Union[str, None] = None,
                       trigger: Union[BaseTrigger, None] = None):
        """
        Delete the trigger with given ID from the Job
        """
        if name is None and trigger is None:
            raise ValueError(
                "Neither 'name' nor 'trigger' were given. Please specify at "
                "least one to make an update to a trigger."
            )

        data: Dict[str, Any] = {}

        if name is not None:
            data['name'] = name

        if trigger is not None:
            trigger_data = trigger._jsonify()
            data.update(
                trigger_data if 'cron' in trigger_data
                else {'availability': trigger_data}
            )

        return core.update_job_trigger(self.id, trigger_id, data=data)

    def to_dict(self):
        """
        Helper method to retrieve the metadata of a job in a dictionary format.
        """
        res = {}
        for key, attr in JOB_FIELDS.items():
            res[key] = getattr(self, attr)
        return res


class JobCollection(BMLLCollection[Job]):
    """Container for :class:`Job <bmll._jobs.Job>` objects.
    """

    def __init__(self, results):
        super().__init__(
            [Job(job_dict) for job_dict in results]
        )

    def describe(self):
        """Get a DataFrame containing information about the job.
        """
        self._values: List[Job]
        return pd.DataFrame([job.to_dict() for job in self._values])


class JobRun:
    def __init__(self, data: Dict[str, Any]):
        self._data = deepcopy(data)
        self.__deleted = False

    def __repr__(self):
        latest_state = f'{self.states[-1][0]}'
        return f'{self.__class__.__name__}(job_run_id={self.id}, state={latest_state})'

    # READ-ONLY

    @property
    def id(self):
        """str: Unique identifier of the job."""
        return self._data['jobRunId']

    @property
    def active(self):
        """bool: Whether the job run is still active."""
        return self._data['active']

    @property
    def instance_size(self):
        """int: The instance size of the job run."""
        return self._data['instanceSize']

    @property
    def conda_env(self):
        """str: The conda environment used by the job run."""
        return self._data['condaEnv']

    @property
    def max_runtime_hours(self):
        """int: The max runtime hours of the job run."""
        return self._data['maxRuntimeHours']

    @property
    def script_path(self):
        """str: The script path of the job run."""
        return self._data['scriptPath']

    @property
    def script_area(self):
        """str: The script area of the job run."""
        return self._data['scriptArea']

    @property
    def log_path(self):
        """str: The log path of the job run."""
        return self._data['logPath']

    @property
    def log_area(self):
        """str: The log area of the job run."""
        return self._data['logArea']

    @property
    def script_parameters(self):
        """dict: The parameter of the job run."""
        return self._data['scriptParameters']

    @property
    def vcpu_hours(self):
        """int: The vCPU hours of the job run."""
        return self._data['vcpuHours']

    @property
    def states(self):
        """list[str]: The states of the job run."""
        return self._data['states']

    @property
    def bootstraps(self):
        """List[Bootstrap]: custom bootstraps"""
        return self._data['bootstraps']

    def logs(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ):
        """
        Extract general logs of job run

        Parameters
        ----------
        start_time: str (optional)
            The start datetime as a string (format: 'YYYY-MM-DD HH:MM:SS').
            Example: '2025-01-01 00:00:00'.
            Defaults to today's midnight (00:00:00).
        end_time: str (optional)
            The end datetime as a string (format: 'YYYY-MM-DD HH:MM:SS').
            Example: '2025-01-01 23:59:59'.
            Defaults to the current time.

        Examples
        --------
        >>> job_run = JobRun(data)
        >>> for event in job_run.logs():
        >>>     print(event)
        """

        yield from self._get_logs(core.get_job_run_logs, start_time, end_time)

    def stream_logs(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ):
        """
        Extract stream logs of job run

        Parameters
        ----------
        start_time: str (optional)
            The start datetime as a string (format: 'YYYY-MM-DD HH:MM:SS').
            Example: '2025-01-01 00:00:00'.
            Defaults to today's midnight (00:00:00).
        end_time: str (optional)
            The end datetime as a string (format: 'YYYY-MM-DD HH:MM:SS').
            Example: '2025-01-01 23:59:59'.
            Defaults to the current time.

        Examples
        --------
        >>> job_run = JobRun(data)
        >>> for event in job_run.stream_logs():
        >>>     print(event)
        """

        yield from self._get_logs(core.get_job_run_stream_logs, start_time, end_time)

    def _get_logs(
         self, func: Callable, start_time: Optional[str] = None, end_time: Optional[str] = None
    ):
        try:
            now = datetime.now(timezone.utc)

            if end_time is None:
                end_time = now.strftime('%Y-%m-%dT%H:%M:%S')

            if start_time is None:
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                start_time = start_of_day.strftime('%Y-%m-%dT%H:%M:%S')

            next_token = None

            while True:
                resp = func(self.id, start_time, end_time, next_token=next_token)
                events = resp.get('events', [])

                for event in events:
                    yield event

                next_token = resp.get('nextToken')
                if not next_token:
                    break

        except Exception as err:
            raise JobRunException(f'Failed to get job run logs: {err}')

    def terminate(self):
        """
        Terminate the job run if it is still in progress
        """
        if not self.__deleted:
            response = core.delete_job_run(self.id)
            self.__deleted = True
            return response
        else:
            raise JobRunException("This job run has already been terminated.")

    def to_dict(self):
        """
        Helper method to retrieve the metadata of a job run in a dictionary format.
        """
        res = {}
        for key, attr in JOB_RUN_FIELDS.items():
            res[key] = getattr(self, attr)
        return res


class JobRunCollection(BMLLCollection[JobRun]):
    def __init__(self, results):
        super().__init__(
            [JobRun(data=job_dict) for job_dict in results]
        )

    def describe(self):
        self._values: List[JobRun]
        return pd.DataFrame([job.to_dict() for job in self._values])


@typechecked
def _get_jobs(
        state: Optional[str],
        visibility: Optional[str],
        page:  Optional[int],
        page_size: Optional[int]
) -> JobCollection:
    """ Helper function for getting a JobCollection.
    """
    try:
        results = core.get_jobs(state=state,
                                visibility=visibility,
                                page=page,
                                page_size=page_size)
    except Exception as ex:
        raise JobException('Failed to get jobs: {}'.format(ex)) from ex

    return JobCollection(results)


@typechecked
def _get_previous_job_runs(
    job_id: str,
    max_n_job_runs: int = 10
) -> JobRunCollection:
    """ Helper function for getting a JobRunCollection.
    """
    try:
        results = core.get_job_runs(job_id)
    except Exception as ex:
        raise JobRunException('Failed to get all job runs: {}'.format(ex)) from ex

    return JobRunCollection(results[:max_n_job_runs])


@typechecked
def _get_job_runs(
        state: Optional[str],
        visibility: Optional[str],
        page:  Optional[int],
        page_size: Optional[int]
) -> JobRunCollection:
    """ Helper function for getting a JobRunCollection.
    """
    try:
        results = core.get_all_job_runs(
            state=state,
            visibility=visibility,
            page=page,
            page_size=page_size
        )
    except Exception as ex:
        raise JobRunException('Failed to get all job runs: {}'.format(ex)) from ex

    return JobRunCollection(results)


@typechecked
def _get_job_run_parameters(job_run_id: str) -> Dict[str, Any]:
    """ Helper function for getting a dictionary of JobRun parameters.
    """
    try:
        result = core.get_job_run_parameters(job_run_id)
    except Exception as ex:
        raise JobRunException('Failed to get job run parameters: {}'.format(ex)) from ex

    return result


@typechecked
def _delete_job_run(job_run_id: str) -> Dict[str, Any]:
    """ Helper function for deleting a JobRun."""
    try:
        result = core.delete_job_run(job_run_id)
    except Exception as ex:
        raise JobRunException('Failed to delete job run: {}'.format(ex)) from ex

    return result
