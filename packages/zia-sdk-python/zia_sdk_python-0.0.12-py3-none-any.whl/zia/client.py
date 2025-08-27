"""
Main client for the Neurolabs SDK.
"""

import asyncio
from typing import Optional

from .config import Config
from .endpoints import (
    CatalogEndpoint,
    ImagePredictionEndpoint,
    ResultManagementEndpoint,
    TaskManagementEndpoint,
)
from .http import HTTPSession


class Zia:
    """
    Main client for the Zia Image Recognition API.

    Provides a simple, ergonomic interface for catalog management and image recognition.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        """
        Initialize the Zia client.

        Args:
            api_key: Zia API key (can also be set via NEUROLABS_API_KEY env var)
            base_url: Base URL for the API (defaults to https://api.neurolabs.ai/v2)
            timeout: Request timeout in seconds (defaults to 30.0)
            max_retries: Maximum number of retry attempts (defaults to 3)
        """
        # Create config with explicit values or from environment
        if api_key:
            self.config = Config(
                api_key=api_key,
                base_url=base_url or "https://api.neurolabs.ai/v2",
                timeout=timeout or 60.0,
                max_retries=max_retries or 3,
            )
        else:
            self.config = Config.from_env()

        # Initialize HTTP session
        self._session = HTTPSession(self.config)

        # Initialize endpoints
        self._catalog: Optional[CatalogEndpoint] = None
        self._task_management: Optional[TaskManagementEndpoint] = None
        self._image_recognition: Optional[ImagePredictionEndpoint] = None
        self._result_management: Optional[ResultManagementEndpoint] = None

    @property
    def catalog(self) -> CatalogEndpoint:
        """Access catalog operations."""
        if self._catalog is None:
            self._catalog = CatalogEndpoint(self._session)
        return self._catalog

    @property
    def task_management(self) -> TaskManagementEndpoint:
        """Access image recognition operations."""
        if self._task_management is None:
            self._task_management = TaskManagementEndpoint(self._session)
        return self._task_management

    @property
    def image_recognition(self) -> ImagePredictionEndpoint:
        """Access image prediction operations."""
        if self._image_recognition is None:
            self._image_recognition = ImagePredictionEndpoint(self._session)
        return self._image_recognition

    @property
    def result_management(self) -> ResultManagementEndpoint:
        """Access result management operations."""
        if self._result_management is None:
            self._result_management = ResultManagementEndpoint(self._session)
        return self._result_management

    def list_items_sync(self, limit: int = 50, **kwargs):
        """Synchronous method to list catalog items."""

        async def _list_items():
            async with self as client:
                return await client.catalog.list_items(limit=limit, **kwargs)

        return asyncio.run(_list_items())

    def list_tasks_sync(self, limit: int = 50):
        """Synchronous method to list image recognition tasks."""

        async def _list_tasks():
            async with self as client:
                return await client.task_management.list_tasks(limit=limit)

        return asyncio.run(_list_tasks())

    async def __aenter__(self):
        """Async context manager entry."""
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close the client and release resources."""
        await self._session.close()

    async def health_check(self) -> bool:
        """
        Check if the API is healthy.

        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            # Try to get API info as a health check
            await self._session.get("http://api.neurolabs.ai/health")
            return True
        except Exception:
            return False

    def health_check_sync(self) -> bool:
        """
        Synchronous health check.

        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            return asyncio.run(self.health_check())
        except Exception:
            return False
