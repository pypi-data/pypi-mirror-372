""" Package for _clusters functionality.
"""

import logging
import time
import typing
import uuid
from collections import defaultdict

import pandas as pd
from typeguard import typechecked

from bmll._clusters.exceptions import ClusterException
from bmll._clusters import core, validation
from bmll._clusters.constants import (
    CLUSTER_COLUMN_RESPONSE_DICT,
    CLUSTER_STARTING_STATUS,
    CLUSTER_READY_STATUS,
    CLUSTER_STOPPING_STATUS,
    CLUSTER_STOPPED_STATUS,
    JOB_COLUMN_RESPONSE_DICT,
    JOB_STARTING_STATUS,
    JOB_FAILED_STATUS,
    JOB_RUNNING_STATUS,
    JOB_STOPPED_STATUS,
)
from bmll._core.collections import BMLLCollection
from bmll._core.enum import Area


__all__ = (
    'ClusterConfig',
    'Cluster',
    'Job',
    'JobCollection',
    '_get_clusters',
)


_logger = logging.getLogger(__name__)

_STATUS_CACHE_DELAY = 20  # seconds
_TIMEZONE = 'utc'


class ClusterConfig:
    """Configuration for the environment that a spark job will run in.

    These parameters will be used to configure the spark environment. Unspecified
    parameters will be left as the cluster default value.  For further information
    see `Spark documentation \
    <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-configure.html>`_.

    In addition to the configurable variables described below,
    `yarn.nodemanager.vmem-check-enabled` and `yarn.nodemanager.pmem-check-enabled` are set
    to 'false'. This is to stop Yarn killing containers which exceed their preset limits.

    Args:
        driver_memory: str, default '1g'
            memory available to the driver process as a number followed by g for gigabytes,
            m for megabytes etc. e.g. '4g' for 4 gigabytes.

        driver_memory_overhead: str, default '5g'
            memory available to the drivers's non-Java processes (such as python) as a number followed
            by g for gigabytes, m for megabytes etc. e.g. '4g' for 4 gigabytes

        executor_memory: str, default '5g'
            memory available to the executor process as a number followed by g for gigabytes,
            m for megabytes etc. e.g. '4g' for 4 gigabytes

        executor_memory_pyspark: str, default '8g'
            memory available to the executor's pyspark process as a number followed by g for gigabytes,
            m for megabytes etc. e.g. '4g' for 4 gigabytes

        executor_memory_overhead: str, default None, meaning it is set to `executor_memory_pyspark`
            memory available to the executor's non-Java processes (such as python) as a number followed
            by g for gigabytes, m for megabytes etc. e.g. '4g' for 4 gigabytes

        parallelism: int, default 100
            Default number of partitions to use for RDDs.

        executor_cores: int, default 1
            Number of cores to use on each executor.

        maximize_resources: bool, default True
            If True then maximise a number of settings.

        max_result_size: int, default '0', meaning no limit on the result
            Limit of total size of serialized results of all partitions for each Spark action
            (e.g. collect) in bytes. Jobs will be aborted if the total size is above this limit.

        max_attempts: int, default 1
            The maximum number of attempts that will be made to submit the application.

        num_executors: int
            Number of executors to use.

    See Also:
        * :class:`bmll._clusters.Cluster`
        * :class:`bmll._clusters.Job`
    """

    @typechecked
    def __init__(self,
                 driver_memory: str = '1g', driver_memory_overhead: str = '5g',
                 executor_memory: str = '5g', executor_memory_pyspark: str = '8g',
                 executor_memory_overhead: typing.Optional[str] = None, parallelism: int = 100,
                 executor_cores: int = 1, maximize_resources: bool = True,
                 max_attempts: int = 1, max_result_size: str = '0',
                 num_executors: typing.Optional[int] = None
                 ):

        self._spark_params = []
        self._cluster_settings = {}

        # explicit pyspark arguments
        self.add_setting('spark-defaults', 'spark.driver.memory', driver_memory)
        self.add_job_setting('--driver-memory', driver_memory)

        self.add_setting('spark-defaults', 'spark.executor.memory', executor_memory)
        self.add_job_setting('--executor-memory', executor_memory)

        if num_executors is not None:
            self.add_setting('spark-defaults', 'spark.executor.instances', num_executors)
            self.add_job_setting('--num-executors', str(num_executors))

        self.add_setting('spark-defaults', 'spark.executor.cores', executor_cores)
        self.add_job_setting('--executor-cores', str(executor_cores))

        # '--conf' pyspark arguments
        self.add_setting('spark-defaults', 'spark.driver.memory.overhead', driver_memory_overhead)
        self.add_job_setting('--conf', f'spark.driver.memoryOverhead={driver_memory_overhead}')

        self.add_setting(
            'spark-defaults', 'spark.executor.pyspark.memory', executor_memory_pyspark
        )
        self.add_job_setting('--conf', f'spark.executor.pyspark.memory={executor_memory_pyspark}')

        if executor_memory_overhead is None:
            executor_memory_overhead = executor_memory_pyspark

        self.add_setting(
            'spark-defaults', 'spark.executor.memory.overhead', executor_memory_overhead
        )
        self.add_job_setting('--conf', f'spark.executor.memoryOverhead={executor_memory_overhead}')

        self.add_setting(
            'spark-defaults', 'spark.maximizeResourceAllocation.enabled', maximize_resources
        )
        self.add_job_setting(
            '--conf', f"spark.maximizeResourceAllocation.enabled={str(maximize_resources).lower()}"
        )

        self.add_setting('spark-defaults', 'spark.default.parallelism', parallelism)
        self.add_job_setting('--conf', f"spark.default.parallelism={parallelism}")

        self.add_setting('spark-defaults', 'spark.yarn.maxAppAttempts', max_attempts)
        self.add_job_setting('--conf', f'spark.yarn.maxAppAttempts={max_attempts}')

        self.add_setting('spark-defaults', 'spark.driver.maxResultSize', max_result_size)
        self.add_job_setting('--conf', f'spark.driver.maxResultSize={max_result_size}')

        self._add_non_configurable_defaults()

    def _add_non_configurable_defaults(self):
        self.add_setting('yarn-site', "yarn.nodemanager.vmem-check-enabled", "false")
        self.add_setting('yarn-site', "yarn.nodemanager.pmem-check-enabled", "false")

    @property
    def spark_params(self):
        """The Spark parameters"""
        return self._spark_params

    @property
    def cluster_settings(self):
        """The Spark settings"""
        return self._cluster_settings

    def add_setting(self, classification, key, value):
        """Add a static setting to be used during the cluster start-up.

        The classification, key and value are the classification and properties
        as documented on the `AWS Configuring Applications \
        <http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`_
        page, *e.g.*:

        ```conf.add_setting('yarn-site', 'yarn.scheduler.minimum-allocation-mb', 100)```

        Settings added with this function will only be used during cluster
        creation and will be ignored when passed to the
        :meth:`Cluster.submit <bmll._clusters.Cluster.submit>` method.

        Args:
            classification : str
                see `AWS Configuring Applications \
                <http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`_.
            key : str
                see `AWS Configuring Applications \
                <http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`_.
            value : str
                see `AWS Configuring Applications \
                <http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`_.

        Examples:
            Create a ClusterConfig object and add to the classification 'spark-defaults' the key
            'spark.executor.memoryOverhead' and value '384'.

            >>> from bmll import compute
            >>> clu_conf = compute.ClusterConfig()
            >>> clu_conf.add_setting('spark-defaults', 'spark.executor.memoryOverhead', '384')
        """
        if type(value) is bool:
            value = str(value).lower()

        self._cluster_settings.setdefault(classification, {})[key] = str(value)

    @typechecked
    def add_job_setting(self, param_name: str, value: str):
        """Add arbitrary setting to be used when submitting Spark jobs.

        Additional parameters will be used to configure the spark environment.
        For further information see `Spark documentation for submitting applications \
        <https://spark.apache.org/docs/latest/submitting-applications.html>`.

        Args:
            param_name: str
                Name of spark parameter.
            value: str
                Value of the spark parameter.

        Raises:
            TypeError
                raises if `param_name` or `value` are not strings.

            ValueError
                raises if `param_name="--py-files"`.  Python files to be submitted with spark jobs
                should be passed when calling :meth:`Cluster.submit <bmll.compute.Cluster.submit>`

        Examples:
            Create a ClusterConfig object and add the custom `--conf` setting to set the
            spark.executor.memoryOverhead to 384 (MiB).

            >>> from bmll import compute
            >>> clu_conf = compute.ClusterConfig()
            >>> clu_conf.spark_params
            ['--driver-memory', '1g',
            '--executor-memory', '5g',
            '--executor-cores', '1',
            '--conf', 'spark.driver.memoryOverhead=5g',
            '--conf', 'spark.executor.pyspark.memory=8g',
            '--conf', 'spark.executor.memoryOverhead=8g',
            '--conf', 'spark.maximizeResourceAllocation.enabled=true',
            '--conf', 'spark.default.parallelism=100',
            '--conf', 'spark.yarn.maxAppAttempts=1',
            '--conf', 'spark.driver.maxResultSize=0']

            >>> clu_conf.add_job_setting('--conf', 'spark.mock.parameter=384')
            >>> clu_conf.spark_params
            ['--driver-memory', '1g',
            '--executor-memory', '5g',
            '--executor-cores', '1',
            '--conf', 'spark.driver.memoryOverhead=5g',
            '--conf', 'spark.executor.pyspark.memory=8g',
            '--conf', 'spark.executor.memoryOverhead=8g',
            '--conf', 'spark.maximizeResourceAllocation.enabled=true',
            '--conf', 'spark.default.parallelism=100',
            '--conf', 'spark.yarn.maxAppAttempts=1',
            '--conf', 'spark.driver.maxResultSize=0',
            '--conf', 'spark.mock.parameter=384']
        """
        if param_name == '--py-files':
            raise ValueError('Distribution of python files is handled by '
                             'Cluster.submit(py_files=["...", ...]) and not '
                             'by the add_job_setting method with "--py-files".')

        self._spark_params.extend([param_name, value])


