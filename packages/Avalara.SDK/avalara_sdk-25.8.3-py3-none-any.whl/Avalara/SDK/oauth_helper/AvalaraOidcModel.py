from typing import List


class AvalaraOidcModel:
    """Avalara OpenID Connect (OIDC) model"""

    issuer: str
    jwks_uri: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    end_session_endpoint: str
    check_session_iframe: str
    revocation_endpoint: str
    introspection_endpoint: str
    device_authorization_endpoint: str
    frontchannel_logout_supported: bool
    frontchannel_logout_session_supported: bool
    backchannel_logout_supported: bool
    backchannel_logout_session_supported: bool
    scopes_supported: List[str]
    claims_supported: List[str]
    grant_types_supported: List[str]
    response_types_supported: List[str]
    response_modes_supported: List[str]
    token_endpoint_auth_methods_supported: List[str]
    id_token_signing_alg_values_supported: List[str]
    subject_types_supported: List[str]
    code_challenge_methods_supported: List[str]
    request_parameter_supported: bool

    def __init__(self, json_obj=None) -> None:
        if json_obj:
            self.issuer = json_obj.issuer
            self.jwks_uri = json_obj.jwks_uri
            self.authorization_endpoint = json_obj.authorization_endpoint
            self.token_endpoint = json_obj.token_endpoint
            self.userinfo_endpoint = json_obj.userinfo_endpoint
            self.end_session_endpoint = json_obj.end_session_endpoint
            self.check_session_iframe = json_obj.check_session_iframe
            self.revocation_endpoint = json_obj.revocation_endpoint
            self.introspection_endpoint = json_obj.introspection_endpoint
            self.device_authorization_endpoint = (
                json_obj.device_authorization_endpoint
            )
            self.frontchannel_logout_supported = (
                json_obj.frontchannel_logout_supported
            )
            self.frontchannel_logout_session_supported = (
                json_obj.frontchannel_logout_session_supported
            )

            self.backchannel_logout_supported = (
                json_obj.backchannel_logout_supported
            )
            self.backchannel_logout_session_supported = (
                json_obj.backchannel_logout_session_supported
            )
            self.scopes_supported = json_obj.scopes_supported
            self.claims_supported = json_obj.claims_supported
            self.grant_types_supported = json_obj.grant_types_supported
            self.response_types_supported = json_obj.response_types_supported
            self.response_modes_supported = json_obj.response_modes_supported
            self.token_endpoint_auth_methods_supported = (
                json_obj.token_endpoint_auth_methods_supported
            )
            self.id_token_signing_alg_values_supported = (
                json_obj.id_token_signing_alg_values_supported
            )
            self.subject_types_supported = json_obj.subject_types_supported
            self.code_challenge_methods_supported = (
                json_obj.code_challenge_methods_supported
            )

            self.request_parameter_supported = (
                json_obj.request_parameter_supported
            )
