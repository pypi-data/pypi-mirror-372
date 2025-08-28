import datetime
from functools import partial

from bmll._rest import DEFAULT_SESSION
from bmll._utils import chunk_call, ID_COL_TYPE, to_list_of_str

__all__ = ('query', 'available_markets', 'ReferenceDataClient', 'availability',)
DEFAULT_CHUNK_SIZE = 40_000
VALID_DATA_TYPES = ['LOB', 'ListingLevelMetric', 'InstrumentLevelMetric', 'MarketLevelMetric', 'DataFeed']


class ReferenceDataClient:
    """
    The ReferenceDataClient provides a convenient interface to interact with the BMLL Reference Data API.

    Args:
        session (bmll.Session, optional):

            if provided use this session object to communicate with the API, else use the default session.

    """

    def __init__(self, session=None):
        self._session = session or DEFAULT_SESSION

    def query(self,
              start_date=None,
              end_date=None,
              object_ids=None,
              object_type=None,
              chunk_size=DEFAULT_CHUNK_SIZE,
              schema='Equity',
              **constraint):
        """Find reference data for Listings relating to a set of constraints, optionally over a date
        range and including sibling Listings on multilateral trading facilities or primary exchange.

        Args:
            start_date:
                `str` or `datetime.date` (optional)

                First date to get data for. iso-formatted date. Defaults to the previous business day.

            end_date:
                `str` or `datetime.date` (optional)

                Last date to get data for. iso-formatted date. Defaults to same date as start_date.

            object_ids:
                `list` of `int` (optional)

                List of bmll ids to get reference data for.

            object_type:
                `str` (optional)

                Must be either:
                    * Listing
                    * Instrument
                    * Market
                    * Index
                    * IndexMarket

            chunk_size:
                `int` (optional), default `DEFAULT_CHUNK_SIZE`

                Maximum number of object IDs to send in request.
                As there is a payload size limit, large requests must be broken down into multiple calls.

            schema:
                `str` (optional)

                Must be either:
                    * Equity (defaults)
                    * Future

            constraint:
                Keyword arguments for constraints to search for reference data.

                For example:

                    MIC='XLON' or MIC=['XLON', 'XPAR']

                Allowed constraints include:
                    * MIC
                    * Ticker
                    * FIGI
                    * FIGIShareClass
                    * ISIN
                    * OPOL
                    * DisplayName
                    * Description
                    * Index
                    * Issuer
                    * IndexCode.
                    * StartDate
                    * Schema

                Note: constraints look for exact matches.
                An index supplied as a constraint is identified by its index code; for example

                    reference.query(object_type='Listing', Index='buk100p')
                    reference.query(object_type='Instrument', Index=['buk100p', 'bep50p'])

        Returns:
            `pandas.DataFrame`:
                DataFrame of reference data matching the given criteria.

        """
        constraint = {identifier_name: to_list_of_str(identifiers)
                      for identifier_name, identifiers in constraint.items()}

        start_date = str(start_date) if start_date else None
        end_date = str(end_date) if end_date else None

        req = partial(self._get_page,
                      start_date=start_date,
                      end_date=end_date,
                      object_type=object_type,
                      schema=schema,
                      **constraint)

        df = chunk_call(req, object_ids, chunk_size)

        bmll_index_columns = [
            col for col in ('ListingId', 'InstrumentId', 'MarketId', 'IndexId', 'IndexMarketId')
            if col in df.columns
        ]
        dtype_column_map = {'Date': 'datetime64[ns]'}
        dtype_column_map.update({col: 'bool' for col in ('IsPrimary', 'IsAlive') if col in df.columns})
        dtype_column_map.update({index_col: ID_COL_TYPE for index_col in bmll_index_columns})

        df = (
            df
            [sorted(df.columns)]
            .set_index(['Date'] + bmll_index_columns)
            .sort_index()
            .reset_index()
            .drop_duplicates()
            .reset_index(drop=True)
            .replace({"True": True, "False": False, "None": None})
            .astype(dtype_column_map)  # Must be after string to bool conversion.
        )

        return df

    def available_markets(self, start_date=None, end_date=None):
        """
        Get the available markets

        Args:
            start_date:
                `str` or `datetime.date` (optional)

                First date to get data for.  iso-formatted date

                Default, previous business day.

            end_date:
                `str` or `datetime.date` (optional)

                Last date to get data for. iso-formatted date

                Defaults to same date as start_date.

        Returns:
            `pandas.DataFrame`:
                DataFrame of reference data matching the given criteria.


        """
        return self.query(start_date=start_date, end_date=end_date, object_type='Market')

    def availability(self, mics, date=None, data_type='LOB', *, latest_status=False):
        """
        Check if L3 data is available for the given mics on the given date

        Args:
            mics:
                `list[str]`

                List of mics to check availability for.

            date:
                `str` or `datetime.date` or `datetime.datetime` or `None`

                Date to check availability for iso-formatted date string or datetime.date/datetime.datetime
                If a datetime.datetime is given, the time portion will be ignored.
                If this is `None`, we default to today.

                *Note* this parameter is mutually exclusive with `latest_status` - both cannot be used togther.

            data_type:
                `str`

                The type of data to check availability for.
                Accepted Values: 'LOB', 'ListingLevelMetric', 'InstrumentLevelMetric', 'MarketLevelMetric', 'DataFeed'

            latest_status:
                `bool`

                When `True`, return the latest availability status, regardless of date.

                *Note* this parameter is mutually exclusive with `date` - both cannot be used togther.

        Returns:
            `dict`:
                Dictionary of {'mic': {'ready': boolean, 'date': datetime, 'dataType': string}}
        """
        if date is not None and latest_status:
            raise ValueError("Both 'date' and 'latest_status' were provided, but they are mutually exclusive.")

        if date is not None:
            if isinstance(date, str):
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('If iso_date is a string, it must have the format YYYY-MM-DD')
            elif type(date) in (datetime.date, datetime.datetime):
                date = date.strftime('%Y-%m-%d')
            else:
                raise TypeError('iso_date must be either a string, a datetime.date or a datetime.datetime')

        if data_type not in VALID_DATA_TYPES:
            raise ValueError(f'data_type must be one of {VALID_DATA_TYPES}, received data_type="{data_type}"')
        url = '/availability'
        params = {
            'mics': mics,
            'dataType': data_type,
        }

        if not latest_status:
            params['date'] = date
        else:
            params['latestStatus'] = True

        return self._session.execute('post', 'reference', url, json=params)

    def _get_page(self, start_date, end_date, object_ids, object_type, schema, token=None, **constraint):
        """Get reference data for a given constraint and date range, and handle the
        paginated response.

        Parameters
        ----------
        start_date: str
            isoformat date
        end_date: str
            isoformat date
        object_ids: list(int)
            Look up reference data for these ids
        object_type: str
            Must be either "Listing", "Instrument", or "Market"
        schema: str
            Must be either "Equity" or "Future"
        **constraint: list(str)
            Field name to list of values

        Returns
        -------
        dict:
            Dictionary of {'date': {'id': {'field': 'value'}}}
        """

        params = {
            'objectType': object_type,
            'startDate': start_date,
            'endDate': end_date,
            'token': token,
            'schema': schema,
        }

        if object_ids:
            params['objectIds'] = object_ids

        params.update(constraint)

        return self._session.execute('post', 'reference', '/query', json=params)


# we set up a default client and session so that users can still call
# bmll.reference.query() etc.
_DEFAULT_CLIENT = ReferenceDataClient()
query = _DEFAULT_CLIENT.query
available_markets = _DEFAULT_CLIENT.available_markets
availability = _DEFAULT_CLIENT.availability
