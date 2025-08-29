#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import contextlib
import unittest
from typing import Any
from unittest.mock import patch

from requests.auth import HTTPDigestAuth

from mbzero import mbzauth as mba
from mbzero import mbzrequest as mbr

MUSICBRAINZ_API = mbr.MUSICBRAINZ_API
OTHER_API = "https://example.com"


@patch("requests_oauthlib.OAuth2Session.post")
class SubmissionTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.client = "test_client"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}
        self.data = "data"
        self.data_type = "xml"
        self.cred = mba.MbzCredentials()
        self.cred.oauth2_new("token", "refresh", "client_id", "client_secret")

    def testSend(self, mock_post):
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendDefaultClient(self, mock_post):
        mbr.MbzRequest(
            self.user_agent,
        ).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.user_agent
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendPayloadNone(self, mock_post):
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            headers=self.headers,
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendWrongType(self, mock_post):
        with contextlib.suppress(Exception):
            mbr.MbzRequest(self.user_agent, client=self.client).post(
                "/request",
                data="data",
                data_type="WRONG",  # type: ignore
                credentials=self.cred,
                headers=self.headers,
            )
        mock_post.assert_not_called()

    def testSendOpts(self, mock_post):
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
            opts={"limit": 10},
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expPayload["limit"] = 10
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendOptsExtraHeaders(self, mock_post):
        extraHeaders = {"my": "header"}
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
            opts={"extra_headers": extraHeaders},
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = dict(self.headers, **extraHeaders)
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendOptsExtraPayloads(self, mock_post):
        extraPayload = {"my": "payload"}
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
            opts={"extra_payload": extraPayload},
        )
        expPayload = dict(self.payload, **extraPayload)
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendOptsAPIOther(self, mock_post):
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
            opts={"url": OTHER_API},
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url=OTHER_API + "/request",
            data=self.data,
            params=expPayload,
            headers=expHeaders,
        )

    def testSendOptsAPINone(self, mock_post):
        mbr.MbzRequest(self.user_agent, client=self.client).post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
            opts={"url": ""},
        )
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        mock_post.assert_called_once_with(
            url="/request", data=self.data, params=expPayload, headers=expHeaders
        )

    def testSendSetAPINone(self, mock_post):
        req = mbr.MbzRequest(self.user_agent, client=self.client)
        req.set_url("")
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        expHeaders = self.headers.copy()
        expHeaders["Content-Type"] = "application/xml; charset=utf-8"
        req.post(
            "/request",
            data="data",
            data_type="xml",
            credentials=self.cred,
            payload=self.payload,
            headers=self.headers,
        )
        mock_post.assert_called_once_with(
            url="/request", data=self.data, params=expPayload, headers=expHeaders
        )

    def testSubmissionSend(self, mock_post):
        mbr.MbzSubmission(
            self.user_agent, "request", data="data", data_type="xml"
        ).send(credentials=self.cred)
        headers = self.headers
        headers["Content-Type"] = "application/xml; charset=utf-8"
        payload = self.payload
        payload["client"] = self.user_agent
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=self.payload,
            headers=self.headers,
        )

    def testSubmissionSendWrongType(self, mock_post):
        with contextlib.suppress(Exception):
            mbr.MbzSubmission(
                self.user_agent,
                "request",
                data="data",
                data_type="WRONG",  # type: ignore
            ).send(credentials=self.cred)
        mock_post.assert_not_called()

    @patch("requests.post")
    def testSubmissionCredentials(self, mock_post, *_):
        cred = mba.MbzCredentials()
        cred.auth_set("user", "pass")
        mbr.MbzSubmission(
            self.user_agent, "request", data="data", data_type="xml"
        ).send(credentials=cred)
        headers = self.headers
        headers["Content-Type"] = "application/xml; charset=utf-8"
        payload = self.payload
        payload["client"] = self.user_agent
        mock_post.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            data=self.data,
            params=self.payload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
        )

    def testSubmissionCredentialsNone(self, _):
        t = False
        try:
            mbr.MbzSubmission(
                self.user_agent,
                "entity",
                "XML_DATA",
                "xml",
            ).send(
                None  # type: ignore
            )
        except mbr.MbzWebServiceError:
            t = True
        self.assertTrue(t)
