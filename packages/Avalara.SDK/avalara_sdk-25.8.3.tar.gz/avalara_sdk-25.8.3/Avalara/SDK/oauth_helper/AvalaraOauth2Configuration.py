from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import (
    AVALARA_SDK_CONSTANTS,
    AvalaraApiEnvironment,
)
import json
from collections import namedtuple
from Avalara.SDK.oauth_helper.AvalaraOidcModel import (
    AvalaraOidcModel,
)


class AvalaraOauth2Configuration:
    """Repesents singlton instance of Avalara OpenID Connect (OIDC) configuration

    Returns:
        _type_: Instance with Avalara OpenID Connect (OIDC) model
    """

    api_environment: AvalaraApiEnvironment
    oidc_url: str
    avalara_oidc_data: AvalaraOidcModel
    scope: str
    __initialized: bool
    __instance = None

    def __new__(cls, scope, api_environment):
        if cls.__instance is None:
            cls.__instance = super(AvalaraOauth2Configuration, cls).__new__(
                cls
            )
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(
        self, scope=None, api_environment=AvalaraApiEnvironment.Production
    ):
        if self.__instance.__initialized:
            return
        self.__instance.__initialized = True
        self.api_environment = api_environment
        self.oidc_url = self.__get_oidc_url()
        self.avalara_oidc_data = self.__get_oidc_data(self.oidc_url)
        # self.scope = self.__get_oidc_scope_list_to_string()
        self.scope = scope

    def __get_oidc_scope_list_to_string(self) -> str:
        """Returns Avalara OIDC scopes as string

        Returns:
            str: space seprated scopes
        """
        return " ".join(self.avalara_oidc_data.scopes_supported)

    def __get_oidc_url(self) -> str:
        if self.api_environment == AvalaraApiEnvironment.Production:
            return AVALARA_SDK_CONSTANTS.PRODUCTION_OPENID_CONFIG_URL
        elif self.api_environment == AvalaraApiEnvironment.Sandbox:
            return AVALARA_SDK_CONSTANTS.SANDBOX_OPENID_CONFIG_URL
        elif self.api_environment == AvalaraApiEnvironment.QA:
            return AVALARA_SDK_CONSTANTS.QA_OPENID_CONFIG_URL
        else:
            return AVALARA_SDK_CONSTANTS.MSG_INVALID_URL

    def __get_oidc_data(self, url) -> AvalaraOidcModel:
        try:
            response = urlopen(url)
        except HTTPError:
            response = urlopen(
                AVALARA_SDK_CONSTANTS.PRODUCTION_OPENID_CONFIG_URL
            )
        except URLError:
            response = urlopen(
                AVALARA_SDK_CONSTANTS.PRODUCTION_OPENID_CONFIG_URL
            )

        # convert json data to model object
        avalara_oidc_model = json.loads(
            response.read().decode('utf-8'),
            object_hook=lambda d: namedtuple('AvalaraOidcModel', d.keys())(
                *d.values()
            ),
        )
        return avalara_oidc_model