class Cluster:
    """Manager for a cluster.

    This object can be used to submit and manage jobs on the cluster, and to
    terminate the cluster. Object of this class object should not be
    instantiated directly. It should only be created from a call to
    :func:`create_cluster <bmll.compute.create_cluster>` or from a
    :class:`ClusterCollection <bmll._clusters.ClusterCollection>`.
    Clusters can be managed visually using the `clusters </clusters#://>`_ page
    on the BMLL site.

    See Also:
        * :func:`create_cluster <bmll.compute.create_cluster>`
        * :class:`ClusterCollection <bmll._clusters.ClusterCollection>`
    """
    __job_collection_class__ = None  # This is set after JobCollection is defined
    __job_class__ = None  # This is set after Job is defined

    def __init__(self, name=None, log_area=None, log_path=None,
                 node_type=None, node_count=None, cluster_settings=None,
                 spot_pricing=False, terminate_on_idle=None, response_data=None,
                 cluster_bootstraps=None, tags=None, conda_env='py311-stable',
                 notification_email_map=None):

        self._get_status = _timed_cache(_STATUS_CACHE_DELAY, self._fetch_status)

        if response_data is not None:
            self._set_from_response(response_data)
        else:
            # checking if a cluster limit is breached is done in the endpoint
            try:
                response = core.create_cluster(
                    name,
                    core.NodeType[node_type],
                    node_count=node_count,
                    log_path=log_path,
                    log_area=log_area,
                    cluster_config=cluster_settings,
                    terminate_on_idle=terminate_on_idle,
                    spot_pricing=spot_pricing,
                    cluster_bootstraps=cluster_bootstraps,
                    tags=tags,
                    conda_env=conda_env,
                    notification_email_map=notification_email_map,
                )
            except Exception as e:
                raise ClusterException(f"Failed to create cluster: {e}") from e

            # set attributes for new cluster
            self._active = True
            self._aws_node_type = core.NodeType[node_type]
            self._cluster_bootstraps = cluster_bootstraps
            self._id = response['id']
            self._job_count = 0
            self._jobs = []
            self._name = name
            self._node_count = node_count
            self._node_type = node_type.upper()
            self._ready_timestamp = pd.NaT
            self._started_timestamp = _parse_server_timestamp(response['creation_req_timestamp'])
            self._stopped_timestamp = pd.NaT
            self._status = CLUSTER_STARTING_STATUS
            self._tags = tags
            self._user = response['username']
            self._conda_env = conda_env
            self._notification_email_map = notification_email_map

            _logger.debug('Created new cluster (%s).', self.id)

    @property
    def active(self):
        """bool: Whether the cluster is still active."""
        return self._get_active(self.status)

    @property
    def aws_node_type(self):
        """str: AWS name for type of instances in cluster."""
        return self._aws_node_type

    @property
    def cluster_bootstraps(self):
        """list: Bootstraps submitted to the cluster."""
        return self._cluster_bootstraps

    @property
    def id(self):
        """str: Unique identifier of the cluster."""
        return self._id

    @property
    def job_count(self):
        """int: Number of jobs submitted to cluster."""
        return self.jobs.size

    @property
    def jobs(self):
        """:class:`JobCollection`: Jobs submitted to cluster."""
        try:
            results = core.get_jobs(self.id)
        except Exception as e:
            raise ClusterException('Failed to get jobs: {}'.format(e))

        return self.__job_collection_class__(self.id, results)

    @property
    def name(self):
        """str: Cluster's name."""
        return self._name

    @property
    def node_count(self):
        """int: Number of nodes in a cluster."""
        return self._node_count

    @property
    def node_type(self):
        """str: Type of instances in cluster."""
        return self._node_type

    @property
    def ready_timestamp(self):
        """pd.Timestamp or pd.NaT: When cluster was ready to use."""
        if pd.isna(self._ready_timestamp):
            try:
                self._ready_timestamp = _parse_server_timestamp(
                    self._get_status()[CLUSTER_COLUMN_RESPONSE_DICT['Ready']])
            except Exception:
                raise ClusterException("Property 'ready_timestamp' not available.")

        return self._ready_timestamp

    @property
    def started_timestamp(self):
        """pd.Timestamp: When cluster was created."""
        return self._started_timestamp

    @property
    def status(self):
        """str: Status of the cluster. The status may be cached for a short time."""
        if self._status not in CLUSTER_STOPPED_STATUS:
            try:
                self._status = _format_status(self._get_status()['cluster_state'])
            except Exception:
                raise ClusterException("Property 'status' not available.")

        return self._status

    @property
    def stopped_timestamp(self):
        """pd.Timestamp: When cluster was terminated."""
        if pd.isna(self._stopped_timestamp):
            try:
                self._stopped_timestamp = _parse_server_timestamp(
                    self._get_status()[CLUSTER_COLUMN_RESPONSE_DICT['Stopped']])
            except Exception:
                raise ClusterException("Property 'stopped_timestamp' not available.")

        return self._stopped_timestamp

    @property
    def tags(self):
        return self._tags

    @property
    def total_running_time(self):
        """pd.Timedelta: Length of time for which cluster has run/ran."""
        return _get_duration(self.started_timestamp, self.stopped_timestamp)

    @property
    def user(self):
        """str: User who created cluster."""
        return self._user

    @property
    def conda_env(self):
        """str: The conda environment used by the cluster."""
        return self._conda_env

    @property
    def notification_email_map(self):
        """dict: a map of notification triggers to email addresses to notify."""
        return self._notification_email_map

    def __repr__(self):
        return '{}(id={}, active={}, started={})'.format(
            self.__class__.__name__, self.id, self.active, self.started_timestamp)

    def describe(self):
        """Get a DataFrame containing information about the cluster.

        This can be used to obtain the data otherwise available in the
        attributes of the :class:`Cluster` in one dataframe.

        Returns:
            pandas.DataFrame
                DataFrame containing the following columns:
                'ID', 'Name', 'Status', 'Total running time', 'Started', 'Ready',
                'Stopped', 'Node type', 'AWS node type', 'Node count', 'User', 'Job count', 'Active'.
        """
        return _describe(self, CLUSTER_COLUMN_RESPONSE_DICT)

    @typechecked
    def distcp(self,
               s3_path: str,
               cluster_path: str,
               is_folder: bool = False,
               copy_from_cluster: bool = False,
               area: str = Area.USER,
               distcp_params: typing.Optional[list] = None,
               failure_action: str = core.JobFailureAction.CONTINUE,
               name: str = 'dist-cp'
               ):
        """Submit a dist-cp job to be run on a cluster, a tool used to copy data between
        s3 and a clusters hdfs file system.  dist-cp (distributed copy) is an
        Apache Hadoop tool used for large inter/intra-cluster copying. See
        `here <https://hadoop.apache.org/docs/current/hadoop-distcp/DistCp.html>` for
        technical details.  `Cluster.distcp` uses the AWS implementation s3-dist-cp, for
        further details see
        `here <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/UsingEMR_s3distcp.html>`

        The `distcp` method adds `hdfs:///` as a prefix to `cluster_path` before submitting the
        dist-cp job to the cluster.  Users are not permitted to write files directly to the root
        directory but can save files in a user defined directory contained in
        the root directory.  The user defined directory does not need to be created
        before submitting a dist-cp job.

        Args:
            s3_path: str
                The path to the directory to be copied from / to.
                This may be relative to the script_area parameter or a full S3 path.
                Note: This is assumed to exist.
            cluster_path: str
                The hdfs directory used by the cluster master and worker nodes.
            is_folder: bool, optional
                if false `distcp` will handle the path of origin (`s3_path` or `cluster_path`)
                as an individual file, and if true `distcp` with handle the path as a folder.
            copy_from_cluster: bool
                Defines the direction of the copy.
            area: str, optional
                The area from which to read the s3_path.
                Possible values are :class:`Area <bmll._core.enum.Area>`
                The default is 'user'.
            distcp_params: list
                List of strings of additional options that may be fast.  See
                `S3DistCp <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/UsingEMR_s3distcp.html>`
                for further details.
            failure_action: str (optional)
                The action to take if a job fails.
                Possible values are :class:`JobFailureAction <bmll._clusters.core.JobFailureAction>`  # noqa
                The default is 'continue'.
            name: str (optional)
                A user defined name for the dist-cp job.

        Returns:
            :class:`Job <bmll._clusters.Job>` object
                Object with which to manage the dist-cp job submitted.

        Examples:
            The examples below demonstrates how to make a copy files and folders from s3 to a cluster hdfs
            file system and also copying from a cluster to s3.  First create a cluster,

            >>> from bmll import compute  # doctest: +SKIP
            >>> clu = compute.create_cluster()  # doctest: +SKIP

            Copy a file from s3 to hdfs,

            >>> clu.distcp(s3_path='/test/file.txt', cluster_path='/clu-file-dir')  # doctest: +SKIP

            Copy a folder from s3 to hdfs,

            >>> clu.distcp(s3_path='/test/', cluster_path='/clu-dir', is_folder=True)  # doctest: +SKIP

            Copy a file from hdfs to s3,

            >>> clu.distcp(s3_path='/test/', cluster_path='/clu-dir/file.txt', copy_from_cluster=True)  # doctest: +SKIP

            Copy a folder from hdfs to s3,

            >>> clu.distcp(s3_path='/test/', cluster_path='/clu-dir/', copy_from_cluster=True, is_folder=True)  # doctest: +SKIP

        """
        self._assert_alive()
        validation.argument_check(area, 'area', Area)
        validation.argument_check(failure_action, 'failure_action', core.JobFailureAction)

        if distcp_params is None:
            distcp_params = []

        # For copying single files using s3-dist-cp, we need to pass a regex pattern that
        # captures the file using --srcPattern.  Therefore it should not be contained in
        # distcp_params passed by users.
        if not is_folder and [item for item in distcp_params if '--srcPattern' in item]:
            raise ValueError('--srcPattern cannot be specified in distcp_params when copying '
                             'single files')

        if not copy_from_cluster:
            # Note s3_path is assumed to exist
            if cluster_path == '':
                raise ClusterException('Cannot copy files to the root directory of hdfs, '
                                       'cluster_path must specify a directory.')

        if copy_from_cluster:
            src_path = cluster_path
            src_area = 'hdfs'
            dst_path = s3_path
            dst_area = area
        else:
            src_path = s3_path
            src_area = area
            dst_path = cluster_path
            dst_area = 'hdfs'

        try:
            job_id = core.submit_job(cluster_id=self.id,
                                     name=name,
                                     job_type='distcp',
                                     script='s3-dist-cp',
                                     area='local',
                                     parameters={
                                            'src': [src_area, src_path],
                                            'dest': [dst_area, dst_path],
                                            'extra': distcp_params,
                                            'is_folder': is_folder,
                                        },
                                     failure_action=core.JobFailureAction[
                                            failure_action.upper()
                                        ].value)
        except Exception as e:
            raise ClusterException(f"Failed to run {name}: {e}")

        # Confirm distcp submission.
        _logger.debug('Submitted "%s" with parameters %s to cluster %s', name, distcp_params, self.id)

        job = self.__job_class__(self.id, result={'id': job_id, 'name': 'dist-cp', 'state': JOB_STARTING_STATUS})
        self._jobs.append(job)

        return job

    def _assert_alive(self):
        """ Check that the cluster is alive, if it is not then raise an exception.

        Raises:
            ClusterException
                If the cluster has been stopped.
        """
        if self.status in CLUSTER_STOPPED_STATUS:
            raise ClusterException('Cannot submit jobs to an inactive cluster.')

    @typechecked
    def submit(self, script_path: str, name: typing.Optional[str] = None, script_area: str = Area.USER,
               failure_action: str = core.JobFailureAction.CONTINUE,
               cluster_config: typing.Optional[ClusterConfig] = None,
               job_type: str = core.JobType.SPARK,
               py_files: list = [],
               **job_parameters
               ):
        """Submit a job or script to be run on the cluster.

        To wait for the job to finish running before returning, use:
        :code:`job = cluster.submit(...).wait()`.

        Args:
            script_path: str
                The path to the script to run.
                This may be relative to the script_area parameter or a full S3 path.
                Note: This is assumed to exist, and no checks are done.

            name: str, optional
                A user defined name for the job.
                The default is the basename of the algorithm script.

            script_area: str, optional
                The area from which to read the script.
                Possible values are :class:`Area <bmll._core.enum.Area>`
                The default is 'user'.

            failure_action: str, optional
                The action to take if a job fails.
                Possible values are :class:`JobFailureAction <bmll._clusters.core.JobFailureAction>`  # noqa
                The default is 'continue'.

            cluster_config: :class:`bmll.compute.ClusterConfig`, optional
                Configuration settings for the cluster. (only used if job_type = 'spark')
                The default is None, meaning the default :class:`ClusterConfig`.

            job_type: str, optional
                The type of job to be submitted to the cluster.
                Possible values are :class:`JobType <bmll._clusters.core.JobType>`
                The default is 'spark'.

            py_files:
                List of python files to be distributed with your spark job.
            job_parameters:
                Keyword arguments for script.
                These parameters will be passed to the script.

                If job_type = 'spark':
                    These parameters will be serialised to json and consumed in the script by calling :func:`parameters <bmll2._internals.api.cluster.utils.parameters>`  # noqa
                Else:
                    These parameters will be passed into the script as command like args. (None values will be ignored).  # noqa


        Examples:
            >>> from bmll import compute  # doctest: +SKIP
            >>> cluster = compute.create_cluster()  # doctest: +SKIP
            >>> cluster.submit('my_spark_script.py')  # doctest: +SKIP
            Submitted script 'my_spark_script.py' with parameters {} to cluster '<CLUSTER_ID>'.
            Job(id=<JOB-1>, status=Pending)

            >>> cluster.submit('my_shell_script.sh', job_type='shell')  # doctest: +SKIP
            Submitted script 'my_shell_script.sh' with parameters {} to cluster '<CLUSTER_ID>'.
            Job(id=<JOB-2>, status=Pending)

            >>> files = ['file_one.py', 'file_two.py']  # doctest: +SKIP
            >>> cluster.submit('my_python_script.py', py_files=files)  # doctest: +SKIP
            Submitted script 'my_python_script.py' with parameters {} to cluster '<CLUSTER_ID>'.

        Returns:
            :class:`Job <bmll._clusters.Job>` object
                Object with which to manage the job submitted.

        See Also:
            * :class:`ClusterConfig <bmll.compute.ClusterConfig>`
        """
        self._assert_alive()
        validation.argument_check(script_area, 'script_area', Area)
        validation.argument_check(failure_action, 'failure_action', core.JobFailureAction)
        validation.argument_check(job_type, 'job_type', core.JobType)

        spark_params = cluster_config.spark_params if cluster_config else []

        if len(py_files) > 0 and job_type != core.JobType.SPARK:
            raise ClusterException("Non-spark jobs cannot be submitted with py_files.")

        if job_type == core.JobType.SPARK:
            parameters = {
                'spark_params': spark_params,
                'py_files': py_files
            }
        else:
            parameters = {}

        name = name or uuid.uuid4().hex
        # store job parameters in a file as these could be large deps
        bmll_config_path = core.upload_bmll_config(name, job_parameters)

        # payload
        payload = dict(
            name=name,
            script=script_path,
            area=Area[script_area].value,
            parameters_area='parameters',
            failure_action=core.JobFailureAction[
                failure_action.upper()
            ].value,
            job_type=core.JobType[job_type].value,
            parameters=parameters,
            bmll_config_path=bmll_config_path,
        )

        try:
            job_id = core.submit_job(self.id, **payload)
        except Exception as e:
            raise ClusterException("Failed to run jobs: %s" % e) from e

        # confirm job submission
        _logger.debug(
            'Submitted script %r with config path %r to cluster %r.', script_path, bmll_config_path, self.id,
        )

        # create job object using known result and add to _jobs
        job = self.__job_class__(self.id, result={'id': job_id, 'name': name, 'state': JOB_STARTING_STATUS})
        self._jobs.append(job)

        return job

    def terminate(self):
        """Send a termination request to stop the cluster.

        Running _clusters incur billing. After a cluster has been provisioned using
        :meth:`create_cluster <bmll.compute.create_cluster>`, it will usually terminate
        itself if no jobs are running (if the :code:`terminate_on_idle` argument is
        set to True).  This command send an explicit request to the cluster to stop.
        """
        try:
            core.terminate_cluster(self.id)
        except Exception as e:
            raise ClusterException("Failed to terminate cluster: %s" % e) from e

    def wait(self):
        """Pause the execution of code until the cluster is provisioned.

        This pauses until the cluster status is one of 'Waiting', 'Terminated',
        'Terminating', or 'Terminated with errors'.

        After :meth:`create_cluster <bmll.compute.create_cluster>` it can take time to
        provision the cluster.  This command can be used to pause
        execution until the cluster is ready.

        Returns:
            :class:`bmll.clusters.Cluster`
        """
        _wait(self)

        return self

    def _fetch_status(self):
        """Get the cluster status dict and return it."""
        try:
            return core.get_cluster(self.id)
        except Exception as e:
            raise ClusterException("Failed to get cluster status information: %s" % e) from e

    @staticmethod
    def _get_active(status):
        """bool: Is the cluster currently active?"""
        return _format_status(status) not in CLUSTER_STOPPED_STATUS + (CLUSTER_STOPPING_STATUS,)

    def _set_from_response(self, response):
        """
        Set :class:`bmll._clusters.Cluster` attributes using the response from
        :meth:`bmll.compute.get_clusters`.

        The response contains the following:
        {
          'cluster_state': str,
          'cluster_type': str,
          'core_node_count': int,
          'core_node_type': str,
          'creation_timestamp': str,
          'id': str,
          'job_count': int,
          'log_uri': str,
          'master_node_type': str,
          'master_public_dns_name': str,
          'name': str,
          'notification_email_map': dict,
          'ready_timestamp': str,
          'status_change_reason_code': str,
          'status_change_reason_text': str,
          'terminated_with_errors': bool,
          'termination_timestamp': str,
          'user': str,
        }.
        """
        self._active = self._get_active(response['cluster_state'])
        self._aws_node_type = response['core_node_type']
        self._id = response['id']
        # Job response not contained in cluster response
        # expensive to query separately to get jobs for each cluster
        # set as [] for now and only get actual value when explicitly requested
        self._jobs = []
        self._job_count = response['job_count']
        self._name = response['name']
        self._node_count = response['core_node_count']
        self._node_type = response['cluster_type']
        self._ready_timestamp = _parse_server_timestamp(response['ready_timestamp'])
        self._started_timestamp = _parse_server_timestamp(response['creation_timestamp'])
        self._status = _format_status(response['cluster_state'])
        self._stopped_timestamp = _parse_server_timestamp(response['termination_timestamp'])
        self._user = response['user']
        self._tags = response.get('tags')
        self._conda_env = response.get('conda_env')
        self._notification_email_map = response.get('notification_email_map')


