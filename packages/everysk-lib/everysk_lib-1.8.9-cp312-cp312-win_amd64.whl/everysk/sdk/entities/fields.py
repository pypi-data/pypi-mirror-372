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
from typing import Any

from everysk.config import settings
from everysk.core.datetime import DateTime
from everysk.core.fields import ChoiceField, DateTimeField, ListField, StrField, _min_max_validate
from everysk.core.log import Logger
from everysk.sdk.engines.market_data import MarketDataPublic
from everysk.sdk.entities.tags import Tags

log = Logger(name=__name__)


###############################################################################
#   CurrencyField Class Implementation
###############################################################################
class CurrencyField(ChoiceField):
    """
    A field for currency codes with validation capabilities.

    This class extends the standard ChoiceField and adds validation for the values
    added or inserted into it.
    """

    _choices: list[str] = None
    _market_data: MarketDataPublic = MarketDataPublic()

    def __init__(
        self,
        default: str = None,
        choices: list = None,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = True,
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            choices=choices,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )

    def _get_choices(self) -> set():
        """
        Get all available currencies.

        Returns:
            A list of all available currencies.
        """
        if not self._choices:
            try:
                self._choices = {
                    item['code'] for item in self._market_data.get_currencies(fields='code', status__eq='active')
                }
            except Exception as error:
                log.error('Failed to get currencies from public Market Data: %s', error)

            # If we don't have a list of currencies we set to the one in the settings
            if not self._choices:
                self._choices = set(settings.ENTITY_BASE_CURRENCY_DEFAULT_LIST)

        return self._choices


###############################################################################
#   EntityNameField Class Implementation
###############################################################################
class EntityNameField(StrField):
    """
    This class is a subclass of StrField and provides specific validation for name, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from settings).
        max_size (int): The maximum allowed size for the list (default is the value from settings).
    """

    attr_type = str

    def __init__(
        self,
        default: Any = None,
        regex: str = None,
        min_size: int = settings.ENTITY_NAME_MIN_LENGTH,
        max_size: int = settings.ENTITY_NAME_MAX_LENGTH,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = True,
        empty_is_none: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )


###############################################################################
#   EntityDescriptionField Class Implementation
###############################################################################
class EntityDescriptionField(StrField):
    """
    This class is a subclass of StrField and provides specific validation for description, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from settings).
        max_size (int): The maximum allowed size for the list (default is the value from settings).
    """

    attr_type = str

    def __init__(
        self,
        default: Any = None,
        regex: str = None,
        min_size: int = settings.ENTITY_DESCRIPTION_MIN_LEN,
        max_size: int = settings.ENTITY_DESCRIPTION_MAX_LEN,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )


###############################################################################
#   EntityLinkUIDField Class Implementation
###############################################################################
class EntityLinkUIDField(StrField):
    """
    This class is a subclass of StrField and provides specific validation for link uid, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from settings).
        max_size (int): The maximum allowed size for the list (default is the value from settings).
    """

    attr_type = str

    def __init__(
        self,
        default: Any = None,
        regex: str = None,
        min_size: int = settings.ENTITY_LINK_UID_MIN_LENGTH,
        max_size: int = settings.ENTITY_LINK_UID_MAX_LENGTH,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )


###############################################################################
#   EntityWorkspaceField Class Implementation
###############################################################################
class EntityWorkspaceField(StrField):
    """
    This class is a subclass of StrField and provides specific validation for workspace, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from settings).
        max_size (int): The maximum allowed size for the list (default is the value from settings).
    """

    attr_type = str

    def __init__(
        self,
        default: Any = None,
        regex: str = settings.ENTITY_WORKSPACE_REGEX,
        min_size: int = settings.ENTITY_WORKSPACE_MIN_LENGTH,
        max_size: int = settings.ENTITY_WORKSPACE_MAX_LENGTH,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = True,
        empty_is_none: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )


###############################################################################
#   EntityDateTimeField Class Implementation
###############################################################################
class EntityDateTimeField(DateTimeField):
    """
    This class is a subclass of StrField and provides specific validation for date, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from DateTime market start).
        max_size (int): The maximum allowed size for the list (default is one day delta from now).
    """

    attr_type = DateTime

    def __init__(
        self,
        default: Any = None,
        min_date: DateTime = None,
        max_date: DateTime = None,
        force_time: str = 'MIDDAY',
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = True,
        empty_is_none: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            default,
            min_date=min_date,
            max_date=max_date,
            force_time=force_time,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )

    def validate(self, attr_name: str, value: Any, attr_type: type = None) -> None:
        """
        Checks if value is greater than min and lower than max including both values.

        Args:
            attr_name (str): The name of the attribute being validated.
            value (Any): The value to validate.
            attr_type (type): The type of the attribute being validated.

        Raises:
            FieldValueError: If the value is not within the specified range.

        Example:
            >>> from everysk.sdk.entities.fields import EntityDateTimeField
            >>> from everysk.core.datetime.datetime import DateTime
            >>> field = EntityDateTimeField(min_date=DateTime(2023-01-01), max_date=DateTime(2023-12-31))
            >>> try:
            >>> ... field.validate("test_field", DateTime(2023, 6, 15))
            >>> ... print("Valid Date")
            >>> except Exception as e:
            >>> ... print(f"Validation error: {e}")
            >>> Valid Date
        """
        min_date = self.min_date if self.min_date is not None else DateTime.market_start()
        max_date = (
            self.max_date if self.max_date is not None else DateTime.now().delta(1, 'D').force_time('LAST_MINUTE')
        )
        _min_max_validate(min_date, max_date, value, attr_name)
        return super().validate(attr_name, value, attr_type)


###############################################################################
#   EntityTagsField Class Implementation
###############################################################################
class EntityTagsField(ListField):
    """
    This class is a subclass of ListField and provides specific validation for tags, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is the value from settings).
        max_size (int): The maximum allowed size for the list (default is the value from settings).
    """

    attr_type = Tags

    def __init__(
        self,
        default: Any = None,
        min_size: int = settings.ENTITY_MIN_TAG_SIZE,
        max_size: int = settings.ENTITY_MAX_TAG_SIZE,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        if default is not None and not isinstance(default, Tags):
            default = Tags(default)
        super().__init__(
            default=default,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        This method ensures that the provided value is in the expected format before assigning it to an attribute.
        If the value is None, it is replaced with an empty TagsList. If it is not already a TagsList instance,
        it is converted into one.

        Args:
            value (Any): The value to clean, None, A TagsList instance, or any other value.

        Example:
            >>> from everysk.sdk.entities.tags import Tags
            >>> from everysk.sdk.entities.fields import EntityTagsField
            >>> field = EntityTagsField()

            >>> cleaned_value_none = field.clean_value(None)
            >>> print(cleaned_value_none)
            >>> []

            >>> cleaned_non_empty_tags = field.clean_value(Tags(['tag1', 'tag2']))
            >>> print(cleaned_non_empty_tags)
            >>> ['tag1', 'tag2']
        """
        value = super().clean_value(value)
        if value is None:
            value = Tags()
        elif not isinstance(value, Tags):
            value = Tags(value)
        return value
