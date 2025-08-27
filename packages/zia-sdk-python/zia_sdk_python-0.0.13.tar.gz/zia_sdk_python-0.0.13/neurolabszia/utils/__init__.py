"""
DataFrame utilities for the Zia SDK.

This module provides functions to convert NLIRResult objects to pandas DataFrames
and Spark DataFrames for data analysis and processing.
"""

from .dataframe import (
    analyze_results_dataframe,
    filter_high_confidence_detections,
    get_dynamic_spark_schema,
    get_product_summary,
    get_spark_schema_from_dataframe,
    ir_results_to_dataframe,
    ir_results_to_summary_dataframe,
    to_spark_dataframe,
)

__all__ = [
    "ir_results_to_dataframe",
    "ir_results_to_summary_dataframe",
    "analyze_results_dataframe",
    "filter_high_confidence_detections",
    "get_product_summary",
    "get_spark_schema_from_dataframe",
    "get_dynamic_spark_schema",
    "to_spark_dataframe",
]
