"""
Catalog endpoint for the Neurolabs SDK.
"""

from pathlib import Path
from typing import Optional

from ..models.catalog import NLCatalogItem, NLCatalogItemCreate
from .base import BaseEndpoint


class CatalogEndpoint(BaseEndpoint):
    """Catalog endpoint for managing catalog items."""

    async def list_items(
        self,
        name: Optional[str] = None,
        custom_id: Optional[str] = None,
        barcode: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NLCatalogItem]:
        """
        List catalog items with optional filtering.

        Args:
            name: Filter by item name
            custom_id: Filter by custom ID
            barcode: Filter by barcode
            limit: Number of items to return (max 100)
            offset: Offset for pagination

        Returns:
            List of catalog items
        """
        params = {"limit": min(limit, 100), "offset": offset}
        if name:
            params["name"] = name
        if custom_id:
            params["custom_id"] = custom_id
        if barcode:
            params["barcode"] = barcode

        response = await self._get("/catalog-items", params=params)
        return [NLCatalogItem.model_validate(item) for item in response["items"]]

    async def list_all_items(
        self,
        name: Optional[str] = None,
        custom_id: Optional[str] = None,
        barcode: Optional[str] = None,
        batch_size: int = 100,
    ) -> list[NLCatalogItem]:
        """
        Get all catalog items with automatic pagination.

        Args:
            name: Filter by item name
            custom_id: Filter by custom ID
            barcode: Filter by barcode
            batch_size: Number of items to fetch per request (max 100)

        Returns:
            List of all catalog items matching the filters
        """
        all_items = []
        offset = 0
        batch_size = min(batch_size, 100)

        while True:
            params = {"limit": batch_size, "offset": offset}
            if name:
                params["name"] = name
            if custom_id:
                params["custom_id"] = custom_id
            if barcode:
                params["barcode"] = barcode

            response = await self._get("/catalog-items", params=params)
            items = [NLCatalogItem.model_validate(item) for item in response["items"]]

            if not items:
                break

            all_items.extend(items)

            # Check if we've reached the end
            if len(items) < batch_size:
                break

            offset += batch_size

        return all_items

    async def get_item(self, item_uuid: str) -> NLCatalogItem:
        """
        Get a specific catalog item by UUID.

        Args:
            item_uuid: UUID of the catalog item

        Returns:
            Catalog item
        """
        response = await self._get(f"/catalog-items/{item_uuid}")
        return NLCatalogItem.model_validate(response)

    async def create_item(self, item: NLCatalogItemCreate) -> NLCatalogItem:
        """
        Create a new catalog item.

        Args:
            item: Catalog item data

        Returns:
            Created catalog item
        """
        data = item.model_dump(exclude_none=True, exclude={"thumbnail"})
        files = {}

        # Handle thumbnail binary data
        if item.thumbnail:
            files["thumbnail"] = ("thumbnail", item.thumbnail)
        else:
            raise ValueError("Thumbnail binary data is required")

        try:
            response = await self._post("/catalog-items", data=data, files=files)
            return NLCatalogItem.model_validate(response)
        finally:
            if files:
                for file in files.values():
                    if hasattr(file, "close"):
                        file.close()

    async def upload_reference_images(
        self, item_uuid: str, image_paths: list[Path]
    ) -> NLCatalogItem:
        """
        Upload reference images for a catalog item.

        Args:
            item_uuid: UUID of the catalog item
            image_paths: List of paths to reference images

        Returns:
            Updated catalog item
        """
        files = {}
        for i, path in enumerate(image_paths):
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            files["images"] = open(path, "rb")

        try:
            response = await self._post(
                f"/catalog-items/{item_uuid}/reference-images", files=files
            )
            return NLCatalogItem.model_validate(response)
        finally:
            for file in files.values():
                file.close()
