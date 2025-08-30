# -*- coding: utf_8 -*-
###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Callable, Any, Self

from everysk.config import settings
from everysk.core.datetime import Date, DateTime
from everysk.core.fields import DateField, DictField, FloatField, ListField, StrField
from everysk.core.object import BaseDict, BaseDictConfig, CLASS_KEY
from everysk.core.exceptions import FieldValueError
from everysk.sdk.engines import cryptography
from everysk.sdk.entities.base import BaseSDK


###############################################################################
#   ExtraDataField Class Implementation
###############################################################################
class ExtraDataField(DictField):

    def clean_value(self, value: Any) -> Any:
        """
        This function is used to clean the value before it is assigned to the field.
        It can be used to ensure consistency in the data.
        """
        if isinstance(value, dict):
            value = BaseDict(**value)

        return super().clean_value(value)


###############################################################################
#   Security Class Implementation
###############################################################################
class Security(BaseDict, BaseSDK):
    """
    This class represents a security entity and its attributes.

    Attributes:
        status (StrField): The status of the security.
        id (StrField): The unique identifier of the security.
        symbol (StrField): The symbol of the security.
        quantity (FloatField): The quantity of the security.
        instrument_class (StrField): The class of the instrument.
        ticker (StrField): The ticker symbol of the security.
        label (StrField): The label of the security.
        name (StrField): The name of the security.
        isin (StrField): The ISIN (International Securities Identification Number) of the security.
        exchange (StrField): The exchange where the security is traded.
        currency (StrField): The currency of the security.
        fx_rate (FloatField): The foreign exchange rate of the security.
        market_price (FloatField): The market price of the security.
        premium (FloatField): The premium associated with the security.
        market_value (FloatField): The market value of the security.
        market_value_in_base (FloatField): The market value of the security in the base currency.
        instrument_type (StrField): The type of instrument.
        instrument_subtype (StrField): The subtype of the instrument.
        asset_class (StrField): The asset class of the security.
        asset_subclass (StrField): The asset subclass of the security.
        error_type (StrField): The type of error associated with the security.
        error_message (StrField): The error message associated with the security.
        maturity_date (DateField): The maturity date of the security.
        indexer (StrField): The indexer used for the security.
        percent_index (FloatField): The percentage index value.
        rate (FloatField): The rate value.
        coupon (FloatField): The coupon value.
        multiplier (FloatField): The multiplier value.
        underlying (StrField): The underlying asset of the security.
        series (StrField): The series of the security.
        option_type (StrField): The type of option (if applicable).
        strike (FloatField): The strike price (if applicable).
        issue_price (FloatField): The issue price of the security.
        issue_date (DateField): The issue date of the security.
        issuer (StrField): The issuer of the security.
        issuer_type (StrField): The type of issuer.
        cost_price (FloatField): The cost price of the security.
        unrealized_pl (FloatField): The unrealized profit or loss of the security.
        unrealized_pl_in_base (FloatField): The unrealized profit or loss of the security in the base currency.
        book (StrField): The book associated with the security.
        trader (StrField): The trader responsible for the security.
        trade_id (StrField): The trade identifier of the security.
        operation (StrField): The operation related to the security.
        accounting (StrField): The accounting information of the security.
        warranty (FloatField): The warranty associated with the security.
        return_date (DateField): The return date of the security.
        settlement (DateField): The settlement date of the security.
        look_through_reference (StrField): The look-through reference of the security.
        extra_data (DictField): Additional data associated with the security.
        hash (StrField): The hash value of the security.
        display (StrField): The display information of the security.
        comparable (StrField): The comparable information of the security.
        previous_quantity (FloatField): The previous quantity of the security (not sure about its use).

    Example:
        >>> security = Security()
        >>> security.symbol = 'AAPL'
        >>> security.quantity = 100
        >>> security.market_price = 150.0
        >>> security.currency = 'USD'
        >>> security.name = 'Apple Inc.'
        >>> security.status = 'OK'
        >>> security
        {
            'status': 'OK',
            'id': None,
            'symbol': 'AAPL',
            'quantity': 100.0,
            'instrument_class': None,
            'ticker': None,
            'label': None,
            'name': 'Apple Inc.',
            'isin': None,
            'exchange': None,
            'currency': 'USD',
            'fx_rate': None,
            'market_price': 150.0,
            'premium': None,
            'market_value': None,
            'market_value_in_base': None,
            'instrument_type': None,
            'instrument_subtype': None,
            'asset_class': None,
            'asset_subclass': None,
            'error_type': None,
            'error_message': None,
            'maturity_date': None,
            'indexer': None,
            'percent_index': None,
            'rate': None,
            'coupon': None,
            'multiplier': None,
            'underlying': None,
            'series': None,
            'option_type': None,
            'strike': None,
            'issue_price': None,
            'issue_date': None,
            'issuer': None,
            'issuer_type': None,
            'cost_price': None,
            'unrealized_pl': None,
            'unrealized_pl_in_base': None,
            'book': None,
            'trader': None,
            'trade_id': None,
            'operation': None,
            'accounting': None,
            'warranty': None,
            'return_date': None,
            'settlement': None,
            'look_through_reference': None,
            'extra_data': None,
            'hash': None,
            'display': None,
            'comparable': None,
            'previous_quantity': None
        }
    """
    class Config(BaseDictConfig):
        default_status = StrField(default=settings.SECURITY_STATUS_OK, readonly=True)
        valid_status = ListField(default=[settings.SECURITY_STATUS_OK, settings.SECURITY_STATUS_DELISTED], readonly=True)
        exclude_keys: frozenset[str] = frozenset(['_is_frozen', '_silent', '_errors', '_orderable_attributes'])

    _config: Config = None
    status = StrField()
    id = StrField(required_lazy=True, min_size=1, max_size=settings.SYMBOL_ID_MAX_LEN)

    symbol = StrField(required_lazy=True, max_size=settings.SYMBOL_MAX_LENGTH)
    quantity = FloatField(required_lazy=True, min_size=settings.QUANTITY_MIN_VALUE, max_size=settings.QUANTITY_MAX_VALUE)
    instrument_class = StrField()

    ticker = StrField()
    label = StrField(min_size=0, max_size=settings.LABEL_MAX_LENGTH)
    name = StrField()
    isin = StrField(min_size=0, max_size=settings.SYMBOL_MAX_LENGTH)
    exchange = StrField()
    currency = StrField()
    fx_rate = FloatField(min_size=settings.FX_RATE_MIN_VALUE, max_size=settings.FX_RATE_MAX_VALUE)
    market_price = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    premium = FloatField()
    market_value = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    market_value_in_base = FloatField()

    instrument_type = StrField()
    instrument_subtype = StrField()
    asset_class = StrField()
    asset_subclass = StrField()

    error_type = StrField(min_size=0, max_size=settings.PORTFOLIO_SECURITY_ERROR_TYPE_MAX_LEN)
    error_message = StrField(min_size=0, max_size=settings.PORTFOLIO_SECURITY_ERROR_MESSAGE_MAX_LEN)

    maturity_date = DateField(empty_is_none=True)
    indexer = StrField()
    percent_index = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    rate = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    coupon = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)

    multiplier = FloatField(min_size=settings.MULTIPLIER_MIN_VALUE, max_size=settings.MULTIPLIER_MAX_VALUE)
    underlying = StrField()
    series = StrField()
    option_type = StrField()
    strike = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)

    issue_price = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    issue_date = DateField(empty_is_none=True)
    issuer = StrField()
    issuer_type = StrField()

    cost_price = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    unrealized_pl = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)
    unrealized_pl_in_base = FloatField(min_size=settings.PRICE_MIN_VALUE, max_size=settings.PRICE_MAX_VALUE)

    book = StrField()
    trader = StrField(min_size=0, max_size=settings.PORTFOLIO_SECURITY_TYPE_MAX_LEN)
    trade_id = StrField()

    operation = StrField()
    accounting = StrField()
    warranty = FloatField(min_size=settings.QUANTITY_MIN_VALUE, max_size=settings.QUANTITY_MAX_VALUE)

    return_date = DateField(empty_is_none=True)
    settlement = DateField(empty_is_none=True)

    look_through_reference = StrField()

    extra_data = ExtraDataField(default=None)

    hash = StrField()
    display = StrField()
    comparable = StrField()

    #NOT SURE ABOUT IT
    previous_quantity = FloatField(min_size=settings.QUANTITY_MIN_VALUE, max_size=settings.QUANTITY_MAX_VALUE)

    def __init__(self, **kwargs):
        kwargs.pop('id_', None)
        kwargs.pop('mic', None)
        kwargs.pop(CLASS_KEY, None)

        # This creates the Security with all default attributes
        super().__init__()

        # We check if the extra_data is not initialized
        _extra_data = kwargs.pop('extra_data', None) or BaseDict()
        if not isinstance(_extra_data, (BaseDict, dict)):
            raise FieldValueError(f'attribute extra_data must be a dictionary. {type(_extra_data)}')

        self.extra_data = BaseDict()
        if _extra_data is not None:
            for extra_key, extra_value in _extra_data.items():
                self._add_extra_data(extra_key, extra_value)

        for key, value in kwargs.items():
            # If the key already exists in the class we just store it
            if key in self:
                self[key] = value
            # otherwise we store it inside the extra_data key.
            else:
                self._add_extra_data(key, value)

        # If for some reason the extra_data is empty we convert it to None
        if not self.extra_data:
            self.extra_data = None

    def _add_extra_data(self, key: str, value: Any) -> None:
        """
        Add an extra data attribute to the security.

        This method adds an extra data attribute to the security object by storing it in the 'extra_data' dictionary.

        Args:
            key (str): The key for the extra data attribute.
            value (Any): The value of the extra data attribute.

        Example:
            >>> security = Security()
            >>> security._add_extra_data('industry', 'Technology')
            >>> security.extra_data
            {'industry': 'Technology'}
        """
        if value is None or isinstance(value, (int, str, bool, float, Date, DateTime)):
            self.extra_data[key] = value

    def _process_maturity_date(self, value: Date) -> str:
        """
        Converts a Date object to a string.

        Args:
            value (Date): The Date object to be converted.

        Returns:
            str: The converted Date, now represented as a string.

        Example:
            >>> _process_maturity_date(Date(2023, 9, 9))
            '20230909'
        """
        return Date.strftime_or_null(value)

    def _process_issue_date(self, value: Date) -> str:
        """
        Converts a Date object to a string.

        Args:
            value (Date): The Date object to be converted.

        Returns:
            str: The converted Date, now represented as a string.

        Example:
            >>> _process_issue_date(Date(2023, 9, 9))
            '20230909'
        """
        return Date.strftime_or_null(value)

    def _process_return_date(self, value: Date) -> str:
        """
        Converts a Date object to a string.

        Args:
            value (Date): The Date object to be converted.

        Returns:
            str: The converted Date, now represented as a string.

        Example:
            >>> _process_return_date(Date(2023, 9, 9))
            '20230909'
        """
        return Date.strftime_or_null(value)

    def _process_settlement(self, value: Date) -> str:
        """
        Converts a Date object to a string.

        Args:
            value (Date): The Date object to be converted.

        Returns:
            str: The converted Data, now represented as a string.

        Example:
            >>> _process_settlement(Date(2023, 9, 9))
            '20230909'
        """
        return Date.strftime_or_null(value)

    @staticmethod
    def _get_attr(security: dict, key: str, fallback_func: Callable | None = None) -> Any:
        """
        Get an attribute value from a security dictionary with optional fallback.

        This static method attempts to retrieve a value associated with a given key from a security dictionary.
        If the key is not found in the main dictionary, it checks if the key exists in the 'extra_data' dictionary
        within the security dictionary. If the key is still not found and a fallback function is provided, the
        fallback function is called to provide a default value.

        Args:
            security (dict): A dictionary representing a security and its attributes.
            key (str): The key for the attribute value to retrieve.
            fallback_func (Callable | None, optional): A fallback function to call if the key is not found in
                the main or 'extra_data' dictionaries. Defaults to None.

        Returns:
            Any: The attribute value if found, or the result of the fallback function (if provided), or None.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> security_data = {
            ...     'symbol': 'AAPL',
            ...     'name': 'Apple Inc.',
            ...     'extra_data': {'industry': 'Technology'},
            ... }
            >>> symbol = Security._get_attr(security_data, 'symbol')
            >>> industry = Security._get_attr(security_data, 'industry')
            >>> missing_attr = Security._get_attr(security_data, 'missing_attribute', lambda: 'Unknown')
            >>> symbol
            'AAPL'
            >>> industry
            'Technology'
            >>> missing_attr
            'Unknown'
        """
        if key in security:
            return security[key]

        extra_data: dict = security['extra_data'] or {}
        if key in extra_data:
            return extra_data[key]

        if fallback_func is not None:
            return fallback_func()

        return None

    @staticmethod
    def generate_security_id() -> str:
        """
        Generate a unique security ID.

        This static method generates a unique security ID by combining a prefix specified in
        'settings.SECURITY_ID_PREFIX' with a unique identifier of a specified length
        using the 'cryptography.generate_unique_id' function.

        Returns:
            str: A unique security ID.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> unique_id = Security.generate_security_id()
            >>> unique_id
            'SEC123456789'
        """
        return f'{settings.SECURITY_ID_PREFIX}{cryptography.generate_random_id(length=settings.SECURITY_ID_LENGTH)}'

    @staticmethod
    def sort_header(header: list[str]) -> list[str]:
        """
        Sort a header list based on a predefined order of properties.

        This static method takes a list of header strings and sorts them based on a predefined order
        specified in `settings.PORTFOLIO_PROPERTIES_ORDER`. Properties that are not found in the predefined
        order are sorted alphabetically at the end.

        Args:
            header (list[str]): A list of header strings to be sorted.

        Returns:
            list[str]: A sorted list of header strings.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> header = ['symbol', 'name', 'price', 'quantity']
            >>> sorted_header = Security.sort_header(header)
            >>> sorted_header
            ['quantity', 'name', 'price', 'symbol']
        """

        def sorting_key(element: str) -> tuple[int, str]:
            try:
                return (settings.PORTFOLIO_PROPERTIES_ORDER.index(element), '')
            except ValueError:
                return (len(settings.PORTFOLIO_PROPERTIES_ORDER), element)

        return sorted(header, key=sorting_key)

    def generate_consolidation_key(self, consolidation_keys: str) -> str:
        """
        Generate a consolidation key based on specified attributes.

        This method generates a consolidation key by extracting values from the security object
        based on the provided consolidation keys. It uses the `_get_attr` method to retrieve
        attribute values, and if a value is missing, it falls back to generating a security ID.

        Args:
            consolidation_keys (str): A string containing comma-separated attribute keys used for consolidation.

        Returns:
            str: The consolidation key generated from the specified attributes.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> security_data = {
            ...     'symbol': 'AAPL',
            ...     'name': 'Apple Inc.',
            ...     'industry': 'Technology',
            ...     'extra_data': {'country': 'USA'}
            ... }
            >>> security = Security(security_data)
            >>> consolidation_keys = 'symbol,name,industry,country'
            >>> consolidation_key = security.generate_consolidation_key(consolidation_keys)
            >>> consolidation_key
            'AAPL_Apple Inc._Technology_USA'
        """
        key_: list[Any] = [Security._get_attr(self, key, fallback_func=self.generate_security_id) for key in consolidation_keys]
        key: str = "_".join(str(v) for v in key_)

        return key

    @staticmethod
    def from_list(sec_as_list: list[Any], headers: list[str]) -> Self:
        """
        Create a Security object from a list of values and corresponding headers.

        This static method takes a list of values representing a security's attributes and a list
        of headers specifying the order of attributes. It constructs a Security object using the
        provided values and headers.

        Args:
            sec_as_list (list[Any]): A list of attribute values for the security.
            headers (list[str]): A list of headers specifying the order of attributes.

        Returns:
            Self: A new Security object initialized with the provided attribute values.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> sec_as_list = ['AAPL', 'Apple Inc.', 150.0, 100]
            >>> headers = ['symbol', 'name', 'market_price', 'quantity']
            >>> security = Security.from_list(sec_as_list, headers)
            >>> security
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'market_price': 150.0,
                'quantity': 100
            }
        """
        return Security(**dict(zip(headers, sec_as_list)))

    def validate_required_fields(self) -> bool:
        """
        Validate the required fields of the Security object.

        This method checks if the 'id' attribute is present in the Security object. If not, it generates
        a security ID using the 'generate_security_id' method and assigns it to the 'id' attribute.
        Then, it calls the superclass method to validate other required fields.

        Returns:
            bool: True if all required fields are valid, False otherwise.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> security = Security()
            >>> security.name = 'Apple Inc.'
            >>> security.quantity = 100
            >>> security.market_price = 150.0
            >>> security.validate_required_fields()
            True
        """
        if self.get('id', None) is None:
            self.id = self.generate_security_id()

        return super().validate_required_fields()

    def to_list(self, header: list[str] | None = None) -> list[Any]:
        """
        Convert the Security object to a list of attribute values.

        This method converts the Security object and its attributes to a list of values.
        The order of attributes in the list is determined by the 'header' parameter.
        If 'header' is not provided, it defaults to the sorted order specified by the
        'Security.sort_header' method.

        Args:
            header (list[str] | None, optional): A list of attribute keys specifying the order of attributes.
                Defaults to None.

        Returns:
            list[Any]: A list of attribute values for the Security object.

        Example:
            >>> from everysk.sdk.entities.portfolio.security import Security
            >>> security = Security()
            >>> security.symbol = 'AAPL'
            >>> security.quantity = 100
            >>> security.market_price = 150.0
            >>> security.name = 'Apple Inc.'
            >>> attribute_list = security.to_list()
            >>> attribute_list
            ['AAPL', 100, 150.0, 'Apple Inc.', # ... (other attributes)]
        """
        if header is None:
            header = Security.sort_header(self.keys())

        security: dict = self.to_dict(add_class_path=False)

        return [Security._get_attr(security, key) for key in header]

    def _process_extra_data(self, value: dict | BaseDict | None) -> dict:
        """
        Process the extra data attribute.
        """
        return value.to_dict() if hasattr(value, 'to_dict') else value
