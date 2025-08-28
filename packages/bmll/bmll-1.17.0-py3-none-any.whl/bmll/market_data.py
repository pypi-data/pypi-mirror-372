import pandas as pd
import backoff

from bmll._rest import DEFAULT_SESSION
from bmll.exceptions import MarketDataError

__all__ = ('instrument_market_state', 'instrument_cbbo', 'MarketDataClient')
MAX_POLL_TIME = 60*5


def _is_wait(result):
    return result.get('wait', False)


class MarketDataClient:
    """
    The MarketDataClient provides a convenient interface to interact with the BMLL Market Data API.

    Args:
        session: :class:`bmll.Session`, optional
            if provided use this session object to communicate with the API, else use the default session.
    """

    def __init__(self, session=None):
        self._session = session or DEFAULT_SESSION

    def instrument_market_state(self, object_id, date):
        """Retrieve the market state of listings relating to an instrument on a given day.

        Args:
        date: str or datetime.date
            Date to get data for.  iso-formatted date
        object_id: int
            BMLL id of listing/instrument.

        Returns:
            :class:`pandas.DataFrame`
        """
        return self._get_data(f'/instrument/marketState/{object_id}/{date}')

    def instrument_cbbo(self, object_id, date, level):
        """Retrieve the consolidated best bid offer for an instrument on a given day.

        Args:
            date: str or datetime.date
                Date to get data for.  iso-formatted date
            object_id: int
                BMLL id of listing/instrument.

        Returns:
            :class:`pandas.DataFrame`
        """
        return self._get_data(f'/instrument/cbbo/{object_id}/{date}/{level}')

    def _get_data(self, endpoint):
        """
        Retrieve data from market data service.

        Args:
            endpoint: str
                endpoint to request data from.

        Returns:
            :class:`pandas.DataFrame`
                DataFrame of reference data matching the given criteria.
        """
        result = self._poll_query(endpoint)
        if _is_wait(result):
            raise MarketDataError(f'Failed to download market data for: {endpoint!r}.')
        return self._format(result)

    @backoff.on_predicate(backoff.expo, _is_wait, max_time=MAX_POLL_TIME, base=2, factor=0.1, max_value=30)
    def _poll_query(self, endpoint):
        return self._session.execute('get', 'market-data', endpoint)

    @staticmethod
    def _format(json_result):
        df = pd.DataFrame(**json_result)
        for col in df:
            if 'timestamp' in col:
                df[col] = pd.to_datetime(df[col])
            elif 'price' in col:
                df[col] = df[col].astype(float)
        return df


_DEFAULT_CLIENT = MarketDataClient()
instrument_market_state = _DEFAULT_CLIENT.instrument_market_state
instrument_cbbo = _DEFAULT_CLIENT.instrument_cbbo
