import json
import logging
import os
import time
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import quote

import requests
from dotenv import find_dotenv, load_dotenv

from okapi_aether_sdk.error import (
    AuthenticationError,
    ClientError,
    RequestFailedError,
    RequestTimeoutError,
    ServerError,
    SetupError,
    UnexpectedError,
)

# Configure logging
logger = logging.getLogger(__name__)


class AetherApi:
    """
    Provides an interface for interacting with the Aether API,
    handling authentication, generic HTTP operations, and various helper routines.

    Before sending requests, you need to log in.
    This requires the following credentials as environment variables:

      * AETHER_AUTH0_USERNAME
      * AETHER_AUTH0_PASSWORD
      * AETHER_BASE_URL
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url: str = self._api_base_url(base_url)
        self.access_token: Optional[str] = None

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """Authenticate the user to retrieve an access token.

        If username and password are provided, they will be used for authentication.
        Otherwise, it retrieves the credentials from environment variables.
        """
        if not username or not password:
            username = os.getenv("AETHER_AUTH0_USERNAME")
            password = os.getenv("AETHER_AUTH0_PASSWORD")

        if not username or not password:
            raise SetupError(
                "Both username and password must be provided, either directly or via environment variables."
            )
        logger.info("Logging in to OKAPI:Aether...")
        self.access_token = self._get_access_token_from_auth0(username, password)
        logger.info("Authentication succeeded. You are ready to go.")

    def get(
        self, path: str, response_format: Literal["json", "html"] = "json", timeout: float = 20.0
    ) -> Any:
        """
        Sends a GET request to the specified path.

        :param path: The path to send the GET request to.
        :param response_format: Output format of the API response.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the GET request.
        """
        return self._send_request("GET", path, None, response_format, timeout)

    def post(self, path: str, request_body: Dict[str, Any], timeout: float = 20.0) -> Any:
        """
        Sends a POST request to the specified path with a request body.

        :param path: The path to send the POST request to.
        :param request_body: The body of the request, typically in JSON format.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the POST request.
        """
        return self._send_request("POST", path, request_body, "json", timeout)

    def put(self, path: str, request_body: Dict[str, Any], timeout: float = 20.0) -> Any:
        """
        Sends a PUT request to the specified path with a request body.

        :param path: The path to send the PUT request to.
        :param request_body: The body of the request, typically in JSON format.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the PUT request.
        """
        return self._send_request("PUT", path, request_body, "json", timeout)

    def patch(self, path: str, request_body: Dict[str, Any], timeout: float = 20.0) -> Any:
        """
        Sends a PATCH request to the specified path with a request body.

        :param path: The path to send the PATCH request to.
        :param request_body: The body of the request, typically in JSON format.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the PATCH request.
        """
        return self._send_request("PATCH", path, request_body, "json", timeout)

    def delete(self, path: str, timeout: float = 20.0) -> Any:
        """
        Sends a DELETE request to the specified path.

        :param path: The path to send the DELETE request to.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the DELETE request.
        """
        return self._send_request("DELETE", path, None, "json", timeout)

    def get_elements(self, path: str, timeout: float = 20.0) -> Optional[List[Any]]:
        """
        Fetches all elements from a list endpoint.

        :param path: The path to the list endpoint.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of elements from the response, or None if an error occurs.
        """
        response_data = self.get(path, timeout=timeout)

        if response_data is None:
            logger.warning("The response data is None. Returning None.")
            return None

        if "elements" in response_data:
            return response_data["elements"]
        elif "data" in response_data:
            return response_data["data"]

        logger.warning(f"Unexpected response format: {response_data}. Returning empty list.")
        return []

    def get_all_elements(self, path: str, timeout: float = 20.0) -> List[Any]:
        """
        Retrieves all elements from a paginated endpoint.

        :param path: The path to the endpoint.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of all elements retrieved from the endpoint.
        """
        full_elements = []
        page = 1
        sep = "&" if "?" in path else "?"

        while True:
            elements = self.get_elements(f"{path}{sep}page={page}", timeout)

            if not elements:
                logger.info("No more elements found at page %d.", page)
                break  # Exit if no more elements are returned

            full_elements.extend(elements)
            logger.info("Retrieved %d elements from page %d.", len(elements), page)
            page += 1  # Move to the next page

        logger.info("Total elements retrieved: %d", len(full_elements))
        return full_elements

    def get_request_id(self, path: str, data: Dict[str, Any], timeout: float = 20.0) -> str:
        """
        Sends a request to create a new resource and retrieves the request ID.

        :param path: The path to send the POST request for resource creation.
        :param data: The data for creating the resource.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID from the response, or an empty string if not found.
        """
        response_data = self.post(path, data, timeout)

        if "request_id" in response_data:
            return response_data["request_id"]

        logger.warning(f"Unexpected response format: {response_data}. Returning empty string.")
        return ""

    def wait_for_request_result(
        self,
        url_endpoint_results: str,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> Dict[str, Any]:
        """
        Send a request to the OKAPI platform and wait for the results.
        This method polls the results endpoint until a valid response is received or the max wait time is reached.

        :param url_endpoint_results: the URL where to get the result from.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: dict containing the results from the request.
        """
        retries = 0

        # Initialize result with a default structure in case all retries fail
        result: Dict[str, Any] = {"data": {}, "status": 200}

        # Retry loop for polling the result endpoint
        while retries < max_retries:
            try:
                # Attempt to retrieve the result from the endpoint
                result = self.get(url_endpoint_results, timeout=timeout)

                # Exit early if the response does not contain a request_id
                if not result.get("request_id"):
                    break

            except requests.exceptions.Timeout as e:
                # Raise a timeout error if this was the last allowed attempt
                if retries + 1 == max_retries:
                    raise RequestTimeoutError("Request timed out after multiple attempts.")

                # Log the timeout and retry after delay
                logger.warning("Timeout Error: %s. Retrying...", str(e))

            # Wait before the next retry attempt
            time.sleep(retry_delay)
            retries += 1

        return result

    def _api_base_url(self, base_url: Optional[str]) -> str:
        """Get the base URL for the API.

        If a base URL is provided, return it. Otherwise,
        load the environment variable or return a default URL.
        """
        if not {"AETHER_AUTH0_USERNAME", "AETHER_AUTH0_PASSWORD"}.issubset(os.environ):
            load_dotenv()  # Load environment variables from .env file
            load_dotenv(
                find_dotenv(usecwd=True)
            )  # Load environment variables from current working directory

        api_url = str(
            base_url or os.getenv("AETHER_BASE_URL", "https://api-aether.okapiorbits.com")
        ).strip()

        if api_url.endswith("/"):
            api_url = api_url[:-1]
        return api_url

    def _headers(self) -> Dict[str, str]:
        """
        Constructs the headers for HTTP requests, including authorization.

        :return: A dictionary containing the headers.
        """
        if self.access_token is None:
            raise AuthenticationError("Not authenticated - call login() first.")
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _html_headers(self) -> Dict[str, str]:
        """
        Construct headers for requests expecting HTML content.

        :return: A dictionary containing the headers.
        """
        if self.access_token is None:
            raise AuthenticationError("Not authenticated - call login() first.")
        return {
            "Accept": "text/html",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _get_access_token_from_auth0(self, username: str, password: str) -> str:
        """
        Obtains an access token from Auth0.

        :return: The access token as a string.
        :raises AuthenticationError: If an error occurs during authentication.
        """
        auth0_url = "https://okapi-development.eu.auth0.com/oauth/token"
        audience = "https://api.okapiorbits.space/picard"
        headers = {"Content-type": "application/json"}
        body = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "audience": audience,
            "scope": (
                "neptune_propagation neptune_propagation_request "
                "pass_predictions pass_prediction_requests "
                "pass_predictions_long pass_prediction_requests_long"
            ),
            "client_id": "jrk0ZTrTuApxUstXcXdu9r71IX5IeKD3",
        }

        try:
            response = requests.post(auth0_url, headers=headers, data=json.dumps(body), timeout=4)
            response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
            return response.json().get("access_token")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error occurred during authentication: {str(e)}")
            raise AuthenticationError(f"Auth0 returned {response.status_code} {response.json()}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout Error: {str(e)}")
            raise RequestTimeoutError(f"Timeout Error: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {str(e)}")
            raise RequestFailedError(f"Request Error: {str(e)}")

    def _send_request(
        self,
        method: str,
        path: str,
        request_body: Optional[Dict[str, Any]] = None,
        response_format: Literal["json", "html"] = "json",
        timeout: float = 20.0,
    ) -> Any:
        """
        Sends an HTTP request and handles retries and errors.

        :param method: The HTTP method to use (GET, POST, PUT, PATCH, DELETE).
        :param path: The path for the request.
        :param request_body: The body of the request, if applicable.
        :param response_format: Output format of the API response.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The response data from the request.
        :raises RequestFailedError: If the request fails after the maximum number of retries.
        """
        if path.startswith("/") and len(path) > 1:
            path = path[1:]
        url = f"{self.base_url}/{path}"
        headers = self._html_headers() if response_format == "html" else self._headers()

        try:
            logger.debug(f"Sending {method} request to {url}")

            if method == "POST":
                response = requests.post(url, json=request_body, headers=headers, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=request_body, headers=headers, timeout=timeout)
            elif method == "PATCH":
                response = requests.patch(url, json=request_body, headers=headers, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return (
                self._handle_html_response(response)
                if response_format == "html"
                else self._handle_response(response)
            )

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {method} {url}: {e}")
            self._handle_http_error(e, response)

    def _handle_http_error(self, error: Exception, response: requests.Response) -> None:
        """
        Handles HTTP errors based on the response status code.

        :param error: The caught HTTP error.
        :param response: The response object.
        :raises ClientError: If the error is due to a client side (4xx) issue.
        :raises ServerError: If the error is due to a server side (5xx) issue.
        :raises UnexpectedError: For any other unforeseen error.
        """
        if response is not None:
            try:
                error_text = response.json()
                if not error_text:
                    error_text = response.text
            except ValueError:
                error_text = response.text
            if 400 <= response.status_code < 500:
                logger.error(f"Client Error: {error} - {error_text}")
                raise ClientError(
                    response.status_code, f"Client Error: {error} - {error_text}"
                ) from error
            elif 500 <= response.status_code < 600:
                logger.error(f"Server Error: {error} - {error_text}")
                raise ServerError(
                    response.status_code, f"Server Error: {error} - {error_text}"
                ) from error
            else:
                logger.error(f"Unexpected Error: {error} - {error_text}")
                raise UnexpectedError(f"Unexpected Error: {error} - {error_text}")
        else:
            logger.error(f"Unexpected Error: {error}")
            raise UnexpectedError(f"Unexpected Error: {error}")

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handles the response from an HTTP request.

        :param response: The response object from the HTTP request.
        :return: The parsed JSON response data, if applicable.
        :raises UnexpectedError: For any unhandled response status codes.
        """
        if response.status_code in (200, 201, 204):
            return response.json() if response.status_code != 204 else None
        elif response.status_code == 202:
            logger.info(f"Request accepted, pending results: {response.json()}")
            data = response.json()
            data["status"] = {**data.get("status", {}), "status_code": response.status_code}
            return data
        else:
            logger.error(f"Unhandled response status: {response.status_code} - {response.text}")
            raise UnexpectedError(
                f"Unhandled response status: {response.status_code} - {response.text}"
            )

    def _handle_html_response(self, response: requests.Response) -> str:
        """
        Handles an HTTP response expected to return HTML content.

        :param response: The response object from the HTTP request.
        :return: The HTML string content if the request is successful.
        :raises UnexpectedError: For any unhandled response status codes.
        """
        if response.status_code == 200:
            return response.text
        else:
            logger.error(
                f"Unhandled HTML response status: {response.status_code} - {response.text}"
            )
            raise UnexpectedError(
                f"Unhandled HTML response status: {response.status_code} - {response.text}"
            )

    def _build_query(self, filters: dict) -> str:
        """
        Constructs a query string from a dictionary of filters.

        :param filters: A dictionary of filters to apply to the query.
        :return: A URL-encoded query string.
        """
        query = []

        for key, value in filters.items():
            if isinstance(value, dict):
                # Add each operator value to the query
                for op, op_value in value.items():
                    if isinstance(op_value, str):
                        query.append(f"{key}[{quote(op)}]={quote(op_value)}")
                    else:
                        query.append(f"{key}[{quote(op)}]={op_value}")
            elif isinstance(value, list):
                query.append(f"{key}={quote(','.join(str(item) for item in value))}")
            elif isinstance(value, bool):
                query.append(f"{key}={json.dumps(value)}")
            elif isinstance(value, str):
                query.append(f"{key}={quote(value)}")
            else:
                query.append(f"{key}={value}")

        return "&".join(query)
