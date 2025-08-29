#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

import re
from typing import TYPE_CHECKING, Any, Literal, Union

import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException

from mbzero.mbzerror import MbzWebServiceError

if TYPE_CHECKING:
    from .mbzauth import MbzCredentials

    _OptsKeys = Literal[
        "url", "extra_headers", "extra_payload", "fmt", "limit", "offset"
    ]
    _OptsDict = dict[_OptsKeys, Any]

    _Data = Union[str, bytes]

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"


class MbzRequest:
    """Base class for requests"""

    def __init__(self, user_agent: str, client: str | None = None):
        """Initialize a request

        :param user_agent: User agent to send for each request. The recommended format
            is either 'Application name/<version> ( contact-url )' or
            'Application name/<version> ( contact-email )'
        :param client: Value of the 'client' parameter to send on POST, PUT, and DELETE
            requests. The recommended format is 'application-version', where version does
            not contain a '-' character.
            If left empty and if the user_agent follows the recommended format, the value
            will be inferred from the user_agent
        """
        self.url = MUSICBRAINZ_API
        self.user_agent = user_agent
        self.client = client or MbzRequest._infer_client_from_user_agent(
            self.user_agent
        )
        self.payload: dict[str, Any] = {"fmt": "json"}

    @staticmethod
    def _infer_client_from_user_agent(user_agent: str) -> str:
        match = re.match(
            r"(?P<app_name>[^(]+)/(?P<version>[^(]+) *\(.*\)",
            user_agent,
        )
        if match is not None:
            # A match has been found: set the client in the recommended format
            app_name = match.group("app_name").strip()
            version = match.group("version").strip()
            return f"{app_name}-{version}"
        else:
            # No match could be found: use the user_agent as-is
            return user_agent

    def set_url(self, url: str):
        """Change the API root URL

        :param url: New API root URL
        """
        self.url = url

    def _send(
        self,
        method: Literal["get", "post", "put", "delete"],
        request: str,
        data: "_Data | None" = None,
        credentials: "MbzCredentials | None" = None,
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        opts: "_OptsDict | None" = None,
    ) -> bytes:
        url = self.url

        _payload = self.payload.copy()
        if payload is not None:
            _payload.update(payload)
        _headers = headers.copy() if headers is not None else {}

        # Add user agent for all request
        if "User-Agent" not in _headers:
            _headers["User-Agent"] = self.user_agent

        # Process special options
        if opts is not None:
            if "url" in opts:
                url = opts["url"]
            if "extra_headers" in opts:
                _headers.update(opts["extra_headers"])
            if "extra_payload" in opts:
                _payload.update(opts["extra_payload"])
            for opt in "fmt", "limit", "offset":
                opt_value = opts.get(opt, None)
                if opt_value is not None:
                    _payload[opt] = opt_value

        if method == "get":
            requests_method = requests.get
        elif method == "post":
            requests_method = requests.post
        elif method == "put":
            requests_method = requests.put
        elif method == "delete":
            requests_method = requests.delete
        else:
            raise MbzWebServiceError(f"Invalid request method: {method}")

        try:
            if credentials:
                if credentials.has_oauth2():
                    oauth2_method = credentials._get_request_method(method)
                    r = oauth2_method(
                        url=url + request, params=_payload, headers=_headers, data=data
                    )
                elif credentials.has_auth():
                    (username, password) = credentials.auth()
                    assert (username is not None) and (password is not None)

                    # There is a bug in the requests lib that incorrectly fills the
                    # Authentication header when using digest authentication and when
                    # the URL path contains semicolons.
                    # -> bug: https://github.com/psf/requests/issues/6990
                    # -> see also: https://www.rfc-editor.org/rfc/rfc2396#section-3.3
                    #
                    # Until this is fixed in requests (and to support older versions),
                    # semicolons can be escaped to work around this bug.
                    escaped_url = (url + request).replace(";", "%3B")
                    r = requests_method(
                        url=escaped_url,
                        params=_payload,
                        headers=_headers,
                        data=data,
                        auth=HTTPDigestAuth(username, password),
                    )
                else:
                    raise MbzWebServiceError("Credentials set but not initialized")
            else:
                r = requests_method(
                    url=url + request, params=_payload, headers=_headers, data=data
                )
            r.raise_for_status()
            return r.content
        except RequestException as e:
            raise MbzWebServiceError._from_requests_error(e) from e

    def get(
        self,
        request: str,
        credentials: "MbzCredentials | None" = None,
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        opts: "_OptsDict | None" = None,
    ):
        """Send a GET request

        :param request: The path from the API root URL to the ressource to request.
            This must include the leading '/'
        :param credentials: Credentials to use for the request. If not set, the request
            not be authenticated
        :param headers: Additional request headers to add to the request
        :param payload: Additional request parameters to add to the request
        :param opts: Special options to modify the request
        """

        return self._send(
            method="get",
            request=request,
            credentials=credentials,
            headers=headers,
            payload=payload,
            opts=opts,
        )

    def post(
        self,
        request: str,
        data: "_Data",
        data_type: Literal["xml"],
        credentials: "MbzCredentials",
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        opts: "_OptsDict | None" = None,
    ):
        """Send a POST request

        :param request: The path from the API root URL to the ressource to request.
            This must include the leading '/'
        :param data: The content to submit
        :param data_type: The content type (only "xml" is supported)
        :param credentials: Credentials to use for the request
        :param headers: Additional request headers to add to the request
        :param payload: Additional request parameters to add to the request
        :param opts: Special options to modify the request
        """

        if credentials is None:
            raise MbzWebServiceError("Submission requires credentials")

        if data_type != "xml":
            raise MbzWebServiceError(
                f"Musicbrainz does not support {data_type} content"
            )

        _headers = headers.copy() if headers is not None else {}
        _headers["Content-Type"] = "application/xml; charset=utf-8"

        # Add client for all POST requests
        _payload = payload.copy() if payload is not None else {}
        if "client" not in _payload:
            _payload["client"] = self.client

        return self._send(
            "post",
            request=request,
            data=data,
            credentials=credentials,
            headers=_headers,
            payload=_payload,
            opts=opts,
        )

    def put(
        self,
        request: str,
        credentials: "MbzCredentials",
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        opts: "_OptsDict | None" = None,
    ):
        """Send a PUT request

        :param request: The path from the API root URL to the ressource to request.
            This must include the leading '/'
        :param credentials: Credentials to use for the request
        :param headers: Additional request headers to add to the request
        :param payload: Additional request parameters to add to the request
        :param opts: Special options to modify the request
        """

        if credentials is None:
            raise MbzWebServiceError("Submission requires credentials")

        # Add client for all PUT requests
        _payload = payload.copy() if payload is not None else {}
        if "client" not in _payload:
            _payload["client"] = self.client

        return self._send(
            "put",
            request=request,
            credentials=credentials,
            headers=headers,
            payload=_payload,
            opts=opts,
        )

    def delete(
        self,
        request: str,
        credentials: "MbzCredentials",
        headers: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        opts: "_OptsDict | None" = None,
    ):
        """Send a DELETE request

        :param request: The path from the API root URL to the ressource to request.
            This must include the leading '/'
        :param credentials: Credentials to use for the request
        :param headers: Additional request headers to add to the request
        :param payload: Additional request parameters to add to the request
        :param opts: Special options to modify the request
        """

        if credentials is None:
            raise MbzWebServiceError("Submission requires credentials")

        # Add client for all DELETE requests
        _payload = payload.copy() if payload is not None else {}
        if "client" not in _payload:
            _payload["client"] = self.client

        return self._send(
            "delete",
            request=request,
            credentials=credentials,
            headers=headers,
            payload=_payload,
            opts=opts,
        )


