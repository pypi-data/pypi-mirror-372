"""
Integration tests for the Zia SDK core features.

These tests require a valid NEUROLABS_API_KEY environment variable and will make real API calls.
Run with: pytest zia/tests/test_integration.py -v
"""

import asyncio
from pathlib import Path

import pytest

from zia import NLCatalogItem, NLCatalogItemCreate, NLIRTaskCreate

# Use fixtures from conftest.py instead of defining them here


class TestIntegrationBasics:
    """Basic integration tests that can run with environment variables."""

    @pytest.mark.asyncio
    async def test_health_check_with_real_api(self, integration_client):
        """Test health check with real API (if API key is available)."""
        async with integration_client:
            is_healthy = await integration_client.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_catalog_list_with_real_api(self, integration_client):
        """Test catalog listing with real API (if API key is available)."""
        async with integration_client:
            items = await integration_client.catalog.list_items(limit=5)
            assert isinstance(items[0], NLCatalogItem)
            assert isinstance(items, list)
            assert len(items) <= 5
            assert items[0].uuid is not None
            assert items[0].name is not None
            assert items[0].status is not None
            assert items[0].thumbnail_url is not None
            assert items[0].created_at is not None
            assert items[0].updated_at is not None

    @pytest.mark.asyncio
    async def test_task_list_with_real_api(self, integration_client):
        """Test task listing with real API (if API key is available)."""
        async with integration_client:
            tasks = await integration_client.task_management.list_tasks(limit=5)
            assert isinstance(tasks, list)
            assert len(tasks) <= 5


class TestCatalogIntegration:
    """Integration tests for catalog operations."""

    @pytest.mark.asyncio
    async def test_create_catalog_item_with_thumbnail(
        self, integration_client, test_thumbnail_path
    ):
        """Test creating a catalog item with thumbnail binary data."""
        # Read the test image
        with open(test_thumbnail_path, "rb") as f:
            thumbnail_data = f.read()

        # Create catalog item with thumbnail
        item = NLCatalogItemCreate(
            name="Test Product - Integration Test",
            brand="Test Brand",
            barcode="1234567890123",
            thumbnail=thumbnail_data,
        )

        async with integration_client:
            # Create the item
            created_item = await integration_client.catalog.create_item(item)

            # Verify the item was created
            assert created_item.uuid is not None
            assert created_item.name == "Test Product - Integration Test"
            assert created_item.brand == "Test Brand"
            assert created_item.barcode == "1234567890123"
            assert created_item.status.value in ["ONBOARDED", "INCOMPLETE"]
            assert created_item.thumbnail_url is not None

            print(f"Created catalog item: {created_item.uuid}")

            # Clean up - delete the item (if delete endpoint exists)
            # Note: This depends on whether the API supports deletion

    @pytest.mark.asyncio
    async def test_get_catalog_items(self, integration_client):
        """Test retrieving catalog items."""
        async with integration_client:
            # Get items with pagination
            items = await integration_client.catalog.list_items(limit=5)

            # Verify we got a list of items
            assert isinstance(items, list)
            assert len(items) <= 5

            if items:
                # Verify item structure
                item = items[0]
                assert hasattr(item, "uuid")
                assert hasattr(item, "name")
                assert hasattr(item, "status")
                assert hasattr(item, "thumbnail_url")
                assert hasattr(item, "created_at")
                assert hasattr(item, "updated_at")

                print(f"Retrieved {len(items)} catalog items")

    @pytest.mark.asyncio
    async def test_get_all_catalog_items(self, integration_client):
        """Test retrieving all catalog items with automatic pagination."""
        # TODO: Implement this test
        pass

        # async with integration_client:
        #     # Get all items
        #     all_items = await integration_client.catalog.list_all_items(batch_size=10)
        #
        #     # Verify we got a list of items
        #     assert isinstance(all_items, list)
        #
        #     if all_items:
        #         print(f"Retrieved {len(all_items)} total catalog items")
        #
        #         # Verify item structure
        #         item = all_items[0]
        #         assert hasattr(item, 'uuid')
        #         assert hasattr(item, 'name')
        #         assert hasattr(item, 'status')


