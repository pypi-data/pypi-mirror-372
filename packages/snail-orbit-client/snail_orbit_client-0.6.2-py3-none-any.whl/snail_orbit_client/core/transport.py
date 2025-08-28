"""HTTP transport layer with unified sync/async support.

This module provides a clean abstraction over HTTP operations, supporting both
synchronous and asynchronous modes through a common interface. It handles
retries, rate limiting, error handling, and response processing.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urljoin

import httpx

from ..exceptions import create_exception_from_response

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Generator

    from .protocols import AuthProvider, ClientConfiguration, HttpTransport


class BaseTransport:
    """Base transport with common functionality."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        config: ClientConfiguration,
    ) -> None:
        """Initialize transport with configuration."""
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.config = config

        # Rate limiting state (thread-safe for sync, single-threaded for async)
        self._rate_limit_tokens = config.rate_limit
        self._rate_limit_last_refill = time.time()

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limits."""
        if self.config.rate_limit <= 0:
            return

        now = time.time()
        elapsed = now - self._rate_limit_last_refill

        # Refill tokens based on elapsed time (token bucket algorithm)
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
        """Get request headers with authentication."""
        headers = {
            'Authorization': self.auth.get_auth_header(method, path, params),
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


class SyncHttpTransport(BaseTransport):
    """Synchronous HTTP transport implementation."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        config: ClientConfiguration,
    ) -> None:
        """Initialize sync transport."""
        super().__init__(base_url, auth, config)

        # Create httpx client with configuration
        self._client = httpx.Client(
            timeout=config.timeout,
            verify=config.verify_ssl,
            limits=httpx.Limits(
                max_connections=getattr(config, 'pool_connections', 10),
                max_keepalive_connections=getattr(config, 'pool_maxsize', 10),
            ),
            max_redirects=getattr(config, 'max_redirects', 5),
        )

    def __enter__(self) -> SyncHttpTransport:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make a synchronous HTTP request."""
        self._check_rate_limit()

        url = self._build_url(path)
        request_headers = self._get_headers(method, path, headers, params)

        if json_data is not None:
            request_headers['Content-Type'] = 'application/json'

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )
                return self._handle_response(response)
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Request failed after {attempt + 1} attempts') from e

        raise Exception(
            f'Request failed after {self.config.max_retries + 1} attempts'
        ) from last_exception

    def paginate(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> Generator[Any, None, None]:
        """Synchronous pagination through API results."""
        offset = 0
        params = params or {}

        while True:
            page_params = {
                **params,
                'limit': limit,
                'offset': offset,
            }

            # Since this is sync paginate, we need to avoid async call
            # We'll directly call the sync HTTP request
            self._check_rate_limit()
            full_url = self._build_url(url)
            headers = self._get_headers('GET', url, None, page_params)

            http_response = self._client.get(
                full_url, params=page_params, headers=headers
            )
            data = self._handle_response(http_response)

            if not data or 'items' not in data:
                break

            items = data['items']
            if not items:
                break

            for item in items:
                yield item

            # Check if we have more pages
            if data.get('count', 0) <= offset + limit:
                break

            offset += limit


class AsyncHttpTransport(BaseTransport):
    """Asynchronous HTTP transport implementation."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        config: ClientConfiguration,
    ) -> None:
        """Initialize async transport."""
        super().__init__(base_url, auth, config)

        # Create httpx async client with configuration
        self._client = httpx.AsyncClient(
            timeout=config.timeout,
            verify=config.verify_ssl,
            limits=httpx.Limits(
                max_connections=getattr(config, 'pool_connections', 10),
                max_keepalive_connections=getattr(config, 'pool_maxsize', 10),
            ),
            max_redirects=getattr(config, 'max_redirects', 5),
        )

    async def __aenter__(self) -> AsyncHttpTransport:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an async HTTP request."""
        self._check_rate_limit()

        url = self._build_url(path)
        request_headers = self._get_headers(method, path, headers, params)

        if json_data is not None:
            request_headers['Content-Type'] = 'application/json'

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )
                return self._handle_response(response)
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue
                raise Exception(f'Request failed after {attempt + 1} attempts') from e

        raise Exception(
            f'Request failed after {self.config.max_retries + 1} attempts'
        ) from last_exception

    async def paginate(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Any]:
        """Async pagination through API results."""
        offset = 0
        params = params or {}

        while True:
            page_params = {
                **params,
                'limit': limit,
                'offset': offset,
            }

            response = await self.request('GET', url, params=page_params)

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


def create_transport(
    mode: Literal['sync', 'async'],
    base_url: str,
    auth: AuthProvider,
    config: ClientConfiguration,
) -> HttpTransport:
    """Factory function to create appropriate transport based on mode."""
    if mode == 'sync':
        return SyncHttpTransport(base_url, auth, config)
    elif mode == 'async':
        return AsyncHttpTransport(base_url, auth, config)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Must be 'sync' or 'async'.")
