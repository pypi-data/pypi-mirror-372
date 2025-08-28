import base64
import collections
import copy
import datetime
import hashlib
import json
import logging
import os
import pathlib
import warnings
from http import HTTPStatus
from typing import Dict, Optional

import backoff
import jwt
import numpy as np
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from requests import exceptions as requests_exc
from requests import Session as RequestsSession

from bmll.exceptions import (
    AuthenticationError, ConnectivityError, LoginError, QuotaReachedError, RequestTooLarge, QUOTA_EXCEEDED_ERROR,
)
from bmll.metadata import __version__ as _bmll_version

__all__ = ('Session', 'DEFAULT_SESSION', 'login', 'logout')

Headers = Dict[str, str]
_logger = logging.getLogger(__name__)


def _set_bmll_base_url_if_possible():
    """
        Checks for the BMLL_BASE_URL environment variable and sets it if it can be found via the bmll2 config.
        This environment variable is used by bmll2 to authenticate, so we use bmll2 lab authentication if and
        only if it can be (or has been) set.
    """
    try:
        from bmll2._internals.api.configure import CONFIG_PATH
    except ModuleNotFoundError:
        CONFIG_PATH = None
    if CONFIG_PATH and not os.environ.get('BMLL_BASE_URL'):
        config_path = pathlib.Path(CONFIG_PATH)
        bmll_base_url = None
        if config_path.exists():
            # This file is created by the scheduled cluster bootstrap script. If BMLL_BASE_URL is not an
            # environment variable, we create it using the variable stored here.
            bmll_base_url = json.loads(config_path.read_text()).get('bmll_base_url')
            if not bmll_base_url:
                # If bmll_base_url is not in .nb_extension_instance_vars.json, check for nexus_base_url and
                # reconstruct bmll_base_url from it.
                nexus_base_url = json.loads(config_path.read_text()).get('nexus_base_url')
                if nexus_base_url:
                    bmll_base_url = nexus_base_url.split('nexus.')[1]
        if bmll_base_url:
            os.environ['BMLL_BASE_URL'] = bmll_base_url


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)):
            return None

        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


