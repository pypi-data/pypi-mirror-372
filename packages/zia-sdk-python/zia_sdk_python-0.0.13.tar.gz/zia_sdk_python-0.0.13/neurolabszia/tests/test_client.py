"""
Tests for the Neurolabs client.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from neurolabszia import Config
from neurolabszia.models import NLIRResult, NLIRResultStatus, NLIRPostprocessingResults


class TestConfig:
    """Test configuration validation."""

    def test_valid_config(self):
        """Test valid configuration creation."""
        config = Config(api_key="test-key", base_url="https://api.test.com/v2")
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.test.com/v2"

    def test_invalid_api_key(self):
        """Test invalid API key validation."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            Config(api_key="")

    def test_invalid_base_url(self):
        """Test invalid base URL validation."""
        with pytest.raises(ValueError, match="Base URL must start with"):
            Config(api_key="test-key", base_url="invalid-url")


class TestClient:
    """Test client functionality."""

    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.config.api_key == "test-api-key"
        assert client.config.base_url == "https://api.test.com/v2"

    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        # Mock the session
        client._session = AsyncMock()
        client._session.get.return_value = MagicMock()

        result = await client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test failed health check."""
        # Mock the session to raise an exception
        client._session = AsyncMock()
        client._session.get.side_effect = Exception("Connection failed")

        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager."""
        client._session = AsyncMock()

        async with client as c:
            assert c is client

        client._session.__aenter__.assert_called_once()
        client._session.__aexit__.assert_called_once()


class TestCatalogEndpoint:
    """Test catalog endpoint functionality."""

    @pytest.mark.asyncio
    async def test_list_items(self, client):
        """Test listing catalog items."""
        # Mock the catalog endpoint
        client._catalog = AsyncMock()
        mock_items = [{"uuid": "1", "name": "Item 1"}]
        client._catalog.list_items.return_value = mock_items

        items = await client.catalog.list_items(limit=10)
        assert items == mock_items
        client._catalog.list_items.assert_called_once_with(limit=10)


class TestTaskManagementEndpoint:
    """Test image recognition endpoint functionality."""

    @pytest.mark.asyncio
    async def test_list_tasks(self, client):
        """Test listing image recognition tasks."""
        # Mock the image recognition endpoint
        client._task_management = AsyncMock()
        mock_tasks = [{"uuid": "1", "name": "Task 1"}]
        client._task_management.list_tasks.return_value = mock_tasks

        tasks = await client.task_management.list_tasks(limit=10)
        assert tasks == mock_tasks
        client.task_management.list_tasks.assert_called_once_with(limit=10)


