"""
API endpoints for the Neurolabs SDK.
"""

from .base import BaseEndpoint
from .catalog import CatalogEndpoint
from .image_recognition import (
    ImagePredictionEndpoint,
    ResultManagementEndpoint,
    TaskManagementEndpoint,
)

__all__ = [
    "BaseEndpoint",
    "CatalogEndpoint",
    "TaskManagementEndpoint",
    "ImagePredictionEndpoint",
    "ResultManagementEndpoint",
]
