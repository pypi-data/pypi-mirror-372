"""Loads configuration data from an Open ID Connect discovery endpoint."""

from tenduke_core.config import TendukeConfig
from tenduke_core.http.session_factory import SessionFactory


def load_openid_config(session_factory: SessionFactory, config: TendukeConfig):
    """Load the Open ID Connect details from a discovery URL."""
    if not config.idp_oidc_discovery_url:
        return
    session = session_factory.create()
    response = session.get(config.idp_oidc_discovery_url)
    response_json = response.json()
    config.idp_oauth_device_code_url = response_json.get(
        "device_authorization_endpoint", config.idp_oauth_device_code_url
    )
    config.idp_oauth_authorization_url = response_json.get(
        "authorization_endpoint", config.idp_oauth_authorization_url
    )
    config.idp_oauth_token_url = response_json.get("token_endpoint", config.idp_oauth_token_url)
    config.idp_userinfo_url = response_json.get("userinfo_endpoint", config.idp_userinfo_url)
    config.idp_jwks_uri = response_json.get("jwks_uri", config.idp_jwks_uri)
