"""
Catalog models for the Neurolabs SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class NLCatalogItemStatus(str, Enum):
    """Status values for catalog items."""

    READY = "ONBOARDED"
    PROCESSING = "INCOMPLETE"


class NLCatalogItem(BaseModel):
    """Model representing a catalog item."""

    uuid: str = Field(..., description="Unique identifier for the item")
    status: NLCatalogItemStatus = Field(..., description="Current status of the item")
    thumbnail_url: str = Field(..., description="URL to the item's thumbnail image")
    name: str = Field(..., description="Name of the item")
    barcode: Optional[str] = Field(None, description="Barcode of the item")
    custom_id: Optional[str] = Field(None, description="Custom identifier")
    height: Optional[float] = Field(None, description="Height of the item in meters")
    width: Optional[float] = Field(None, description="Width of the item in meters")
    depth: Optional[float] = Field(None, description="Depth of the item in meters")
    brand: Optional[str] = Field(None, description="Brand of the item")
    size: Optional[str] = Field(None, description="Size of the item")
    container_type: Optional[str] = Field(None, description="Type of container")
    flavour: Optional[str] = Field(None, description="Flavour of the item")
    packaging_size: Optional[str] = Field(None, description="Packaging size")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class NLCatalogItemCreate(BaseModel):
    """Model for creating a new catalog item."""

    name: str = Field(..., description="Name of the item")
    thumbnail: bytes = Field(
        None, description="Binary data of the item's thumbnail image"
    )
    barcode: str = Field(None, description="Barcode of the item")
    custom_id: Optional[str] = Field(None, description="Custom identifier")
    height: Optional[float] = Field(None, description="Height of the item in meters")
    width: Optional[float] = Field(None, description="Width of the item in meters")
    depth: Optional[float] = Field(None, description="Depth of the item in meters")
    brand: Optional[str] = Field(None, description="Brand of the item")
    size: Optional[str] = Field(None, description="Size of the item")
    container_type: Optional[str] = Field(None, description="Type of container")
    flavour: Optional[str] = Field(None, description="Flavour of the item")
    packaging_size: Optional[str] = Field(None, description="Packaging size")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate item name."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        if len(v) > 255:
            raise ValueError("Item name cannot exceed 255 characters")
        return v.strip()

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, v: Optional[str]) -> Optional[str]:
        """Validate barcode format."""
        if v is not None:
            if len(v) > 14:
                raise ValueError("Barcode cannot exceed 14 characters")
            if not v.isalnum():
                raise ValueError("Barcode must contain only alphanumeric characters")
        return v
