import logging
import time
import requests
import gzip
from http import HTTPStatus
from io import BytesIO

import pandas as pd

from bmll._rest import DEFAULT_SESSION


class ApiV2Client:
    """
    Helper class to manage asynchronous queries to APIv2 and their results.
    """

    def __init__(self, session=None, max_retries=300, wait_time=1, verbose=False):
        self._session = session if session is not None else DEFAULT_SESSION
        self._max_retries = max_retries
        self._wait_time = wait_time
        self._verbose = verbose

        self._logger = logging.getLogger(f"{__name__}.ApiV2Client")
        if not self._logger.handlers:  # Prevent duplicate handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
        self._logger.propagate = False

    def initiate_query(self, payload, endpoint='/query'):
        """
        Initiates an asynchronous query and returns the query ID.

        Args:
            payload (dict): The payload for the POST request.
            endpoint (str): The API endpoint for initiating queries.

        Returns:
            str: The unique query ID.

        Raises:
            ValueError: If the response does not contain an 'id' key.
        """
        self._logger.info("Initiating asynchronous query.")
        self._logger.debug(f"POST {endpoint} with payload: {payload}")

        response = self._session.execute('post', 'apiv2', endpoint, json=payload)
        self._logger.debug(f"Received response: {response}")

        query_id = response.get('id')
        if query_id:
            self._logger.info(f"Query initiated successfully. Query ID: {query_id}")
            return query_id
        else:
            self._logger.error(f"Response missing 'id': {response}")
            raise ValueError(f"Response does not contain 'id': {response}")

    def poll_query(self, query_id, endpoint='/query'):
        """
        Polls the server for the status of a query until completion.

        Args:
            query_id (str): The unique ID of the query to poll.
            endpoint (str): The API endpoint for polling queries.

        Returns:
            str: A presigned URL for downloading the query results.

        Raises:
            TimeoutError: If the query does not complete within the maximum retries.
            ValueError: If the response does not contain expected data.
        """
        self._logger.info(f"Starting to poll for query ID: {query_id}")

        for attempt in range(1, self._max_retries + 1):
            self._logger.debug(f"Polling attempt {attempt}/{self._max_retries} for query ID: {query_id}")
            response = self._session.execute('get', 'apiv2', endpoint, params={'id': query_id})

            if response:
                status = response.get('status')
                self._logger.info(f"Attempt {attempt}: Query status is '{status}'")

                if status == 'SUCCESS':
                    link = response.get('link')
                    if link:
                        self._logger.info("Query completed successfully")
                        return link
                    else:
                        self._logger.error(f"'link' not found in the response: {response}")
                        raise ValueError(f"'link' not found in the response: {response}")

                elif status in {'FAILED', 'CANCELLED'}:
                    self._logger.error(f"Query failed or was cancelled. Status: {status}")
                    raise ValueError(f"Query failed or was cancelled. Status: {status}")
            else:
                self._logger.error(f"Invalid response received on attempt {attempt}: {response}")
                raise ValueError(f"Invalid response received: {response}")

            time.sleep(self._wait_time)

        self._logger.error("Max retries reached. Query did not complete in time.")
        raise TimeoutError("Max retries reached. Query did not complete in time.")

    def download_data(self, url):
        """
        Downloads data from a presigned URL and loads it into a DataFrame.

        Args:
            url (str): The presigned S3 URL.

        Returns:
            pd.DataFrame: The downloaded data.

        Raises:
            Exception: If the download request fails.
        """
        self._logger.info("Starting download from presigned URL.")

        try:
            response = requests.get(url)
            self._logger.debug(f"HTTP response status: {response.status_code}")
        except requests.RequestException as e:
            self._logger.error(f"Request to URL failed: {e}")
            raise Exception(f"Failed to fetch data: {e}")

        if response.status_code == HTTPStatus.OK:
            try:
                with gzip.GzipFile(fileobj=BytesIO(response.content)) as gzipped_file:
                    df = pd.read_csv(gzipped_file).dropna(how='all')
                    self._logger.info(f"Download and decompression successful. DataFrame shape: {df.shape}")
                    return df
            except Exception as e:
                self._logger.error(f"Error reading or decompressing the response content: {e}")
                raise Exception(f"Failed to parse downloaded data: {e}")
        else:
            self._logger.error(f"Failed to download data. HTTP status: {response.status_code}")
            raise Exception(f"Failed to download data. HTTP status: {response.status_code}")

    def query(self, payload):
        """
        Orchestrates the asynchronous query process: initiation, polling, and downloading.

        Args:
            payload (dict): The payload for the POST request.

        Returns:
            pd.DataFrame: The query results as a DataFrame.
        """
        query_id = self.initiate_query(payload)

        download_link = self.poll_query(query_id)

        df = self.download_data(download_link)
        return df


_DEFAULT_CLIENT = ApiV2Client()
apiv2_query = _DEFAULT_CLIENT.query
