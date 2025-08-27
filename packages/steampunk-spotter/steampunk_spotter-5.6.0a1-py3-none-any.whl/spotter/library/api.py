"""Provide API client."""

import json
import ssl
import sys
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional, Tuple

import requests
from requests import Session
from requests.adapters import HTTPAdapter

from spotter.library.storage import Storage
from spotter.library.utils import get_current_cli_version


class CustomHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        # this creates a default context with secure default settings,
        # which enables server certficiate verification using the
        # system's default CA certificates
        context = ssl.create_default_context()

        # alternatively, you could create your own context manually
        # but this does NOT enable server certificate verification
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        super().init_poolmanager(*args, **kwargs, ssl_context=context)  # type: ignore[no-untyped-call]


class CustomHTTPAdapterDoNotValidateServer(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        context = ssl.SSLContext()
        super().init_poolmanager(*args, **kwargs, ssl_context=context)  # type: ignore[no-untyped-call]


class ApiClient:
    """A client interface for interacting with the API."""

    DEFAULT_ENDPOINT = "https://api.spotter.steampunk.si/api"
    DEFAULT_HEADERS: ClassVar[Dict[str, str]] = {
        "Accept": "application/json",
        "User-Agent": f"steampunk-spotter/{get_current_cli_version()}",
    }
    DEFAULT_TIMEOUT = 10

    def __init__(
        self,
        base_url: str,
        storage: Storage,
        api_token: Optional[str],
        username: Optional[str],
        password: Optional[str],
        debug: bool,
        cacert: Optional[Path],
        verify: bool,
    ):
        """
        Construct ApiClient object.

        :param base_url: Base API endpoint url
        :param storage: Storage object, where tokens are stored
        :param api_token: API token
        :param username: Username
        :param password: Password
        :param debug: Enable debug mode
        """
        self._base_url = base_url.rstrip("/")
        self._storage = storage
        self._api_token = api_token
        self._username = username
        self._password = password
        self._debug = debug
        self._me: Optional[Dict[str, Any]] = None

        self._storage_tokens_path = "tokens" if self._storage.exists("tokens") else "tokens.json"
        if self._storage_tokens_path == "tokens":
            self._old_tokens_fallback()

        session = Session()
        if verify is False:
            session.verify = False
            session.mount("https://", CustomHTTPAdapterDoNotValidateServer())
        else:
            session.verify = str(cacert) if cacert else True
            session.mount("https://", CustomHTTPAdapter())

        self.session = session

    def _url(self, path: str) -> str:
        """
        Construct the full API endpoint URL based on the base path.

        :return: Full API endpoint URL based on the base path
        """
        return self._base_url + path

    def _check_auth_status(self) -> None:
        """Check if user is logged (if file with tokens exists in the storage)."""
        if not self._storage.exists(self._storage_tokens_path):
            print(
                "Error: you are not logged in!\n"
                "To log in, you should provide your API token or username and password:\n\n"
                "    - using spotter login command;\n"
                "    - via --token/-t option;\n"
                "    - by setting SPOTTER_TOKEN environment variable;\n"
                "    - via --username/-u and --password/-p options;\n"
                "    - by setting SPOTTER_USERNAME and SPOTTER_PASSWORD environment variables.\n",
                file=sys.stderr,
            )
            sys.exit(2)

    def _get_endpoint_tokens(self) -> Dict[str, str]:
        """
        Retrieve tokens for particular API endpoint from storage.

        :return: Dict with tokens
        """
        self._check_auth_status()

        tokens = self._storage.read_json(self._storage_tokens_path)
        endpoint_tokens = tokens.get(self._base_url, {})

        if not endpoint_tokens:
            print(
                f"Error: no {self._base_url} endpoint in {self._storage.path / self._storage_tokens_path}.",
                file=sys.stderr,
            )
            sys.exit(2)

        if not isinstance(endpoint_tokens, dict):
            print(
                f"Error: the {self._base_url} JSON entry from {self._storage.path / self._storage_tokens_path} "
                f"should be of type dict, but is '{type(endpoint_tokens)}'.",
                file=sys.stderr,
            )
            sys.exit(2)

        return endpoint_tokens

    def _get_api_token(self) -> Optional[str]:
        """
        Retrieve API token from storage.

        :return: API token as string
        """
        endpoint_tokens = self._get_endpoint_tokens()

        if not endpoint_tokens:
            print(
                f"Error: no {self._base_url} endpoint in {self._storage.path / self._storage_tokens_path}.",
                file=sys.stderr,
            )
            sys.exit(2)

        if not isinstance(endpoint_tokens, dict):
            print(
                f"Error: the {self._base_url} JSON entry from {self._storage.path / self._storage_tokens_path} "
                f"should be of type dict, but is '{type(endpoint_tokens)}'.",
                file=sys.stderr,
            )
            sys.exit(2)

        return endpoint_tokens.get("api_token", None)

    def _get_access_refresh_tokens(self) -> Tuple[str, str]:
        """
        Retrieve access and refresh token from storage.

        :return: Tokens as tuple of strings (access token, refresh token)
        """
        endpoint_tokens = self._get_endpoint_tokens()

        access_token = endpoint_tokens.get("access", None)
        refresh_token = endpoint_tokens.get("refresh", None)

        if not access_token:
            print(f"Error: no access token in {self._storage.path / self._storage_tokens_path}.", file=sys.stderr)
            sys.exit(2)
        if not refresh_token:
            print(f"Error: no refresh token in {self._storage.path / self._storage_tokens_path}.", file=sys.stderr)
            sys.exit(2)

        return access_token, refresh_token

    def _old_tokens_fallback(self) -> None:
        """Execute a fallback mechanism to ensure that users with old tokens path have the same JSON tokens format."""
        tokens = self._storage.read_json(self._storage_tokens_path)

        access_token = tokens.get("access", None)
        refresh_token = tokens.get("refresh", None)

        if self._base_url not in tokens and access_token and refresh_token:
            self._storage.write_json({self._base_url: tokens}, self._storage_tokens_path)

    def _update_endpoint_tokens(self, updated_tokens: Dict[Any, Any]) -> None:
        """
        Update tokens from storage for particular API endpoint.

        :param updated_tokens: Tokens to be updated as dict that will update the existing JSON from storage
        """
        endpoint_tokens = {}
        if self._storage.exists(self._storage_tokens_path):
            tokens = self._storage.read_json(self._storage_tokens_path)
            endpoint_tokens = tokens.get(self._base_url, {})

        endpoint_tokens.update(updated_tokens)
        self._storage.update_json({self._base_url: endpoint_tokens}, self._storage_tokens_path)

    def debug_print(self, message: str, *args: str) -> None:
        """
        Print a message to the standard error stream if the debug mode is enabled.

        :param message: The message to print with any lazy formatting.
        :param args: Options to be used in the formatting.
        """
        if self._debug:
            print(message.format(*args), file=sys.stderr)

    def _get_me(self) -> Dict[str, Any]:
        if self._me is None:
            response = self.get(path="/v2/users/me/")
            if response.status_code != 200:
                print(self.format_api_error(response), file=sys.stderr)
            self._me = response.json()

        return self._me

    def _debug_print_organization(self, message: str, organization: Dict[str, Any]) -> None:
        self.debug_print(f"{message} ({organization['id']}) {organization['name']}")

    def _debug_print_subscription(self, subscription: Dict[str, Any]) -> None:
        self.debug_print(
            f"Subscription plan {subscription['plan_type']}, {subscription['status']} "
            f"expires {subscription['end_date']}, "
            f"custom policies {'allowed' if subscription['custom_policies_enabled'] else 'not allowed'}"
        )

    def debug_project(self, project_id: str) -> None:
        """
        If in debug mode, fetch and print the information about the selected project.

        :param project_id: UUID of the project to obtain and print the details of.
        """
        if not self._debug:
            return
        me = self._get_me()
        organization: Optional[Dict[str, Any]] = None
        for org in me["organizations"]:
            if project_id in org["projects"]:
                organization = org
                break
        if organization is None:
            self.debug_print(f"Project with id {project_id} not found in any of my organizations")
        else:
            self._debug_print_organization("Project found in organization:", organization)
            self._debug_print_subscription(organization["subscription"])

    def debug_print_me(self) -> None:
        """If in debug mode, fetch and print the information about myself."""
        if not self._debug:
            return
        self.debug_print(f"API endpoint: {self._base_url}")
        me = self._get_me()
        self.debug_print(
            f"Logged in as ({me['id']}) {me['username']} - {me['first_name']} {me['last_name']} <{me['email']}>"
        )

    def debug_organization(self, organization_id: str) -> None:
        """
        If in debug mode, fetch and print the information about this organization.

        :param organization_id: UUID of the organization to print the details of.
        """
        if not self._debug:
            return
        me = self._get_me()
        org_matches = [o for o in me["organizations"] if o["id"] == organization_id]
        if len(org_matches) < 1:
            self.debug_print(f"Organization id {organization_id} not found for any of my organizations")
        else:
            self._debug_print_organization("Target organization:", org_matches[0])
            self._debug_print_subscription(org_matches[0]["subscription"])

    def debug_my_default_organization(self) -> None:
        """If in debug mode, fetch and print the information about my default organization."""
        if not self._debug:
            return
        me = self._get_me()
        try:
            default_organization_id = me["default_organization"]
            default_organization = next(o for o in me["organizations"] if o["id"] == default_organization_id)
            self._debug_print_organization("Default organization", default_organization)
            self.debug_print(f"Projects: {default_organization['projects']}")
            self._debug_print_subscription(default_organization["subscription"])
        except Exception as e:  # noqa: BLE001  # safety catchall
            print(f"Error: obtaining default organization info failed: {e}", file=sys.stderr)

    def login(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Login user to the API using API token or username and password, also verify and store auth tokens to storage.

        Note that we do not use self._request to prevent possible cyclic recursion errors.

        :param timeout: Request timeout
        """
        request_headers = self.DEFAULT_HEADERS.copy()
        updated_auth_tokens = {}

        if self._api_token:
            request_headers.update({"Authorization": f"SPTKN {self._api_token}"})
            updated_auth_tokens.update({"api_token": self._api_token})
        else:
            # old login - generate access and refresh token
            response = self.session.post(
                self._url("/v2/token/"),
                verify=self.session.verify,
                headers=request_headers,
                json={"username": self._username, "password": self._password},
                timeout=timeout,
            )

            if not response.ok:
                print(self.format_api_error(response), file=sys.stderr)
                sys.exit(2)

            try:
                tokens = response.json()
                access_token = tokens["access"]
            except (KeyError, json.JSONDecodeError):
                print(
                    "API error: unexpected response format. Verify SPOTTER_ENDPOINT is set to a Steampunk Spotter instance."
                )
                sys.exit(2)

            updated_auth_tokens.update(tokens)
            request_headers.update({"Authorization": f"Bearer {access_token}"})

        # verify auth tokens and save them to storage
        response = self.session.get(
            self._url("/v3/auth/verify/"), verify=self.session.verify, headers=request_headers, timeout=timeout
        )
        if response.ok:
            self._update_endpoint_tokens(updated_auth_tokens)
            self.debug_print_me()
            self.debug_my_default_organization()
        else:
            print(self.format_api_error(response), file=sys.stderr)
            sys.exit(2)

    def _refresh_login(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Login user to the API using the tokens (access and refresh token) from storage.

        :param timeout: Request timeout
        """
        # get existing tokens and then refresh access token and save it to local storage
        # note that we do not use self._request to prevent possible cyclic recursion errors
        _, refresh_token = self._get_access_refresh_tokens()
        response_token_refresh = self.session.post(
            self._url("/v2/token/refresh/"),
            verify=self.session.verify,
            headers=self.DEFAULT_HEADERS.copy(),
            json={"refresh": refresh_token},
            timeout=timeout,
        )
        if response_token_refresh.ok:
            refreshed_access_token = response_token_refresh.json().get("access", None)
            if not refreshed_access_token:
                print("Error: refreshing access token failed.", file=sys.stderr)
                sys.exit(2)

            access_token = refreshed_access_token
            self._storage.update_json(
                {self._base_url: {"access": access_token, "refresh": refresh_token}}, self._storage_tokens_path
            )
        else:
            print(self.format_api_error(response_token_refresh), file=sys.stderr)
            sys.exit(2)

    def logout(self) -> None:
        """Logout user - remove tokens for the current API endpoint from storage."""
        self._check_auth_status()

        tokens = self._storage.read_json(self._storage_tokens_path)
        endpoint_tokens = tokens.pop(self._base_url, None)
        if endpoint_tokens:
            self._storage.write_json(tokens, self._storage_tokens_path)
        else:
            print(
                f"You are already logged out because there is no {self._base_url} endpoint "
                f"in {self._storage.path / self._storage_tokens_path}.",
                file=sys.stderr,
            )
            sys.exit(0)

    def negotiate_api_version(self) -> str:
        client_versions = {"v3", "v4"}
        response = self._request("GET", "/versions/", ignore_response_status_codes=True)
        if response.status_code >= 400:
            return "v3"
        server_versions = response.json()
        available_versions = client_versions.intersection(server_versions)
        return max(available_versions)

    def _request(  # noqa: PLR0912  # TODO: oh dear
        self,
        method: str,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        allow_auth_retry: bool = True,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send HTTP request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout
        :param allow_auth_retry: Whether to allow reauthenticating and retrying the request
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        # initiate login from start if API token or username and password have been provided and tokens do not exist yet
        if (self._api_token or (self._username and self._password)) and not self._storage.exists(
            self._storage_tokens_path
        ):
            self._storage.remove(self._storage_tokens_path)
            self.login()

        # initiate login from start if endpoint does not exist in tokens
        if self._storage.exists(self._storage_tokens_path):
            tokens = self._storage.read_json(self._storage_tokens_path)
            endpoint_tokens = tokens.get(self._base_url, None)
            if not endpoint_tokens:
                self.login()

        # combine request headers (default + authorization + others)
        request_headers = self.DEFAULT_HEADERS.copy()
        if authorize:
            api_token = self._api_token or self._get_api_token()
            if api_token:
                request_headers.update({"Authorization": f"SPTKN {api_token}"})
            else:
                access_token, _ = self._get_access_refresh_tokens()
                request_headers.update({"Authorization": f"Bearer {access_token}"})
        request_headers.update(headers if headers is not None else {})

        # try to make a request
        try:
            response = self.session.request(
                method,
                self._url(path),
                verify=self.session.verify,
                headers=request_headers,
                json=payload if payload is not None else {},
                timeout=timeout,
            )
        except requests.exceptions.RequestException as e:
            print(f"API error: {e!s}", file=sys.stderr)
            sys.exit(2)

        # if request fails for one time try to log in and make a request again
        if not self._api_token and response.status_code == 401:
            if allow_auth_retry:
                self._refresh_login(timeout)
                # retry, but don't allow any more auth retries
                return self._request(
                    method,
                    path,
                    authorize,
                    headers,
                    payload,
                    timeout,
                    allow_auth_retry=False,
                    ignore_response_status_codes=ignore_response_status_codes,
                )

            print("Error: request failed after reauthenticating.", file=sys.stderr)
            sys.exit(2)
        else:
            # just return the response no matter what the response status code is
            if ignore_response_status_codes:
                return response
            # check if response is ok and can be converted to JSON
            if response.ok:
                try:
                    response.json()
                    return response
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(2)
            else:
                print(self.format_api_error(response), file=sys.stderr)
                sys.exit(2)

    def get(
        self,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send GET request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param timeout: Request timeout
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request(
            "GET",
            path,
            authorize=authorize,
            headers=headers,
            timeout=timeout,
            ignore_response_status_codes=ignore_response_status_codes,
        )

    def post(
        self,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send POST request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request(
            "POST",
            path,
            authorize=authorize,
            headers=headers,
            payload=payload,
            timeout=timeout,
            ignore_response_status_codes=ignore_response_status_codes,
        )

    def patch(
        self,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send PATCH request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request(
            "PATCH",
            path,
            authorize=authorize,
            headers=headers,
            payload=payload,
            timeout=timeout,
            ignore_response_status_codes=ignore_response_status_codes,
        )

    def put(
        self,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send PUT request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param payload: Request payload (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request(
            "PUT",
            path,
            authorize=authorize,
            headers=headers,
            payload=payload,
            timeout=timeout,
            ignore_response_status_codes=ignore_response_status_codes,
        )

    def delete(
        self,
        path: str,
        authorize: Optional[bool] = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        ignore_response_status_codes: Optional[bool] = False,
    ) -> requests.Response:
        """
        Send DELETE request.

        :param path: API endpoint path
        :param authorize: Add Authorization header to authorize request (True/False)
        :param headers: Request headers (JSON payload dict)
        :param timeout: Request timeout in seconds
        :param ignore_response_status_codes: Whether to ignore response status codes (even ones higher than 400)
        :return: Response object
        """
        return self._request(
            "DELETE",
            path,
            authorize=authorize,
            headers=headers,
            timeout=timeout,
            ignore_response_status_codes=ignore_response_status_codes,
        )

    def format_api_error(self, response: requests.Response) -> str:
        """
        Format API error.

        :param response: Response object
        :return: Formatted API error as string
        """
        try:
            try:
                return f"API error: {response.status_code} - {response.json()['message']}"
            except KeyError:
                return f"API error: {response.status_code} - {response.json()['detail']}"
        except (ValueError, KeyError):
            return f"API error: {response.status_code}"
