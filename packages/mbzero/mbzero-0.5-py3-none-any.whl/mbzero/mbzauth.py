#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

from typing import Literal, Tuple

from oauthlib.oauth2 import OAuth2Error
from requests_oauthlib import OAuth2Session

from mbzero.mbzerror import MbzOauth2Error
from mbzero.oauth2_session_revoke import revoke_token

MUSICBRAINZ_OAUTH2_URI = "urn:ietf:wg:oauth:2.0:oob"
MUSICBRAINZ_HN = "https://musicbrainz.org"
MUSICBRAINZ_OAUTH2 = MUSICBRAINZ_HN + "/oauth2"
OAUTH2_PATH_AUTH = "/authorize"
OAUTH2_PATH_TOKEN = "/token"
OAUTH2_PATH_REVOKE = "/revoke"


class MbzCredentials:
    """Class for Musicbrainz authentication."""

    def __init__(self, oauth2_url: str | None = None):
        """Initialize credentials

        :param oauth2_url: optional OAuth2 endpoint"""
        self.name: str | None = None
        self.password: str | None = None
        self.oauth2_url = oauth2_url or MUSICBRAINZ_OAUTH2
        self.oauth2_client_id: str | None = None
        self.oauth2_client_secret: str | None = None
        self.oauth2_session: OAuth2Session | None = None

    def has_auth(self) -> bool:
        """Returns true if name/passwd credentials have been set"""
        return (self.name is not None) and (self.password is not None)

    def has_oauth2(self) -> bool:
        """Returns true if OAuth2 has been set"""
        return self.oauth2_session is not None and self.oauth2_session.authorized

    def auth_set(self, name: str | None, passwd: str | None):
        """Username/password authentication"""
        self.name = name
        self.password = passwd

    def auth(self) -> Tuple[str | None, str | None]:
        """Get username/password"""
        return (self.name, self.password)

    def oauth2_set_url(self, url):
        """Change the default OAuth2 endpoint"""
        self.oauth2_url = url

    def oauth2_new(
        self,
        token: str | None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str = MUSICBRAINZ_OAUTH2_URI,
        scope: list[str] = [],
    ):
        """Create a session with existing tokens

        :param token: access token to use for authentication
        :param refresh_token: refresh token to use for refreshing
        :param client_id: optional client application ID
        :param client_secret: optional client application secret
        :param redirect_uri: optional redirect URI (defaults to the redirect
                             URI defined in the Musicbrainz documentation)
        :param scope: optional Musicbrainz scope"""
        oauth2_token = {"access_token": token, "token_type": "bearer"}
        if refresh_token is not None:
            oauth2_token["refresh_token"] = refresh_token

        try:
            self.oauth2_session = OAuth2Session(
                client_id, scope=scope, redirect_uri=redirect_uri, token=oauth2_token
            )
            self.oauth2_client_id = client_id
            self.oauth2_client_secret = client_secret
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_init(
        self,
        client_id: str,
        url: str | None = None,
        redirect_uri: str = MUSICBRAINZ_OAUTH2_URI,
        scope: list[str] = [],
    ) -> str:
        """Initialize the creation of tokens

        :param client_id: client application ID
        :param url: optional authentification endpoint(defaults to musicbrainz)
        :param redirect_uri: optional redirect URI (defaults to the redirect
                             URI defined in the Musicbrainz documentation)
        :param scope: optional Musicbrainz scope
        :return: an authorization URL to visit"""
        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_AUTH

        try:
            self.oauth2_session = OAuth2Session(
                client_id, redirect_uri=redirect_uri, scope=scope
            )
            auth_url, _ = self.oauth2_session.authorization_url(url)
            self.oauth2_client_id = client_id
            return auth_url
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_confirm(
        self, response_code: str, client_secret: str, url: str | None = None
    ):
        """Confirm the authorization with the response code.

        :param response_code: the response code given by the authentication URL
        :param client_secret: client application secret
        :param url: optional token endpoint (defaults to musicbrainz)
        :return: the access token"""
        if self.oauth2_session is None:
            raise MbzOauth2Error("OAuth2 session not initialiazed")

        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_TOKEN

        try:
            token = self.oauth2_session.fetch_token(
                url, code=response_code, client_secret=client_secret
            )
            self.oauth2_client_secret = client_secret
            return token
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_refresh(self, refresh_token=None, url: str | None = None):
        """Refresh an access token.

        :param refresh_token: optional refresh token used to refresh the
                              access token
        :param url: optional token endpoint (defaults to musicbrainz)
        :return: the new access token"""
        if self.oauth2_session is None:
            raise MbzOauth2Error("OAuth2 session not initialiazed")

        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_TOKEN

        try:
            token = self.oauth2_session.refresh_token(
                url,
                refresh_token=refresh_token,
                client_id=self.oauth2_client_id,
                client_secret=self.oauth2_client_secret,
            )
            return token
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_revoke(self, token=None, url: str | None = None):
        """Revoke a token pair

        :param token: optional token used to refresh the access token.
                      If not provided, the current session's access_token
                      is revoked.
        :param url: optional revocation endpoint (defaults to musicbrainz)
        """
        if self.oauth2_session is None:
            raise MbzOauth2Error("OAuth2 session not initialiazed")
        if token is None:
            token = self.oauth2_session.access_token

        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_REVOKE

        try:
            revoke_token(
                self.oauth2_session,
                url,
                token,
                client_id=self.oauth2_client_id,
                client_secret=self.oauth2_client_secret,
            )
        except OAuth2Error as e:
            raise MbzOauth2Error(e)

    def _get_request_method(self, method: Literal["get", "post", "put", "delete"]):
        if self.oauth2_session is None:
            raise MbzOauth2Error("OAuth2 session not initialiazed")

        if method == "get":
            return self.oauth2_session.get
        elif method == "post":
            return self.oauth2_session.post
        elif method == "put":
            return self.oauth2_session.put
        elif method == "delete":
            return self.oauth2_session.delete
        else:
            raise MbzOauth2Error(f"Invalid request method: {method}")