class MbzRequestLookup(MbzRequest):
    """Class for lookup requests"""

    def __init__(
        self, user_agent: str, entity_type: str, mbid: str, includes: list[str] = []
    ):
        """Initialize a lookup request

        :param user_agent: User agent to be sent on request
        :param entity_type: The MusicBrainz entity type to lookup
        :param mbid: The MusicBrainz ID of the entity to lookup
        :param includes: List of strings of MusicBrainz includes
        """
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.mbid = mbid
        self.includes = includes

    def send(
        self,
        credentials: "MbzCredentials | None" = None,
        opts: "_OptsDict | None" = None,
    ):
        """Format the request and send

        :param credentials: Credentials to use for the request. If not set, the request
            not be authenticated
        :param opts: Special options to modify the request
        """
        payload = self.payload

        if self.includes:
            payload["inc"] = "+".join(self.includes)

        # Lookup requests are done requesting: /{entity-type}/{mbid}
        request = "/%s/%s" % (self.entity_type, self.mbid)

        return super().get(request, credentials=credentials, payload=payload, opts=opts)


class MbzRequestBrowse(MbzRequest):
    """Class for browse requests"""

    def __init__(
        self,
        user_agent: str,
        entity_type: str,
        bw_entity_type: str,
        mbid: str,
        includes: list[str] = [],
    ):
        """Initialize a lookup request

        :param user_agent: User agent to be sent on request
        :param entity_type: The type of linked entities to find
        :param bw_entity_type: The type of entity to look up
        :param mbid: The MusicBrainz ID of the entity to look up
        :param includes: List of strings of MusicBrainz includes
        """
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.bw_entity_type = bw_entity_type
        self.mbid = mbid
        self.includes = includes

    def send(
        self,
        credentials: "MbzCredentials | None" = None,
        opts: "_OptsDict | None" = None,
    ):
        """Format the request and send

        :param credentials: Credentials to use for the request. If not set, the request
            not be authenticated
        :param opts: Special options to modify the request
        """
        payload = self.payload

        if self.includes:
            payload["inc"] = "+".join(self.includes)

        # Browse requests are done requesting: /{entity-type}?{bw_entity_type}={mbid}
        request = f"/{self.entity_type}"
        payload[self.bw_entity_type] = self.mbid

        return super().get(request, credentials=credentials, payload=payload, opts=opts)


