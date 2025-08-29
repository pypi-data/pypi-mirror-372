#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import unittest
from typing import Any
from unittest.mock import patch

from requests.auth import HTTPDigestAuth

from mbzero import mbzauth as mba
from mbzero import mbzrequest as mbr

MUSICBRAINZ_API = mbr.MUSICBRAINZ_API
OTHER_API = "https://example.com"


def _raise_request_exception(*args, **kwargs):
    from requests import exceptions

    raise exceptions.RequestException("mock")


class InferClientFromUserAgentTest(unittest.TestCase):
    def testInferringSuccess(self):
        user_agents = [
            "MyAwesomeTagger/1.2.0 ( http://myawesometagger.example.com )",
            "MyAwesomeTagger/1.2.0 (http://myawesometagger.example.com)",
            "MyAwesomeTagger/1.2.0(http://myawesometagger.example.com)",
            "MyAwesomeTagger/1.2.0 ( me@example.com )",
            "MyAwesomeTagger/1.2.0 (me@example.com)",
            "MyAwesomeTagger/1.2.0(me@example.com)",
        ]
        expected_client = "MyAwesomeTagger-1.2.0"

        for user_agent in user_agents:
            with self.subTest(user_agent=user_agent):
                self.assertEqual(
                    mbr.MbzRequest._infer_client_from_user_agent(user_agent),
                    expected_client,
                )

    def testComplexInferringSuccess(self):
        self.assertEqual(
            mbr.MbzRequest._infer_client_from_user_agent(
                "MyAwesome_Tagger/123.456.789 ( http://myawesometagger.example.com )"
            ),
            "MyAwesome_Tagger-123.456.789",
        )

        self.assertEqual(
            mbr.MbzRequest._infer_client_from_user_agent(
                "MyAwesomeTagger123/v123 ( http://myawesometagger.example.com )"
            ),
            "MyAwesomeTagger123-v123",
        )

    def testInferringFailure(self):
        user_agents = [
            "MyAwesomeTagger",
            "MyAwesomeTagger - 1.2.0 (http://myawesometagger.example.com)",
        ]

        for user_agent in user_agents:
            with self.subTest(user_agent=user_agent):
                self.assertEqual(
                    mbr.MbzRequest._infer_client_from_user_agent(user_agent),
                    user_agent,
                )


@patch("requests.get")
class RequestTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}

    def testSend(self, mock_get):
        mbr.MbzRequest(self.user_agent).get(
            "/request", payload=self.payload, headers=self.headers
        )
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSendOpts(self, mock_get):
        mbr.MbzRequest(self.user_agent).get(
            "/request", payload=self.payload, headers=self.headers, opts={"limit": 10}
        )
        self.payload["limit"] = 10
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSendOptsExtraHeaders(self, mock_get):
        extraHeaders = {"my": "header"}
        expectedHeaders = dict(self.headers, **extraHeaders)
        mbr.MbzRequest(self.user_agent).get(
            "/request",
            payload=self.payload,
            headers=self.headers,
            opts={"extra_headers": extraHeaders},
        )
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            params=self.payload,
            headers=expectedHeaders,
            data=None,
        )

    def testSendOptsExtraPayloads(self, mock_get):
        extraPayload = {"my": "payload"}
        expectedPayload = dict(self.payload, **extraPayload)
        mbr.MbzRequest(self.user_agent).get(
            "/request",
            payload=self.payload,
            headers=self.headers,
            opts={"extra_payload": extraPayload},
        )
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            params=expectedPayload,
            headers=self.headers,
            data=None,
        )

    def testSendOptsAPIOther(self, mock_get):
        mbr.MbzRequest(self.user_agent).get(
            "/request",
            payload=self.payload,
            headers=self.headers,
            opts={"url": OTHER_API},
        )
        mock_get.assert_called_once_with(
            url=OTHER_API + "/request",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSendOptsAPINone(self, mock_get):
        mbr.MbzRequest(self.user_agent).get(
            "/request", payload=self.payload, headers=self.headers, opts={"url": ""}
        )
        mock_get.assert_called_once_with(
            url="/request",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSendSetAPINone(self, mock_get):
        req = mbr.MbzRequest(self.user_agent)
        req.set_url("")
        req.get("/request", payload=self.payload, headers=self.headers)
        mock_get.assert_called_once_with(
            url="/request",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSendCredentials(self, mock_get):
        creds = mba.MbzCredentials()
        creds.auth_set("name", "pass")
        mbr.MbzRequest(self.user_agent).get(
            "/request", creds, payload=self.payload, headers=self.headers
        )
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/request",
            params=self.payload,
            headers=self.headers,
            auth=HTTPDigestAuth("name", "pass"),
            data=None,
        )


@patch("requests.get")
class LookupTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}

    def testLookup(self, mock_get):
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send()
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupAPIOther(self, mock_get):
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            url=OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupAPINone(self, mock_get):
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": ""})
        mock_get.assert_called_once_with(
            url="/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupSetAPI(self, mock_get):
        req = mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        )
        req.set_url(OTHER_API)
        req.send()
        mock_get.assert_called_once_with(
            url=OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupSetAPINone(self, mock_get):
        req = mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        )
        req.set_url("")
        req.send()
        mock_get.assert_called_once_with(
            url="/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupOpts(self, mock_get):
        expectedPayload = self.payload.copy()
        expectedPayload["limit"] = 10
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"limit": 10})
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=expectedPayload,
            headers=self.headers,
            data=None,
        )

    def testLookupOptsNone(self, mock_get):
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"limit": None})
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"fmt": "xml"})
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupFmtNone(self, mock_get):
        mbr.MbzRequestLookup(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"fmt": None})
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testLookupInc(self, mock_get):
        self.payload["inc"] = "recordings+releases+release-groups"
        mbr.MbzRequestLookup(
            self.user_agent,
            "artist",
            "0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            ["recordings", "releases", "release-groups"],
        ).send()
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )


