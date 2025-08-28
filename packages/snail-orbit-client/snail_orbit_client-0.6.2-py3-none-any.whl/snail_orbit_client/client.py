"""Main client classes for Snail Orbit API."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

import httpx

from .auth import AuthHandler
from .config import ClientConfig
from .exceptions import create_exception_from_response
from .generated.models import VersionOutput as Version
from .resources.activity import ActivityResource, AsyncActivityResource
from .resources.auth import AsyncAuthResource, AuthResource
from .resources.custom_fields import AsyncCustomFieldsResource, CustomFieldsResource
from .resources.issues import AsyncIssuesResource, IssuesResource
from .resources.projects import AsyncProjectsResource, ProjectsResource
from .resources.users import AsyncUsersResource, UsersResource


class BaseClient:
    """Base client with common functionality."""

    def __init__(
        self,
        base_url: str,
        token: str | tuple[str, str, str],
        config: ClientConfig | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            base_url: Base URL of the Snail Orbit instance
            token: Authentication token or JWT signing credentials
            config: Client configuration options
        """
        self.base_url = base_url.rstrip('/')
        self.config = config or ClientConfig()
        self._auth_handler = AuthHandler(token)

        # Rate limiting state
        self._rate_limit_tokens = self.config.rate_limit
        self._rate_limit_last_refill = time.time()

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limits."""
        if self.config.rate_limit <= 0:
            return

        now = time.time()
        elapsed = now - self._rate_limit_last_refill

        # Refill tokens based on elapsed time
        if elapsed >= 60:  # Reset every minute
            self._rate_limit_tokens = self.config.rate_limit
            self._rate_limit_last_refill = now

        if self._rate_limit_tokens <= 0:
            raise Exception(
                f'Rate limit exceeded ({self.config.rate_limit} requests/minute)'
            )

        self._rate_limit_tokens -= 1

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return urljoin(self.base_url, path)

    def _get_headers(
        self,
        method: str,
        path: str,
        extra_headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Get request headers."""
        headers = {
            'Authorization': self._auth_handler.get_auth_header(method, path, params),
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json',
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and extract payload."""
        if not response.is_success:
            try:
                error_data = response.json()
                message = error_data.get('error', f'HTTP {response.status_code}')
            except Exception:
                message = f'HTTP {response.status_code}: {response.text}'
                error_data = None

            raise create_exception_from_response(
                response.status_code, message, error_data
            )

        try:
            data = response.json()
        except Exception as e:
            raise Exception(f'Invalid JSON response: {e}') from e

        # Extract payload from success response
        if isinstance(data, dict) and 'payload' in data:
            return data['payload']

        return data


class SnailOrbitClient(BaseClient):
    """Synchronous Snail Orbit API client."""

    def __init__(
        self,
        base_url: str,
        token: str | tuple[str, str, str],
        config: ClientConfig | None = None,
    ) -> None:
        """Initialize the synchronous client."""
        super().__init__(base_url, token, config)

        # Initialize HTTP client
        self._client = httpx.Client(**self.config.to_httpx_kwargs())

        # Initialize resource managers
        self.auth = AuthResource(self)
        self.users = UsersResource(self)
        self.projects = ProjectsResource(self)
        self.issues = IssuesResource(self)
        self.custom_fields = CustomFieldsResource(self)
        self.activity = ActivityResource(self)

    def __enter__(self) -> SnailOrbitClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the client and cleanup resources."""
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a request to the API.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            json_data: JSON request body
            data: Raw request body
            headers: Additional headers

        Returns:
            Response data
        """
        self._check_rate_limit()

        url = self._build_url(path)
        request_headers = self._get_headers(method, path, headers, params)

        # Set content type for JSON requests
        if json_data is not None:
            request_headers['Content-Type'] = 'application/json'

        # Retry logic
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    content=data,
                    headers=request_headers,
                )
                return self._handle_response(response)
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Request timeout after {attempt + 1} attempts') from e
            except httpx.ConnectError as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Connection error after {attempt + 1} attempts') from e

        # If we get here, all retries failed
        raise Exception(
            f'Request failed after {self.config.max_retries + 1} attempts'
        ) from last_exception

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request."""
        return self.request('GET', path, params=params)

    def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        data: bytes | None = None,
    ) -> Any:
        """Make a POST request."""
        return self.request('POST', path, json_data=json_data, data=data)

    def put(self, path: str, json_data: dict[str, Any] | None = None) -> Any:
        """Make a PUT request."""
        return self.request('PUT', path, json_data=json_data)

    def delete(self, path: str) -> Any:
        """Make a DELETE request."""
        return self.request('DELETE', path)

    def get_version(self) -> Version:
        """Get system version information."""
        response = self.get('/api/v1/version')
        # Extract payload from response wrapper
        payload = (
            response.get('payload', response)
            if isinstance(response, dict)
            else response
        )
        return Version.model_validate(payload)

    def paginate(
        self, path: str, params: dict[str, Any] | None = None, limit: int = 100
    ) -> Iterator[Any]:
        """Paginate through API results.

        Args:
            path: API path
            params: Query parameters
            limit: Items per page

        Yields:
            Individual items from paginated results
        """
        offset = 0
        params = params or {}

        while True:
            page_params = {
                **params,
                'limit': limit,
                'offset': offset,
            }

            response = self.get(path, params=page_params)

            if not response or 'items' not in response:
                break

            items = response['items']
            if not items:
                break

            yield from items

            # Check if we have more pages
            if response.get('count', 0) <= offset + limit:
                break

            offset += limit


