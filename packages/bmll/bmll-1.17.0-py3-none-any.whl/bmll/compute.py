""" Interface to the Compute service.
"""
from typing import Optional, Union, Literal, List
from datetime import datetime
import warnings

import pandas as pd
from typeguard import typechecked

from bmll._rest import DEFAULT_SESSION
from bmll._clusters import core, validation
from bmll._clusters.components import ClusterConfig, Cluster, _get_clusters
from bmll._clusters.exceptions import ClusterException
from bmll._clusters.core import JobType, NodeType, JobFailureAction, ClusterState
from bmll._tasks.components import _get_tasks
from bmll._tasks import core as task_core
from bmll._tasks.exceptions import TaskFetchException
from bmll._jobs.components import (
    Bootstrap, Job, Notification, _get_jobs, _get_job_runs,
    _get_job_run_parameters, _delete_job_run
)
from bmll._jobs import core as job_core
from bmll._triggers import CronTrigger, L3Availability
from bmll._utils import validate_env, validate_instance_size, validate_script_parameters
from bmll._core.enum import Area
from bmll.exceptions import InvalidArgumentError


__all__ = (
    # HTTP interface
    'ComputeClient',

    # Clusters API
    'get_clusters',
    'ClusterConfig',
    'create_cluster',
    'NodeType',
    'Area',
    'JobType',
    'JobFailureAction',
    'ClusterException',
    'InvalidArgumentError',
    'ClusterState',
    'get_tasks',
    'TaskFetchException',
    'create_job',
    'get_jobs',
    'get_job_runs',
    'get_job_run_parameters',
    'CronTrigger',
    'L3Availability',
)


