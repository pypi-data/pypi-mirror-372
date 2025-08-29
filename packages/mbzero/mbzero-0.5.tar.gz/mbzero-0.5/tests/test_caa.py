#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import unittest
from unittest.mock import patch

from mbzero import caarequest as caa

CAA_API = caa.CAA_API
OTHER_API = "https://example.com"


def _raise_exception(*args, **kwargs):
    from requests import exceptions as rexc

    raise rexc.RequestException


@patch("requests.head")
@patch("requests.get")
class CaaTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testCaa(self, mock_get, _):
        caa.CaaRequest(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send()
        mock_get.assert_called_once_with(
            url=CAA_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testCaaAPIOther(self, mock_get, _):
        caa.CaaRequest(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            url=OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testCaaAPINone(self, mock_get, _):
        caa.CaaRequest(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(opts={"url": ""})
        mock_get.assert_called_once_with(
            url="/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testCaaSetAPI(self, mock_get, _):
        req = caa.CaaRequest(
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

    def testCaaSetAPINone(self, mock_get, _):
        req = caa.CaaRequest(
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

    def testCaaItemRequest(self, mock_get, _):
        caa.CaaRequest(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3", "front"
        ).send()
        mock_get.assert_called_once_with(
            url=CAA_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3/front",
            params=self.payload,
            headers=self.headers,
            data=None,
        )

    def testCaaHeadAPIOther(self, _, mock_head):
        caa.CaaRequest(
            self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        ).send(head=True, opts={"url": OTHER_API})
        mock_head.assert_called_once_with(
            OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
        )


class CaaTestException(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"

    @patch("requests.head", _raise_exception)
    def testCaaHeadException(self):
        t = False
        try:
            caa.CaaRequest(
                self.user_agent, "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
            ).send(head=True)
        except caa.MbzWebServiceError:
            t = True
        self.assertTrue(t)
