"""Dataclass for storing application configuration."""

from dataclasses import dataclass
from typing import Optional

import dataconf


# These are the options for the program.
# The number of attributes here breaks a pylint rule.
# Breaking this up into idp/licensingapi/local or whatever sub-configs is likely
# to cause more complexity for applications using the SDK.
#
# pylint: disable=too-many-instance-attributes
@dataclass
class TendukeConfig:
    """Configuration properties for interacting with licensing and oauth / open ID connect.

    Attributes:
        token_path: Location on disk to save license tokens.
        public_key_path: Location on disk to save public keys.
        licensing_api_url: Protocol and host name for API tenant.
        token_refresh_leeway_seconds:
            The number of seconds before expiry time that an ID Token or JWT will be
            automatically refreshed.
        http_timeout_seconds: Timeout for HTTP requests.
        licensing_api_authorization_model: Method of authorization used for API calls.
        idp_oidc_discovery_url:
            Used to retrieve the details of the Open ID Connect endpoints for the identity
            provider.
        idp_oauth_authorization_url:
            Endpoint for Authorization Request in Authorization Code or Implicit Grant flows.
        idp_oauth_device_code_url:
            Endpoint for Device Authorization Request in Device Authorization Grant flow.
        idp_oauth_token_url: Endpoint for Access Token Request or Device Access Token Request.
        idp_oauth_client_id: Application credentials for OAuth/Open ID Connect.
        idp_userinfo_url: Endpoint handling the UserInfo Request.
        idp_oauth_client_secret:
            Application credentials for OAuth/Open ID Connect. Required for some OAuth flows or for
            some Identity Providers.
        idp_oauth_scope:
            Scopes to include in the Access and ID tokens requested via Open ID Connect.
        idp_jwks_uri:
            URL path to read public key used to verify JWTs received from Authorization Server
            authenticating Open ID Connect session.
        auth_redirect_uri:
            Fully specified URL for OAuth redirect_uri to listen for redirect during PKCE Flow.
        auth_redirect_path:
            Redirect path fragment to listen for redirect during PKCE Flow. For desktop clients,
            this path will be appended to http://localhost (either on the specified port or a random
            ephemeral port). This fragment is ignored if auth_redirect_uri is specified.
        auth_redirect_port: Local redirect port to listen on for PKCE Flow Client.
        auth_success_message: File containing response for successful login (see PKCE Flow Client).
        https_proxy: Proxy to use for HTTPS requests.
    """

    token_path: str
    public_key_path: str
    licensing_api_url: str
    token_refresh_leeway_seconds: float = 30.0
    http_timeout_seconds: float = 30.0
    auth_redirect_path: str = "/login/callback"
    auth_redirect_port: int = 0
    auth_redirect_uri: Optional[str] = None
    licensing_api_authorization_model: Optional[str] = None
    idp_oidc_discovery_url: Optional[str] = None
    idp_oauth_authorization_url: Optional[str] = None
    idp_oauth_device_code_url: Optional[str] = None
    idp_oauth_token_url: Optional[str] = None
    idp_oauth_client_id: Optional[str] = None
    idp_userinfo_url: Optional[str] = None
    idp_oauth_client_secret: Optional[str] = None
    idp_oauth_scope: Optional[str] = None
    idp_jwks_uri: Optional[str] = None
    auth_success_message: Optional[str] = None
    https_proxy: Optional[str] = None

    @classmethod
    def load(
        cls: type["TendukeConfig"],
        prefix: Optional[str] = None,
        file_name: Optional[str] = None,
        **kwargs,
    ) -> "TendukeConfig":
        """Load the configuration.

        Priority order for configuration values:
        - environment variables
        - configuration file
        - kwargs

        Args:
            prefix: Optionally override default prefix for environment variables.
            file_name: Configuration file to load.
        """
        config_builder = dataconf.multi.dict(kwargs)

        if file_name:
            config_builder = config_builder.file(file_name)

        if prefix:
            config_builder = config_builder.env(prefix)

        config = config_builder.on(TendukeConfig)
        return config  # pyright: ignore[reportReturnType]