class Job:
    """Represents a job running on a :class:`Cluster`.

    This object gives access to properties of the job on a cluster.  It can be used to
    check job status and running times.
    This object should not be created directly. It should only be created from a call to
    :meth:`Cluster.submit` or contained within :class:`ClusterCollection`.
    """

    def __init__(self, cluster_id, result):
        """Encapsulate a job running on a cluster.

        This object should not be instantiated directly.
        It should only be created from a call to
        :meth:`bmll._clusters.Cluster.submit` or contained within
        :class:`bmll._clusters.ClusterCollection`.

        Args:
            cluster_id: str
                Unique identifier for the cluster to which the jobs belong.
            result: dict
                Response from `bmll._clusters.core.get_jobs(...)`:

                .. code-block:: python

                     {
                        'end_date_time': str,
                        'id': str,
                        'jar': str,
                        'name': str,
                        'start_date_time': str,
                        'state': str
                    }.
        """
        self._get_status = _timed_cache(_STATUS_CACHE_DELAY, self._fetch_status)

        self._active = self._get_active(result['state'])
        self._cluster_id = cluster_id
        self._id = result['id']
        self._name = result['name']
        # these two are not present in non-API obtained result used when job initially submitted
        self._started_timestamp = _parse_server_timestamp(result.get('start_date_time'))
        self._stopped_timestamp = _parse_server_timestamp(result.get('end_date_time'))
        self._status = _format_status(result['state'])

    @property
    def active(self):
        """bool: Whether the job is still active."""
        return self._get_active(self.status)

    @property
    def cluster_id(self):
        """str: Unique identifier of the cluster."""
        return self._cluster_id

    @property
    def id(self):
        """str: Unique identifier of the job."""
        return self._id

    @property
    def name(self):
        """str: Name of job."""
        return self._name

    @property
    def started_timestamp(self):
        """pd.Timestamp or pd.NaT: When the job was started."""
        if pd.isna(self._started_timestamp):
            try:
                self._started_timestamp = \
                    _parse_server_timestamp(self._get_status()['start_date_time'])
            except Exception:
                raise ClusterException("Property 'started_timestamp' not available.")

        return self._started_timestamp

    @property
    def stopped_timestamp(self):
        """pd.Timestamp or pd.NaT: When the job was stopped."""
        if pd.isna(self._stopped_timestamp):
            try:
                self._stopped_timestamp = \
                    _parse_server_timestamp(self._get_status()['end_date_time'])
            except Exception:
                raise ClusterException("Property 'stopped_timestamp' not available.")

        return self._stopped_timestamp

    @property
    def status(self):
        """str: Running state of job. The status may be cached for a short time.
        """
        if self._status not in JOB_FAILED_STATUS + JOB_STOPPED_STATUS:
            try:
                self._status = _format_status(self._get_status()['state'])
            except Exception:
                raise ClusterException("Property 'status' not available.")

        return self._status

    @property
    def total_running_time(self):
        """pd.Timedelta or pd.NaT: Length of time for which the job was running."""
        return _get_duration(self.started_timestamp, self.stopped_timestamp)

    def __repr__(self):
        return "{}(id={}, status={})".format(self.__class__.__name__, self._id, self.status)

    def describe(self):
        """Get a DataFrame containing information about the cluster.

        This can be used to obtain the data otherwise available in the
        attributes of the :class:`Job` in one dataframe.

        Returns:
            pd.DataFrame
                DataFrame containing the following columns:
                'ID', 'Name', 'Status', 'Total running time', 'Started', 'Stopped', 'Active'.
        """
        return _describe(self, JOB_COLUMN_RESPONSE_DICT)

    def wait(self):
        """Pauses execution until the job has finished.

        Running a job on a cluster does not by default pause the notebook.  This
        method can be used to pause excecution if the reuslts of the job are required
        before continuing.  It returns only when Job has status 'Cancelled',
        'Completed' 'Interrupted' or 'Failed'.  It can be chained with
        :meth:`Cluster.submit`.

        Returns:
            :class:`Job`
                The same job object

        See Also:
            :meth:`Cluster.submit`
        """
        _wait(self)

        return self

    def _fetch_status(self):
        """Get the job status dict and return it"""
        statuses = core.get_jobs(self._cluster_id)
        for status in statuses:
            if status['id'] == self._id:
                return status

    @staticmethod
    def _get_active(status):
        """bool: Is the job currently active?"""
        return _format_status(status) == JOB_RUNNING_STATUS


