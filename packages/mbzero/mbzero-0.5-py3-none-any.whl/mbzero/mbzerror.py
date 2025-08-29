#  SPDX-FileCopyrightText: 2024 Louis Rannou
#
#  SPDX-License-Identifier: BSD-2

from requests.exceptions import HTTPError, RequestException


class MbzError(Exception):
    """Base class for all exceptions related to MusicBrainz."""

    pass


class MbzWebServiceError(MbzError):
    """Error related to MusicBrainz API requests."""

    @staticmethod
    def _from_requests_error(e: RequestException) -> "MbzWebServiceError":
        """Convert a requests error to a mbzero one.
        The error will be analyzed to try to use a more specific error instance if
        possible.

        :param e: The error to convert
        :return: The converted error
        """
        if isinstance(e, HTTPError):
            status_code = e.response.status_code

            if status_code == 400:
                return MbzBadRequestError(e)
            elif status_code == 401:
                return MbzUnauthorizedError(e)
            elif status_code == 404:
                return MbzNotFoundError(e)

        # Base exception if no specific one could be found
        return MbzWebServiceError(e)


class MbzBadRequestError(MbzWebServiceError):
    """Error raised when the request does not have valid and sufficient
    authentication for accessing the resource"""

    pass


class MbzUnauthorizedError(MbzWebServiceError):
    """Error raised when the request does not have valid and sufficient
    authentication for accessing the resource"""

    pass


class MbzNotFoundError(MbzWebServiceError):
    """Error raised when an entity is not found"""

    pass


class MbzOauth2Error(MbzWebServiceError):
    """OAuth2 failure"""

    pass
