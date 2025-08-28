"""
Snail Orbit Python Client Library

A comprehensive client library for the Snail Orbit project management system.
"""

from __future__ import annotations

from .client import SnailOrbitAsyncClient, SnailOrbitClient
from .config import ClientConfig
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    SnailOrbitError,
    ValidationError,
)

__all__ = [
    # Client and configuration
    'SnailOrbitClient',
    'SnailOrbitAsyncClient',
    'ClientConfig',
    # Exceptions
    'SnailOrbitError',
    'AuthenticationError',
    'ValidationError',
    'NotFoundError',
    'RateLimitError',
]