class TestImageRecognitionIntegration:
    """Integration tests for image recognition operations."""

    @pytest.mark.asyncio
    async def test_create_task_with_catalog_items(self, integration_client):
        """Test creating an image recognition task with catalog items."""
        async with integration_client:
            # First, get some catalog items to use
            catalog_items = await integration_client.catalog.list_items(limit=2)

            if not catalog_items:
                pytest.skip("No catalog items available for testing")

            # Create task with catalog items
            task = NLIRTaskCreate(
                name="Integration Test Task",
                catalog_items=[item.uuid for item in catalog_items],
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await integration_client.task_management.create_task(task)

            # Verify the task was created
            assert created_task.uuid is not None
            assert created_task.name == "Integration Test Task"
            assert created_task.compute_realogram is False
            assert created_task.compute_shares is False
            assert created_task.created_at is not None
            assert created_task.updated_at is not None

            print(f"Created task: {created_task.uuid}")

            return created_task

    @pytest.mark.asyncio
    async def test_upload_images_via_binary(self, integration_client, test_image_path):
        """Test uploading images via binary data."""
        async with integration_client:
            # First create a task
            catalog_items = await integration_client.catalog.list_items(limit=1)
            if not catalog_items:
                pytest.skip("No catalog items available for testing")

            task = NLIRTaskCreate(
                name="Integration Test Upload Images Via Binary Data",
                catalog_items=[catalog_items[0].uuid],
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await integration_client.task_management.create_task(task)

            # Upload image via binary
            image_paths = [test_image_path]
            result_uuids = await integration_client.image_recognition.upload_images(
                task_uuid=created_task.uuid, image_paths=image_paths
            )

            # Verify we got result UUIDs
            assert isinstance(result_uuids, list)
            assert len(result_uuids) == 1
            assert result_uuids[0] is not None

            print(f"Uploaded image, got result UUID: {result_uuids[0]}")

            return created_task, result_uuids[0]

    @pytest.mark.asyncio
    async def test_upload_images_via_url(self, integration_client):
        """Test uploading images via URL."""
        async with integration_client:
            # First create a task
            catalog_items = await integration_client.catalog.list_items(limit=1)
            if not catalog_items:
                pytest.skip("No catalog items available for testing")

            task = NLIRTaskCreate(
                name="URL Upload Test Task",
                catalog_items=[catalog_items[0].uuid],
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await integration_client.task_management.create_task(task)

            # Upload image via URL (using a public test image)
            image_urls = [
                "https://storage.googleapis.com/nlb-dev-public/zia-sdk-python/demo.jpeg",  # Public test image
                "https://storage.googleapis.com/nlb-dev-public/zia-sdk-python/demo1.jpeg",  # Another public test image
            ]

            result_uuids = await integration_client.image_recognition.upload_image_urls(
                task_uuid=created_task.uuid, image_urls=image_urls
            )

            # Verify we got result UUIDs
            assert isinstance(result_uuids, list)
            assert len(result_uuids) == 2
            assert all(uuid is not None for uuid in result_uuids)

            print(
                f"Uploaded {len(image_urls)} images via URL, got result UUIDs: {result_uuids}"
            )

            return created_task, result_uuids

    @pytest.mark.asyncio
    async def test_get_ir_results(self, integration_client):
        """Test retrieving IR results."""
        async with integration_client:
            # First create a task and upload an image
            catalog_items = await integration_client.catalog.list_items(
                name="Test Product - Integration Test"
            )
            if not catalog_items:
                pytest.skip("No catalog items available for testing")

            task = NLIRTaskCreate(
                name="Results Test Task",
                catalog_items=[catalog_items[0].uuid],
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await integration_client.task_management.create_task(task)

            # Upload a test image
            image_path = (
                Path(__file__).parent.parent.parent
                / "data"
                / "display"
                / "pocm_ab.jpeg"
            )
            if image_path.exists():
                image_paths = [image_path, image_path]
                result_uuids = await integration_client.image_recognition.upload_images(
                    task_uuid=created_task.uuid, image_paths=image_paths
                )

                if result_uuids:
                    # Wait a bit for processing
                    await asyncio.sleep(30)

                    # Get results
                    results = (
                        await integration_client.result_management.get_task_results(
                            task_uuid=created_task.uuid, limit=10
                        )
                    )

                    # Verify we got results
                    assert isinstance(results, list)

                    if results:
                        result = results[0]
                        assert hasattr(result, "uuid")
                        assert hasattr(result, "task_uuid")
                        assert hasattr(result, "image_url")
                        assert hasattr(result, "status")
                        assert hasattr(result, "failure_reason")
                        assert hasattr(result, "created_at")
                        assert hasattr(result, "updated_at")

                        print(f"Retrieved {len(results)} results")
                        print(f"Result status: {result.status.value}")
                        print(f"Result failure reason: {result.failure_reason}")

                        # Test getting a specific result
                        specific_result = (
                            await integration_client.result_management.get_result(
                                task_uuid=created_task.uuid, result_uuid=result.uuid
                            )
                        )

                        assert specific_result.uuid == result.uuid
                        assert specific_result.task_uuid == created_task.uuid

    @pytest.mark.asyncio
    async def test_get_all_ir_results(self, integration_client):
        """Test retrieving all IR results with automatic pagination."""
        # TODO: Implement this test
        pass

        # async with integration_client:
        #     # Get all tasks
        #     tasks = await integration_client.image_recognition.list_all_tasks(batch_size=5)
        #
        #     if not tasks:
        #         pytest.skip("No tasks available for testing")
        #
        #     # Get results for the first task
        #     task = tasks[0]
        #     all_results = await integration_client.image_recognition.get_all_task_results(
        #         task_uuid=task.uuid,
        #         batch_size=10
        #     )
        #
        #     # Verify we got results
        #     assert isinstance(all_results, list)
        #
        #     if all_results:
        #         print(f"Retrieved {len(all_results)} total results for task {task.uuid}")
        #
        #         # Verify result structure
        #         result = all_results[0]
        #         assert hasattr(result, 'uuid')
        #         assert hasattr(result, 'task_uuid')
        #         assert hasattr(result, 'status')


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, integration_client, test_image_path):
        """Test the complete workflow: catalog → task → upload → results."""
        async with integration_client:
            print("\n=== Starting End-to-End Workflow Test ===")

            # 1. Get all catalog items
            print("1. Getting all catalog items...")
            catalog_items = await integration_client.catalog.list_all_items(
                batch_size=10
            )
            print(f"   Found {len(catalog_items)} catalog items")

            if not catalog_items:
                pytest.skip("No catalog items available for testing")

            # 2. Create a task with all catalog items
            print("2. Creating task with catalog items...")
            task = NLIRTaskCreate(
                name="End-to-End Test Task",
                catalog_items=[
                    item.uuid for item in catalog_items[:5]
                ],  # Use first 5 items
                compute_realogram=False,
                compute_shares=False,
            )

            created_task = await integration_client.task_management.create_task(task)
            print(f"   Created task: {created_task.uuid}")

            # 3. Upload images to task
            print("3. Uploading images to task...")
            image_paths = [test_image_path]
            result_uuids = await integration_client.image_recognition.upload_images(
                task_uuid=created_task.uuid, image_paths=image_paths
            )
            print(
                f"   Uploaded {len(result_uuids)} images, got result UUIDs: {result_uuids}"
            )

            # 4. Get IR results from task
            print("4. Getting IR results...")
            # Wait a bit for processing
            await asyncio.sleep(40)

            results = await integration_client.result_management.get_task_results(
                task_uuid=created_task.uuid, limit=10
            )
            print(f"   Retrieved {len(results)} results")

            # 5. Display number of facings from results
            print("5. Analyzing results...")
            if results:
                for result in results:
                    print(f"   Result {result.uuid}:")
                    print(f"     Status: {result.status.value}")
                    print(f"     Failure reason: {result.failure_reason}")
                    print(f"     Confidence score: {result.confidence_score}")

                    if result.coco:
                        print(f"     COCO data available: {result.coco}")

                    if result.postprocessing_results:
                        print(
                            f"     Postprocessing results: {result.postprocessing_results}"
                        )

            print("=== End-to-End Workflow Test Complete ===\n")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