@patch("requests.get")
class BrowseTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}

    def testBrowse(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send()
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseAPIOther(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": OTHER_API})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=OTHER_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseAPINone(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": ""})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url="/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseSetAPI(self, mock_get):
        req = mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        )
        req.set_url(OTHER_API)
        req.send()
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=OTHER_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseSetAPINone(self, mock_get):
        req = mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        )
        req.set_url("")
        req.send()
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url="/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseOpts(self, mock_get):
        self.payload["limit"] = 10
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"limit": 10})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseOptsNone(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"limit": None})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"fmt": "xml"})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseFmtNone(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent, "release", "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"fmt": None})
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testBrowseInc(self, mock_get):
        mbr.MbzRequestBrowse(
            self.user_agent,
            "release",
            "artist",
            "0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            ["recordings", "releases", "release-groups"],
        ).send()
        self.payload["inc"] = "recordings+releases+release-groups"
        self.payload["artist"] = "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )


@patch("requests.get")
class SearchTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}

    def testSearch(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send()
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchAPIOther(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            opts={"url": OTHER_API}
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=OTHER_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchAPINone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(opts={"url": ""})
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url="/release", params=self.payload, headers=self.headers, data=None
        )

    def testSearchSetAPI(self, mock_get):
        req = mbr.MbzRequestSearch(self.user_agent, "release", "QUERY")
        req.set_url(OTHER_API)
        req.send()
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=OTHER_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchSetAPINone(self, mock_get):
        req = mbr.MbzRequestSearch(self.user_agent, "release", "QUERY")
        req.set_url("")
        req.send()
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url="/release", params=self.payload, headers=self.headers, data=None
        )

    def testSearchOpts(self, mock_get):
        self.payload["limit"] = 10
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            opts={"limit": 10}
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchOptsNone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            opts={"limit": None}
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            opts={"fmt": "xml"}
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testSearchFmtNone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send(
            opts={"fmt": None}
        )
        self.payload["query"] = "QUERY"
        mock_get.assert_called_once_with(
            url=MUSICBRAINZ_API + "/release",
            params=self.payload,
            headers=self.headers,
            data=None,
        )


@patch("requests.get", _raise_request_exception)
@patch("requests.post", _raise_request_exception)
class RequestsExceptionTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testSendException(self):
        t = False
        try:
            mbr.MbzRequest(self.user_agent).get(
                "/request", payload=self.payload, headers=self.headers
            )
        except mbr.MbzWebServiceError:
            t = True
        self.assertTrue(t)

    def testPostException(self):
        t = False
        try:
            mbr.MbzSubmission(self.user_agent, "entity", "XML_DATA", "xml").send(
                mba.MbzCredentials()
            )
        except mbr.MbzWebServiceError:
            t = True
        self.assertTrue(t)