class SnailOrbitAsyncClient(BaseClient):
    """Asynchronous Snail Orbit API client."""

    def __init__(
        self,
        base_url: str,
        token: str | tuple[str, str, str],
        config: ClientConfig | None = None,
    ) -> None:
        """Initialize the asynchronous client."""
        super().__init__(base_url, token, config)

        # Initialize HTTP client
        self._client = httpx.AsyncClient(**self.config.to_httpx_kwargs())

        # Initialize resource managers
        self.auth = AsyncAuthResource(self)
        self.users = AsyncUsersResource(self)
        self.projects = AsyncProjectsResource(self)
        self.issues = AsyncIssuesResource(self)
        self.custom_fields = AsyncCustomFieldsResource(self)
        self.activity = AsyncActivityResource(self)

    async def __aenter__(self) -> SnailOrbitAsyncClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an async request to the API."""
        self._check_rate_limit()

        url = self._build_url(path)
        request_headers = self._get_headers(method, path, headers, params)

        # Set content type for JSON requests
        if json_data is not None:
            request_headers['Content-Type'] = 'application/json'

        # Retry logic
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    content=data,
                    headers=request_headers,
                )
                return self._handle_response(response)
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Request timeout after {attempt + 1} attempts') from e
            except httpx.ConnectError as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Connection error after {attempt + 1} attempts') from e

        # If we get here, all retries failed
        raise Exception(
            f'Request failed after {self.config.max_retries + 1} attempts'
        ) from last_exception

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make an async GET request."""
        return await self.request('GET', path, params=params)

    async def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        data: bytes | None = None,
    ) -> Any:
        """Make an async POST request."""
        return await self.request('POST', path, json_data=json_data, data=data)

    async def put(self, path: str, json_data: dict[str, Any] | None = None) -> Any:
        """Make an async PUT request."""
        return await self.request('PUT', path, json_data=json_data)

    async def delete(self, path: str) -> Any:
        """Make an async DELETE request."""
        return await self.request('DELETE', path)

    async def get_version(self) -> Version:
        """Get system version information."""
        response = await self.get('/api/v1/version')
        # Extract payload from response wrapper
        payload = (
            response.get('payload', response)
            if isinstance(response, dict)
            else response
        )
        return Version.model_validate(payload)

    async def paginate(
        self, path: str, params: dict[str, Any] | None = None, limit: int = 100
    ) -> AsyncIterator[Any]:
        """Async paginate through API results."""
        offset = 0
        params = params or {}

        while True:
            page_params = {
                **params,
                'limit': limit,
                'offset': offset,
            }

            response = await self.get(path, params=page_params)

            if not response or 'items' not in response:
                break

            items = response['items']
            if not items:
                break

            for item in items:
                yield item

            # Check if we have more pages
            if response.get('count', 0) <= offset + limit:
                break

            offset += limit
