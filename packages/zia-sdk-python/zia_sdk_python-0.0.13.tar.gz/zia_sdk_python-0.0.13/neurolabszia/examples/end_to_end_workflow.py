#!/usr/bin/env python3
"""
End-to-End Workflow Example for Zia SDK

This script demonstrates the complete workflow:
1. Grab all catalog items
2. Create a task with all catalog items
3. Send images to task
4. Get IR Results from task
5. Display number of facings from the results

Usage:
    export NEUROLABS_API_KEY="your-api-key-here"
    python examples/end_to_end_workflow.py
"""

import asyncio
import os
from pathlib import Path

from neurolabszia import NLCatalogItemCreate, NLIRTaskCreate, Zia


async def main():
    """Run the complete end-to-end workflow."""

    # Check for API key
    api_key = os.getenv("NEUROLABS_API_KEY")
    if not api_key:
        print("❌ Error: NEUROLABS_API_KEY environment variable not set")
        print("Please set it with: export NEUROLABS_API_KEY='your-api-key-here'")
        return

    print("🚀 Starting End-to-End Workflow Example")
    print("=" * 50)

    # Initialize client
    async with Zia(api_key=api_key) as client:
        # 1. Grab all catalog items
        print("\n1️⃣ Getting all catalog items...")
        try:
            catalog_items = await client.catalog.list_all_items(batch_size=10)
            print(f"   ✅ Found {len(catalog_items)} catalog items")

            if not catalog_items:
                print("   ⚠️  No catalog items found. Creating a test item...")

                # Create a test catalog item if none exist
                test_image_path = (
                    Path(__file__).parent.parent / "data" / "display" / "pocm_ab.jpeg"
                )
                thumbnail_data_path = Path(__file__).parent.parent / "data" / "display" / "bud_light_thumbnail.png"
                if thumbnail_data_path.exists():
                    with open(thumbnail_data_path, "rb") as f:
                        thumbnail_data = f.read()

                    test_item = NLCatalogItemCreate(
                        name="Test Product for Workflow",
                        brand="Test Brand",
                        barcode="1234567890123",
                        thumbnail=thumbnail_data,
                    )

                    created_item = await client.catalog.create_item(test_item)
                    catalog_items = [created_item]
                    print(f"   ✅ Created test item: {created_item.uuid}")
                else:
                    print("   ❌ No thumbnail image found. Cannot create test item.")
                    return

        except Exception as e:
            print(f"   ❌ Error getting catalog items: {e}")
            return

        # 2. Create a task with catalog items
        print("\n2️⃣ Creating task with catalog items...")
        try:
            # Use first 5 catalog items (or all if less than 5)
            catalog_item_uuids = [item.uuid for item in catalog_items[:5]]

            task = NLIRTaskCreate(
                name="End-to-End Workflow Task",
                catalog_items=catalog_item_uuids,
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await client.task_management.create_task(task)
            print(f"   ✅ Created task: {created_task.uuid}")
            print(f"   📋 Task name: {created_task.name}")
            print(f"   🔗 Using {len(catalog_item_uuids)} catalog items")

        except Exception as e:
            print(f"   ❌ Error creating task: {e}")
            return

        # 3. Send images to task
        print("\n3️⃣ Uploading images to task...")
        try:
            # Use the test image if available
            test_image_path = (
                Path(__file__).parent.parent / "data" / "display" / "pocm_ab.jpeg"
            )

            if test_image_path.exists():
                image_paths = [test_image_path]
                result_uuids = await client.image_recognition.upload_images(
                    task_uuid=created_task.uuid, image_paths=image_paths
                )
                print(f"   ✅ Uploaded {len(result_uuids)} images")
                print(f"   📸 Result UUIDs: {result_uuids}")
            else:
                print("   ⚠️  No test image found. Using URL upload instead...")

                # Fallback to URL upload
                image_urls = [
                    "https://httpbin.org/image/jpeg",
                    "https://httpbin.org/image/png",
                ]
                result_uuids = await client.image_recognition.upload_image_urls(
                    task_uuid=created_task.uuid, image_urls=image_urls
                )
                print(f"   ✅ Uploaded {len(result_uuids)} images via URL")
                print(f"   📸 Result UUIDs: {result_uuids}")

        except Exception as e:
            print(f"   ❌ Error uploading images: {e}")
            return

        # 4. Get IR Results from task
        print("\n4️⃣ Getting IR results...")
        try:
            # Wait a bit for processing
            print("   ⏳ Waiting for processing...")
            await asyncio.sleep(30)

            # Get results
            results = await client.result_management.get_task_results(
                task_uuid=created_task.uuid, limit=10
            )
            print(f"   ✅ Retrieved {len(results)} results")

        except Exception as e:
            print(f"   ❌ Error getting results: {e}")
            return

        # 5. Display number of facings from the results
        print("\n5️⃣ Analyzing results...")
        try:
            if results:
                print(f"   📊 Found {len(results)} results to analyze:")

                for i, result in enumerate(results, 1):
                    print(f"\n   Result {i}:")
                    print(f"     🆔 UUID: {result.uuid}")
                    print(f"     📊 Status: {result.status.value}")
                    print(f"     🎯 Confidence: {result.confidence_score}")
                    print(f"     ⏱️  Duration: {result.duration}s")
                    print(f"     📅 Created: {result.created_at}")

                    if result.failure_reason:
                        print(f"     ❌ Failure: {result.failure_reason}")

                    # Analyze COCO data for detections
                    if result.coco:
                        print(f"     🎯 COCO Data: {result.coco}")

                    # Analyze postprocessing results
                    if result.postprocessing_results:
                        print(
                            f"     🔄 Postprocessing: {result.postprocessing_results}"
                        )

                        # Look for realogram data
                        if "realogram" in result.postprocessing_results:
                            realogram = result.postprocessing_results["realogram"]
                            if realogram and "item_entries" in realogram:
                                item_count = len(realogram["item_entries"])
                                print(
                                    f"     📦 Detected {item_count} items in realogram"
                                )

                        # Look for shares data
                        if "shares" in result.postprocessing_results:
                            shares = result.postprocessing_results["shares"]
                            if shares:
                                print(
                                    f"     📈 Share analysis available for {len(shares)} images"
                                )
            else:
                print(
                    "   ⚠️  No results found yet. Processing may still be in progress."
                )

        except Exception as e:
            print(f"   ❌ Error analyzing results: {e}")
            return

        print("\n✅ End-to-End Workflow Complete!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
