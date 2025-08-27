"""
HTTP session management for the Neurolabs SDK.
"""

import asyncio
import time
from typing import Any, Optional

import httpx

from ..config import Config
from ..exceptions import (
    NeurolabsAuthError,
    NeurolabsError,
    NeurolabsNotFoundError,
    NeurolabsRateLimitError,
    NeurolabsTimeoutError,
    NeurolabsValidationError,
)


class HTTPSession:
    """HTTP session with authentication, retries, and error handling."""

    def __init__(self, config: Config):
        """Initialize HTTP session with configuration."""
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            limits = httpx.Limits(max_connections=10)
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                limits=limits,
                headers={
                    "X-API-Key": self.config.api_key,
                    "User-Agent": "neurolabs-python-sdk",
                },
            )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _map_error(self, response: httpx.Response) -> NeurolabsError:
        """Map HTTP response to appropriate exception."""
        request_id = response.headers.get("X-Request-ID")

        try:
            error_data = response.json()
            message = error_data.get("detail", response.reason_phrase)
        except Exception:
            message = response.reason_phrase

        # Log security-relevant errors (but not sensitive data)
        if response.status_code in (401, 403):
            # Don't log the actual error message as it might contain sensitive info
            message = "Authentication or authorization failed"

        if response.status_code == 400:
            return NeurolabsValidationError(message, request_id=request_id)
        elif response.status_code in (401, 403):
            return NeurolabsAuthError(message, response.status_code, request_id)
        elif response.status_code == 404:
            return NeurolabsNotFoundError(message, request_id)
        elif response.status_code == 408:
            return NeurolabsTimeoutError(message, request_id)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            return NeurolabsRateLimitError(
                message, int(retry_after) if retry_after else None, request_id
            )
        else:
            return NeurolabsError(
                f"HTTP {response.status_code}: {message}",
                response.status_code,
                request_id,
            )

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic."""
        await self._ensure_client()

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)

                # Don't retry on client errors (4xx)
                if 400 <= response.status_code < 500:
                    if response.status_code != 429:  # Don't retry on rate limit
                        raise self._map_error(response)

                # Retry on server errors (5xx) and rate limits
                if response.status_code >= 500 or response.status_code == 429:
                    if attempt < self.config.max_retries:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            await asyncio.sleep(int(retry_after))
                        else:
                            # Exponential backoff with jitter
                            delay = (2**attempt) + (time.time() % 1)
                            await asyncio.sleep(delay)
                        continue
                    else:
                        raise self._map_error(response)

                return response

            except httpx.TimeoutException:
                if attempt < self.config.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    raise NeurolabsTimeoutError("Request timed out")
            except httpx.RequestError as e:
                if attempt < self.config.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    raise NeurolabsError(f"Request failed: {e}")

    async def get(
        self, url: str, params: Optional[dict[str, Any]] = None
    ) -> httpx.Response:
        """Make GET request."""
        return await self._request("GET", url, params=params)

    async def post(
        self,
        url: str,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make POST request."""
        # Use json parameter for JSON data, data parameter for form data
        kwargs = {}
        if data is not None and files is None:
            kwargs["json"] = data
        elif data is not None:
            kwargs["data"] = data
        if files is not None:
            kwargs["files"] = files

        return await self._request("POST", url, **kwargs)

    async def put(
        self, url: str, data: Optional[dict[str, Any]] = None
    ) -> httpx.Response:
        """Make PUT request."""
        kwargs = {"json": data} if data is not None else {}
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str) -> httpx.Response:
        """Make DELETE request."""
        return await self._request("DELETE", url)
