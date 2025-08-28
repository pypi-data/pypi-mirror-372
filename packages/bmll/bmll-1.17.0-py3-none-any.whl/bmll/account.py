""" Interface to the Account service.
"""
import datetime
from typing import Optional

import pandas as pd

from bmll._rest import DEFAULT_SESSION

__all__ = (
    'get_permissions', 'AccountClient',
)


class AccountClient:
    """
    The AccountClient provides a convenient interface to interact with the BMLL Account API.

    Args:
        session: :class:`bmll.Session`, optional
            if provided use this session object to communicate with the API, else use the default session.
    """

    def __init__(self, session=None):
        self._session = session or DEFAULT_SESSION

    def _get_permission_dimensions(self) -> dict:
        """Retrieve all the possible dimensions you can be permissioned on.

        Returns:
            dict:
                Json reponse from the permission/dimensions endpoint,
                with keys metric_groups and object_groups
        """
        return self._session.execute('get', 'account', '/permissions/dimensions')

    def _get_account_permissions(self, auth_type: Optional[str]) -> dict:
        """Wrapper function for the permissions endpoint

        Args:
            auth_type: str
                The auth type the permission set applies to. Must be one of cognito, lambda
                Defaults to lambda.

        Returns:
            dict:
                Json reponse from the permissions endpoint with market id and list of
                permitted_metric_groups
        """
        return self._session.execute('get', 'account', '/permissions', params={'auth_type': auth_type or 'lambda'})

    def get_permissions(self, auth_type: Optional[str] = None) -> pd.DataFrame:
        """ Get a dataframe containing all the metric_groups in each market with a bool
            representing if you are permissioned on them.

        Args:
            auth_type: str
                The auth type the permission set applies to. Must be one of cognito, lambda
                Defaults to lambda.

        Returns:
            :class:`pandas.DataFrame`:
                DataFrame containing your permissions information.
        """
        auth_type = auth_type or 'lambda'
        if auth_type not in ['cognito', 'lambda']:
            raise ValueError(f'auth_type must be one of [\'cognito\', \'lambda\'], got {auth_type}')
        dimensions = self._get_permission_dimensions()
        account_permissions = self._get_account_permissions(auth_type)['object_group_permissions']
        account_permissions_map = {
            each.pop('id'): each.get('permitted_metric_groups', [])
            for each in account_permissions
        }

        # columns for dataframe 
        metric_groups = [group['id'] for group in dimensions['metric_groups']]
        columns = ['name'] + metric_groups

        user_permissions = []
        for venue in dimensions['object_groups']:
            venue_id = venue['id']
            row = {
                'name': venue['name'],
            }
            # venue id is an integer and needs to be a string
            permitted_metric_groups = account_permissions_map.get(venue_id, {})
            for metric_group in metric_groups:
                row[metric_group] = metric_group in permitted_metric_groups
            user_permissions.append(row)

        # create dataframe and sort columns by order from endpoint
        permissions_df = pd.DataFrame(user_permissions, columns=columns)
        permissions_df = permissions_df[columns]
        permissions_df = permissions_df.sort_values(by='name').reset_index(drop=True)
        return permissions_df

    def get_quota(self) -> dict:
        """Return a dictionary summarising the number of calls left on your usage plan for
        each service

        Returns:
            dict:
                ```python
                {
                    'time-series': {'limit': int, 'tier': str, 'remaining': int},
                    'reference': {'limit': int, 'tier': str, 'remaining': int},
                }
                ```
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        first_day_of_month = now.replace(day=1)
        last_day_of_month = _last_day_of_month(now)
        params = {
            'start_date': first_day_of_month.date().isoformat(),
            'end_date': last_day_of_month.date().isoformat(),
        }
        quota = self._session.execute('get', 'account', '/quota')['quota']
        current_usage = self._session.execute('get', 'account', '/usage', params=params)['usage']

        services = ['time-series', 'reference']
        quota_information = {}
        for service in services:
            lambda_name = f'{service}-service-lambda'
            limit = quota[lambda_name]['limit']
            tier = quota[lambda_name]['tierName']
            no_usage = current_usage[lambda_name] is None or len(current_usage[lambda_name]) == 0
            remaining = limit if no_usage else current_usage[lambda_name][-1][1]
            quota_information[service] = {'limit': limit, 'tier': tier, 'remaining': remaining}
        return quota_information


def _last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


_DEFAULT_CLIENT = AccountClient()
get_permissions = _DEFAULT_CLIENT.get_permissions
get_quota = _DEFAULT_CLIENT.get_quota
