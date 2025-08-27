"""
Data models for the Zia SDK.
"""

from .catalog import NLCatalogItem, NLCatalogItemCreate
from .image_recognition import (
    NLIRCOCOAlternativePrediction,
    NLIRCOCOAnnotation,
    NLIRCOCOCategory,
    NLIRCOCOImage,
    NLIRCOCOInfo,
    NLIRCOCOLicense,
    NLIRCOCONeurolabsAnnotation,
    NLIRCOCONeurolabsCategory,
    NLIRCOCOResult,
    NLIRModalities,
    NLIRModality,
    NLIRPostprocessingResults,
    NLIRResult,
    NLIRResults,
    NLIRResultStatus,
    NLIRShare,
    NLIRShareValue,
    NLIRTask,
    NLIRTaskCreate,
    NLIRTaskCreateWithAllCatalogItems,
    NLIRTaskStatus,
)

__all__ = [
    "NLCatalogItem",
    "NLCatalogItemCreate",
    "NLIRTask",
    "NLIRResult",
    "NLIRTaskCreate",
    "NLIRResultStatus",
    "NLIRTaskStatus",
    "NLIRCOCOResult",
    "NLIRCOCOInfo",
    "NLIRCOCOImage",
    "NLIRCOCOLicense",
    "NLIRCOCONeurolabsCategory",
    "NLIRCOCOCategory",
    "NLIRCOCOAlternativePrediction",
    "NLIRCOCONeurolabsAnnotation",
    "NLIRCOCOAnnotation",
    "NLIRResults",
    "NLIRTaskCreateWithAllCatalogItems",
    "NLIRPostprocessingResults",
    "NLIRModalities",
    "NLIRModality",
    "NLIRShare",
    "NLIRShareValue",
]
