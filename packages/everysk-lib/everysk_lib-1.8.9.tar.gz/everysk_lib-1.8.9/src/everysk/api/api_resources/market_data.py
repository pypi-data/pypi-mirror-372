###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources.api_resource import APIResource
from everysk.api import utils

###############################################################################
#   Market Data Implementation
###############################################################################
class MarketData(APIResource):

    def refresh(self): # pylint: disable=arguments-differ
        """
        Refreshes the current instance of MarketData.
        """
        return self

    @classmethod
    def class_url(cls) -> str:
        """
        Returns the class URL in the following format: '/market_data'

        Returns:
            str: The class url

        Example:
            >>> from everysk.api.api_resources.market_data import MarketData
            >>> MarketData.class_url()
            >>> '/market_data'
        """
        return f'/{cls.class_name()}'

    @classmethod
    def __call_method(cls, method, **kwargs):
        """
        A generic function to call various methods on the MarketData object dynamically.
        It constructs and sends an API request based on the specified method and additional keyword arguments.

        Args:
            method (str):
                The name of the method to be called on the MarketData object.

            **kwargs:
                Variable keyword arguments that are passed to the method being called.
                These arguments should align with the expected parameters of the target method.

        Returns:
            response: The response from the API after executing the specified method with the provided arguments.
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{method}'
        response = api_req.post(url, kwargs)
        return response

    @classmethod
    def symbolsSearch(cls, **kwargs):
        """
        Searches symbols in MarketData using the user's id to verify permissions and sessions.
        The function internally calls '__call_method' with 'symbols_search' to perform the actual search operation.
        The results and their format are dependent on the implementation of the 'symbols_search' method within the MarketData object.

        Args:
            **kwargs:
                A dictionary of keyword arguments that should include, but not limited to:

            user_id (str):
                The ID of the user initiating the symbol search. It is essential for identifying the user's session and permissions.

            user_role (str, optional):
                The role of the user which may influence the search results based on role-based access controls.

            time_zone (str, optional):
                The user's time zone, potentially used to adjust the timing information in the search results.

            query (str):
                The search string used to query the symbol database. This parameter is essential for executing the search and must be provided.
        """
        return cls.__call_method('symbols_search', **kwargs)

    @classmethod
    def symbolsCheck(cls, **kwargs):
        """
        This class method checks the validity of market data symbols by invoking the 'symbols_check' method.
        It validates the symbols against the current market data and potentially other validation criteria.
        The outcome depends on the implementation of the 'symbols_check' method within the MarketData object.

        Args:
            **kwargs:
                A dictionary of keyword arguments that should include:

            securities (list):
                A list of securities to be checked. Each security should be a dictionary containing at least 'symbol' and optionally 'quantity'.

            date (str, optional):
                The date for which the securities are to be validated. Defaults to a predefined portfolio date if not specified.

            base_currency (str, optional):
                The base currency to be used for validation. Defaults to a predefined currency if not specified.

        Returns:
            dict: The symbols check data
        """
        return cls.__call_method('symbols_check', **kwargs)

    @classmethod
    def symbolsPrice(cls, **kwargs):
        """
        Retrieves market prices for specified symbols on a given date using MarketData. This method
        calls the 'symbols_price' method, passing the user's specifications for symbols and date.
        The method internally delegates the request to '__call_method' with 'symbols_price' and the provided keyword arguments.
        Which should align with the expected parameters of the 'symbols_price' method within the MarketData object.

        Args:
            **kwargs:
                A dictionary of keyword arguments that should include:

            user_id (str):
                The ID of the user requesting the price data. Essential for access control and auditing.

            user_role (str):
                The role of the user which may influence data access permissions.

            time_zone (str):
                The time zone of the user, possibly affecting the timing and relevancy of the returned data.

            symbols (list):
                A list of symbol identifiers for which prices are being retrieved. This is a mandatory argument.

            date (str, optional):
                The specific date for which the price information is requested. Defaults to a pre-defined portfolio date if not provided.

        Returns:
            dict: The symbols price data.
        """
        return cls.__call_method('symbols_price', **kwargs)

    @classmethod
    def symbolsRealtimePrice(cls, **kwargs):
        """
        Retrieves real-time price data for specified symbols using MarketData. This method is
        a wrapper around the 'symbols_real_time_prices' method, detailing the expected arguments and
        processing them to fetch real-time prices.
        This method utilizes '__call_method' to invoke 'symbols_real_time_prices' with the provided keyword arguments

        Args:
            **kwargs:
                A dictionary of keyword arguments that should include:

            user_id (str):
                The ID of the user requesting real-time price data, important for identifying the session and applying data access rules.

            user_role (str):
                The role of the user, which may affect the scope of data accessible based on permissions.

            time_zone (str):
                The time zone specification of the user, potentially relevant for time-based data adjustments.

            symbols (list):
                A list of market data symbols for which real-time prices are requested. This argument is mandatory.

        Returns:
            dict: The real time price.
        """
        return cls.__call_method('symbols_real_time_prices', **kwargs)

    @classmethod
    def symbolsHistorical(cls, **kwargs):
        """
        Retrieves historical data for specified symbols from MarketData. This method interacts
        with the 'symbols_historical' method, detailing the required arguments to fetch historical
        price information.
        The method internally calls '__call_method' with 'symbols_historical' and the provided keyword arguments.

        Args:
            **kwargs:
                A dictionary of keyword arguments that should include:
            user_id (str):
                The ID of the user requesting historical data, crucial for access control and session identification.

            user_role (str):
                The role of the user, which can influence the granularity and scope of accessible data.

            time_zone (str):
                The user's time zone, potentially important for time-aligning the returned data.

            symbols (list):
                The list of symbols for which historical data is being requested. This is a mandatory field.

            start_date (str, optional):
                The start date for the historical data retrieval.

            end_date (str, optional):
                The end date for the historical data query.

            fill_method (str, optional):
                Method to fill missing data.

            drop_na (bool, optional):
                Flag to drop or retain missing values.

            with_date_range (bool, optional):
                Include a complete date range in the response.

            periodicity (str, optional):
                The granularity of the historical data.

            vendor (str, optional):
                The data vendor source.

        Returns:
            dict: The historical data.
        """
        return cls.__call_method('symbols_historical', **kwargs)
