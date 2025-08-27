"""
DataFrame utilities for converting Neurolabs SDK data models to pandas DataFrames and Spark DataFrames.

This module provides functions to convert NLIRResult objects to pandas DataFrames
for data analysis and processing. It matches categories with annotations using
the category_id and creates flat DataFrames with all attributes for each detected item.

Usage:
    from zia.utils import ir_results_to_dataframe, ir_results_to_summary_dataframe

    # Convert results to DataFrame
    df = ir_results_to_dataframe(results)

    # Create summary DataFrame
    df_summary = ir_results_to_summary_dataframe(results)
"""

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    try:
        from pyspark.sql.types import StructType
    except ImportError:
        StructType = None


def get_dynamic_spark_schema(df: pd.DataFrame) -> "StructType | None":
    """
    Dynamically generate a Spark schema based on the actual DataFrame structure.

    This function analyzes the pandas DataFrame and creates a matching Spark schema,
    ensuring no mismatches between the DataFrame columns and schema fields.

    Args:
        df: pandas DataFrame created by ir_results_to_dataframe()

    Returns:
        pyspark.sql.types.StructType schema that matches the DataFrame exactly

    Raises:
        ImportError: If pyspark is not installed
    """
    try:
        from pyspark.sql.types import (
            ArrayType,
            BooleanType,
            DoubleType,
            FloatType,
            IntegerType,
            StringType,
            StructField,
            StructType,
            TimestampType,
        )
        from pyspark.sql.types import StructType as SparkStructType
    except ImportError:
        raise ImportError(
            "pyspark is required for Spark schema generation. "
            "Install it with: pip install pyspark"
        )

    fields = []

    for column_name, dtype in df.dtypes.items():
        # Handle different pandas dtypes
        if dtype == "object":
            # Check if it's a datetime column
            if column_name in ["result_created_at", "result_updated_at"]:
                spark_type = TimestampType()
            # Check if it's the alternative_predictions column (list of dicts)
            elif column_name == "alternative_predictions":
                # Define schema for alternative prediction items
                alt_pred_schema = SparkStructType(
                    [
                        StructField("category_id", IntegerType(), True),
                        StructField("category_name", StringType(), True),
                        StructField("score", FloatType(), True),
                    ]
                )
                spark_type = ArrayType(alt_pred_schema)
            elif column_name in ["is_beer", "orientation", "realogram_slot", "realogram_shelf", "realogram_stack"]:
                spark_type = StringType()
            elif column_name.startswith("share_"):
                spark_type = FloatType()
            else:
                spark_type = StringType()
        elif dtype == "int64":
            spark_type = IntegerType()
        elif dtype == "float64":
            # Handle score columns
            if column_name.endswith("_score"):
                spark_type = FloatType()
            else:
                spark_type = DoubleType()
        elif dtype == "bool":
            spark_type = BooleanType()
        elif dtype == "datetime64[ns]":
            spark_type = TimestampType()
        else:
            # Default to string for unknown types
            spark_type = StringType()

        fields.append(StructField(column_name, spark_type, True))

    return StructType(fields)


def get_spark_schema_from_dataframe(df: pd.DataFrame) -> "StructType | None":
    """
    Generate Spark schema directly from the DataFrame structure.

    This is the recommended approach to ensure perfect schema matching.

    Args:
        df: pandas DataFrame created by ir_results_to_dataframe()

    Returns:
        pyspark.sql.types.StructType schema that matches the DataFrame exactly

    Raises:
        ImportError: If pyspark is not installed
    """
    return get_dynamic_spark_schema(df)


