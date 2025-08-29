"""Client API module."""

from typing import Any, Literal

import requests
from requests import HTTPError, Response, Session
from requests.auth import AuthBase
from sincpro_framework import logger

from .pydantic import BaseModel


class HTTPErrorWithDetail(Exception):
    """HTTP error exception."""

    def __init__(
        self,
        message: str,
        reason: str,
        http_error: int,
        content: Any = None,
        text: str = None,
    ) -> None:
        """Initialize the HTTP error."""
        self.http_code = http_error
        self.reason = reason
        self.content = content
        self.text = text
        super().__init__(f"{message}: {text or content}")


class ApiResponse(BaseModel):
    """API response model."""

    raw_response: dict | None = None


class ClientAPI:
    """Client API class."""

    def __init__(self, session: Session | None = None, auth: AuthBase | None = None) -> None:
        """Initialize the client API."""
        self._session = session
        self._auth = auth

    @property
    def use_session(self) -> bool:
        """Set the session."""
        return bool(self._session)

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        raise NotImplementedError("You must implement the base_url property")

    def execute_request(
        self,
        resource: str,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        params=None,
        headers=None,
        data=None,
        timeout=None,
        auth=None,
    ) -> Response:  # pylint: disable=too-many-arguments
        """Low-level function for API calls.
        It wraps the requests library for managing sessions and custom Exceptions

        Args:
            resource (str): Path of the resource.
            method (str, optional): HTTP method to execute. Defaults to "GET".
            params (Dict[str, Any], optional): Query parameters to include in the URL. Defaults to None.
            headers (Dict[str, str], optional): HTTP method to execute. Defaults to None.
            data (Any, optional): Payload to send in the body. Defaults to None.
            timeout (int, optional): Amount of seconds to wait for a timeout and raise an exception
            auth (AuthBase, optional): Authentication object to use in the request. Defaults to None.

        Raises:
            APIHTTPError: Error that occurred during the execution of the request if HTTPError takes place.

        Returns:
            Response: Model for the HTTP response in requests
        """
        url = f"{self.base_url}{resource}"
        logger.debug(f"Requesting:[{method}] {url}", with_auth=bool(auth or self._auth))
        kwargs = {
            "url": url,
            "method": method,
        }
        if data:
            kwargs["json"] = data
        if headers:
            kwargs["headers"] = headers
        if params:
            kwargs["params"] = params
            logger.debug(f"Params: {params}")
        if timeout:
            kwargs["timeout"] = timeout
        if self._auth:
            kwargs["auth"] = self._auth
        if auth:
            kwargs["auth"] = auth

        if method != "GET":
            logger.debug(f"Body: {data}")

        if self.use_session:
            response = self._session.request(**kwargs)
        else:
            response = requests.request(**kwargs)
        try:
            response.raise_for_status()
        except HTTPError as error:
            if hasattr(error.response, "content") or hasattr(error.response, "text"):
                kwargs = {
                    "message": str(error),
                    "reason": error.response.reason,
                    "http_error": error.response.status_code,
                }

                if hasattr(error.response, "content"):
                    kwargs["content"] = error.response.content
                if hasattr(error.response, "text"):
                    kwargs["text"] = error.response.text

                raise HTTPErrorWithDetail(**kwargs) from error
            raise error
        return response
