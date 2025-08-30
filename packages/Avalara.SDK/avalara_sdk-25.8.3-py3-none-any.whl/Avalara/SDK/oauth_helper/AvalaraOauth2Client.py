from datetime import datetime
import json

import urllib3
import urllib

from Avalara.SDK.oauth_helper.AvalaraCache import AvalaraCache
from Avalara.SDK.oauth_helper.AvalaraOauth2Configuration import (
    AvalaraOauth2Configuration,
)
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import (
    AVALARA_SDK_CONSTANTS,
    AvalaraApiEnvironment,
)


class AvalaraOauth2Client:
    """Utility class with Avalara Oauth2 helper methods"""

    client_id: str
    client_secret: str
    required_scopes: str
    avalara_api_environment: AvalaraApiEnvironment
    cache: AvalaraCache

    # constructor
    def __init__(
        self,
        client_id,
        client_secret,
        required_scopes,
        avalara_api_environment,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.required_scopes = required_scopes
        self.oauth2_config = AvalaraOauth2Configuration(
            required_scopes, avalara_api_environment
        )
        self.cache = AvalaraCache()
        self.__is_token_returned_from_cache = False
        self.__token_renewal_seconds_before_ttl_end = 300

    def get_avalara_access_token_info(self) -> dict:
        """Provides Avalara api access token and related data
           If access token information is present in cache it is returned
           from cache. Information is fetched and added to cache if it is
           not present.
           As a business rule ttl for cach expiry is set 5 minutes earlier than
           actual token lifetime.

        Returns:
            dict: Dictionary with Avalara access token and related data
        """
        cached_token_data = self.__get_access_token_data_from_cache()
        if cached_token_data is not None:
            self.__is_token_returned_from_cache = True
            return cached_token_data
        else:
            access_token_data = self.__get_access_token_data(
                self.oauth2_config.avalara_oidc_data.token_endpoint,
                self.client_id,
                self.client_secret,
                grant_type=(
                    AVALARA_SDK_CONSTANTS.AVALARA_OIDC_VALUES_GRANT_TYPE_CLIENT_CREDENTIALS
                ),
            )
            self.__add_access_token_data_in_cache(access_token_data)
            self.__is_token_returned_from_cache = False
            return access_token_data

    def __add_access_token_data_in_cache(self, access_token_data: dict):
        clienr_creds_validity_seconds = access_token_data.get(
            AVALARA_SDK_CONSTANTS.OAUTH_RESPONSE_KEY_CLIENT_CREDS_EXPIRES_IN
        )
        ttl_seconds = (
            int(clienr_creds_validity_seconds)
            if clienr_creds_validity_seconds
            else None
        )
        if ttl_seconds is None:
            ttl_seconds = 3600
        self.cache.set_item_with_ttl(
            self.client_id,
            access_token_data,
            ttl_seconds - self.__token_renewal_seconds_before_ttl_end,
        )

    def __get_access_token_data_from_cache(self):
        cached_item = self.cache.get(self.client_id)
        if (
            cached_item is not None
            and cached_item[0].get("access_token") is not None
        ):
            item_expired = datetime.utcnow() > cached_item[1]
            if item_expired:
                return None
            else:
                return cached_item[0]
        else:
            return None

    def get_access_token_for_device_flow(self, device_code) -> dict:
        '''Returns access token for device flow'''

        return self.__get_access_token_data(
            self.oauth2_config.avalara_oidc_data.token_endpoint,
            self.client_id,
            self.client_secret,
            grant_type=AVALARA_SDK_CONSTANTS.AVALARA_OIDC_VALUES_GRANT_TYPE_DEVICE_FLOW,
            device_code=device_code,
        )

    def initiate_device_authorization_flow(self) -> dict:
        """Initiates the Device Code Flow by calling the
        /device/authorize endpoint to retrieve the device_code and user_code.
        Provides Avalara device authorization code and related data

        Returns:
            dict: Dictionary with Avalara device authorization code
            and related data
        """
        return self.__get_device_authorization_user_code(
            self.oauth2_config.avalara_oidc_data.device_authorization_endpoint,
            self.client_id,
            self.client_secret,
        )

    def __get_access_token_data(
        self, url, client_id, client_secret, grant_type, device_code=None
    ) -> dict:
        data = {
            "grant_type": AVALARA_SDK_CONSTANTS.AVALARA_OIDC_VALUES_GRANT_TYPE_DEVICE_FLOW,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if device_code is not None:
            data["device_code"] = device_code
        encoded_data = urllib.parse.urlencode(data)
        http = urllib3.PoolManager()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = http.request(
            'POST',
            url,
            headers=headers,
            body=encoded_data,
        )
        resp_dict = json.loads(response.data.decode('utf-8'))
        return resp_dict

    def __get_device_authorization_user_code(
        self, url, client_id, client_secret
    ) -> dict:
        data = {
            "grant_type": AVALARA_SDK_CONSTANTS.AVALARA_OIDC_VALUES_GRANT_TYPE_DEVICE_FLOW,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        encoded_data = urllib.parse.urlencode(data)
        http = urllib3.PoolManager()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = http.request(
            'POST',
            url,
            headers=headers,
            body=encoded_data,
        )
        resp_dict = json.loads(response.data.decode('utf-8'))
        return resp_dict
