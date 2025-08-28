""" Various constants and mappings to support the OO Cluster API.
"""

from collections import OrderedDict

__all__ = (
    "CLUSTER_COLUMN_RESPONSE_DICT",
    "CLUSTER_STARTING_STATUS",
    "CLUSTER_READY_STATUS",
    "CLUSTER_STOPPING_STATUS",
    "CLUSTER_STOPPED_STATUS",
    "JOB_COLUMN_RESPONSE_DICT",
    "JOB_STARTING_STATUS",
    "JOB_FAILED_STATUS",
    "JOB_RUNNING_STATUS",
    "JOB_STOPPED_STATUS",
    "USER_BOOTSTRAP_FILENAME",
)


USER_BOOTSTRAP_FILENAME = 'default_bootstrap.sh'


# mapping between DataFrame name and name in API response
CLUSTER_COLUMN_RESPONSE_DICT = OrderedDict([
    ('ID', 'id'),
    ('Name', 'name'),
    ('Status', 'cluster_state'),
    ('Total running time', None),
    ('Started', 'creation_timestamp'),
    ('Ready', 'ready_timestamp'),
    ('Stopped', 'termination_timestamp'),
    ('Node type', 'cluster_type'),
    ('AWS node type', 'core_node_type'),
    ('Node count', 'core_node_count'),
    ('User', 'user'),
    ('Job count', 'job_count'),
    ('Active', None),
    ('Conda Environment', 'conda_env'),
    ('Notification Email Map', 'notification_email_map'),
])
CLUSTER_STARTING_STATUS = 'Starting'
CLUSTER_BOOTSTRAPPING_STATUS = 'Bootstrapping'
CLUSTER_STARTUP_STATUS = (CLUSTER_STARTING_STATUS, CLUSTER_BOOTSTRAPPING_STATUS)
CLUSTER_READY_STATUS = 'Waiting'
CLUSTER_RUNNING_STATUS = 'Running'
CLUSTER_STOPPING_STATUS = 'Terminating'
CLUSTER_TERMINATED_STATUS = 'Terminated'
CLUSTER_TERMINATED_ERROR_STATUS = 'Terminated with errors'
CLUSTER_STOPPED_STATUS = (CLUSTER_TERMINATED_STATUS, CLUSTER_TERMINATED_ERROR_STATUS)

JOB_COLUMN_RESPONSE_DICT = OrderedDict([
    ('ID', 'id'),
    ('Name', 'name'),
    ('Status', 'state'),
    ('Total running time', None),
    ('Started', 'start_date_time'),
    ('Stopped', 'end_date_time'),
    ('Active', None)
])
JOB_STARTING_STATUS = 'Pending'
JOB_FAILED_STATUS = ('Failed', 'Interrupted')
JOB_RUNNING_STATUS = 'Running'
JOB_STOPPED_STATUS = ('Cancelled', 'Completed')
