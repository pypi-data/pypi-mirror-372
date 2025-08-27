"""
Command-line interface for the Zia SDK.
"""

import asyncio
import sys

from zia import Zia


async def health_check():
    """Check API health."""
    try:
        async with Zia() as client:
            is_healthy = await client.health_check()
            if is_healthy:
                print("✅ API is healthy")
                return 0
            else:
                print("❌ API is not healthy")
                return 1
    except Exception as e:
        print(f"❌ Error checking API health: {e}")
        return 1


async def list_items(limit: int = 10):
    """List catalog items."""
    try:
        async with Zia() as client:
            items = await client.catalog.list_items(limit=limit)
            print(f"Found {len(items)} catalog items:")
            for item in items:
                print(f"  - {item.name} ({item.uuid})")
            return 0
    except Exception as e:
        print(f"❌ Error listing items: {e}")
        return 1


async def list_tasks(limit: int = 10):
    """List image recognition tasks."""
    try:
        async with Zia() as client:
            tasks = await client.image_recognition.list_tasks(limit=limit)
            print(f"Found {len(tasks)} image recognition tasks:")
            for task in tasks:
                print(f"  - {task.name} ({task.uuid})")
            return 0
    except Exception as e:
        print(f"❌ Error listing tasks: {e}")
        return 1


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: zia <command> [options]")
        print("Commands:")
        print("  health     Check API health")
        print("  items      List catalog items")
        print("  tasks      List image recognition tasks")
        return 1

    command = sys.argv[1]

    if command == "health":
        return asyncio.run(health_check())
    elif command == "items":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        return asyncio.run(list_items(limit))
    elif command == "tasks":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        return asyncio.run(list_tasks(limit))
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
