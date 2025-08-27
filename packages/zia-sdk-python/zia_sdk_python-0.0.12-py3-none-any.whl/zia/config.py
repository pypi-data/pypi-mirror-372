"""
Configuration management for the Neurolabs SDK.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Configuration for the Neurolabs SDK."""

    api_key: str = Field(..., description="Neurolabs API key")
    base_url: str = Field(
        default="https://api.neurolabs.ai/v2",
        description="Base URL for the Neurolabs API",
    )
    timeout: float = Field(default=60.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL."""
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v

    @classmethod
    def from_env(cls, config_file: Optional[Path] = None) -> "Config":
        """
        Create configuration from environment variables and optional config file.

        Args:
            config_file: Optional path to configuration file

        Returns:
            Config instance

        Raises:
            ValueError: If required configuration is missing
        """
        # Load from config file if provided
        config_data = {}
        if config_file and config_file.exists():
            # TODO: Implement config file loading (TOML/YAML)
            pass

        # Environment variables take precedence
        api_key = os.getenv("NEUROLABS_API_KEY") or config_data.get("api_key")
        if not api_key:
            raise ValueError(
                "NEUROLABS_API_KEY environment variable is required. "
                "Set it or pass api_key parameter."
            )

        return cls(
            api_key=api_key,
            base_url=os.getenv(
                "NEUROLABS_BASE_URL",
                config_data.get("base_url", "https://api.neurolabs.ai/v2"),
            ),
            timeout=float(
                os.getenv("NEUROLABS_TIMEOUT", config_data.get("timeout", 60.0))
            ),
            max_retries=int(
                os.getenv("NEUROLABS_MAX_RETRIES", config_data.get("max_retries", 3))
            ),
        )