class ClusterCollection(BMLLCollection):
    """Container for :class:`Cluster <bmll._clusters.Cluster>` objects.

    This container allows description of all clusters in the collection (typically
    all active clusters returned :meth:`get_clusters <bmll.get_clusters>`) as
    well as a way to terminate all clusters.  Operations such
    as iteration and use of the :code:`in` keyword are also implemented.
    These objects are created by a call to :meth:`bmll.compute.get_clusters`
    and should not be instantiated directly.

    See Also:
        * :class:`bmll._clusters.Cluster`
    """
    __cluster_class__ = Cluster

    def __init__(self, results):
        super().__init__([self.__cluster_class__(response_data=cluster_dict) for cluster_dict in results])

    def describe(self):
        """Get a DataFrame containing information about the cluster.

        This can be used to obtain the data otherwise available in the
        attributes of the :class:`Cluster` in one dataframe.

        Returns:
            pandas.DataFrame
                DataFrame containing the following columns:
                'ID', 'Name', 'Status', 'Total running time', 'Started', 'Ready',
                'Stopped', 'Node type', 'Node count', 'User', 'Job count', 'Active'.
        """
        # bulk query to get data for all _clusters
        # (even though the cluster collection may only contain alive ones)
        state = core.ClusterState.ALL
        try:
            results = core.get_clusters(state)
        except Exception as ex:
            raise ClusterException('Failed to get clusters: {}'.format(ex)) from ex

        filtered_results = ([cluster_dict for cluster_dict in results
                             if cluster_dict['id'] in self._ids])

        data_dict = defaultdict(list)
        for response_data in filtered_results:
            for col, response_key in CLUSTER_COLUMN_RESPONSE_DICT.items():
                if response_key is not None:
                    data_dict[col].append(response_data[response_key])

        df = pd.DataFrame(data_dict, columns=CLUSTER_COLUMN_RESPONSE_DICT.keys())

        if not df.empty:
            # ignore if DataFrame is empty (or we get a ValueError)
            for time_col in ('Started', 'Stopped', 'Ready'):
                df[time_col] = df[time_col].apply(_parse_server_timestamp)
            df['Active'] = df.Status.apply(self.__cluster_class__._get_active)
            df['Status'] = df.Status.apply(_format_status)
            df['Total running time'] = df.apply(
                lambda row: _get_duration(row['Started'], row['Stopped']), axis=1)

        return df

    def terminate(self):
        """Terminate all _clusters in a :class:`ClusterCollection`.

        Applies :meth:`Cluster.terminate` to all the _clusters in the collection.
        This can be useful to ensure there are no remaining active _clusters
        after calling :func:`get_clusters <bmll.compute.get_clusters>`.

        See Also:
            :meth:`Cluster.terminate`
        """
        for cluster in self._values:
            if cluster.active:
                cluster.terminate()
            else:
                # as _values is in creation order and only one cluster active at once
                break


