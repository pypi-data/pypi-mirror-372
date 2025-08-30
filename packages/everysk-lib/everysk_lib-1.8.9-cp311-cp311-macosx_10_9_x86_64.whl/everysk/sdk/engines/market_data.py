###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from functools import lru_cache
from typing import Any

from everysk.config import settings
from everysk.core.fields import DateField, ListField, StrField, BoolField, ChoiceField
from everysk.core.datetime import Date
from everysk.core.http import HttpGETConnection
from everysk.sdk.base import BaseSDK


###############################################################################
#   MarketData Class Implementation
###############################################################################
class MarketData(BaseSDK):

    date = DateField(default=Undefined)
    start_date = DateField(default=None)
    end_date = DateField(default=None)
    ticker_list = ListField(default=None)
    ticker_type = ChoiceField(default=None, choices=settings.ENGINES_MARKET_DATA_TICKER_TYPES)
    projection = StrField(default=None)
    nearest = BoolField(default=False)
    real_time = BoolField(default=False)

    def get_security(
        self,
        date: Date = Undefined,
        ticker_list: list[str] = Undefined,
        ticker_type: list[str] = Undefined,
        projection: str = Undefined,
        nearest: bool = Undefined
    ) -> dict:
        """
        Get security data.

        Args:
            date (Date): The date.
            ticker_list (list[str]): The ticker list.
            ticker_type (list[str]): The ticker type.
            projection (str): The projection.
            nearest (bool): The nearest flag.

        Returns:
            dict: The security data.
        """
        return self.get_response(self_obj=self, params={'date': date, 'ticker_list': ticker_list, 'ticker_type': ticker_type, 'projection': projection, 'nearest': nearest})

    def get_historical(
        self,
        date: Date = Undefined,
        start_date: Date = Undefined,
        end_date: Date = Undefined,
        ticker_list: list[str] = Undefined,
        ticker_type: str = Undefined,
        projection: str = Undefined,
        nearest: bool = Undefined,
        real_time: bool = Undefined
    ) -> dict:
        """
        Get historical data.

        Args:
            date (Date): The date.
            start_date (Date): The start date.
            end_date (Date): The end date.
            ticker_list (list[str]): The ticker list.
            ticker_type (str): The ticker type.
            projection (str): The projection.

        Returns:
            dict: The historical data.
        """
        return self.get_response(self_obj=self, params={'date': date, 'start_date': start_date, 'end_date': end_date, 'ticker_list': ticker_list, 'ticker_type': ticker_type, 'projection': projection, 'nearest': nearest, 'real_time': real_time})

    def search(
        self,
        conditions: list[list[str, str, Any]],
        fields: list[str] | None = None,
        order_by: str | None = None,
        limit: int | None = Undefined,
        date: str | Date = Undefined,
        path: str = ''
    ) -> list[dict]:
        """
        Search assets via Market Data Beta with dynamic filters.

        Args:
            *conditions: Each condition is a list or tuple with (field, operator, value). Example: ('cnpj_fundo', '=', '56903183000100')
            fields (list[str]): List of fields to include in the response.
            order_by (str): Field to order the results by. Prefix with '-' for descending order (e.g., '-columnA').
            limit (int): Limit the number of results.
            date (str | Date): The date to search for.
            path (str): The path to search for.

        Returns:
            list[dict]: The search results.

        """
        return self.get_response(self_obj=self, params={'conditions': conditions, 'fields': fields, 'order_by': order_by, 'limit': limit, 'date': date, 'path': path})

    def get_currencies(self) -> dict:
        """
        Get the currencies information from the Market Data engine.

        Returns:
            dict: A dictionary with the currencies information.

        Example:
            >>> from everysk.sdk.engines import MarketData

            >>> market_data = MarketData()
            >>> currencies = market_data.currencies()
            >>> currencies
            {
                'base_currencies': [
                    ["AED", "Uae Dirham/Us Dollar Fx Spot Rate"],
                    ["USD", "Us Dollar/Us Dollar Fx Spot Rate"],
                    ...
                ],
                'crypto_currencies': [
                    ["BTC", "Bitcoin"],
                    ["ETH", "Ethereum"],
                    ...
                ],
            }

        """
        return self.get_response(self_obj=self)


