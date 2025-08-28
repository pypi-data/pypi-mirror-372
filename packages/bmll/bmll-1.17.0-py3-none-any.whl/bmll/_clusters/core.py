""" Low level functions for managing clusters.
"""
import logging

from bmll import _rest
from bmll._core.enum import StrEnum
from bmll._utils import validate_env


__all__ = (
    'get_clusters', 'get_cluster', 'get_jobs', 'terminate_cluster',
    'create_cluster', 'submit_job',
    'upload_bmll_config',
    'ClusterState', 'JobFailureAction', 'NodeType', 'JobType',
)


class ClusterState(StrEnum):
    """ Enum for the state of the clusters to return from get_clusters.
    """
    ALL = 'all'
    """ALL: clusters in any state e.g. running, terminated, bootstrapping, waiting"""
    ACTIVE = 'active'
    """ACTIVE: clusters in an active state e.g. running, bootstrapping, waiting"""
    INACTIVE = 'inactive'
    """INACTIVE: clusters in an inactive state e.g. terminating, terminated"""
    FAILED = 'failed'
    """FAILED: clusters in a failed state e.g. terminated_with_errors"""


class JobFailureAction(StrEnum):
    """
    The action to take if a job fails. If a job fails:
        'cancel_and_wait' will cancel all other jobs but allow the cluster to continue running.
        'continue' will allow all other jobs and the cluster to continue running.
        'terminate_cluster' will cancel all other jobs and shut down the cluster.
    """
    CONTINUE_JOBS = 'continue_jobs'  # backwards compatibility
    CONTINUE = 'continue'
    TERMINATE = "terminate"
    CANCEL = "cancel"


class NodeType(StrEnum):
    """The NodeType of the Cluster."""
    # keep lowercase options for backwards compatibility.
    CPU = cpu = "cpu"


class JobType(StrEnum):
    """Job Types which can be submitted to a cluster."""
    SPARK = spark = "spark"
    SHELL = shell = "shell"
    MPIRUN = mpirun = "mpirun"


_AWS_JOB_FAILURE_ACTIONS = {
    JobFailureAction.CONTINUE_JOBS: 'CONTINUE',
    JobFailureAction.CONTINUE: 'CONTINUE',
    JobFailureAction.TERMINATE: "TERMINATE_CLUSTER",
    JobFailureAction.CANCEL: "CANCEL_AND_WAIT"
}

_AVAILABLE_ENVS = {'py311-stable', 'py311-latest'}


logger = logging.getLogger(__name__)


SESSION = _rest.DEFAULT_SESSION


def get_clusters(state=ClusterState.ACTIVE, include_org=False, tags=None):
    """ Return a list of the users clusters.  By default only return those that
    are active (running or starting).

    Args:
        state: ClusterState
            which clusters to return

        include_org: bool, optional
            If true will also return organisation level clusters.
            The default is False.

        tags: dict, optional
            Filter request by tag of cluster.  For example scheduled clusters can be
            filtered by task_id - `tags={'task_id': '10'}`
            Note: the tag value must be a string.

    Returns:
        list of dict
            information about each cluster. Each dict contains
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
          'ready_timestamp': str,
          'status_change_reason_code': str,
          'status_change_reason_text': str,
          'terminated_with_errors': bool,
          'termination_timestamp': str,
          'user': str,
          'conda_env': str,
          'notification_email_map': dict,
        }
    Timestamps are in ISO format and may be None if the event for the timestamp
    has not yet occurred.
    """
    params = {'state': state.value, 'include_org': include_org}
    tags = tags if tags else {}

    if any([k in params.keys() for k in tags.keys()]):
        raise ValueError('"state" and "include_org" are not valid query tag keys')

    if not all([isinstance(value, str) for value in tags.values()]):
        raise ValueError('Tag values must be of type string.')

    params.update(tags)

    response = SESSION.execute(
        'get',
        'compute',
        '/clusters',
        params=params
    )
    return response['result']


def terminate_cluster(cluster_id):
    """ Terminate a cluster.  No return value.

    Args:
        cluster_id: str
            the ID of the cluster to terminate
    """
    SESSION.execute(
        'delete',
        'compute',
        '/clusters/{}'.format(cluster_id),
    )


def get_cluster(cluster_id):
    """ Return information on a single cluster

    Args:
        cluster_id: str
            the ID of the cluster to query for

    Returns:
        dict
            information about the cluster:
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
              'ready_timestamp': str,
              'status_change_reason_code': str,
              'status_change_reason_text': str,
              'terminated_with_errors': bool,
              'termination_timestamp': str,
              'user': str,
              'conda_env': str,
              'notification_email_map': dict,
            }
    Timestamps are in ISO format and may be None if the event for the timestamp
    has not yet occurred.

    """
    response = SESSION.execute(
        'get',
        'compute',
        '/clusters/{}'.format(cluster_id),
    )
    return response['result']


