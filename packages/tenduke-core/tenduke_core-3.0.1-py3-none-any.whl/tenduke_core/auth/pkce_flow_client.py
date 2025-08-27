"""Client for Proof Key for Code Exchange (PKCE) flow."""

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse

# no type stubs have been published for authlib but they may come in future:
#  https://github.com/lepture/authlib/issues/460
from authlib.common.security import generate_token  # type: ignore[import-untyped]
from authlib.integrations.requests_client import OAuth2Session  # type: ignore[import-untyped]

from tenduke_core.config import TendukeConfig
from tenduke_core.http import SessionFactory

from ..exceptions.oauth import AuthenticationFailed
from .oauth_client import OAuthClient
from .token_response import TokenResponse

AUTH_SUCCESS_MESSAGE = """
HTTP/1.1 200 OK
Connection: close
Content-Type: text/html
Content-Length: 147

<html>
  <head>
  <title>Login Handler</title>
  <body>
    <h1>Login request complete</h1>
    <p>You may close this window.</p>
  </body>
</html>
"""


def _is_default_port(parsed_result):
    if parsed_result.port is None:
        return True
    return (parsed_result.scheme == "http" and parsed_result.port == 80) or (
        parsed_result.scheme == "https" and parsed_result.port == 443
    )


class PkceFlowClient(OAuthClient):
    """Client for Proof Key for Code Exchange (PKCE) flow."""

    class RedirectHttpServer(HTTPServer):
        """HTTP Server to handle redirect with code."""

        def __init__(
            self,
            *args,
            success_http: Optional[str] = AUTH_SUCCESS_MESSAGE,
            **kwargs,
        ):
            """Construct an instance of the HTTP Server.

            Args:
                success_http: HTTP message to send once redirect request is received.
            """
            self.success_http = success_http
            self.authorization_response = ""
            super().__init__(*args, **kwargs)

    class RedirectHandler(BaseHTTPRequestHandler):
        """Handler class for redirect with code."""

        def do_GET(self):  # pylint: disable=invalid-name
            """Handle OAuth redirect."""
            self.wfile.write(self.server.success_http.encode("UTF-8"))  # pyright:ignore[reportAttributeAccessIssue]
            self.wfile.flush()
            self.server.authorization_response = self.path  # pyright:ignore[reportAttributeAccessIssue]

    def __init__(self, config: TendukeConfig, session_factory: SessionFactory, *args, **kwargs):
        """Construct an instance of the PkceFlowClient.

        Args:
            config:
                Configuration parameters for interacting with the OAuth / Open ID Authorization
                Server.
            session_factory:
                Used to create requests Session configured with the settings from config and with
                the configured User-Agent header value.
        """
        self.code_verifier = kwargs.pop("code_verifier", None)
        self.state = kwargs.pop("state", None)
        self._client = None
        super().__init__(config, session_factory)

    def _build_redirect_uri(self, port: Optional[int] = None):
        port = port or self.config.auth_redirect_port
        redirect_uri = self.config.auth_redirect_uri
        parsed_result = urlparse(redirect_uri)
        if parsed_result.hostname in (
            "localhost",
            "127.0.0.1",
            "::1",
        ) and _is_default_port(parsed_result):
            # ParsedResult.host_name returns the hostname only, we need to escape as per RFC2732
            host_name = "[::1]" if parsed_result.hostname == "::1" else parsed_result.hostname
            # urllib.parse is more flexible with types than mypy gives it credit for
            new_uri = f"{host_name}:{port}"  # type: ignore[str-bytes-safe]
            updated = parsed_result._replace(netloc=new_uri)  # type: ignore[arg-type]
            redirect_uri = urlunparse(updated)  # type: ignore[assignment]
        if not redirect_uri:
            port = port or self.config.auth_redirect_port
            redirect_uri = urljoin(f"http://localhost:{port}", self.config.auth_redirect_path)
        return redirect_uri

    def _resolve_port(self):
        redirect_uri = self.config.auth_redirect_uri
        parsed_result = urlparse(redirect_uri)
        if parsed_result.port is not None and parsed_result.port not in (0, 80, 443):
            return parsed_result.port
        return self.config.auth_redirect_port

    def create_authorization_url(self, port: Optional[int] = None) -> str:
        """Generate and return authorization url.

        Args:
            port: The port number to use in the redirect URI

        Returns:
            URL for authorization request.
        """
        self.code_verifier = generate_token(128)

        redirect_uri = self._build_redirect_uri(port)

        self._client = OAuth2Session(
            client_id=self.config.idp_oauth_client_id,
            scope=self.config.idp_oauth_scope,
            redirect_uri=redirect_uri,
            code_challenge_method="S256",
        )
        url, state = self._client.create_authorization_url(  # type: ignore[attr-defined]
            self.config.idp_oauth_authorization_url, code_verifier=self.code_verifier
        )
        self.state = state
        return url

    def fetch_token(
        self, authorization_response: Optional[str], port: Optional[int] = None
    ) -> TokenResponse:
        """Fetch token based on authorization response.

        Args:
            authorization_response:
                Redirect URL request with authorization code to exchange for token.

        Returns:
            TokenResponse object for the authorization code in the authorization_reponse parameter.
        """
        redirect_uri = self._build_redirect_uri(port)

        if self._client is None:
            self._client = OAuth2Session(
                client_id=self.config.idp_oauth_client_id,
                scope=self.config.idp_oauth_scope,
                redirect_uri=redirect_uri,
                code_challenge_method="S256",
            )
        token = self._client.fetch_token(  # type: ignore[attr-defined]
            self.config.idp_oauth_token_url,
            authorization_response=authorization_response,
            state=self.state,
            code_verifier=self.code_verifier,
        )
        token = TokenResponse.from_api(token)
        self.token = token
        return token

    def login_with_default_browser(self) -> TokenResponse:
        """Launch system default browser for user to log in.

        Returns:
            TokenResponse object with token for the authenticated user.

        Raises:
            OAuth2Error: Authentication failed.
        """
        authorization_response = None
        success_http = AUTH_SUCCESS_MESSAGE

        if self.config.auth_success_message:
            success_http = Path(self.config.auth_success_message).read_text("UTF-8")

        port = self._resolve_port()

        with self.RedirectHttpServer(
            ("", port),
            self.RedirectHandler,
            success_http=success_http,
        ) as httpd:
            url = self.create_authorization_url(httpd.server_port)
            webbrowser.open(url)
            httpd.handle_request()
            authorization_response = httpd.authorization_response

        if authorization_response:
            return self.fetch_token(authorization_response, httpd.server_port)

        raise AuthenticationFailed()