@typechecked
def _get_clusters(
        active_only: bool = True, max_n_clusters: int = 10,
        include_organisation: bool = False, tags: typing.Optional[dict] = None, *,
        cluster_collection_class: typing.Type[ClusterCollection] = ClusterCollection,
):
    """ Helper function for getting a ClusterCollection.
    """
    if active_only:
        state = core.ClusterState.ACTIVE
    else:
        state = core.ClusterState.ALL

    try:
        results = core.get_clusters(state, include_org=include_organisation, tags=tags)
    except Exception as ex:
        raise ClusterException('Failed to get clusters: {}'.format(ex)) from ex

    return cluster_collection_class(results[:max_n_clusters])


class JobCollection(BMLLCollection):
    """Container for :class:`Cluster <bmll._clusters.Job>` objects.

    This container allows description of all jobs in the collection (typically
    all jobs submitted to a cluster, from the :attr:`Cluster.jobs` attribute)
    .  Operations such
    as iteration and use of the :code:`in` keyword are also implemented.
    These objects are obtained from the attribute :attr:`Cluster.jobs`
    and should not be instantiated directly.

    See Also:
        * :class:`bmll._clusters.Cluster`
        * :class:`bmll._clusters.Job`
    """
    __job_class__ = Job

    def __init__(self, cluster_id, results):
        super().__init__([self.__job_class__(cluster_id, job_dict) for job_dict in results])
        self._cluster_id = cluster_id

    @property
    def cluster_id(self):
        """str: Unique identifier of the cluster."""
        return self._cluster_id

    def describe(self):
        """Get a DataFrame containing information about the cluster.

        This can be used to obtain the data otherwise available in the
        attributes of the :class:`Job` in one dataframe.

        Returns:
            pandas.DataFrame
                DataFrame containing the following columns:
                'ID', 'Name', 'Status', 'Total running time', 'Started', 'Stopped', 'Active'.
        """
        results = core.get_jobs(self._cluster_id)
        data_dict = defaultdict(list)
        for response_data in results:
            for col, response_key in JOB_COLUMN_RESPONSE_DICT.items():
                if response_key is not None:
                    data_dict[col].append(response_data[response_key])

        df = pd.DataFrame(data_dict, columns=JOB_COLUMN_RESPONSE_DICT.keys())

        if not df.empty:
            # ignore if DataFrame is empty (or we get a ValueError)
            for time_col in ('Started', 'Stopped'):
                df[time_col] = df[time_col].apply(_parse_server_timestamp)
            df['Active'] = df.Status.apply(self.__job_class__._get_active)
            df['Status'] = df.Status.apply(_format_status)
            df['Total running time'] = df.apply(
                lambda row: _get_duration(row['Started'], row['Stopped']), axis=1)

        return df


