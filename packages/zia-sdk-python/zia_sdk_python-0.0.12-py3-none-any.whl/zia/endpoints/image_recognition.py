"""
Image recognition endpoint for the Neurolabs SDK.
"""

from pathlib import Path
from typing import Any, Optional

from ..models.image_recognition import NLIRResult, NLIRTask, NLIRTaskCreate
from .base import BaseEndpoint


class TaskManagementEndpoint(BaseEndpoint):
    """Image recognition endpoint for managing tasks and results."""

    async def list_tasks(self, limit: int = 50, offset: int = 0) -> list[NLIRTask]:
        """
        List image recognition tasks.

        Args:
            limit: Number of tasks to return (max 100)
            offset: Offset for pagination

        Returns:
            List of image recognition tasks
        """
        params = {"limit": min(limit, 100), "offset": offset}
        response = await self._get("/image-recognition/tasks", params=params)
        return [NLIRTask.model_validate(task) for task in response["items"]]

    async def list_all_tasks(self, batch_size: int = 100) -> list[NLIRTask]:
        """
        Get all image recognition tasks with automatic pagination.

        Args:
            batch_size: Number of tasks to fetch per request (max 100)

        Returns:
            List of all image recognition tasks
        """
        all_tasks = []
        offset = 0
        batch_size = min(batch_size, 100)

        while True:
            params = {"limit": batch_size, "offset": offset}
            response = await self._get("/image-recognition/tasks", params=params)
            tasks = [NLIRTask.model_validate(task) for task in response["items"]]

            if not tasks:
                break

            all_tasks.extend(tasks)

            # Check if we've reached the end
            if len(tasks) < batch_size:
                break

            offset += batch_size

        return all_tasks

    async def get_task(self, task_uuid: str) -> NLIRTask:
        """
        Get a specific image recognition task by UUID.

        Args:
            task_uuid: UUID of the task

        Returns:
            Image recognition task
        """
        response = await self._get(f"/image-recognition/tasks/{task_uuid}")
        return NLIRTask.model_validate(response)

    async def create_task(self, task: NLIRTaskCreate) -> NLIRTask:
        """
        Create a new image recognition task.

        Args:
            task: Task creation data

        Returns:
            Created image recognition task
        """
        data = task.model_dump(exclude_none=True, mode="json", by_alias=True)
        response = await self._post("/image-recognition/tasks", data=data)
        return NLIRTask.model_validate(response)

    async def delete_task(self, task_uuid: str) -> bool:
        """
        Delete an image recognition task.

        Args:
            task_uuid: UUID of the task to delete

        Returns:
            True if successful
        """
        await self._delete(f"/image-recognition/tasks/{task_uuid}")
        return True


class ImagePredictionEndpoint(BaseEndpoint):
    """Image prediction endpoint for managing image predictions."""

    async def upload_images(
        self,
        task_uuid: str,
        image_paths: list[Path],
        callback_url: Optional[str] = None,
    ) -> list[str]:
        """
        Upload images to a task for processing.

        Args:
            task_uuid: UUID of the task
            image_paths: List of paths to images
            callback_url: Optional callback URL for webhook notifications
        Returns:
            List of IR result UUIDs
        """
        files = {}
        for i, path in enumerate(image_paths):
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            files["images"] = open(path, "rb")

        try:
            response = await self._post(
                f"/image-recognition/tasks/{task_uuid}/images",
                files=files,
                data={"callback_url": callback_url} if callback_url else None,
            )
            return response  # Returns list of IR result UUIDs
        finally:
            for file in files.values():
                file.close()

    async def upload_image_urls(
        self, task_uuid: str, image_urls: list[str], callback_url: Optional[str] = None
    ) -> list[str]:
        """
        Upload image URLs to a task for processing.

        Args:
            task_uuid: UUID of the task
            image_urls: List of image URLs
            callback_url: Optional callback URL for webhook notifications
        Returns:
            List of IR result UUIDs
        """
        data = {"urls": image_urls, "callback_url": callback_url}
        response = await self._post(
            f"/image-recognition/tasks/{task_uuid}/urls", data=data
        )
        return response  # Returns list of IR result UUIDs


class ResultManagementEndpoint(BaseEndpoint):
    """Image recognition result endpoint for managing results."""

    async def get_task_results(
        self, task_uuid: str, limit: int = 50, offset: int = 0
    ) -> list[NLIRResult]:
        """
        Get results for a specific task.

        Args:
            task_uuid: UUID of the task
            limit: Number of results to return (max 100)
            offset: Offset for pagination

        Returns:
            List of image recognition results
        """
        params = {"limit": min(limit, 100), "offset": offset}
        response = await self._get(
            f"/image-recognition/tasks/{task_uuid}/results", params=params
        )
        return [NLIRResult.model_validate(result) for result in response["items"]]

    async def get_task_results_raw(
        self, task_uuid: str, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """
        Get raw JSON results for a specific task without parsing into models.

        Args:
            task_uuid: UUID of the task
            limit: Number of results to return (max 100)
            offset: Offset for pagination

        Returns:
            Raw JSON response from the API
        """
        params = {"limit": min(limit, 100), "offset": offset}
        return await self._get(
            f"/image-recognition/tasks/{task_uuid}/results", params=params
        )

    async def get_all_task_results(
        self, task_uuid: str, batch_size: int = 100
    ) -> list[NLIRResult]:
        """
        Get all results for a specific task.

        Args:
            task_uuid: UUID of the task
            batch_size: Number of results to fetch per request (max 100)

        Returns:
            List of all image recognition results
        """
        all_results = []
        offset = 0
        batch_size = min(batch_size, 100)

        while True:
            params = {"limit": batch_size, "offset": offset}
            response = await self._get(
                f"/image-recognition/tasks/{task_uuid}/results", params=params
            )
            results = [
                NLIRResult.model_validate(result) for result in response["items"]
            ]

            if not results:
                break

            all_results.extend(results)

            # Check if we've reached the end
            if len(results) < batch_size:
                break

            offset += batch_size

        return all_results

    async def get_all_task_results_raw(
        self, task_uuid: str, batch_size: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get all raw JSON results for a specific task without parsing into models.

        Args:
            task_uuid: UUID of the task
            batch_size: Number of results to fetch per request (max 100)

        Returns:
            List of raw JSON responses from the API
        """
        all_results = []
        offset = 0
        batch_size = min(batch_size, 100)

        while True:
            params = {"limit": batch_size, "offset": offset}
            response = await self._get(
                f"/image-recognition/tasks/{task_uuid}/results", params=params
            )

            if not response["items"]:
                break

            all_results.extend(response["items"])

            # Check if we've reached the end
            if len(response["items"]) < batch_size:
                break

            offset += batch_size

        return all_results

    async def get_result(self, task_uuid: str, result_uuid: str) -> NLIRResult:
        """
        Get a specific result by UUID.

        Args:
            task_uuid: UUID of the task
            result_uuid: UUID of the result

        Returns:
            Image recognition result
        """
        response = await self._get(
            f"/image-recognition/tasks/{task_uuid}/results/{result_uuid}"
        )
        return NLIRResult.model_validate(response)

    async def get_result_raw(self, task_uuid: str, result_uuid: str) -> dict[str, Any]:
        """
        Get raw JSON for a specific result by UUID without parsing into model.

        Args:
            task_uuid: UUID of the task
            result_uuid: UUID of the result

        Returns:
            Raw JSON response from the API
        """
        return await self._get(
            f"/image-recognition/tasks/{task_uuid}/results/{result_uuid}"
        )