class MarketDataPublic:
    ## Public attributes
    cache_timeout: int = 60 * 60 * 24 # Timeout for cache 24 hours
    http_timeout: int = 30 # Timeout for HTTP requests 30 seconds

    ## Private methods
    def _get_server_url(self) -> str:
        """ Get the public URL for the Market Data engine. """
        return settings.MARKET_DATA_PUBLIC_URL

    def _get_response(self, url: str, params: dict) -> dict:
        """
        Get the response from the Market Data engine.

        Args:
            url (str): The URL to send the request to.
            params (dict): The parameters to include in the request.
        """
        with HttpGETConnection(url=url, timeout=self.http_timeout, params=params) as conn:
            response = conn.get_response()

        return response.json()

    # To use lru_cache, don't use unhashable types like dict or list as params.
    @lru_cache(maxsize=128)
    def _get_response_cache(self, endpoint: str, **params: dict) -> list[dict[str, str]]:
        """
        Get the cached response from the Market Data engine or fetch a new one.

        Args:
            endpoint (str): The API endpoint to call.
            params (dict): The parameters to include in the request.
        """
        if 'limit' not in params:
            params['limit'] = '*'

        url = f'{self._get_server_url()}/{endpoint}'
        return self._get_response(url=url, params=params)

    ## Public methods
    def get_countries(self, **params) -> list[dict[str, str]]:
        """
        Get all countries information from the Market Data.
        Fields: code, created_at, currency, name, region, updated_at

        Args:
            fields (list[str]): The fields to include in the response.
            order_by (str): The field to order the results by.
            limit (int): The maximum number of results to return.
        """
        params['order_by'] = params.get('order_by', 'code__asc')
        return self._get_response_cache(endpoint='countries', **params)

    def get_cryptos(self, **params) -> list[dict[str, str]]:
        """
        Get all crypto information from the Market Data.
        Fields: code, created_at, mkt_cap, name, status, updated_at, vendor_symbol, volume

        Args:
            fields (list[str]): The fields to include in the response.
            order_by (str): The field to order the results by.
            limit (int): The maximum number of results to return.
        """
        params['order_by'] = params.get('order_by', 'code__asc')
        return self._get_response_cache(endpoint='cryptos', **params)

    def get_currencies(self, **params) -> list[dict[str, str]]:
        """
        Get all currency information from the Market Data.
        Fields: code, created_at, name, status, updated_at

        Args:
            fields (list[str]): The fields to include in the response.
            order_by (str): The field to order the results by.
            limit (int): The maximum number of results to return.
        """
        params['order_by'] = params.get('order_by', 'code__asc')
        return self._get_response_cache(endpoint='currencies', **params)

    def get_exchanges(self, **params) -> list[dict[str, str]]:
        """
        Get all exchange information from the Market Data.
        Fields: country, created_at, description, exchange_type, mic, updated_at

        Args:
            fields (list[str]): The fields to include in the response.
            order_by (str): The field to order the results by.
            limit (int): The maximum number of results to return.
        """
        params['order_by'] = params.get('order_by', 'mic__asc')
        return self._get_response_cache(endpoint='exchanges', **params)

    def get_holidays(self, **params) -> list[dict[str, str]]:
        """
        Get all holiday information from the Market Data.
        Fields: calendar, created_at, date, description, updated_at, year
        If some range is needed you can use year__gt=2024, year__lt=2026.

        Args:
            fields (list[str]): The fields to include in the response.
            order_by (str): The field to order the results by.
            limit (int): The maximum number of results to return.
        """
        params['order_by'] = params.get('order_by', 'date__asc')
        return self._get_response_cache(endpoint='holidays', **params)
