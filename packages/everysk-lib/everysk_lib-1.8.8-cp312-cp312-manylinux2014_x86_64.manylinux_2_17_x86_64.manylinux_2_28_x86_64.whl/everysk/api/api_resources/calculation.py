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
from everysk.api import utils
from everysk.api.api_resources.api_resource import APIResource

###############################################################################
#   Calculation Implementation
###############################################################################
class Calculation(APIResource):
    """
    A class representing calculations for financial analysis.

    This class inherits from APIResource and provides methods for executing various financial calculations and analyses.
    """
    def refresh(self): # pylint: disable=arguments-differ
        """
        Refreshes the calculation instance.
        This method refreshes the calculation instance by performing any necessary updates or recalculations.

        Returns:
            Calculation: The refreshed calculation instance.

        Example:
            >>> from everysk.api.api_resources.calculation import Calculation
            >>> data = {'param1', 'param2'}
            >>> retrieve_params = {'some': 'data'}
            >>> calculation = Calculation(retrieve_params, data)
            >>> calculation.refresh()
        """
        return self

    @classmethod
    def class_name(cls) -> str:
        """
        This method returns the class name 'calculations'.

        Returns:
            str: 'calculations'

        Example:
            >>> from everysk.api.api_resources.calculation import Calculation
            >>> Calculation.class_name()
            >>> 'calculations'
        """
        return 'calculations'

    @classmethod
    def class_url(cls) -> str:
        """
        This method returns the class URL in the following format: '/calculations'.

        Returns:
            str: '/calculations'

        Example:
            >>> from everysk.api.api_resources.calculation import Calculation
            >>> url = Calculation.class_url()
            >>> print(url)
            >>> '/calculations'
        """
        return f'/{cls.class_name()}'

    @classmethod
    def __call_method(cls, method, **kwargs):
        """
        Generic helper method to call various calculation methods on the API. This method acts as a central
        dispatcher that sends requests to different calculation endpoints based on the 'method' argument. The
        specific parameters for each calculation should be passed as keyword arguments, which will vary depending
        on the calculation method being called.

        Args:
            method:
                The calculation method to call. This should match one of the API's available endpoints.

            **kwargs:
                Additional keyword arguments. The contents and requirements of kwargs will depend on the specific API method being invoked.

        Returns:
            dict: The response from the API
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{method}'
        response = api_req.post(url, kwargs)
        return response

    @classmethod
    def riskAttribution(cls, **kwargs): # pylint: disable=invalid-name
        """
        Performs a risk attribution analysis on a specified portfolio or a set of securities. This method calculates and
        attributes the portfolio's risk based on the following parameters

        Args:
            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label.
                `securities` is not required if `portfolio_id` is being provided, check https://everysk.com/api/docs/#-a-name-securities-a-securities for more info.

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency, check https://support.everysk.com/hc/en-us/articles/115005366147-Supported-Currencies to see all the available currencies.

            nlv (float, optional):
                The net liquidating value of the portfolio (also known as NAV).

            horizon (int, optional):
                Simulates the behavior of each security via their underlying risk factors. It accepts 1, 5 20, or 60.
                For more information, check https://support.everysk.com/hc/en-us/articles/360016288574-Simulation-Horizon

            sampling (int, optional):
                refers to the collection frequency of historical prices and rates to calculate invariant risk factors. Use 1 for daily sampling and 5 for weekly (non-overlapping) sampling.
                Accepted values are 1 or 5. Click here for different horizon and sampling combinations.

            aggregation (str, optional):
                Computes individual security MCTR's and aggregates them according to a supported criteria.
                Check https://support.everysk.com/hc/en-us/sections/360003156634-Risk-Aggregations for more information

            projection (list, optional):
                User supplied array of securities to be used as a top-down factor model. Maximum number of elements in the projection list is 15

            volatility_half_life (int, optional):
                Half life of volatility information in the following months: 0 (no decay), 2, 6, 12, 24, or 48.

            correlation_half_life (int, optional):
                Half life of correlation information in months: 0 (no decay), 2, 6, 12, 24 or 48.

            risk_measure (str, optional):
                MCTR measures forward-looking portfolio risk properties: vol (annualized portfolio P&L volatility), var (portfolio P&L Value-at-Risk), and cvar (portfolio P&L Conditional Value-at-Risk).

            filter (str, optional):
                Selects portfolio identifiers meeting specific criteria, like isolating fixed income securities. It computes across the entire portfolio but displays results only for the filtered subset
                For additional information, click here: https://everysk.com/api/docs/#-a-name-filters-a-filter-expression

            **kwargs: Additional keyword arguments

        Returns:
            dict: The risk attribution result
        """
        return cls.__call_method('risk_attribution', **kwargs)

    @classmethod
    def parametricRiskAttribution(cls, **kwargs): # pylint: disable=invalid-name
        """
        Calculates the magnitude of a security's reaction to changes in underlying factors, most often in terms of its price to other factors.
        `securities` is not required if `portfolio_id` is being provided.

        Args:
            id (str):
                string used to identify the portfolio

            projection (list):
                User supplied array of securities to be used as a top-down factor model. Maximum number of elements in the projection array is 15.

            portfolio_id (str, optional):
                It is the ID of and existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency and nlv.

            securities (list):
                Array of objects used to describe the securities in the portfolio. Each object has its own ID, symbol, quantity, and label.

            use_cashflow (boolean, optional):
                For fixed income securities, setting the flag to True maps each cash flow event (like interest or principal payments) to specific points on the interest rate curve.
                If False, it uses Macaulay duration to link bond price to adjacent points on the curve.

            sampling (int, optional):
                refers to the collection frequency of historical prices and rates to calculate invariant risk factors. Use 1 for daily sampling and 5 for weekly (non-overlapping) sampling.
                Accepted values are 1 or 5. Click here for different horizon and sampling combinations.

            confidence (str, optional):
                Determines the confidence level for calculation VaR and CVaR. Values accepted: `1sigma`, `2sigma`, `3sigma`, `85%`, `90%`, `95%`, `97%`, or `99%`.
                For additional information click here: https://everysk.com/api/docs/#-a-name-confidence-a-confidence

            historical_days (str, optional):
                Number of business days used to calculate the covariance for the primitive risk factors: `0 (no decay)`, `2`, `6`, `12`, `24` or `48`.

            exponential_decay (float, optional):
                Factor used in the exponentially weighted moving average (ewma): 0 (no decay); it accepts float values from 0 to 1.

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The parametric risk attribution result.
        """
        return cls.__call_method('parametric_risk_attribution', **kwargs)

    @classmethod
    def stressTest(cls, **kwargs): # pylint: disable=invalid-name
        """
        Stress Test calculates the expected behavior of the portfolio under different scenarios, including extreme events.
        For instance, it takes into account that correlations and volatility tend to increase in periods of market distress.

        Args:
            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency.

            nlv (float, optional):
                The net liquidating value of the portfolio (also known as NAV).

            horizon (int, optional):
                Simulates the behavior of each security via their underlying risk factors. It accepts 1, 5 20, or 60.

            sampling (int, optional):
                refers to the collection frequency of historical prices and rates to calculate invariant risk factors. Use 1 for daily sampling and 5 for weekly (non-overlapping) sampling.
                Accepted values are 1 or 5. Click here for different horizon and sampling combinations.

            aggregation (str, optional):
                Computes individual security MCTR's and aggregates them according to a supported criteria.
                Check https://support.everysk.com/hc/en-us/sections/360003156634-Risk-Aggregations for more information

            projection (list, optional):
                User supplied array of securities to be used as a top-down factor model. Maximum number of elements in the projection list is 15

            volatility_half_life (int, optional):
                Half life of volatility information in the following months: 0 (no decay), 2, 6, 12, 24, or 48.

            correlation_half_life (int, optional):
                Half life of correlation information in months: 0 (no decay), 2, 6, 12, 24 or 48.

            shock (str, optional):
                The security being used for the stress test.

            magnitude (file):
                The magnitude of the shock. For more details click here: https://everysk.com/api/docs/#-a-name-magnitude-a-magnitude

            confidence (str, optional):
                Determines the confidence level for calculation VaR and CVaR. Values accepted: `1sigma`, `2sigma`, `3sigma`, `85%`, `90%`, `95%`, `97%`, or `99%`.
                For additional information click here: https://everysk.com/api/docs/#-a-name-confidence-a-confidence

            filter (str, optional):
                Selects portfolio identifiers meeting specific criteria, like isolating fixed income securities. It computes across the entire portfolio but displays results only for the filtered subset
                For additional information, click here: https://everysk.com/api/docs/#-a-name-filters-a-filter-expression

            **kwargs (dict):
                Additional keyword arguments.

        Returns:
            dict: The stress test result.
        """
        return cls.__call_method('stress_test', **kwargs)

    @classmethod
    def exposure(cls, **kwargs):
        """
        Calculates the delta-adjusted notional exposure of each security, converted to the base currency of the portfolio.
        To compute the exposures for a portfolio, make an HTTP POST to your calculation resource URI: `POST /calculations/exposure`

        Args:
            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency.

            nlv (float, optional):
                The net liquidating value of the portfolio (also known as NAV).

            sampling (int, optional):
                refers to the collection frequency of historical prices and rates to calculate invariant risk factors. Use 1 for daily sampling and 5 for weekly (non-overlapping) sampling.
                Accepted values are 1 or 5. Click here for different horizon and sampling combinations.

            aggregation (str, optional):
                Computes individual security MCTR's and aggregates them according to a supported criteria.
                Check https://support.everysk.com/hc/en-us/sections/360003156634-Risk-Aggregations for more information

            filter (str, optional):
                Selects portfolio identifiers meeting specific criteria, like isolating fixed income securities. It computes across the entire portfolio but displays results only for the filtered subset
                For additional information, click here: https://everysk.com/api/docs/#-a-name-filters-a-filter-expression

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The exposure calculation result.
        """
        return cls.__call_method('exposure', **kwargs)

    @classmethod
    def properties(cls, **kwargs):
        """
        Calculates the overall portfolio properties with a single API call.
        Sensitivities, exposures and risk are aggregated from individual securities to a portfolio level.

        Args:
            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency.

            nlv (float, optional):
                The net liquidating value of the portfolio (also known as NAV).

            horizon (int, optional):
                Simulates the behavior of each security via their underlying risk factors. It accepts 1, 5 20, or 60.

            sampling (int, optional):
                refers to the collection frequency of historical prices and rates to calculate invariant risk factors. Use 1 for daily sampling and 5 for weekly (non-overlapping) sampling.
                Accepted values are 1 or 5. Click here for different horizon and sampling combinations.

            aggregation (str, optional):
                Computes individual security MCTR's and aggregates them according to a supported criteria.
                Check https://support.everysk.com/hc/en-us/sections/360003156634-Risk-Aggregations for more information

            projection (list, optional):
                User supplied array of securities to be used as a top-down factor model. Maximum number of elements in the projection list is 10.

            volatility_half_life (int, optional):
                Half life of volatility information in the following months: 0 (no decay), 2, 6, 12, 24, or 48.

            correlation_half_life (int, optional):
                Half life of correlation information in months: 0 (no decay), 2, 6, 12, 24 or 48.

            confidence (str, optional):
                Determines the confidence level for calculation VaR and CVaR. Values accepted: `1sigma`, `2sigma`, `3sigma`, `85%`, `90%`, `95%`, `97%`, or `99%`.
                For additional information click here: https://everysk.com/api/docs/#-a-name-confidence-a-confidence

            **kwargs (dict):
                Additional keyword arguments.

        Returns:
            dict: The calculation properties.
        """
        return cls.__call_method('properties', **kwargs)

    @classmethod
    def backtest(cls, **kwargs):
        """
        Performs a backtest on the provided portfolio using specified parameters.

        Args:
            user_id (int):
                The ID of the user performing the backtest.

            user_role (str):
                The role of the user, which can influence the backtest computation based on access rights.

            time_zone (str):
                User's time zone, used for aligning the timestamps in the backtest results.

            backtest_date1 (str):
                The start date for the backtest period.

            backtest_date2 (str):
                The end date for the backtest period.

            backtest_periodicity (str):
                The periodicity of the backtest calculations (e.g., daily, weekly, monthly).

            backtest_benchmark_ticker (str):
                The ticker symbol of the benchmark against which to compare the portfolio's performance.

            backtest_rfrate_ticker (str):
                The ticker symbol for the risk-free rate used in the backtest.

            projection_tickers (list):
                A list of tickers used for projections in the backtest.

            output_type (str):
                The type of output expected from the backtest (e.g., full, summary).

            **kwargs (dict):
                Additional keyword arguments that can be passed to the backtest function.

        Returns:
            dict: The backtest result.

        Example:
            >>> backtest_results = ClassName.backtest(
            >>> ... user_id=123,
            >>> ... user_role='analyst',
            >>> ... time_zone='EST',
            >>> ... backtest_date1='2020-01-01',
            >>> ... backtest_date2='2020-12-31',
            >>> ... backtest_periodicity='monthly',
            >>> ... backtest_benchmark_ticker='SPY',
            >>> ... backtest_rfrate_ticker='US10Y',
            >>> ... output_type='summary'
            >>> )
            >>> print(backtest_results)
        """
        return cls.__call_method('backtest', **kwargs)

    @classmethod
    def backtestStatistics(cls, **kwargs): # pylint: disable=invalid-name
        """
        Retrieves backtest statistics by executing a backtest based on the provided parameters.
        This method internally calls a function to compute backtest statistics and returns a detailed result dict.

        Args:
            user_id (int):
                The ID of the user performing the backtest. This is essential for accessing and
                manipulating the user's data securely.

            user_role (str):
                The role of the user which can influence the level of detail and data accessible in the backtest results.

            time_zone (str):
                The user's time zone, which is crucial for aligning the time-sensitive data in the backtest.

            backtest_date1 (str):
                The starting date for the backtest period, used to delineate the time range for the analysis.

            backtest_date2 (str):
                The ending date for the backtest period, defining the closure of the analysis interval.

            backtest_periodicity (str):
                Specifies the frequency of data points (e.g., daily, weekly, monthly) used in the backtest.

            backtest_benchmark_ticker (str):
                Ticker symbol for the benchmark index against which the portfolio is evaluated.

            backtest_rfrate_ticker (str):
                Ticker symbol for the risk-free rate, used in certain financial metrics and calculations.

            projection_tickers (list):
                List of ticker symbols used for projecting the portfolio's performance.

            output_type (str):
                Determines the format of the output (e.g., 'full', 'summary', 'detailed').

            **kwargs (dict):
                Additional keyword arguments that can influence the backtest computation and its results.

        Returns:
            dict: The backtest statistics.

        Example:
            >>> backtest_results = ClassName.backtestStatistics(
            >>> ... user_id=12345,
            >>> ... user_role='analyst',
            >>> ... time_zone='GMT',
            >>> ... backtest_date1='2021-01-01',
            >>> ... backtest_date2='2021-12-31',
            >>> ... backtest_periodicity='monthly',
            >>> ... backtest_benchmark_ticker='SPY',
            >>> ... backtest_rfrate_ticker='US10Y',
            >>> ... output_type='summary'
            >>> ... )
            >>> print(backtest_results)
        """
        return cls.__call_method('backtest_statistics', **kwargs)

    @classmethod
    def aggregations(cls, **kwargs):
        """
        Performs financial aggregations on a user's portfolio to generatea summary statistics and insights.
        This method calculates aggregated data points based on the provided portfolio.

        Args:
            user_id (int):
                The ID of the user for whom the aggregation is being performed. Essential for identifying
                the user's data and ensuring data security.

            user_role (str):
                The role of the user, which can define access levels and influence the aggregation results.

            user_settings (dict):
                User-specific settings that can affect the aggregation, such as preferences or configurations.

            portfolio (Portfolio):
                The user's portfolio object on which the aggregation is to be performed.

            output_type (str):
                Specifies the format in which the output is generated, e.g., 'summary', 'detailed'.

            **kwargs (dict):
                Additional keyword arguments that can be used to pass extra parameters necessary for
                the aggregation process.

        Returns:
            dict: The aggregation result.

        Example:
            >>> aggregation_results = ClassName.aggregations(
            >>> ... user_id=12345,
            >>> ... user_role='manager',
            >>> ... user_settings={'setting1': 'value1', 'setting2': 'value2'},
            >>> ... portfolio=portfolio_object,
            >>> ... output_type='detailed'
            >>> )
            >>> print(aggregation_results)
        """
        return cls.__call_method('aggregations', **kwargs)

    @classmethod
    def fundamentals(cls, **kwargs):
        """
        Retrieves fundamental data.

        Args:
            user_id (int):
                The ID of the user for whom the fundamental data is being retrieved. It ensures the
                personalized and secure access to the necessary data.

            user_role (str):
                The role of the user, which may influence the scope of the retrieved fundamental data.

            user_settings (dict):
                Settings that provide context on user preferences or configurations, impacting
                how fundamental data is calculated and presented.

            portfolio (Portfolio):
                The portfolio object for which fundamentals are being calculated.

            projection_tickers (list):
                List of tickers for which the user seeks to project fundamental data.

            output_type (str):
                Determines the format and detail level of the output, such as 'summary' or 'detailed'.

            **kwargs (dict):
                Additional keyword arguments allowing for further customization of the fundamental data retrieval.

        Returns:
            dict: The fundamental data.

        Example:
            >>> fundamental_data = ClassName.fundamentals(
            >>> ... user_id=12345,
            >>> ... user_role='analyst',
            >>> ... user_settings={'currency': 'USD', 'fiscal_period': 'Q1'},
            >>> ... portfolio=portfolio_object,
            >>> ... output_type='detailed'
            >>> )
            >>> print(fundamental_data)
        """
        return cls.__call_method('fundamentals', **kwargs)

    @classmethod
    def daysToUnwind(cls, **kwargs): # pylint: disable=invalid-name
        """
        Calculates the number of days required to unwind a position in the portfolio, considering the liquidity of each
        asset. This calculation can help in assessing the market risk associated with the portfolio's current composition.

        Args:
            user_id (int):
                The ID of the user for whom the calculation is performed. Ensures that the computation is
                personalized and secure.

            user_role (str):
                The role of the user, impacting the level of detail and type of data accessible in the results.

            user_settings (dict):
                Settings that influence the computation, such as risk preferences or market assumptions.

            portfolio (Portfolio):
                The portfolio object for which the days to unwind are being calculated.

            days (list):
                A list of days over which the unwind period is considered. Must be provided explicitly.

            liquidity_terms (object, optional):
                An object defining the terms for liquidity calculation, such as market impact.
                If not provided, a default set of terms is used.

            **kwargs (dict): Additional keyword arguments to fine-tune the calculation or provide extra context.

        Returns:
            dict: The days to unwind calculation result.

        Example:
            >>> unwind_data = ClassName.daysToUnwind(
            >>> ... user_id=12345,
            >>> ... user_role='analyst',
            >>> ... user_settings={'market_conditions': 'normal'},
            >>> ... portfolio=portfolio_object,
            >>> ... days=[10, 20, 30],
            >>> ... liquidity_terms={'market_impact': 0.5}
            )
            >>> print(unwind_data)
        """
        return cls.__call_method('days_to_unwind', **kwargs)

    @classmethod
    def sensitivity(cls, **kwargs):
        """
        Calculates sensitivity. `securities` parameter is not required if `portfolio_id` is being provided.
        Click here for more info https://everysk.com/api/docs/#-a-name-securities-a-securities

        Args:
            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label

            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency. To see all supported currencies click here => https://support.everysk.com/hc/en-us/articles/115005366147-Supported-Currencies

            sensitivity_type (str, optional):
                The sensitivity type. Check https://everysk.com/api/docs/#sensitivity for the accepted values.

            compute_notional (boolean, optional):
                Determines whether sensitivities should be weighted by the notional exposure or unitized.

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The sensitivity calculation result.
        """
        return cls.__call_method('sensitivity', **kwargs)

    @classmethod
    def underlying_stress_sensitivity(cls, **kwargs):
        """
        Calculates sensitivity for each underlying stress scenario.
        `securities` parameter is not required if `portfolio_id` is being provided.
        Click here for more info https://everysk.com/api/docs/#-a-name-securities-a-securities

        Args:
            securities (list):
                Array of objects to describe the securities in the portfolio. Each object, represents a security with a unique id, symbol, quantity and label

            stress_values (list[float]):
                How much should the underlying values be stressed by in percentages. (0.01, 0, 0.05)

            portfolio_id (str, optional):
                ID of an existing portfolio. When passing a portfolio's ID as parameter the calculation will be performed using the given portfolio's securities, date, base currency, and nlv.

            date (str date, optional):
                Date in the following format: `YYYYMMDD`. The date instructs the API to use the market conditions and security prices prevailing on that date.

            base_currency (str, optional):
                3-letter ISO 4217 code for currency. To see all supported currencies click here => https://support.everysk.com/hc/en-us/articles/115005366147-Supported-Currencies

            sensitivity_type (str, optional):
                The sensitivity type. Check https://everysk.com/api/docs/#sensitivity for the accepted values.

            compute_notional (boolean, optional):
                Determines whether sensitivities should be weighted by the notional exposure or unitized.

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The sensitivity calculation result.
        """
        return cls.__call_method('underlying_stress_sensitivity', **kwargs)

    @classmethod
    def optimize(cls, **kwargs):
        """
        Executes an optimization calculation for a given portfolio, applying specified user settings and constraints.

        Args:
            user_id (int):
                The ID of the user for whom the optimization is being performed, ensuring personalized
                and secure processing.

            user_role (str):
                The role of the user, which may affect the optimization process and results.

            user_settings (dict):
                Configuration settings specific to the user that can influence the optimization.

            portfolio (Portfolio):
                The portfolio object to be optimized.

            optimization_model (str):
                The model used for optimization. The default model is specified if not provided.

            optimization_date (str):
                The target date for the optimization. The date affects the data used in the optimization process.

            constraints (object):
                An object defining the constraints to be applied during the optimization.

            to_model_portfolio (bool, optional):
                Flag indicating whether the output should be a model portfolio.

            **kwargs (dict):
                Additional keyword arguments allowing for further customization and specification of the optimization process.

        Returns:
            dict: The optimization result.

        Example:
            >>> optimization_result = ClassName.optimize(
            >>> ... user_id=12345,
            >>> ... user_role='analyst',
            >>> ... user_settings={'risk_tolerance': 'medium', 'objective': 'minimize_risk'},
            >>> ... portfolio=portfolio_object,
            >>> ... optimization_model='mean_variance',
            >>> ... optimization_date='2023-01-01',
            >>> ... constraints={'max_weight': 0.1}
            >>> )
            >>> print(optimization_result)
        """
        return cls.__call_method('optimize', **kwargs)

    @classmethod
    def bondPricer(cls, **kwargs): # pylint: disable=invalid-name
        """
        Calculate the price of a bond based on its bond-specific parameters.

        Args:
            portfolio (str):
                The portfolio that is going to be analyzed.

            m2m_spreads (object):
                Mark to market spreads mapping for each fixed income security in the form: {"symbol": fee, ...}

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The dictionary with the pricing (PU) for each fixed income security.
        """
        return cls.__call_method('bond_pricer', **kwargs)

    @classmethod
    def marginalTrackingError(cls, **kwargs): # pylint: disable=invalid-name
        """
        Tracking error is the divergence between the price behavior of a position or a portfolio and the price behavior fo a benchmark.

        Args:
            portfolio1 (str):
                The portfolio that is going to be analyzed.

            portfolio2 (str):
                The portfolio that is going the be used as a benchmark to calculate the deviation of differences.

            weekly (boolean, optional):
                The Calculation API will use weekly return to calculate the tracking error.

            EWMA (boolean, optional):
                The default is False, if `True`, the exponentially weighted moving average will be applied to volatilities.

            exponential_decay (float, optional):
                Weighting factor determining the rate at which "older" data enter into the calculation of the `EWMA`.
                It accepts float values from 0 to 1.
                This parameter is only used when `EWMA` is True

            nDays (int, optional):
                Number of historical business days used in calculation when `weekly` is False

            nWeeks (int, optional):
                Number of historical weeks used in calculation when `weekly` is True

            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The marginal tracking error calculation result.
        """
        return cls.__call_method('marginal_tracking_error', **kwargs)