# Register the bmll SDK's JobCollection and Job classes on the Custer class
# This has to be done after these classes are defined
Cluster.__job_collection_class__ = JobCollection
Cluster.__job_class__ = Job


def _describe(obj, response_col_dict):
    """DataFrame containing information about the Cluster or Job object.

    Parameters
    ----------
    obj: :class:`bmll._clusters.Cluster` or
    :class:`bmll._clusters.Job`
        Object for which data will be returned.
    response_col_dict: dict
        Mapping between keys in response and DataFrame column names
        The order of the keys defines the column order.

    Returns
    -------
    pandas.DataFrame
    """
    response_data = obj._get_status()

    data_dict = {col: response_data[response_key] for col, response_key
                 in response_col_dict.items() if response_key is not None}

    # round any timestamps
    data_dict = {col: _parse_server_timestamp(val)
                 if col in ('Started', 'Stopped', 'Ready') else val
                 for col, val in data_dict.items()}

    # add derived variables
    data_dict['Active'] = obj._get_active(data_dict['Status'])
    data_dict['Status'] = _format_status(data_dict['Status'])
    data_dict['Total running time'] = _get_duration(data_dict['Started'],
                                                    data_dict['Stopped'])

    return pd.DataFrame([data_dict], columns=response_col_dict.keys())


