#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2


import requests
from requests.exceptions import RequestException

from .mbzerror import MbzWebServiceError
from .mbzrequest import MbzRequest

CAA_API = "https://coverartarchive.org"


class CaaRequest(MbzRequest):
    def __init__(self, user_agent, entity_type, mbid, item_request=None):
        """Initialize a CAA request

        :param user_agent: string User agent to be sent on request
        :param entity_type: string Musicbrainz entity
        :param mbid: string Musicbrainz ID
        :param item_request: optional request"""
        super().__init__(user_agent)
        self.url = CAA_API
        self.entity_type = entity_type
        self.mbid = mbid
        self.item_request = item_request

    def head(self, request, opts=None):
        """Send a request

        :param: request: the request to send to the server
        :param url:  Optional API endpoint (defaults is musicbrainz.org API)"""

        url = self.url or ""

        if opts is not None:
            url = opts.get("url", "")

        try:
            r = requests.head(url + request)
            r.raise_for_status()
            return r.content
        except RequestException as e:
            raise MbzWebServiceError._from_requests_error(e) from e

    def send(self, head=False, opts=None):
        """Format the request and send

        :param head: use a HEAD request instead of GET
        :param opts: Optional dictionary of parameters.
                     Valid option is url, extra_headers, extra_payload"""
        payload = self.payload

        if self.item_request is None:
            request = "/{}/{}".format(self.entity_type, self.mbid)
        else:
            request = "/{}/{}/{}".format(self.entity_type, self.mbid, self.item_request)

        if not head:
            return super().get(request, payload=payload, opts=opts)
        else:
            return self.head(request, opts=opts)