class TestImageRecognitionResults:
    """Test image recognition results functionality."""

    def test_ir_result_model_creation(self, sample_base_ir_result_data):
        """Test creating NLIRResult model from sample data."""
        result = NLIRResult(**sample_base_ir_result_data)

        assert result.uuid == "43632c23-bbaf-4118-ab39-875a4db2de9c"
        assert result.task_uuid == "f4c84578-ed86-45a0-ac89-930b4eeb63c3"
        assert result.status == NLIRResultStatus.PROCESSED
        assert result.failure_reason == ""
        assert result.duration == 16.546352
        assert result.confidence_score is None
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)
        assert result.postprocessing_results == NLIRPostprocessingResults(**{"realogram": None, "shares": []})

    def test_coco_result_model_creation(self, sample_base_ir_result_data):
        """Test creating NLIRCOCOResult model from sample data."""
        result = NLIRResult(**sample_base_ir_result_data)

        assert result.coco is not None
        coco = result.coco

        # Test info
        assert coco.info.year == "2025"
        assert coco.info.version == "1"
        assert coco.info.date_created == "08/09/2025, 22:27:05"

        # Test images
        assert len(coco.images) == 1
        image = coco.images[0]
        assert image.id == 1
        assert image.width is None
        assert image.height is None
        assert image.license == 1

        # Test licenses
        assert len(coco.licenses) == 1
        license_obj = coco.licenses[0]
        assert license_obj.id == 1

        # Test categories
        assert len(coco.categories) == 4
        category = coco.categories[1]  # The one with neurolabs data
        assert category.id == 1
        assert category.neurolabs.productUuid == "nb9cde09-2206-42d3-8323-567b01gf43a5"
        assert category.name == "Keystone Light 24/12C"
        assert category.neurolabs is not None
        assert category.neurolabs.barcode == "71990480066"
        assert category.neurolabs.brand == "Keystone"

        # Test annotations
        assert len(coco.annotations) == 2
        annotation = coco.annotations[0]
        assert annotation.id == 0
        assert annotation.area == 134676
        assert annotation.bbox == [102, 440, 522, 258]
        assert annotation.iscrowd == 0
        assert annotation.image_id == 1
        assert annotation.category_id == 1
        assert annotation.neurolabs.score == 0.869894652
        assert len(annotation.neurolabs.alternative_predictions) == 2

    @pytest.mark.asyncio
    async def test_get_ir_result(self, client, sample_base_ir_result_data):
        """Test getting a single IR result."""
        # Mock the task management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_result.return_value = sample_base_ir_result_data

        result = await client.result_management.get_result(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3",
            result_uuid="43632c23-bbaf-4118-ab39-875a4db2de9c",
        )
        assert result == sample_base_ir_result_data
        client._result_management.get_result.assert_called_once_with(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3",
            result_uuid="43632c23-bbaf-4118-ab39-875a4db2de9c",
        )

    @pytest.mark.asyncio
    async def test_list_ir_results(self, client, sample_ir_results_list_data):
        """Test listing IR results."""
        # Mock the task management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_task_results.return_value = (
            sample_ir_results_list_data
        )

        results = await client.result_management.get_task_results(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", limit=10
        )
        assert results == sample_ir_results_list_data
        client._result_management.get_task_results.assert_called_once_with(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", limit=10
        )

    @pytest.mark.asyncio
    async def test_get_ir_result_with_model_parsing(
        self, client, sample_base_ir_result_data
    ):
        """Test getting IR result and parsing it into the model."""
        # Mock the task management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_result.return_value = sample_base_ir_result_data

        raw_result = await client.result_management.get_result(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3",
            result_uuid="43632c23-bbaf-4118-ab39-875a4db2de9c",
        )
        result_model = NLIRResult(**raw_result)

        assert result_model.uuid == "43632c23-bbaf-4118-ab39-875a4db2de9c"
        assert result_model.status == NLIRResultStatus.PROCESSED
        assert result_model.coco is not None
        assert len(result_model.coco.annotations) == 2
        assert result_model.coco.annotations[0].neurolabs.score == 0.869894652

    @pytest.mark.asyncio
    async def test_get_ir_result_raw(self, client, sample_base_ir_result_data):
        """Test getting raw JSON IR result without parsing."""
        # Mock the result management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_result_raw.return_value = (
            sample_base_ir_result_data
        )

        raw_result = await client.result_management.get_result_raw(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3",
            result_uuid="43632c23-bbaf-4118-ab39-875a4db2de9c",
        )

        # Should return raw JSON without parsing
        assert raw_result == sample_base_ir_result_data
        assert isinstance(raw_result, dict)
        assert raw_result["uuid"] == "43632c23-bbaf-4118-ab39-875a4db2de9c"
        assert raw_result["status"] == "PROCESSED"
        assert "coco" in raw_result
        client._result_management.get_result_raw.assert_called_once_with(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3",
            result_uuid="43632c23-bbaf-4118-ab39-875a4db2de9c",
        )

    @pytest.mark.asyncio
    async def test_get_task_results_raw(self, client, sample_ir_results_list_data):
        """Test getting raw JSON task results without parsing."""
        # Mock the result management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_task_results_raw.return_value = (
            sample_ir_results_list_data
        )

        raw_results = await client.result_management.get_task_results_raw(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", limit=10
        )

        # Should return raw JSON without parsing
        assert raw_results == sample_ir_results_list_data
        assert isinstance(raw_results, dict)
        assert "items" in raw_results
        assert "total" in raw_results
        assert "limit" in raw_results
        assert "offset" in raw_results
        assert len(raw_results["items"]) == 1
        assert raw_results["items"][0]["uuid"] == "43632c23-bbaf-4118-ab39-875a4db2de9c"
        client._result_management.get_task_results_raw.assert_called_once_with(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", limit=10
        )

    @pytest.mark.asyncio
    async def test_get_all_task_results_raw(self, client, sample_ir_results_list_data):
        """Test getting all raw JSON task results without parsing."""
        # Mock the result management endpoint
        client._result_management = AsyncMock()
        client._result_management.get_all_task_results_raw.return_value = (
            sample_ir_results_list_data["items"]
        )

        raw_results = await client.result_management.get_all_task_results_raw(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", batch_size=100
        )

        # Should return list of raw JSON items without parsing
        assert raw_results == sample_ir_results_list_data["items"]
        assert isinstance(raw_results, list)
        assert len(raw_results) == 1
        assert raw_results[0]["uuid"] == "43632c23-bbaf-4118-ab39-875a4db2de9c"
        client._result_management.get_all_task_results_raw.assert_called_once_with(
            task_uuid="f4c84578-ed86-45a0-ac89-930b4eeb63c3", batch_size=100
        )

    def test_ir_result_status_enum(self):
        """Test IR result status enum values."""
        assert NLIRResultStatus.IN_PROGRESS == "IN_PROGRESS"
        assert NLIRResultStatus.FAILED == "FAILED"
        assert NLIRResultStatus.PROCESSED == "PROCESSED"

    def test_ir_result_with_failed_status(self):
        """Test IR result with failed status."""
        failed_result_data = {
            "uuid": "test-uuid",
            "task_uuid": "test-task-uuid",
            "image_url": "https://example.com/image.jpg",
            "status": "FAILED",
            "failure_reason": "Image processing failed",
            "duration": None,
            "created_at": "2025-08-09T22:27:05.672621",
            "updated_at": "2025-08-09T22:27:21.647052",
            "postprocessing_results": None,
            "coco": None,
            "confidence_score": None,
        }

        result = NLIRResult(**failed_result_data)
        assert result.status == NLIRResultStatus.FAILED
        assert result.failure_reason == "Image processing failed"
        assert result.coco is None
