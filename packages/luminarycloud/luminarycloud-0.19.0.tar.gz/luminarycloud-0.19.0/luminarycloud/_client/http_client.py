import logging
from typing import MutableMapping
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .._auth import Auth0Client
from .. import __version__


MAX_ERROR_BODY_LENGTH = 1000
REDACTED_HEADERS = ["Authorization", "x-api-key"]

logger = logging.getLogger(__name__)


class HTTPErrorWithBody(requests.HTTPError):
    """Custom HTTPError that includes response body text."""

    def __init__(self, response: requests.Response, *args, **kwargs):
        body_preview = response.text[:MAX_ERROR_BODY_LENGTH] + (
            "... [truncated]" if len(response.text) > MAX_ERROR_BODY_LENGTH else ""
        )
        message = f"{response.status_code} Error for {response.url}\nBody: {body_preview}"
        super().__init__(message, response=response, *args, **kwargs)


class HttpClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        auth0_client: Auth0Client | None = None,
        *,
        timeout: int = 10,
        retries: int = 3,
        backoff_factor: float = 0.3,
        retriable_status_codes: tuple = (500, 502, 503, 504, 429),
        log_body: bool = True,
        max_body_log_length: int = 500,
    ):
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["x-client-version"] = f"python-sdk-v{__version__}"
        if api_key:
            self.session.headers["x-api-key"] = api_key
            self.auth0_client = None
        elif auth0_client:
            self.auth0_client = auth0_client
        else:
            raise ValueError("Either api_key or auth0_client must be provided")
        self.timeout = timeout
        self.log_body = log_body
        self.max_body_log_length = max_body_log_length

        # Retry config
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=retriable_status_codes,
            allowed_methods=frozenset(["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _sanitize_headers(
        self, headers: MutableMapping[str, str | bytes]
    ) -> MutableMapping[str, str | bytes]:
        clean: MutableMapping[str, str | bytes] = {}
        for k, v in headers.items():
            if k in REDACTED_HEADERS:
                clean[k] = "[REDACTED]"
            else:
                clean[k] = v
        return clean

    def _log_request(self, method: str, url: str, kwargs: dict):
        if not logger.isEnabledFor(logging.DEBUG):
            return
        line = f"REQUEST {method} {url}\nHeaders: {self._sanitize_headers(self.session.headers)}"
        if self.log_body:
            body = kwargs.get("json") or kwargs.get("data")
            body_str = str(body)
            if body_str and len(body_str) > self.max_body_log_length:
                body_str = body_str[: self.max_body_log_length] + "... [truncated]"
            line += f"\nBody: {body_str}"
        logger.debug(line)

    def _log_response(self, resp: requests.Response):
        if not logger.isEnabledFor(logging.DEBUG):
            return
        line = f"RESPONSE {resp.status_code} {resp.url}\nHeaders: {resp.headers}"
        if self.log_body:
            body_str = resp.text
            if body_str and len(body_str) > self.max_body_log_length:
                body_str = body_str[: self.max_body_log_length] + "... [truncated]"
            line += f"\nBody: {body_str}"
        logger.debug(line)

    def _authenticate_session(self) -> None:
        if self.auth0_client:
            self.session.headers["Authorization"] = (
                f"Bearer {self.auth0_client.fetch_access_token()}"
            )

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        self._authenticate_session()
        url = self._url(path)
        self._log_request(method, url, kwargs)
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        self._log_response(resp)
        return resp

    def _json_or_error(self, resp: requests.Response) -> dict:
        if resp.status_code >= 400:
            raise HTTPErrorWithBody(resp)
        return resp.json() if resp.text else {}

    # ---- Raw methods ----
    def raw_get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def raw_post(self, path: str, body: dict | None = None, **kwargs) -> requests.Response:
        return self._request("POST", path, json=body, **kwargs)

    def raw_put(self, path: str, body: dict | None = None, **kwargs) -> requests.Response:
        return self._request("PUT", path, json=body, **kwargs)

    def raw_patch(self, path: str, body: dict | None = None, **kwargs) -> requests.Response:
        return self._request("PATCH", path, json=body, **kwargs)

    def raw_delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    def raw_head(self, path: str, **kwargs) -> requests.Response:
        return self._request("HEAD", path, **kwargs)

    # ---- JSON convenience methods ----
    def get(self, path: str, **kwargs) -> dict:
        return self._json_or_error(self.raw_get(path, **kwargs))

    def post(self, path: str, body: dict | None = None, **kwargs) -> dict:
        return self._json_or_error(self.raw_post(path, body, **kwargs))

    def put(self, path: str, body: dict | None = None, **kwargs) -> dict:
        return self._json_or_error(self.raw_put(path, body, **kwargs))

    def patch(self, path: str, body: dict | None = None, **kwargs) -> dict:
        return self._json_or_error(self.raw_patch(path, body, **kwargs))

    def delete(self, path: str, **kwargs) -> dict:
        return self._json_or_error(self.raw_delete(path, **kwargs))

    def head(self, path: str, **kwargs) -> dict:
        resp = self.raw_head(path, **kwargs)
        if resp.status_code >= 400:
            raise HTTPErrorWithBody(resp)
        return dict(resp.headers)
