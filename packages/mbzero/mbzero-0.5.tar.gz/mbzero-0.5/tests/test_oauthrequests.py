#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import unittest
from unittest.mock import patch

from mbzero import mbzauth as mba
from mbzero import mbzrequest as mbr


class RequestResultOK:
    def __init__(self):
        self.ok = True
        self.content = "Request OK content"

    def raise_for_status(self):
        return True


class Oauth2RequestTest(unittest.TestCase):
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
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    @patch("requests_oauthlib.OAuth2Session.get")
    def testSend(self, mock_get):
        mock_get.return_value = RequestResultOK()
        mbr.MbzRequest(self.user_agent).get("/request", credentials=self.cred)
        mock_get.assert_called_once_with(
            url=mbr.MUSICBRAINZ_API + "/request",
            params={"fmt": "json"},
            headers=self.headers,
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.get")
    def testLookup(self, mock_get):
        mock_get.return_value = RequestResultOK()
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(credentials=self.cred)
        mock_get.assert_called_once_with(
            url=mbr.MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.get")
    def testBrowse(self, mock_get):
        mock_get.return_value = RequestResultOK()
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(credentials=self.cred)
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=mbr.MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.get")
    def testSearch(self, mock_get):
        mock_get.return_value = RequestResultOK()
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            credentials=self.cred
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=mbr.MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )
