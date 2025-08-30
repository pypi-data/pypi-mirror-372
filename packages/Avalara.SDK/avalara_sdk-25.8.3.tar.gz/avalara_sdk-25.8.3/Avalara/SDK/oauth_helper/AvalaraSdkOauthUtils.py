from enum import Enum
from functools import wraps
import sys

import urllib3
import urllib
from Avalara.SDK.exceptions import (
    ApiException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ServiceException,
    ApiValueError,
)


class AvalaraApiEnvironment(Enum):
    Production = 1
    Sandbox = 2
    QA = 3


def avalara_retry_oauth(max_retry_attempts=1):
    """Function decorator to enforce retry oauth on 401 or 403 error

    Args:
        max_retry_attempts (int, optional): maximum number or retry attempts.
        Defaults to 1.
    """

    def avalara_retry_oauth_decorator(func):
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            result = None
            max_retry_attempts_allowed = max_retry_attempts
            for attempt_count in range(max_retry_attempts_allowed + 1):
                try:
                    result = func(*args, **kwargs)
                except (UnauthorizedException, ForbiddenException) as err:
                    # range is 0 indexed so attempt_count initializes to 0
                    if attempt_count < max_retry_attempts_allowed:
                        # retry
                        continue
                    else:
                        raise err
                break
            if result is not None:
                return result

        return wrapper_function

    return avalara_retry_oauth_decorator


class AVALARA_SDK_CONSTANTS:
    """Avalara SDK constants"""

    # Avalara Identity OpenId Config URLs constants
    PRODUCTION_OPENID_CONFIG_URL = (
        "https://identity.avalara.com/.well-known/openid-configuration"
    )
    SANDBOX_OPENID_CONFIG_URL = (
        "https://ai-sbx.avlr.sh/.well-known/openid-configuration"
    )
    QA_OPENID_CONFIG_URL = (
        "https://ai-awsfqa.avlr.sh/.well-known/openid-configuration"
    )

    # OIDC configuration key/values constants
    OIDC_KEYS_SCOPES_SUPPORTED = "scopes_supported"

    AVALARA_OIDC_VALUES_GRANT_TYPE_DEVICE_FLOW = (
        "urn:ietf:params:oauth:grant-type:device_code"
    )

    AVALARA_OIDC_VALUES_GRANT_TYPE_CLIENT_CREDENTIALS = "client_credentials"

    # Oauth request/response constants
    OAUTH_RESPONSE_KEY_CLIENT_CREDS_EXPIRES_IN = "expires_in"

    # Message strings
    MSG_INVALID_URL = "Invalid URL"
