"""
Zia Image Recognition SDK

A simple, ergonomic Python SDK for the Zia Image Recognition API.
"""

# config.py in your SDK
from pathlib import Path
import importlib.metadata

# Version is managed by Poetry in pyproject.toml
__version__ = importlib.metadata.version("zia-sdk-python")

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env", override=False)

from .client import Zia
from .config import Config
from .exceptions import (
    NeurolabsAuthError,
    NeurolabsError,
    NeurolabsRateLimitError,
    NeurolabsValidationError,
)
from .models import (
    NLCatalogItem,
    NLCatalogItemCreate,
    NLIRResult,
    NLIRTask,
    NLIRTaskCreate,
)

__all__ = [
    "Zia",
    "Config",
    "NeurolabsError",
    "NeurolabsAuthError",
    "NeurolabsRateLimitError",
    "NeurolabsValidationError",
    "NLCatalogItem",
    "NLCatalogItemCreate",
    "NLIRTask",
    "NLIRResult",
    "NLIRTaskCreate",
]

# Import utils functions for backward compatibility
try:
    from .utils import (
        analyze_results_dataframe,
        filter_high_confidence_detections,
        get_dynamic_spark_schema,
        get_product_summary,
        get_spark_schema_from_dataframe,
        ir_results_to_dataframe,
        ir_results_to_summary_dataframe,
        to_spark_dataframe,
    )

    __all__.extend(
        [
            "ir_results_to_dataframe",
            "ir_results_to_summary_dataframe",
            "analyze_results_dataframe",
            "filter_high_confidence_detections",
            "get_product_summary",
            "get_spark_schema_from_dataframe",
            "get_dynamic_spark_schema",
            "to_spark_dataframe",
        ]
    )
except ImportError:
    # Utils not available (missing dependencies)
    pass
