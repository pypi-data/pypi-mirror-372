""" Low level functions for managing jobs.
"""
from typing import Optional, Dict, Any
from copy import deepcopy

from bmll import _rest


__all__ = (
    'get_jobs',
    'create_job',
    'update_job',
    'delete_job',
    'get_all_job_runs',
    'get_job_runs',
    'create_job_run',
    'delete_job_run',
    'create_job_trigger',
    'get_job_run_stream_logs',
    'get_job_run_logs'
)

SESSION = _rest.DEFAULT_SESSION


def get_jobs(
    state: Optional[str],
    visibility: Optional[str],
    page:  Optional[int],
    page_size: Optional[int]
):
    params = {}

    if state:
        params['state'] = state
    if visibility:
        params['visibility'] = visibility
    if page:
        params['page'] = page
    if page_size:
        params['pageSize'] = page_size

    response = SESSION.execute(
        'get',
        'compute',
        '/jobs',
        params=params
    )
    return response['result']


def create_job(data: Dict[str, Any]):

    create_data = {
        k: v for (k, v) in data.items()
        if v is not None
    }

    response = SESSION.execute(
        'post',
        'compute',
        '/jobs',
        json=create_data
    )
    return response['result']


def update_job(
    job_id: str, patch_data: Dict[str, Any]
):
    response = SESSION.execute(
        'patch',
        'compute',
        f'/jobs/{job_id}',
        json=patch_data
    )
    response_data = response['result']

    patch_data_copy = deepcopy(patch_data)
    patch_data_copy['updatedTs'] = response_data['updatedTs']

    return patch_data_copy


def delete_job(
    job_id: str
):
    response = SESSION.execute(
        'delete',
        'compute',
        f'/jobs/{job_id}'
    )
    return response['result']


def get_all_job_runs(
    state: Optional[str],
    visibility: Optional[str],
    page:  Optional[int],
    page_size: Optional[int]
):
    params = {}

    if state:
        params['state'] = state
    if visibility:
        params['visibility'] = visibility
    if page:
        params['page'] = page
    if page_size:
        params['pageSize'] = page_size

    response = SESSION.execute(
        'get',
        'compute',
        '/runs',
        params=params
    )
    return response['result']


def get_job_runs(
    job_id: str
):
    response = SESSION.execute(
        'get',
        'compute',
        f'/jobs/{job_id}/runs'
    )
    return response['result']


def create_job_run(
    job_id: str,
    data: Optional[Dict[str, Any]]
):
    response = SESSION.execute(
        'post',
        'compute',
        f'/jobs/{job_id}/runs',
        json=data
    )
    return response['result']


def delete_job_run(
    job_run_id: str
):
    response = SESSION.execute(
        'delete',
        'compute',
        f'/runs/{job_run_id}'
    )
    return response['result']


def get_job_run_parameters(job_run_id: str):
    response = SESSION.execute(
        'get',
        'compute',
        f'/runs/{job_run_id}/parameters'
    )
    return response['result']


def get_job_run_logs(
    job_run_id: str, start_time: str, end_time: str, next_token: Optional[str] = None
):
    params = {
        'startTime': start_time,
        'endTime': end_time
    }

    if next_token:
        params.update({'nextToken': next_token})

    response = SESSION.execute(
        'get',
        'compute',
        f'/runs/{job_run_id}/logs',
        params=params
    )

    return response['result']


def get_job_run_stream_logs(
    job_run_id: str, start_time: str, end_time: str, next_token: Optional[str] = None
):
    params = {
        'startTime': start_time,
        'endTime': end_time
    }

    if next_token:
        params.update({'nextToken': next_token})

    response = SESSION.execute(
        'get',
        'compute',
        f'/runs/{job_run_id}/stream',
        params=params
    )

    return response['result']


def create_job_trigger(job_id: str, data: Dict[str, Any]):
    response = SESSION.execute(
        'post',
        'compute',
        f'/jobs/{job_id}/triggers',
        json=data,
    )
    return response['result']


def delete_job_trigger(job_id: str, trigger_id: str):
    SESSION.execute(
        'delete',
        'compute',
        f'/jobs/{job_id}/triggers/{trigger_id}',
    )


def update_job_trigger(job_id: str, trigger_id: str, data: Dict[str, Any]):
    SESSION.execute(
        'patch',
        'compute',
        f'/jobs/{job_id}/triggers/{trigger_id}',
        json=data,
    )
