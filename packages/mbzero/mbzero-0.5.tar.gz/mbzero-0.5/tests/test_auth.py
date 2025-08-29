#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import unittest
from unittest.mock import patch

from mbzero import mbzauth as mba


def _raise_exception(*args, **kwargs):
    raise Exception("mock")


class AuthTest(unittest.TestCase):
    def testAuth(self):
        cred = mba.MbzCredentials()
        self.assertFalse(cred.has_auth())
        cred.auth_set("name", "pass")
        self.assertTrue(cred.has_auth())
        self.assertEqual(cred.auth(), ("name", "pass"))
        cred.auth_set(None, None)
        self.assertFalse(cred.has_auth())

    def testOauth2(self):
        cred = mba.MbzCredentials()
        self.assertFalse(cred.has_oauth2())
        cred.oauth2_new("token")
        self.assertTrue(cred.has_oauth2())
        cred.oauth2_new(None)
        self.assertFalse(cred.has_oauth2())


class Oauth2TestInit(unittest.TestCase):
    def setUp(self):
        self.client_id = "clientID"
        self.client_secret = "clientSecret"
        self.token = "token"
        self.refresh = "refresh"
        self.cred = mba.MbzCredentials()

    @patch("requests_oauthlib.OAuth2Session.authorization_url")
    def testInit(self, mock_auth):
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with(mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_AUTH)

    @patch("requests_oauthlib.OAuth2Session.authorization_url")
    def testInitURLOther(self, mock_auth):
        self.cred = mba.MbzCredentials(oauth2_url="somewhere")
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with("somewhere" + mba.OAUTH2_PATH_AUTH)

    @patch("requests_oauthlib.OAuth2Session.authorization_url")
    def testInitURLChange(self, mock_auth):
        self.cred.oauth2_set_url("somewhere")
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with("somewhere" + mba.OAUTH2_PATH_AUTH)

    @patch("requests_oauthlib.OAuth2Session.authorization_url")
    def testInitURLSetOther(self, mock_auth):
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id, url="somewhere")
        mock_auth.assert_called_once_with("somewhere")

    @patch("requests_oauthlib.OAuth2Session.__init__", _raise_exception)
    def testInitFails(self):
        t = False
        try:
            self.cred.oauth2_init(self.client_id)
        except mba.MbzOauth2Error:
            t = True
        self.assertTrue(t)

    @patch("requests_oauthlib.OAuth2Session.__init__", _raise_exception)
    def testNewFails(self):
        t = False
        try:
            self.cred.oauth2_new(None)
        except mba.MbzOauth2Error:
            t = True
        self.assertTrue(t)


class Oauth2Process(unittest.TestCase):
    def setUp(self):
        self.client_id = "clientID"
        self.client_secret = "clientSecret"
        self.token = "token"
        self.refresh = "refresh"
        self.cred = mba.MbzCredentials()
        self.cred.oauth2_new(
            self.token,
            self.refresh,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self.headers = {}

    @patch("requests_oauthlib.OAuth2Session.fetch_token")
    def testConfirm(self, mock_fetch):
        mock_fetch.return_value = {
            "access_token": self.token,
            "refresh_token": self.refresh,
        }
        self.cred.oauth2_confirm("code", self.client_secret)
        mock_fetch.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_TOKEN,
            code="code",
            client_secret=self.client_secret,
        )

    @patch("requests_oauthlib.OAuth2Session.fetch_token", _raise_exception)
    def testConfirmFail(self):
        t = False
        try:
            self.cred.oauth2_confirm("code", self.client_secret)
        except mba.MbzOauth2Error:
            t = True
        self.assertTrue(t)

    @patch("requests_oauthlib.OAuth2Session.fetch_token")
    def testConfirmAPIOther(self, mock_fetch):
        mock_fetch.return_value = {
            "access_token": self.token,
            "refresh_token": self.refresh,
        }
        self.cred.oauth2_confirm("code", self.client_secret, url="somewhere")
        mock_fetch.assert_called_once_with(
            "somewhere", code="code", client_secret=self.client_secret
        )

    @patch("requests_oauthlib.OAuth2Session.refresh_token")
    def testRefresh(self, mock_refresh):
        mock_refresh.return_value = {
            "access_token": self.token,
            "refresh_token": self.refresh,
        }
        self.cred.oauth2_refresh(self.refresh)
        mock_refresh.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_TOKEN,
            refresh_token=self.refresh,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    @patch("requests_oauthlib.OAuth2Session.refresh_token")
    def testRefreshAPIOther(self, mock_refresh):
        mock_refresh.return_value = {
            "access_token": self.token,
            "refresh_token": self.refresh,
        }
        self.cred.oauth2_refresh(self.refresh, url="somewhere")
        mock_refresh.assert_called_once_with(
            "somewhere",
            refresh_token=self.refresh,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    @patch("requests_oauthlib.OAuth2Session.refresh_token", _raise_exception)
    def testRefreshFail(self):
        t = False
        try:
            self.cred.oauth2_refresh(self.refresh)
        except mba.MbzOauth2Error:
            t = True
        self.assertTrue(t)

    def testGet(self):
        assert self.cred.oauth2_session is not None
        self.assertEqual(
            self.cred._get_request_method("get"), self.cred.oauth2_session.get
        )

    def testPost(self):
        assert self.cred.oauth2_session is not None
        self.assertEqual(
            self.cred._get_request_method("post"), self.cred.oauth2_session.post
        )

    def testPut(self):
        assert self.cred.oauth2_session is not None
        self.assertEqual(
            self.cred._get_request_method("put"), self.cred.oauth2_session.put
        )

    def testDelete(self):
        assert self.cred.oauth2_session is not None
        self.assertEqual(
            self.cred._get_request_method("delete"), self.cred.oauth2_session.delete
        )
