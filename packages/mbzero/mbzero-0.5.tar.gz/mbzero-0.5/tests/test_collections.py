import unittest
from typing import Any
from unittest.mock import patch

from requests.auth import HTTPDigestAuth

from mbzero import mbzauth as mba
from mbzero import mbzrequest as mbr

MUSICBRAINZ_API = mbr.MUSICBRAINZ_API
OTHER_API = "https://example.com"


class CollectionModificationTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.client = "test_client"
        self.headers = {"User-Agent": self.user_agent}
        self.payload: dict[str, Any] = {"fmt": "json"}
        self.cred_oauth2 = mba.MbzCredentials()
        self.cred_oauth2.oauth2_new("token", "refresh", "client_id", "client_secret")
        self.cred_basic = mba.MbzCredentials()
        self.cred_basic.auth_set("user", "pass")

    @patch("requests_oauthlib.OAuth2Session.put")
    def testAddOneToCollectionOAuth2(self, mock_put):
        mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        ).send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=MUSICBRAINZ_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.put")
    def testAddOneToCollectionBasicAuth(self, mock_put):
        mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        ).send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=MUSICBRAINZ_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.put")
    def testAddMultipleToCollectionOAuth2(self, mock_put):
        mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        ).send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=MUSICBRAINZ_API
            + "/collection/COLLECTION_ID/releases/RELEASE1;RELEASE2;RELEASE3",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.put")
    def testAddMultipleToCollectionBasicAuth(self, mock_put):
        mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        ).send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=MUSICBRAINZ_API
            + "/collection/COLLECTION_ID/releases/RELEASE1%3BRELEASE2%3BRELEASE3",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.put")
    def testAddToCollectionDifferentURLOAuth2(self, mock_put):
        req = mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        )
        req.set_url(OTHER_API)
        req.send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=OTHER_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.put")
    def testAddToCollectionBasicAuth(self, mock_put):
        req = mbr.MbzAddToCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        )
        req.set_url(OTHER_API)
        req.send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_put.assert_called_once_with(
            url=OTHER_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.delete")
    def testRemoveOneFromCollectionOAuth2(self, mock_delete):
        mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        ).send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=MUSICBRAINZ_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.delete")
    def testRemoveOneFromCollectionBasicAuth(self, mock_delete):
        mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1"],
            client=self.client,
        ).send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=MUSICBRAINZ_API + "/collection/COLLECTION_ID/releases/RELEASE1",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.delete")
    def testRemoveMultipleFromCollectionOAuth2(self, mock_delete):
        mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        ).send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=MUSICBRAINZ_API
            + "/collection/COLLECTION_ID/releases/RELEASE1;RELEASE2;RELEASE3",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.delete")
    def testRemoveMultipleFromCollectionBasicAuth(self, mock_delete):
        mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        ).send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=MUSICBRAINZ_API
            + "/collection/COLLECTION_ID/releases/RELEASE1%3BRELEASE2%3BRELEASE3",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )

    @patch("requests_oauthlib.OAuth2Session.delete")
    def testRemoveFromCollectionDifferentURLOAuth2(self, mock_delete):
        req = mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        )
        req.set_url(OTHER_API)
        req.send(self.cred_oauth2)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=OTHER_API
            + "/collection/COLLECTION_ID/releases/RELEASE1;RELEASE2;RELEASE3",
            params=expPayload,
            headers=self.headers,
            data=None,
        )

    @patch("requests.delete")
    def testRemoveMultipleCollectionsBasicAuth(self, mock_delete):
        req = mbr.MbzRemoveFromCollection(
            self.user_agent,
            "COLLECTION_ID",
            "release",
            ["RELEASE1", "RELEASE2", "RELEASE3"],
            client=self.client,
        )
        req.set_url(OTHER_API)
        req.send(self.cred_basic)
        expPayload = self.payload.copy()
        expPayload["client"] = self.client
        mock_delete.assert_called_once_with(
            url=OTHER_API
            + "/collection/COLLECTION_ID/releases/RELEASE1%3BRELEASE2%3BRELEASE3",
            params=expPayload,
            headers=self.headers,
            auth=HTTPDigestAuth("user", "pass"),
            data=None,
        )
