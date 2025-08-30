###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.config import settings

def get_api_config(params) -> tuple:
    """
    Retrieve API configuration settings from the give parameters or environment variables

    This function checks if the arguments `api_entry`, `api_version`, `api_sid`, `api_token`, and `verify_ssl_certs` are provided in the `params` dictionary.
    If not, it attempts to retrieve them from global variables or environment variables.

    Args:
        params (dict): A dictionary containing the API configuration settings

    Returns:
        tuple: A tuple containing the API entry point, version, session ID, token, and SSL certificate.

    Example:
        >>> data = {
        >>> ...     'api_entry': 'https://example.com',
        >>> ...     'api_version': 'v2',
        >>> ...     'api_sid': 'abc',
        >>> ...     'api_token': 'token_example123',
        >>> ...     'verify_ssl_certs': True
        >>> }

        >>> config = get_api_config(data)
        >>> print(config)
        ('https://example.com', 'v2', 'abc', 'token_example123', True)
    """
    api_entry = params.get('api_entry', None)
    if api_entry is None:
        api_entry = settings.EVERYSK_API_URL

    api_version = params.get('api_version', None)
    if api_version is None:
        api_version = settings.EVERYSK_API_VERSION

    api_sid = params.get('api_sid', None)
    if api_sid is None:
        api_sid = settings.EVERYSK_API_SID

    api_token = params.get('api_token', None)
    if api_token is None:
        api_token = settings.EVERYSK_API_TOKEN

    verify_ssl_certs = params.get('verify_ssl_certs', None)
    if verify_ssl_certs is None:
        verify_ssl_certs = settings.EVERYSK_API_VERIFY_SSL_CERTS

    return (api_entry, api_version, api_sid, api_token, verify_ssl_certs)

from everysk.utils import *
from everysk.api.api_resources import *