class ComputeClient:
    """
    The ComputeClient provides a convenient interface to interact with the BMLL Compute API.

    Args:
        session: :class:`bmll.Session`, optional
            if provided use this session object to communicate with the API, else use the default session.

            Note: this must be a session authenticated by the Lab Auth service.
    """

    def __init__(self, session=None):
        self._session = session or DEFAULT_SESSION
        core.SESSION = self._session
        task_core.SESSION = self._session
        job_core.SESSION = self._session

    @typechecked
    def create_cluster(
        self, name: Optional[str] = None, log_path: Optional[str] = None, log_area: str = 'user',
        node_type: str = NodeType.CPU, node_count: int = 1,
        cluster_config: Optional[ClusterConfig] = None, spot_pricing: bool = False,
        terminate_on_idle: bool = True,
        cluster_bootstraps: Union[list, dict, None] = None,
        tags: Optional[dict] = None,
        conda_env: str = 'py311-stable',
        notification_email_map: Optional[dict] = None
    ):
        """Create a cluster and return a :class:`Cluster <bmll._clusters.Cluster>`
        object to manage it.

        This is the first step in using /_clusters, which allow parallel computation
        at scale. There may be a delay between running the command and the cluster
        becoming active.  The status of the cluster can be checked with
        :class:`Cluster.status <bmll._clusters.Cluster.status>`
        or on the `_clusters </#app/clusters>`_ page of the BMLL site.

        This can be called without constructing a ComputeClient via `bmll.compute.create_cluster()`.
        In this case, a default ComputeClient instance is used.

        Note: You can add a default bootstrap script to your 'user' remote storage area
        that will be run when starting either a workspace or cluster.  The script must
        be named `default_bootstrap.sh` and stored in the base of your 'user' area.

        Note: the `node_type` parameter only applies to the worker ("core")
        nodes of the cluster. The master node is chosen to be a fixed type (an
        `m4.large` instance). The core nodes are `r4.16xlarge` instances. For more
        details on instance types, please see
        https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-supported-instance-types.html

        Args:
            name: str (optional)
                The name given to the cluster.
                The default is None, meaning created from username and timestamp.

            log_path: str (optional)
                Where to put the log files.
                The default is the cluster name.

            log_area: str (optional)
                The area to store the logs.
                Possible values are :class:`Area <bmll._clusters.core.Area>`
                The default is 'user'.

            node_type: str (optional)
                The type of processor provisioned on the nodes of the cluster.
                Possible values are :class:`NodeType <bmll._clusters.core.NodeType>`
                The default is 'cpu'.

            node_count: int (optional)
                The number of core nodes to create within the cluster.
                The default is 1

            cluster_config: :class:`ClusterConfig` (optional)
                Configuration settings for the cluster.
                The default is None, meaning the default :class:`ClusterConfig`

            terminate_on_idle: bool (optional)
                If True, the cluster will terminate as soon as it is idle. Note that if this option
                is set to True and no jobs are submitted to the cluster, then the cluster will
                immediately terminate.
                The default is True

            cluster_bootstraps: list(dict) or dict (optional)
                If not none, create a cluster with user specified bootstraps.  Each dictionary
                must specify the `path` of the bootstrap script.  The optional keys of the dictionary
                are `area`, `args`, and `name`, where `area` is the remote storage area the script is
                located (either 'user' or 'organisation'), `args` are a list of arguments to pass with
                the script, and `name` is the name given to the bootstrap for personal reference.

            tags: dict (optional)
                Optional tags to add to the cluster.  The dictionary `tags` must have string values
                for both keys and values.

            conda_env: str (optional)
                Optional conda_env to run the code in. It defaults to py311-stable, but possible options
                are {'py311-stable', 'py311-latest'}

            notification_email_map: dict (optional)
                Optional map of notification trigger event to a list of email address to contact in case
                of that event. Currently, the only accepted key is 'terminated_with_failures', i.e. the
                cluster has terminated and either one of the jobs or the cluster itself did not complete
                successfully. Defaults to None.

        Returns:
            :class:`Cluster <bmll._clusters.Cluster>`
                The object through which the cluster is managed.

        See Also:
            * :class:`ClusterConfig`
        """
        if conda_env.startswith("py38"):
            warnings.warn("Python 3.8 will soon be unsupported. "
                          f"Please use a Python 3.11-based Conda environment instead of {conda_env!r}. Note "
                          "that the default Conda environment will be py311-stable in future versions.",
                          DeprecationWarning)

        validate_env(conda_env)

        if spot_pricing:
            warnings.warn("Setting spot_pricing=True is deprecated and will be removed in a future release.",
                          DeprecationWarning)

        if log_area not in Area:
            raise InvalidArgumentError(log_area, 'log_area', Area)

        if node_type not in NodeType:
            raise InvalidArgumentError(node_type, 'node_type', NodeType)

        if node_count < 1:
            raise ValueError('node_count must be a positive int, not {!r}.'.format(node_count))

        if cluster_config is None:
            cluster_config = ClusterConfig()
        cluster_settings = cluster_config.cluster_settings

        if name is None:
            username = getattr(self._session, "_USERNAME", "(unavailable)")
            name = f"{username}-{pd.Timestamp.now().round('s')}"

        if log_path is None:
            log_path = name

        if tags is not None:
            if 'task_id' in tags.keys():
                raise ValueError('task_id is a BMLL reserved key name.')

        if cluster_bootstraps is not None and isinstance(cluster_bootstraps, dict):
            cluster_bootstraps = [cluster_bootstraps]

        if cluster_bootstraps is not None:
            validation.check_bootstrap_format(cluster_bootstraps)

        return Cluster(name=name, node_type=node_type, node_count=node_count,
                       log_area=log_area, log_path=log_path, cluster_settings=cluster_settings,
                       spot_pricing=spot_pricing, terminate_on_idle=terminate_on_idle,
                       cluster_bootstraps=cluster_bootstraps,
                       tags=tags, conda_env=conda_env, notification_email_map=notification_email_map
                       )

    @staticmethod
    @typechecked
    def get_clusters(
        active_only: bool = True, max_n_clusters: int = 10,
        include_organisation: bool = False, tags: Optional[dict] = None
    ):
        """
        Get a :class:`ClusterCollection <bmll._clusters.ClusterCollection>`
        of the max_n_clusters most recent _clusters.

        This can be called without constructing a ComputeClient via `bmll.compute.get_clusters()`.
        In this case, a default ComputeClient instance is used.

        Args:
            active_only: bool, default True
                Only show active _clusters.

            max_n_clusters: int, default 10
                Maximum number of most recent _clusters to retrieve.

            include_organisation: bool, optional
                If True will also return organisation level _clusters (for example Scheduling Service).
                The default is False.

        Returns:
            :class:`ClusterCollection <bmll._clusters.ClusterCollection>`
                Object representing a collection _clusters.

        See Also:
            * :class:`Cluster <bmll._clusters.Cluster>`
        """
        return _get_clusters(
            active_only=active_only, max_n_clusters=max_n_clusters,
            include_organisation=include_organisation, tags=tags,
        )

    @staticmethod
    @typechecked
    def get_tasks(active_only: bool = False, max_n_tasks: int = 10, trigger_filter: Optional[str] = None):
        """
        Get a :class:`TaskCollection <bmll._tasks.TaskCollection>`
        of the max_n_tasks most recently created/updated tasks.

        Args:
            * active_only: bool, default False
                Only show active Tasks.
            * max_n_tasks: int, default 10
                Maximum number of most recent Tasks to retrieve.
            * trigger_filter: str, default None
                if included, the output will only include those tasks that have
                been configured based on the particular trigger.
                Supported Values:
                    * l3

        Returns:
            :class:`TaskCollection <bmll._tasks.TaskCollection>`
                Object representing a collection of Tasks.

        See Also:
            * :class:`Task <bmll._tasks.Task>`
        """
        return _get_tasks(active_only=active_only,
                          max_n_tasks=max_n_tasks,
                          trigger_filter=trigger_filter)

    @typechecked
    def create_job(
        self,
        script_path: str,
        name: Optional[str] = None,
        instance_size: int = 16,
        max_runtime_hours: int = 1,
        script_area: Literal['user', 'organisation'] = 'user',
        log_path: str = 'job_run_logs',
        log_area: Literal['user', 'organisation'] = 'user',
        conda_env: str = 'py311-stable',
        visibility: Literal['private', 'public'] = 'private',
        bootstraps: Optional[List[Bootstrap]] = None,
        notifications: Optional[List[Notification]] = None,
        **script_parameters,
    ):
        """Create a job and return a :class:`Job <bmll._jobs.Job>`
        object to manage it.


        Args:
            script_path: str
                The path to the script to run.

            name: str (optional)
                The name given to the Job.
                The default is None, meaning created from username and timestamp.

            instance_size: int (optional)
                The instance memory size of the Job. THe possible options
                are {16, 32, 64, 128, 256, 384, 512, 768, 1024, 1536}
                The default is 16 (GB).

            max_runtime_hours: int (optional)
                The max runtime hours of the Job.
                The default is 1.

            script_area: str (optional)
                The area to store the script.
                Possible values are :class:`Area <bmll._core.Area>`
                The default is 'user'.

            log_path: str (optional)
                Where to put the log files.
                The default is 'job_run_logs'.

            log_area: str (optional)
                The area to store the logs.
                Possible values are :class:`Area <bmll._core.Area>`
                The default is 'user'.

            conda_env: str (optional)
                Optional conda_env to run the code in. The possible options
                are {'py311-stable', 'py311-latest'}
                The default is 'py311-stable'

            visibility: str (optional)
                If 'public' is given, the job is visible in org,
                if 'private' is given, the job is visible in owner only.
                The default is 'private'

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

                The default is None.

        Returns:
            :class:`Job <bmll._jobs.Job>`
                The object through which the Job is managed.
        """
        validate_env(conda_env)
        validate_instance_size(instance_size)
        validate_script_parameters(script_parameters)

        if name is None:
            username = getattr(self._session, "_USERNAME", "(unavailable)")
            name = f'{username}-{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'

        data = {
            'name': name,
            'instanceSize': instance_size,
            'maxRuntimeHours': max_runtime_hours,
            'scriptPath': script_path,
            'scriptArea': script_area,
            'logPath': log_path,
            'logArea': log_area,
            'condaEnv': conda_env,
            'visibility': visibility,
            'scriptParameters': script_parameters,
            'bootstraps': bootstraps if bootstraps else [],
            'notifications': notifications if notifications else [],
        }

        return Job(data)

    @staticmethod
    @typechecked
    def get_jobs(
        state: Literal['active', 'inactive', None] = None,
        visibility: Literal['public', 'private', None] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ):
        """
        Get a :class:`JobCollection <bmll._jobs.JobCollection>`
        of the max_n_jobs most recently created/updated jobs.

        Args:
            * state: string, default None
                The status of job, "active", "inactive".
            * visibility: string, default None
                Whether the job is visible in Org, "public", "private".
                public - the jobs are visible in Org
                private - your own private job
            * page: int, default None
            * page_size: int, default None

        Returns:
            :class:`JobCollection <bmll._jobs.JobCollection>`
                Object representing a collection of Job.

        See Also:
            * :class:`Job <bmll._jobs.Job>`
        """
        return _get_jobs(state=state,
                         visibility=visibility,
                         page=page,
                         page_size=page_size)

    @staticmethod
    @typechecked
    def get_job_runs(
        state: Literal['active', 'inactive', None] = None,
        visibility: Literal['public', 'private', None] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ):
        """
        Get a :class:`JobRunCollection <bmll._jobs.JobRunCollection>`
        of the max_n_job_runs most recently created/updated job runs.

        Args:
            * state: string, default None
                The status of job, "active", "inactive".
            * visibility: string, default None
                Whether the job is visible in Org, "public", "private".
                public - the jobs are visible in Org
                private - your own private job
            * page: int, default None
            * page_size: int, default None

        Returns:
            :class:`JobRunCollection <bmll._jobs.JobRunCollection>`
                Object representing a collection of JobRun.
        """
        return _get_job_runs(state=state,
                             visibility=visibility,
                             page=page,
                             page_size=page_size)

    @staticmethod
    @typechecked
    def get_job_run_parameters(job_run_id: str):
        """
        Get a dictionary of parameters

        Args:
            * job_run_id: str

        Returns:
           a dictionary of parameters
        """
        return _get_job_run_parameters(job_run_id)

    @staticmethod
    @typechecked
    def delete_job_run(job_run_id: str):
        """
        Deletes a job run

        Args:
            * job_run_id: str 

        """
        return _delete_job_run(job_run_id)


# we setup a default client and session so that users can still call
# bmll.compute.get_clusters() etc.

_DEFAULT_CLIENT = ComputeClient()
create_cluster = _DEFAULT_CLIENT.create_cluster
get_clusters = _DEFAULT_CLIENT.get_clusters
get_tasks = _DEFAULT_CLIENT.get_tasks
create_job = _DEFAULT_CLIENT.create_job
get_jobs = _DEFAULT_CLIENT.get_jobs
get_job_runs = _DEFAULT_CLIENT.get_job_runs
get_job_run_parameters = _DEFAULT_CLIENT.get_job_run_parameters
delete_job_run = _DEFAULT_CLIENT.delete_job_run