def get_jobs(cluster_id):
    """ Get information about the jobs submitted to a cluster.

    Args:
        cluster_id: str
            the ID of the cluster to query

    Returns:
        list of dict
            information about each job submitted to the cluster.  Each dict will contain:
            {
                'end_date_time': str,
                'id': str,
                'jar': str,
                'name': str,
                'start_date_time': str,
                'state': str,
            }
    Timestamps are in ISO format and may be None if the event for the timestamp
    has not yet occurred.

    """
    response = SESSION.execute(
        'get',
        'compute',
        '/clusters/{}/jobs'.format(cluster_id),
    )
    return response['result']


def create_cluster(
        name,
        node_type,
        node_count=1,
        log_path=None,
        log_area='user',
        cluster_config=None,
        terminate_on_idle=True,
        spot_pricing=False,
        cluster_bootstraps=None,
        tags=None,
        conda_env='py311-stable',
        notification_email_map=None,
        ssh_key_name=None,
):
    """ Create a new cluster.

    The current python environment's name is detected and passed to the cluster to ensure that
    it uses the same environment.

    Note: the `node_type` parameter only applies to the worker ("core")
    nodes of the cluster. The master node is chosen to be a fixed on-demand instance
    of type (an `m4.large` instance). The core nodes are `r4.16xlarge` instances. For more
    details on instance types, please see
    https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-supported-instance-types.html

    Args:
        name: str
            the name to give the cluster

        node_type: NodeType
            the AWS node type for the cluster

        node_count: int
            the number of core nodes in the cluster

        log_path: str
            path to the folder to save the log files in.
            If None then no log files are created

        log_area: str
            'user' or 'organisation'

        cluster_config: dict
            additional configuration for the cluster - see botocore docs for more information

        terminate_on_idle: bool
            if True then terminate when there are no jobs to run.

        cluster_bootstraps: list, optional
            If not none, create a cluster with user specified bootstraps.

        tags: dict, optional
            Optional tags to add to the cluster.

        conda_env: str, optional
            The name of the Conda environment EMR clusters will use to do their work.
            Defaults to py311-stable.

        ssh_key_name: str, optional
            The name of an SSH key pair to use when creating a cluster. If not
            provided, no SSH key pair will be used.

        notification_email_map: dict, optional
            A map of notification trigger events (e.g. "terminated_with_failures") to
            a list of email addresses to contact in that event.

    Returns:
        Dict with minimal information about the cluster -
        {
            'creation_req_timestamp': str
            'id':str
            'name': str
        }

    """

    validate_env(conda_env)

    params = {
        'name': name,
        'log_path': log_path or 'logs',
        'log_area': log_area,
        'node_type': node_type,
        'node_count': node_count,
        'cluster_config': cluster_config or {},
        'spot_pricing': spot_pricing,
        'terminate_on_idle': terminate_on_idle,
        'bootstrap_actions': cluster_bootstraps or [],
        'conda_env': conda_env,
        'notification_email_map': notification_email_map or {}
    }

    if tags:
        params['tags'] = tags

    if ssh_key_name:
        params["ssh_key_name"] = ssh_key_name

    response = SESSION.execute(
        'post',
        'compute',
        '/clusters/simple',
        json=params
    )
    return response['result']


def submit_job(cluster_id, **kwargs):
    """Submit a job to be run on a cluster.

    Args
        cluster_id: str
            the cluster to submit the job to

        kwargs:
            keyword options for this job

    Returns:
        str
            the ID of the job that has been submitted
    """
    response = SESSION.execute(
        'post',
        'compute',
        '/clusters/{}/job/simple'.format(cluster_id),
        json=kwargs
    )
    job_id = response['result']['job_ids'][0]

    return job_id


def upload_bmll_config(job_name, job_parameters):
    """Upload cluster job parameters.

    Args:
        job_name: str
            The name of the job

        job_parameters: dict
            The parameters to store. Must be JSON serialisable.

    Returns:
        str
            The S3 URI where the parameters where stored.
    """
    payload = {
        'name': job_name,
        'parameters': job_parameters,
    }

    response = SESSION.execute(
        'post',
        'compute',
        '/storage/params',
        json=payload,
    )
    s3_uri = response['result']['s3_uri']

    return s3_uri
