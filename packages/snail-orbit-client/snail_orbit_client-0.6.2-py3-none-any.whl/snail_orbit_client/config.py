"""Client configuration options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class ClientConfig:
    """Configuration options for the Snail Orbit client.

    Attributes:
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts for failed requests
        retry_delay: Base delay between retries in seconds (with exponential backoff)
        enable_caching: Whether to enable response caching
        cache_ttl: Cache time-to-live in seconds
        rate_limit: Maximum requests per minute (0 = no limit)
        user_agent: Custom user agent string
        verify_ssl: Whether to verify SSL certificates
        pool_connections: Number of connection pools to cache
        pool_maxsize: Maximum number of connections per pool
        max_redirects: Maximum number of redirects to follow
    """

    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = False
    cache_ttl: int = 300
    rate_limit: int = 0
    user_agent: str = 'snail-orbit-client/1.0.0'
    verify_ssl: bool = True
    pool_connections: int = 10
    pool_maxsize: int = 10
    max_redirects: int = 5

    def to_httpx_kwargs(self) -> dict[str, Any]:
        """Convert config to httpx client kwargs."""
        return {
            'timeout': self.timeout,
            'verify': self.verify_ssl,
            'limits': httpx.Limits(
                max_connections=self.pool_connections,
                max_keepalive_connections=self.pool_maxsize,
            ),
            'max_redirects': self.max_redirects,
            'headers': {
                'User-Agent': self.user_agent,
            },
        }