class MbzRequestSearch(MbzRequest):
    """Class for search requests"""

    def __init__(self, user_agent: str, entity_type: str, query: str):
        """Initialize a search request

        :param user_agent: User agent to be sent on request
        :param entity_type: The type of entities to search
        :param query: The search query to use
        """
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.query = query

    def send(
        self,
        credentials: "MbzCredentials | None" = None,
        opts: "_OptsDict | None" = None,
    ):
        """Format the request and send

        :param credentials: Credentials to use for the request. If not set, the request
            not be authenticated
        :param opts: Special options to modify the request
        """
        payload = self.payload

        # Search requests are done requesting: /{entity-type}?query={query}
        request = f"/{self.entity_type}"
        payload["query"] = self.query

        return super().get(request, credentials=credentials, payload=payload, opts=opts)


class MbzSubmission(MbzRequest):
    """Class for submissions"""

    def __init__(
        self,
        user_agent: str,
        entity_type: str,
        data: "_Data",
        data_type: Literal["xml"],
        client: str | None = None,
    ):
        """Initialize the submission request

        :param user_agent: User agent to be sent on request
        :param entity_type: MusicBrainz entity to submit
        :param data: Content to submit
        :param data_type: Data content type (only xml is supported)
        :param client: Value of the 'client' parameter to send with the request. If not
            set, it will be inferred from the user_agent if it is in the MusicBrainz
            recommended format
        """
        super().__init__(user_agent, client)
        self.entity_type = entity_type
        self.data = data
        if data_type != "xml":
            raise Exception("Data content %s is not supported" % data_type)
        self.data_type: Literal["xml"] = data_type

    def send(
        self,
        credentials: "MbzCredentials",
        opts: "_OptsDict | None" = None,
    ):
        """Format the submission and send

        :param credentials: Credentials to use for the request
        :param opts: Special options to modify the request
        """
        payload = self.payload

        # Submission requests are done requesting: /{entity-type}
        request = "/%s" % (self.entity_type)

        return super().post(
            request,
            self.data,
            self.data_type,
            credentials=credentials,
            payload=payload,
            opts=opts,
        )