def ir_results_to_dataframe(
    results: list[Any],
    include_bbox: bool = True,
    include_alternative_predictions: bool = True,
    include_modalities: bool = True,
    include_shares: bool = True,
) -> pd.DataFrame:
    """
    Convert a list of NLIRResult objects to a pandas DataFrame.
    
    This function matches categories with annotations using the category_id
    and creates a flat DataFrame with all attributes for each detected item.
    Optionally includes modalities and share of shelf data.

    Args:
        results: List of NLIRResult objects (from zia.models)
        include_bbox: Whether to include bounding box coordinates as separate columns
        include_alternative_predictions: Whether to include alternative predictions
        include_modalities: Whether to include modalities data (is-beer, orientation, realogram)
        include_shares: Whether to include share of shelf data

    Returns:
        pandas DataFrame with one row per detected item
    """
    rows = []
    
    # Pre-process share data to create a lookup map
    share_lookup = {}
    if include_shares:
        for result in results:
            if result.postprocessing_results and result.postprocessing_results.shares:
                for share in result.postprocessing_results.shares:
                    for value in share.values:
                        # Create key: (image_id, product_uuid)
                        key = (share.image_id, value.product_uuid)
                        share_lookup[key] = {
                            "count": value.count,
                            "count_ratio": value.count_ratio,
                            "area": value.area,
                            "area_ratio": value.area_ratio,
                        }

    for result in results:
        if not result.coco:
            continue

        # Create category lookup map
        category_map = {cat.id: cat for cat in result.coco.categories}

        for annotation in result.coco.annotations:
            category = category_map.get(annotation.category_id)
            if not category:
                continue

            # Get product UUID from category
            product_uuid = None
            if category.neurolabs:
                product_uuid = category.neurolabs.productUuid

            row = {
                # Result-level information
                "result_uuid": result.uuid,
                "task_uuid": result.task_uuid,
                "neurolabs_image_link": f"https://app.neurolabs.ai/task-management/{result.task_uuid}/result/{result.uuid}/validation",
                "image_url": result.image_url,
                "result_status": result.status.value,
                "result_duration": result.duration,
                "result_created_at": result.created_at,
                "result_updated_at": result.updated_at,
                "confidence_score": annotation.neurolabs.score if annotation.neurolabs else None, 
                # Image information
                "image_id": annotation.image_id,
                "image_filename": next(
                    (
                        img.file_name
                        for img in result.coco.images
                        if img.id == annotation.image_id
                    ),
                    None,
                ),
                # Category information
                "category_id": annotation.category_id,
                "category_name": category.name,
                "product_uuid": product_uuid,
                "product_name": category.neurolabs.name if category.neurolabs else None,
                "product_brand": category.neurolabs.brand if category.neurolabs else None,
                "product_barcode": category.neurolabs.barcode if category.neurolabs else None,
                "product_custom_id": category.neurolabs.customId if category.neurolabs else None,
                "product_label": category.neurolabs.label if category.neurolabs else None,
                # Annotation information
                "annotation_id": annotation.id,
                "detection_score": annotation.neurolabs.score if annotation.neurolabs else None,
                "area": annotation.area,
                "iscrowd": annotation.iscrowd,
            }

            # Add bounding box coordinates if requested
            if include_bbox and annotation.bbox:
                row.update(
                    {
                        "bbox_x": annotation.bbox[0],
                        "bbox_y": annotation.bbox[1],
                        "bbox_width": annotation.bbox[2],
                        "bbox_height": annotation.bbox[3],
                    }
                )

            # Add modalities data if requested and available
            if include_modalities and annotation.neurolabs and annotation.neurolabs.modalities:
                modalities = annotation.neurolabs.modalities
                
                # Extract is-beer modality
                if modalities.is_beer and len(modalities.is_beer) > 0:
                    row["is_beer"] = modalities.is_beer[0].value
                    row["is_beer_score"] = modalities.is_beer[0].score

                # Extract orientation modality
                if modalities.orientation and len(modalities.orientation) > 0:
                    row["orientation"] = modalities.orientation[0].value
                    row["orientation_score"] = modalities.orientation[0].score

                # Extract realogram modalities
                if modalities.realogram_slot and len(modalities.realogram_slot) > 0:
                    row["realogram_slot"] = modalities.realogram_slot[0].value
                    row["realogram_slot_score"] = modalities.realogram_slot[0].score

                if modalities.realogram_shelf and len(modalities.realogram_shelf) > 0:
                    row["realogram_shelf"] = modalities.realogram_shelf[0].value
                    row["realogram_shelf_score"] = modalities.realogram_shelf[0].score

                if modalities.realogram_stack and len(modalities.realogram_stack) > 0:
                    row["realogram_stack"] = modalities.realogram_stack[0].value
                    row["realogram_stack_score"] = modalities.realogram_stack[0].score

            # Add alternative predictions if requested
            if (
                include_alternative_predictions
                and annotation.neurolabs.alternative_predictions
            ):
                alt_predictions = []
                for alt_pred in annotation.neurolabs.alternative_predictions:
                    alt_category = category_map.get(alt_pred.category_id)
                    alt_predictions.append(
                        {
                            "category_id": alt_pred.category_id,
                            "category_name": alt_category.name
                            if alt_category
                            else f"Unknown_{alt_pred.category_id}",
                            "score": alt_pred.score,
                        }
                    )
                row["alternative_predictions"] = alt_predictions
            else:
                # Ensure alternative_predictions is always a list for Spark compatibility
                row["alternative_predictions"] = []

            # Add share of shelf data if requested and available
            if include_shares and product_uuid:
                share_key = (annotation.image_id, product_uuid)
                if share_key in share_lookup:
                    share_data = share_lookup[share_key]
                    row.update({
                        "share_count": share_data["count"],
                        "share_count_ratio": share_data["count_ratio"],
                        "share_area": share_data["area"],
                        "share_area_ratio": share_data["area_ratio"],
                    })

            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Convert datetime columns
    datetime_columns = ["result_created_at", "result_updated_at"]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def ir_results_to_summary_dataframe(results: list[Any]) -> pd.DataFrame:
    """
    Create a summary DataFrame with aggregated statistics per result.

    Args:
        results: List of NLIRResult objects (from zia.models)

    Returns:
        pandas DataFrame with one row per result and summary statistics

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    summary_rows = []

    for result in results:
        row = {
            "result_uuid": result.uuid,
            "task_uuid": result.task_uuid,
            "image_url": result.image_url,
            "status": result.status.value,
            "duration": result.duration,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
            "confidence_score": result.confidence_score,
            "total_detections": 0,
            "unique_products": 0,
            "avg_detection_score": 0.0,
            "max_detection_score": 0.0,
            "min_detection_score": 0.0,
        }

        if result.coco and result.status.value == "PROCESSED":
            annotations = result.coco.annotations
            if annotations:
                scores = [ann.neurolabs.score for ann in annotations]
                unique_products = len(set(ann.category_id for ann in annotations))

                row.update(
                    {
                        "total_detections": len(annotations),
                        "unique_products": unique_products,
                        "avg_detection_score": sum(scores) / len(scores),
                        "max_detection_score": max(scores),
                        "min_detection_score": min(scores),
                    }
                )

        summary_rows.append(row)

    if not summary_rows:
        return pd.DataFrame()

    df = pd.DataFrame(summary_rows)

    # Convert datetime columns
    datetime_columns = ["created_at", "updated_at"]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def analyze_results_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Analyze a DataFrame created from NLIRResults and return summary statistics.

    Args:
        df: DataFrame created by ir_results_to_dataframe()

    Returns:
        Dictionary with analysis results

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    if df.empty:
        return {"error": "DataFrame is empty"}

    analysis = {
        "total_detections": len(df),
        "unique_products": df["product_name"].nunique()
        if "product_name" in df.columns
        else 0,
        "unique_images": df["result_uuid"].nunique(),
        "score_stats": {
            "mean": df["detection_score"].mean(),
            "std": df["detection_score"].std(),
            "min": df["detection_score"].min(),
            "max": df["detection_score"].max(),
            "median": df["detection_score"].median(),
        },
    }

    # Product analysis
    if "product_name" in df.columns:
        product_counts = df["product_name"].value_counts()
        analysis["top_products"] = product_counts.head(10).to_dict()
        analysis["product_detection_counts"] = {
            "single_detection": (product_counts == 1).sum(),
            "multiple_detections": (product_counts > 1).sum(),
        }

    # Score distribution
    score_ranges = {
        "high_confidence": len(df[df["detection_score"] >= 0.9]),
        "medium_confidence": len(
            df[(df["detection_score"] >= 0.7) & (df["detection_score"] < 0.9)]
        ),
        "low_confidence": len(df[df["detection_score"] < 0.7]),
    }
    analysis["score_distribution"] = score_ranges

    # Bounding box analysis (if available)
    if "bbox_width" in df.columns and "bbox_height" in df.columns:
        analysis["bbox_stats"] = {
            "avg_width": df["bbox_width"].mean(),
            "avg_height": df["bbox_height"].mean(),
            "avg_area": df["area"].mean(),
        }

    # Modalities analysis (if available)
    modality_columns = ["is_beer", "orientation", "realogram_slot", "realogram_shelf", "realogram_stack"]
    available_modalities = [col for col in modality_columns if col in df.columns]
    
    if available_modalities:
        analysis["modalities"] = {}
        for modality in available_modalities:
            analysis["modalities"][modality] = df[modality].value_counts().to_dict()
            
            # Add score analysis if available
            score_col = f"{modality}_score"
            if score_col in df.columns:
                analysis["modalities"][f"{modality}_score_stats"] = {
                    "mean": df[score_col].mean(),
                    "std": df[score_col].std(),
                    "min": df[score_col].min(),
                    "max": df[score_col].max(),
                    "median": df[score_col].median(),
                }

    # Share of shelf analysis (if available)
    share_columns = [col for col in df.columns if col.startswith("share_")]
    if share_columns:
        analysis["share_of_shelf"] = {
            "total_share_entries": len(df[df["row_type"] == "share"]) if "row_type" in df.columns else 0,
            "unique_share_products": df["share_product_uuid"].nunique() if "share_product_uuid" in df.columns else 0,
        }
        
        # Share statistics
        if "share_count_ratio" in df.columns:
            analysis["share_of_shelf"]["count_ratio_stats"] = {
                "mean": df["share_count_ratio"].mean(),
                "std": df["share_count_ratio"].std(),
                "min": df["share_count_ratio"].min(),
                "max": df["share_count_ratio"].max(),
                "median": df["share_count_ratio"].median(),
            }
        
        if "share_area_ratio" in df.columns:
            analysis["share_of_shelf"]["area_ratio_stats"] = {
                "mean": df["share_area_ratio"].mean(),
                "std": df["share_area_ratio"].std(),
                "min": df["share_area_ratio"].min(),
                "max": df["share_area_ratio"].max(),
                "median": df["share_area_ratio"].median(),
            }

    return analysis


def filter_high_confidence_detections(
    df: pd.DataFrame, threshold: float = 0.9
) -> pd.DataFrame:
    """
    Filter DataFrame to include only high-confidence detections.

    Args:
        df: DataFrame created by ir_results_to_dataframe()
        threshold: Minimum confidence score (default: 0.9)

    Returns:
        Filtered DataFrame

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    return df[df["detection_score"] >= threshold]