def _format_status(status):
    """str: Translate statuses to human readable form"""
    if status == 'CANCEL_PENDING':
        return 'Removed from queue'
    return status.replace('_', ' ').capitalize()


def _get_duration(start, end):
    """Get the time interval between two timestamps.

    Parameters
    ----------
    start: pd.Timestamp
          When to start the stopwatch. If pd.NaT, then the function returns pd.NaT.

    end: pd.Timestamp or pd.NaT
         When to end the stopwatch. If pd.NaT, the current time is used.

    Returns
    -------
    pd.Timedelta or pd.NaT
        Return type depends if start is pd.Timestamp or pd.NaT.
    """
    start = _check_timestamp_type(start, pd.NaT)
    end = _check_timestamp_type(end, pd.Timestamp.now(_TIMEZONE))

    return (end.tz_localize(None) - start.tz_localize(None)).round('s')


def _check_timestamp_type(ts, return_val_if_bad):
    """Check timestamp type, returning return_val_if_bad or raising if fails."""
    if not isinstance(ts, pd.Timestamp):
        if pd.isna(ts):
            return return_val_if_bad
        else:
            raise TypeError('Timestamp unexpected type. Should be pd.Timestamp or pd.NaT.')
    else:
        return ts


def _parse_server_timestamp(ts_str):
    """Validate the timestamp returned by the server and format.

    Formatting sets resolution to seconds and removes time-zone information.

    Parameters
    ----------
    ts_str: str or None
        value received in response.

    Returns
    -------
    pd.Timestamp

    Raises
    ------
    ClusterError
        If the str cannot be converted to a pd.Timestamp.
    """
    if ts_str is None:
        ts = pd.NaT
    else:
        try:
            ts = validation.validate_datetime(ts_str)
        except Exception as ex:
            raise ClusterException('An internal error occurred while getting the timestamp. '
                                   'Please contact BMLL support if it continues.') from ex

    return ts.round('s').tz_localize(None)


