"""
Basic usage example for the Zia SDK.
"""

import asyncio

from neurolabszia import NLCatalogItemCreate, Zia, NLIRTaskCreate
from pathlib import Path


async def main():
    """Demonstrate basic SDK usage."""

    # Initialize client (will use NEUROLABS_API_KEY env var if not provided)
    async with Zia() as client:
        # Health check
        is_healthy = await client.health_check()
        print(f"API Health: {is_healthy}")

        # Catalog operations
        print("\n=== Catalog Operations ===")

        # List catalog items (paginated)
        items = await client.catalog.list_items(limit=5)
        print(f"Found {len(items)} catalog items")

        # Get all catalog items (automatic pagination)
        all_items = await client.catalog.list_all_items(batch_size=50)
        print(f"Total catalog items: {len(all_items)}")

        # Create a new catalog item
        new_item = NLCatalogItemCreate(
            name="Example Product", brand="Example Brand", barcode="1234567890123"
        )

        # Note: You would need to add thumbnail data for this to work
        # with open("thumbnail.jpg", "rb") as f:
        #     thumbnail_data = f.read()
        # new_item.thumbnail = thumbnail_data
        # created_item = await client.catalog.create_item(new_item)
        # print(f"Created item: {created_item.name}")

        # Image recognition operations
        print("\n=== Image Recognition Operations ===")

        # List tasks (paginated)
        tasks = await client.image_recognition.list_tasks(limit=5)
        print(f"Found {len(tasks)} image recognition tasks")

        # Get all tasks (automatic pagination)
        all_tasks = await client.image_recognition.list_all_tasks(batch_size=50)
        print(f"Total tasks: {len(all_tasks)}")

        # Create a new task (requires existing catalog item UUIDs)
        task = NLIRTaskCreate(
            name="Example Task",
            catalog_items=["uuid1", "uuid2"]
        )
        created_task = await client.task_management.create_task(task)
        print(f"Created task: {created_task.name}")

        # Upload images to a task (requires task UUID and image paths/links)
        image_paths = [Path("image1.jpg"), Path("image2.jpg")]
        result_uuids = await client.image_recognition.upload_images(
            task_uuid=created_task.uuid,
            image_paths=image_paths
        )
        print(f"Uploaded {len(result_uuids)} images")


if __name__ == "__main__":
    asyncio.run(main())