class Session:
    """The Session class handles low level communication and authentication with the BMLL Services.

    Warning:

        It is only intended for *advanced* users who require a thread-safe interface.

    Notes:

        See `Session.login` for Parameters

    """
    _auth_func = None
    _using_injected_auth = False
    _MAXIMUM_BODY_LENGTH = 512000
    _BACKOFF_PARAMS = {'base': 2, 'factor': 1, 'max_value': 30}
    _BACKOFF_ON_PREDICATE_KWARGS = {'max_time': 30}
    DEFAULT_HEADERS = {'x-bmll-version': _bmll_version}  # type: Headers

    def __init__(self, *args, session=None, **kwargs):
        self.http_session = session or RequestsSession()
        self.SERVICE_URLS = {
            'reference': os.environ.get('BMLL_REFERENCE_URL', 'https://reference.data.bmlltech.com'),
            'time-series': os.environ.get('BMLL_TIME_SERIES_URL', 'https://time-series.data.bmlltech.com'),
            'auth': os.environ.get('BMLL_AUTH_URL', 'http://auth.data.bmlltech.com'),
            'market-data': os.environ.get('BMLL_MARKET_DATA_URL', 'https://market-data.data.bmlltech.com'),
            'account': os.environ.get('BMLL_ACCOUNT_URL', 'https://account.data.bmlltech.com'),
            'lab-auth': os.environ.get('BMLL_LAB_AUTH_URL', 'https://auth.lab.bmlltech.com'),
            'compute': os.environ.get('BMLL_COMPUTE_URL', 'https://compute.lab.bmlltech.com'),
            'apiv2': os.environ.get('BMLL_API_URL', 'https://api.data.bmlltech.com'),
        }
        self._BASE_URL = os.environ.get('BMLL_BASE_URL', 'https://data.bmlltech.com')
        self._USERNAME = os.environ.get('BMLL_USERNAME')
        self._KEY_PATH = os.environ.get('BMLL_KEY_PATH')
        self._KEY_PASSPHRASE = os.environ.get('BMLL_KEY_PASSPHRASE')

        self._TOKEN = None
        self._API_KEY = None
        self._LAB_ORG_ID = None

        self._attempt = 0
        self._login_attempts = 0

        error_queue_length = kwargs.pop('error_queue_length', 10)
        self._request_errors = collections.deque([], maxlen=error_queue_length)

        if args or kwargs:
            self.login(*args, **kwargs)

    def execute(self, method, service, url, *, headers=None, **kw):
        """execute a request against a service."""
        base_url = self.SERVICE_URLS[service]
        resp = None
        headers = self.get_headers(headers)

        if 'json' in kw:
            kw['json'] = json.loads(json.dumps(kw['json'], cls=JsonEncoder))

        try:
            resp = self._request(method, base_url + url, headers=headers, **kw)
        finally:
            if resp and HTTPStatus.OK <= resp.status_code < HTTPStatus.MULTIPLE_CHOICES:
                self._attempt = 0
                self._login_attempts = 0

        if HTTPStatus.OK <= resp.status_code < HTTPStatus.MULTIPLE_CHOICES:
            return resp.json()
        else:
            raise Exception((resp.status_code, resp.json()))

    def _wrap_request(self, *args, headers=None, **kwargs):
        method, url, *_ = args
        # this causes a loop as get auth headers does get api key
        is_api_key_get = method == 'get' and url.endswith('/api-key')
        if headers is not None and 'Authorization' in headers and not is_api_key_get:
            # always get latest auth header
            headers = copy.deepcopy(headers)
            headers.update(self.get_auth_headers())
        return self.http_session.request(*args, headers=headers, **kwargs)

    def _request(self, *args, **kwargs):
        """Make rest request using given args and kwargs.
        Retry with exponential backoff if predicate (self._needs_retry) returns True.
        """
        return backoff.on_predicate(
            backoff.expo,
            self._needs_retry,
            **self._BACKOFF_ON_PREDICATE_KWARGS,
            **self._BACKOFF_PARAMS,
        )(self._wrap_request)(*args, **kwargs)

    def _needs_retry(self, resp):
        """Check rest response and determine whether to retry

        Parameters
        ----------
        resp: requests.Response

        Raises
        ------
        AuthenticationError:
            On receiving consecutive unauthorised responses (after first response we attempt to login again)
        QuotaReachedError:
            Quota for service has been used up
        RequestTooLarge:
            Request body is too large for service

        Returns
        -------
        bool:
            True/False on whether to retry
        """
        self._attempt += 1
        if HTTPStatus.OK <= resp.status_code < HTTPStatus.MULTIPLE_CHOICES:
            return False
        self._request_errors.append(resp)
        if resp.status_code == HTTPStatus.UNAUTHORIZED:
            # Only allow one login retry, then raise AuthenticationError
            self._login_attempts += 1
            if self._login_attempts < 2:
                self.login()
                return True
            else:
                self._login_attempts = 0
                raise AuthenticationError('Unauthorised to access service.')
        elif resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            if resp.json().get('message', None) == QUOTA_EXCEEDED_ERROR:
                raise QuotaReachedError(
                    'Quota reached for requested service. Check your usage at '
                    f'{self._BASE_URL}/#app/permissions'
                )
            return True
        elif (resp.status_code == HTTPStatus.FORBIDDEN
              and int(resp.request.headers.get('content-length', 0)) >= self._MAXIMUM_BODY_LENGTH):
            raise RequestTooLarge('The size of your query is too large.')
        elif resp.status_code in (HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.GATEWAY_TIMEOUT):
            # Retry on 502, 503, 504
            return True
        else:
            # Otherwise do not retry
            return False

    def get_headers(self, headers: Optional[Headers] = None) -> Headers:
        all_headers = self.DEFAULT_HEADERS.copy()
        all_headers.update(headers if headers is not None else self.get_auth_headers())
        return all_headers

    def get_auth_headers(self) -> Headers:
        """return the authenticated headers."""
        if self._TOKEN is None:
            self.login()

        headers = {
            "Authorization": "Bearer {}".format(self._TOKEN),
        }

        if self._API_KEY:
            headers['x-api-key'] = self._API_KEY

        return headers

    def get_last_error(self):
        """ Return the last non-success http response.
        """
        return self.get_error(0)

    def get_error(self, n=None):
        """ Get the nth last non-success http responses. If n is None return a
        list of all the recent errors.
        """
        if n is None:
            return list(reversed(self._request_errors))
        if n < 0:
            raise ValueError("N must be greater than or equal to zero.")
        if n >= len(self._request_errors):
            raise IndexError("Error queue index out of range.")
        return self._request_errors[-(n + 1)]

    # We use a property for the custom auth function in order to cause a deferred look-up of
    # the class attribute in Session.login(). This allows and ensures that we can call
    # _set_authorizer with or without manually instantiating a Session instance.
    @property
    def _custom_auth_func(self):
        """ Return the custom auth function if set.
        """
        return self.__class__._auth_func

    def _auth_status_check(self):
        """ Hit the status check endpoint of the new auth service.
            If the response is not a 200, revert to using the old lab services
        """
        try:
            self.http_session.request('get', self.SERVICE_URLS['lab-auth'] + '/status-check')
        except requests_exc.RequestException:
            _logger.exception('Unable to reach the BMLL services.')
            raise ConnectivityError('Unable to reach the BMLL services. Please contact BMLL support if it continues.')

    def login(self, username=None, key_path=None, passphrase=None, lab_org_id=None):
        """
        Login to the BMLL Remote API.

        To login to the BMLL Remote API you must have registered at https://data.bmlltech.com and generated a key-pair.

        Note: Both key files must exist in the same directory.

        Args:
            username (str, optional):

                [api username](https://data.bmlltech.com/#app/sftp).
                if not provided, then attempt to retrieve the username from the comment section of the public key-file.

            key_path (str, optional):

                the path of your private key.

            passphrase (str, optional):

                the passphrase for your key if exists.

            lab_org_id: str, optional

                the lab org ID for lab-auth login

        """
        _set_bmll_base_url_if_possible()

        if not os.environ.get('BMLL_BASE_URL'):
            self._ssh_auth(username, key_path, passphrase, lab_org_id)
        # for backward compatibility, if BMLL_USERNAME is provided, or username or lab_org_id use ssh_auth instead
        elif ('BMLL_USERNAME' in os.environ
              or username or lab_org_id or key_path
              or self._USERNAME or self._LAB_ORG_ID or self._KEY_PATH):
            self._ssh_auth(username, key_path, passphrase, lab_org_id)
        else:
            self._bmll2_lab_auth()

        _logger.debug('Logged in successfully.')

    def logout(self):
        """Logout of the BMLL Remote API."""
        self._TOKEN = None
        self._API_KEY = None
        self._LAB_ORG_ID = None

        _logger.debug('Logged out.')

    def __enter__(self, *args, **kwargs):
        self.login(*args, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def _bmll2_lab_auth(self):
        """ use the lab auth function from bmll2
        """
        from bmll2 import get_credentials_for_remote_services
        self._TOKEN, self._API_KEY, self._LAB_ORG_ID = get_credentials_for_remote_services()

    def _ssh_auth(self, username=None, key_path=None, passphrase=None, lab_org_id=None):
        """ Execute the ssh auth mechanism

        Args:
            username (str, optional):
                username of the user
            key_path (str, optional):
                the path of your private key.
            passphrase (str, optional):
                the passphrase for your key if exists.
            lab_org_id: (str, optional)
                the lab org ID for lab-auth login
        """
        if key_path:
            self._KEY_PATH = key_path
        elif self._KEY_PATH is None:
            self._KEY_PATH = os.environ.get('BMLL_KEY_PATH')

            if self._KEY_PATH is None:
                raise LoginError('Unable to locate private key.\n'
                                 '\n'
                                 'You must either:\n'
                                 '\n'
                                 '- provide the key_path argument to bmll.login\n'
                                 '- set the BMLL_KEY_PATH environment variable prior to import of bmll.')

        if passphrase:
            self._KEY_PASSPHRASE = passphrase
        else:
            self._KEY_PASSPHRASE = os.environ.get('BMLL_KEY_PASSPHRASE')

        if username:
            self._USERNAME = username

        elif self._USERNAME is None:
            self._USERNAME = os.environ.get('BMLL_USERNAME')

            if self._USERNAME is None:
                self._USERNAME = self._try_get_username()

        if self._USERNAME is None:
            raise LoginError('Unable to locate username.\n'
                             '\n'
                             'You must either:\n'
                             '\n'
                             '- provide the username argument to bmll.login\n'
                             '- set the BMLL_USERNAME environment variable prior to import of bmll.\n'
                             '- set the username as the comment field of your public key.')

        if lab_org_id:
            self._LAB_ORG_ID = lab_org_id

        if self._LAB_ORG_ID is None:
            self._TOKEN, self._API_KEY = self._get_token()
        else:
            self._TOKEN, self._API_KEY = self._get_lab_token()

    def _get_private_key_path(self):
        return pathlib.Path(self._KEY_PATH).expanduser()

    def _get_public_key_path(self):
        return self._get_private_key_path().with_suffix('.pub')

    def _ssh_key_fingerprint(self):
        """ Return the ssh key fingerprint
        """
        # NOTE: the return value can also be obtained from the
        # command
        # ssh-keygen -v -l -f path/to/public_key.pub
        path = self._get_public_key_path()
        key = path.read_text()
        return self._key_to_fingerprint(key)

    def _key_to_fingerprint(self, key):
        """
        Helper function to convert ssh key to fingerprint

        Args:
            key: str
                ssh key

        Returns:
            str:
                fingerprint
        """
        key = base64.b64decode(key.strip().split()[1].encode('ascii'))
        fp_plain = hashlib.md5(key).hexdigest()
        return ':'.join(f'{first}{second}' for first, second in zip(fp_plain[::2], fp_plain[1::2]))

    def _get_key_comment(self, key):
        """Return the comment from public key."""
        key_parts = key.split()
        if len(key_parts) == 3:
            return key_parts[-1]
        else:
            return None

    def _try_get_username(self):
        """Attempt to retrieve the username from the comment section of the public key."""
        path = self._get_public_key_path()
        key = path.read_text()
        username = self._get_key_comment(key)
        return username

    def _get_session_id(self, service):
        data = {
            'iss': self._USERNAME
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        resp = self.execute('post', service, '/auth/identity', json=data, headers=headers)

        return resp['sid']

    def _get_token(self):
        """ Perform log-in against the auth service
        """
        return self._get_auth_token("dd-services", "auth")

    def _get_lab_token(self):
        """ Perform log-in against the lab-auth service
        """
        self._auth_status_check()
        token, _ = self._get_auth_token('lab-services', 'lab-auth')

        headers = {'Authorization': f'Bearer {token}'}
        api_key_response = self.execute('get', 'account', '/api-key', headers=headers)
        api_key = api_key_response['apiKey']

        return token, api_key

    def _get_auth_token(self, audience, service):
        """ Perform log-in against the given service
        """
        # Initial "log in" step, 1st part of handshake
        # We send in the JSON body the "claims" we
        # want
        _logger.debug('Starting log-in process...')

        json_body = {
            "iss": self._USERNAME,
            "aud": audience,
            "exp": (
                    datetime.timedelta(days=1) + datetime.datetime.now(datetime.timezone.utc)
            ).timestamp(),
            "sid": self._get_session_id(service)
        }

        if self._LAB_ORG_ID is not None:
            json_body["accountId"] = self._LAB_ORG_ID

        # Get the token, 2nd part of handshake
        # Here we create a JWT signed with our private SSH key
        # The server has the public counterpart and can verify
        # that the JWT was signed by our private SSH key.
        secret_key_path = self._get_private_key_path()
        password = self._KEY_PASSPHRASE.encode() if self._KEY_PASSPHRASE else None
        priv_rsakey = load_pem_private_key(
            secret_key_path.read_bytes(), password=password,
            backend=default_backend(),
        )
        jws_encoded = jwt.encode(
            json_body, key=priv_rsakey, algorithm="RS256",
        )

        if isinstance(jws_encoded, str):
            # pyjwt >= 2.0.0
            jws = jws_encoded
        else:
            # pyjwt < 2.0.0
            jws = jws_encoded.decode()

        json_body["jws"] = jws

        response = self.execute(
            'post',
            service,
            '/auth/token',
            json=json_body,
            headers={},
        )

        # The (successful) response contains a JWT signed with a
        # secret that only the server knows. The server will
        # validate tokens with this secret on each endpoint
        # invocation

        return response['token'], response.get('api-key')

    def _set_environment(self, env):
        """Developer Mode: set the environment to `local`, `dev` or `staging`."""
        if env not in ['local', 'docker', 'dev', 'staging']:
            return
        if env in ['local', 'docker']:
            if env == 'local':
                self.SERVICE_URLS['account'] = 'https://localhost:64004'
                self.SERVICE_URLS['auth'] = 'https://localhost:64005'
                self.SERVICE_URLS['reference'] = 'https://localhost:64001'
                self.SERVICE_URLS['time-series'] = 'https://localhost:64002'
                self.SERVICE_URLS['market-data'] = 'https://localhost:64007'
                self.SERVICE_URLS['apiv2'] = 'https://api.data.dev.bmll.io'
            else:
                no_docker = ['lab-auth', 'compute']
                no_docker_urls = {
                    service_name: self.SERVICE_URLS[service_name] for service_name in ['lab-auth', 'compute']
                }
                self.SERVICE_URLS = {
                    service_name: f'https://ddserv_{service_name}-service_1:64000'
                    for service_name in self.SERVICE_URLS if service_name not in no_docker
                }
                self.SERVICE_URLS = {**self.SERVICE_URLS, **no_docker_urls}
            # patch headers
            self.get_auth_headers = lambda: {}
            # disable verify
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['CURL_CA_BUNDLE'] = ''
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        else:
            self.SERVICE_URLS = {service_name: url.replace('bmlltech.com', f'{env}.bmll.io')
                                 for service_name, url in self.SERVICE_URLS.items()}

        self._BASE_URL = f'https://data.{env}.bmll.io'


DEFAULT_SESSION = Session()

login = DEFAULT_SESSION.login
logout = DEFAULT_SESSION.logout