def _timed_cache(cache_delay, function):
    """Wrap a function in a time limited cache - if this is called within time_limit
    of the last real call then return the cached value instead of calling function
    N.B. this ignores the parameters passed when determining whether to call function."""
    last_update = 0
    result = None

    def wrapped_function(*args, **kwargs):
        nonlocal last_update, result
        now = time.monotonic()
        if now - cache_delay > last_update:
            result = function(*args, **kwargs)
            last_update = time.monotonic()
        return result

    return wrapped_function


def _wait(obj):
    """Wait for cluster or job to finish.

    If a Cluster, return only when status 'Waiting', 'Terminating',
    'Terminated' or 'Terminated with errors'.
    If a Job, return only when status 'Cancelled', 'Completed', 'Failed' or 'Interrupted'.

    Parameters
    ----------
    obj: :class:`bmll._clusters.Cluster` or
    :class:`bmll._clusters.Job`
    """
    update_time = 2
    start_time = pd.Timestamp.now(_TIMEZONE)
    time_passed = pd.Timedelta(0, 's')

    done_states = (JOB_STOPPED_STATUS + JOB_FAILED_STATUS + (CLUSTER_READY_STATUS,)
                   + CLUSTER_STOPPED_STATUS + (CLUSTER_STOPPING_STATUS,))

    while obj.status not in done_states:
        _logger.debug('Currently in state: %s. Waited for %s seconds.', obj.status, time_passed.seconds)
        time.sleep(update_time)
        time_passed = pd.Timestamp.now(_TIMEZONE) - start_time

    _logger.debug('Finished waiting.')