def get_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a product summary from the detailed DataFrame.

    Args:
        df: DataFrame created by ir_results_to_dataframe()

    Returns:
        DataFrame with one row per product and aggregated statistics

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    if df.empty:
        return pd.DataFrame()

    product_summary = (
        df.groupby(
            [
                "product_uuid",
                "product_name",
                "product_brand",
                "product_barcode",
                "product_custom_id",
            ]
        )
        .agg(
            {
                "result_uuid": "count",  # Number of detections
                "detection_score": ["mean", "max", "min", "std"],
                "task_uuid": "nunique",  # Number of tasks this product appears in
                "result_uuid": "nunique",  # Number of images this product appears in
            }
        )
        .reset_index()
    )

    # Flatten column names
    product_summary.columns = [
        "product_uuid",
        "product_name",
        "product_brand",
        "product_barcode",
        "product_custom_id",
        "total_detections",
        "avg_score",
        "max_score",
        "min_score",
        "score_std",
        "num_tasks",
        "num_images",
    ]

    return product_summary


def to_spark_dataframe(
    results: list[Any],
    spark_session,
    include_bbox: bool = True,
    include_alternative_predictions: bool = True,
    include_modalities: bool = True,
    include_shares: bool = True,
):
    """
    Convert NLIRResult objects to a Spark DataFrame.

    Args:
        results: List of NLIRResult objects
        spark_session: Active Spark session
        include_bbox: Whether to include bounding box fields
        include_alternative_predictions: Whether to include alternative predictions
        include_modalities: Whether to include modalities data (is-beer, orientation, realogram)
        include_shares: Whether to include share of shelf data

    Returns:
        Spark DataFrame

    Raises:
        ImportError: If pyspark is not installed
    """
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        raise ImportError(
            "pyspark is required for Spark DataFrame operations. "
            "Install it with: pip install pyspark"
        )

    # Convert to pandas DataFrame first
    pdf = ir_results_to_dataframe(
        results,
        include_bbox=include_bbox,
        include_alternative_predictions=include_alternative_predictions,
        include_modalities=include_modalities,
        include_shares=include_shares,
    )

    if pdf.empty:
        return spark_session.createDataFrame([], spark_session.sparkContext.emptyRDD())

    # Replace NaN values with None for Spark compatibility
    pdf = pdf.where(pd.notnull(pdf), None)

    # Generate schema from the pandas DataFrame
    schema = get_spark_schema_from_dataframe(pdf)

    # Convert to Spark DataFrame using records
    try:
        return spark_session.createDataFrame(pdf, schema=schema)
    except Exception as e:
        # Provide more detailed error information
        print(f"Error converting to Spark DataFrame: {e}")
        print(f"DataFrame shape: {pdf.shape}")
        print(f"DataFrame columns: {pdf.columns.tolist()}")
        print(f"DataFrame dtypes: {pdf.dtypes.to_dict()}")
        raise