class MbzAddToCollection(MbzRequest):
    """Class for adding entities to a user collection"""

    def __init__(
        self,
        user_agent: str,
        collection_mbid: str,
        entity_type: str,
        entities_mbid: list[str],
        client: str | None = None,
    ):
        """Initialize the add-to-collection request

        :param user_agent: User agent to be sent on request
        :param collection_mbid: MusicBrainz ID of the collection to modify
        :param entity_type: The type of entities to add to the collection. e.g. "release"
        :param entities_mbid: List of MusicBrainz ID of the entities to add to the
            collection. Must not be empty
        :param client: Value of the 'client' parameter to send with the request. If not
            set, it will be inferred from the user_agent if it is in the MusicBrainz
            recommended format
        """
        super().__init__(user_agent, client)
        if len(entities_mbid) == 0:
            raise Exception("List of entities to add to collection cannot be empty")
        self.collection_mbid = collection_mbid
        self.entity_type = entity_type
        self.entities_mbid = entities_mbid

    def send(
        self,
        credentials: "MbzCredentials",
        opts: "_OptsDict | None" = None,
    ):
        """Format the request and send

        :param credentials: Credentials to use for the request
        :param opts: Special options to modify the request
        """
        payload = self.payload

        # add-to-collection requests are done requesting:
        # - /collection/{collection}/{entity_type}/{release1};{release2};...
        joined_entities = ";".join(self.entities_mbid)
        entities_type = f"{self.entity_type}s"  # Include the 's' suffix
        request = (
            f"/collection/{self.collection_mbid}/{entities_type}/{joined_entities}"
        )

        return super().put(
            request,
            credentials=credentials,
            payload=payload,
            opts=opts,
        )


class MbzRemoveFromCollection(MbzRequest):
    """Class for removing entities from a user collection"""

    def __init__(
        self,
        user_agent: str,
        collection_mbid: str,
        entity_type: str,
        entities_mbid: list[str],
        client: str | None = None,
    ):
        """Initialize the remove-from-collection request

        :param user_agent: User agent to be sent on request
        :param collection_mbid: MusicBrainz ID of the collection to modify
        :param entity_type: The type of entities to add to the collection. e.g. "release"
        :param entities_mbid: List of MusicBrainz ID of the entities to remove from the
            collection. Must not be empty
        :param client: Value of the 'client' parameter to send with the request. If not
            set, it will be inferred from the user_agent if it is in the MusicBrainz
            recommended format
        """
        super().__init__(user_agent, client)
        if len(entities_mbid) == 0:
            raise Exception(
                "List of releases to remove from collection cannot be empty"
            )
        self.collection_mbid = collection_mbid
        self.entity_type = entity_type
        self.entities_mbid = entities_mbid

    def send(
        self,
        credentials: "MbzCredentials",
        opts: "_OptsDict | None" = None,
    ):
        """Format the request and send

        :param credentials: Credentials to use for the request
        :param opts: Special options to modify the request
        """
        payload = self.payload

        # remove-from-collection requests are done requesting:
        # - /collection/{collection}/{entity_type}/{release1};{release2};...
        joined_entities = ";".join(self.entities_mbid)
        entities_type = f"{self.entity_type}s"  # Include the 's' suffix
        request = (
            f"/collection/{self.collection_mbid}/{entities_type}/{joined_entities}"
        )

        return super().delete(
            request,
            credentials=credentials,
            payload=payload,
            opts=opts,
        )
