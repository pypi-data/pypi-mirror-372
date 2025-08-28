"""Session management and client lifecycle handling.

This module provides session management capabilities including configuration
validation, resource initialization, and proper cleanup of HTTP connections
and other resources.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, Literal

from .transport import create_transport

if TYPE_CHECKING:
    from .protocols import AuthProvider, ClientConfiguration


class ClientSession:
    """Manages client lifecycle and resource coordination.

    This class serves as the central coordination point for the client,
    managing configuration, transport layer, and resource lifecycle.
    """

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        config: ClientConfiguration,
        mode: Literal['sync', 'async'] = 'async',
    ) -> None:
        """Initialize client session.

        Args:
            base_url: Base URL of the Snail Orbit instance
            auth: Authentication provider
            config: Client configuration
            mode: Operation mode ('sync' or 'async')
        """
        self.base_url = base_url
        self.auth = auth
        self.config = config
        self.mode = mode

        # Create transport layer
        self.transport = create_transport(mode, base_url, auth, config)

        # Track session state
        self._closed = False

    async def __aenter__(self) -> ClientSession:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __enter__(self) -> ClientSession:
        """Sync context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sync context manager exit."""
        self.close_sync()

    async def close(self) -> None:
        """Close the session and cleanup resources (async)."""
        if self._closed:
            return

        if hasattr(self.transport, 'close') and callable(self.transport.close):
            if self.mode == 'async':
                await self.transport.close()
            else:
                self.transport.close()

        self._closed = True

    def close_sync(self) -> None:
        """Close the session and cleanup resources (sync)."""
        if self._closed:
            return

        if hasattr(self.transport, 'close'):
            self.transport.close()

        self._closed = True

    def ensure_open(self) -> None:
        """Ensure the session is still open."""
        if self._closed:
            raise RuntimeError('Session has been closed')

    @property
    def is_closed(self) -> bool:
        """Check if the session is closed."""
        return self._closed


class SessionManager:
    """Factory and manager for client sessions."""

    @staticmethod
    def create_session(
        base_url: str,
        auth: AuthProvider,
        config: ClientConfiguration,
        mode: Literal['sync', 'async'] = 'async',
    ) -> ClientSession:
        """Create a new client session.

        Args:
            base_url: Base URL of the Snail Orbit instance
            auth: Authentication provider
            config: Client configuration
            mode: Operation mode ('sync' or 'async')

        Returns:
            Configured client session
        """
        # Validate configuration
        SessionManager._validate_config(config)

        # Normalize base URL
        base_url = base_url.rstrip('/')
        if not base_url:
            raise ValueError('Base URL cannot be empty')

        return ClientSession(base_url, auth, config, mode)

    @staticmethod
    def _validate_config(config: ClientConfiguration) -> None:
        """Validate client configuration.

        Args:
            config: Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if config.timeout <= 0:
            raise ValueError('Timeout must be positive')

        if config.max_retries < 0:
            raise ValueError('Max retries cannot be negative')

        if config.retry_delay <= 0:
            raise ValueError('Retry delay must be positive')

        if config.rate_limit < 0:
            raise ValueError('Rate limit cannot be negative')

        if not config.user_agent.strip():
            raise ValueError('User agent cannot be empty')


class ResourceRegistry:
    """Registry for managing resource instances.

    This class helps coordinate resource instances and ensures they
    all use the same session and transport layer.
    """

    def __init__(self, session: ClientSession) -> None:
        """Initialize resource registry.

        Args:
            session: Client session to use for all resources
        """
        self.session = session
        self._resources: dict[str, Any] = {}

    def register_resource(self, name: str, resource: Any) -> None:
        """Register a resource instance.

        Args:
            name: Resource name
            resource: Resource instance
        """
        self._resources[name] = resource

    def get_resource(self, name: str) -> Any:
        """Get a registered resource.

        Args:
            name: Resource name

        Returns:
            Resource instance

        Raises:
            KeyError: If resource is not registered
        """
        if name not in self._resources:
            raise KeyError(f'Resource {name} not registered')

        return self._resources[name]

    def list_resources(self) -> list[str]:
        """List all registered resource names.

        Returns:
            List of resource names
        """
        return list(self._resources.keys())

    async def close_all(self) -> None:
        """Close all resources and the session."""
        # Close individual resources if they have close methods
        for resource in self._resources.values():
            if hasattr(resource, 'close') and callable(resource.close):
                with contextlib.suppress(Exception):
                    await resource.close()  # Ignore cleanup errors

        # Close the session
        await self.session.close()

        # Clear registry
        self._resources.clear()
