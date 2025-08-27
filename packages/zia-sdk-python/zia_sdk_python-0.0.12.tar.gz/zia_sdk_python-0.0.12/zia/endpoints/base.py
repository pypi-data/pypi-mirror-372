"""
Base endpoint class for the Neurolabs SDK.
"""

from typing import Any, Optional

from ..http import HTTPSession


class BaseEndpoint:
    """Base class for all API endpoints."""

    def __init__(self, session: HTTPSession):
        """Initialize endpoint with HTTP session."""
        self.session = session

    async def _get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make GET request and return JSON response."""
        response = await self.session.get(path, params=params)
        return response.json()

    async def _post(
        self,
        path: str,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make POST request and return JSON response."""
        response = await self.session.post(path, data=data, files=files)
        return response.json()

    async def _put(
        self, path: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make PUT request and return JSON response."""
        response = await self.session.put(path, data=data)
        return response.json()

    async def _delete(self, path: str) -> dict[str, Any]:
        """Make DELETE request and return JSON response."""
        response = await self.session.delete(path)
        return response.json()
