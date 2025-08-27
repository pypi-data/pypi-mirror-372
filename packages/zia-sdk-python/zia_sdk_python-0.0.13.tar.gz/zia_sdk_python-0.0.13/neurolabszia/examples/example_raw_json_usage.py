#!/usr/bin/env python3
"""
Example script demonstrating how to use both parsed models and raw JSON functions
for image recognition results.
"""

import asyncio

from neurolabszia import Config, Zia


async def main():
    """Demonstrate both parsed and raw JSON approaches."""

    # Initialize client (replace with your actual API key)
    config = Config(
        api_key="your-api-key-here", base_url="https://api.neurolabs.com/v2"
    )
    client = Zia(config)

    # Example task and result UUIDs
    task_uuid = "f4c84578-ed86-45a0-ac89-930b4eeb63c3"
    result_uuid = "43632c23-bbaf-4118-ab39-875a4db2de9c"

    async with client:
        print("=== Image Recognition Results Example ===\n")

        # 1. Get parsed results (using models)
        print("1. Getting parsed results (using NLIRResult models):")
        print("-" * 50)

        try:
            # Get a single parsed result
            result = await client.result_management.get_result(
                task_uuid=task_uuid, result_uuid=result_uuid
            )

            print("✅ Parsed result:")
            print(f"   UUID: {result.uuid}")
            print(f"   Status: {result.status}")
            print(f"   Duration: {result.duration}")
            print(f"   Created at: {result.created_at}")

            if result.coco:
                print(f"   COCO data: {len(result.coco.annotations)} annotations")
                for i, annotation in enumerate(
                    result.coco.annotations[:3]
                ):  # Show first 3
                    print(
                        f"     Annotation {i}: score={annotation.neurolabs.score:.3f}"
                    )

            # Get parsed task results
            results = await client.result_management.get_task_results(
                task_uuid=task_uuid, limit=5
            )
            print(f"   Task results: {len(results)} items")

        except Exception as e:
            print(f"❌ Error getting parsed results: {e}")

        print("\n" + "=" * 60 + "\n")

        # 2. Get raw JSON results (without parsing)
        print("2. Getting raw JSON results (without parsing):")
        print("-" * 50)

        try:
            # Get a single raw result
            raw_result = await client.result_management.get_result_raw(
                task_uuid=task_uuid, result_uuid=result_uuid
            )

            print("✅ Raw result:")
            print(f"   UUID: {raw_result['uuid']}")
            print(f"   Status: {raw_result['status']}")
            print(f"   Duration: {raw_result.get('duration')}")
            print(f"   Created at: {raw_result['created_at']}")

            if "coco" in raw_result and raw_result["coco"]:
                annotations = raw_result["coco"].get("annotations", [])
                print(f"   COCO data: {len(annotations)} annotations")
                for i, annotation in enumerate(annotations[:3]):  # Show first 3
                    score = annotation.get("neurolabs", {}).get("score", 0)
                    print(f"     Annotation {i}: score={score:.3f}")

            # Get raw task results
            raw_results = await client.result_management.get_task_results_raw(
                task_uuid=task_uuid, limit=5
            )

            print(f"   Task results: {len(raw_results.get('items', []))} items")
            print(f"   Total: {raw_results.get('total', 0)}")
            print(f"   Limit: {raw_results.get('limit', 0)}")
            print(f"   Offset: {raw_results.get('offset', 0)}")

            # Example: Access raw JSON data directly
            if raw_results.get("items"):
                first_item = raw_results["items"][0]
                print(f"   First item UUID: {first_item['uuid']}")

                # Access nested COCO data directly
                if "coco" in first_item and first_item["coco"]:
                    categories = first_item["coco"].get("categories", [])
                    print(f"   Categories: {len(categories)}")

                    # Find a category with neurolabs data
                    for category in categories:
                        if category.get("neurolabs"):
                            neurolabs_data = category["neurolabs"]
                            print(
                                f"   Product: {neurolabs_data.get('name', 'Unknown')}"
                            )
                            print(f"   Brand: {neurolabs_data.get('brand', 'Unknown')}")
                            print(
                                f"   Barcode: {neurolabs_data.get('barcode', 'Unknown')}"
                            )
                            break

        except Exception as e:
            print(f"❌ Error getting raw results: {e}")

        print("\n" + "=" * 60 + "\n")

       

if __name__ == "__main__":
    asyncio.run(main())
