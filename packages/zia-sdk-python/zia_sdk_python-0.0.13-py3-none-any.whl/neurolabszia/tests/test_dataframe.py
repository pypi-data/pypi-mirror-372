#!/usr/bin/env python3
"""
Tests for DataFrame workflows and Spark integration.
"""

from unittest.mock import Mock

import pandas as pd

from neurolabszia.utils.dataframe import (
    get_spark_schema_from_dataframe,
    ir_results_to_dataframe,
    to_spark_dataframe,
)
from neurolabszia.models.image_recognition import NLIRResult


class TestDataframe:
    """Test DataFrame conversion and analysis workflows."""

    def test_ir_results_to_dataframe_basic(self, sample_ir_results_list_data):
        """Test basic DataFrame conversion."""

        results = [
            NLIRResult.model_validate(result)
            for result in sample_ir_results_list_data["items"]
        ]
        df = ir_results_to_dataframe(results)

        # Check DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert not df.empty

        # Check required columns
        required_columns = [
            "result_uuid",
            "task_uuid",
            "image_url",
            "result_status",
            "annotation_id",
            "category_id",
            "detection_score",
            "category_name",
            "product_name",
            "product_brand",
        ]

        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_get_spark_schema_from_dataframe(self, sample_ir_results_list_data):
        """Test Spark schema generation from DataFrame."""

        results = [
            NLIRResult.model_validate(result)
            for result in sample_ir_results_list_data["items"]
        ]
        df = ir_results_to_dataframe(results)

        df = ir_results_to_dataframe(results)
        schema = get_spark_schema_from_dataframe(df)

        # Check schema structure
        assert schema is not None
        assert hasattr(schema, "fields")

        # Check schema fields
        field_names = [field.name for field in schema.fields]
        expected_fields = [
            "result_uuid",
            "task_uuid",
            "detection_score",
            "category_name",
        ]

        for field in expected_fields:
            assert field in field_names, f"Missing schema field: {field}"

    def test_to_spark_dataframe(self, sample_ir_results_list_data):
        """Test conversion to Spark DataFrame."""
        # TODO: Add correct spark test

        results = [
            NLIRResult.model_validate(result)
            for result in sample_ir_results_list_data["items"]
        ]

        # Create pandas DataFrame first to get the expected row count
        pdf = ir_results_to_dataframe(results)
        expected_row_count = len(pdf)

        # Mock Spark session with proper count method
        mock_spark = Mock()
        mock_spark_df = Mock()
        mock_spark_df.count.return_value = expected_row_count
        mock_spark.createDataFrame.return_value = mock_spark_df
        mock_spark.sparkContext.emptyRDD.return_value = Mock()

        spark_df = to_spark_dataframe(results, mock_spark)

        # Check that createDataFrame was called
        mock_spark.createDataFrame.assert_called_once()

        assert spark_df.count() == expected_row_count

    def test_realogram_and_shares_models(self):
        """Test that realogram and share of shelf models work correctly."""
        from neurolabszia.models.image_recognition import (
            NLIRModalities,
            NLIRModality,
            NLIRShare,
            NLIRShareValue,
            NLIRPostprocessingResults,
        )

        # Test modality
        modality_data = {
            "score": 1.0,
            "value": "1"
        }
        modality = NLIRModality.model_validate(modality_data)
        assert modality.score == 1.0
        assert modality.value == "1"

        # Test modalities with all types
        modalities_data = {
            "is-beer": [{"score": 1.0, "value": "True"}],
            "orientation": [{"score": 1.0, "value": "FRONT_BACK"}],
            "realogram:slot": [{"score": 1.0, "value": "1"}],
            "realogram:shelf": [{"score": 1.0, "value": "2"}],
            "realogram:stack": [{"score": 1.0, "value": "0"}]
        }
        modalities = NLIRModalities.from_dict(modalities_data)
        assert modalities.is_beer is not None
        assert modalities.is_beer[0].value == "True"
        assert modalities.orientation is not None
        assert modalities.orientation[0].value == "FRONT_BACK"
        assert modalities.realogram_slot is not None
        assert modalities.realogram_slot[0].value == "1"
        assert modalities.realogram_shelf is not None
        assert modalities.realogram_shelf[0].value == "2"
        assert modalities.realogram_stack is not None
        assert modalities.realogram_stack[0].value == "0"

        # Test share value
        share_value_data = {
            "group_by": "products",
            "product_uuid": "0f5285de-7542-40bf-9df6-7a85b53753b6",
            "count": 1,
            "count_ratio": 0.03333333333333333,
            "area": 18522,
            "area_ratio": 0.020090658527140613
        }
        share_value = NLIRShareValue.model_validate(share_value_data)
        assert share_value.group_by == "products"
        assert share_value.product_uuid == "0f5285de-7542-40bf-9df6-7a85b53753b6"
        assert share_value.count == 1
        assert share_value.count_ratio == 0.03333333333333333
        assert share_value.area == 18522
        assert share_value.area_ratio == 0.020090658527140613

        # Test share
        share_data = {
            "image_id": 1,
            "values": [share_value_data]
        }
        share = NLIRShare.model_validate(share_data)
        assert share.image_id == 1
        assert len(share.values) == 1
        assert share.values[0].group_by == "products"

        # Test postprocessing results
        postprocessing_data = {
            "shares": [share_data]
        }
        postprocessing = NLIRPostprocessingResults.model_validate(postprocessing_data)
        assert len(postprocessing.shares) == 1
        assert postprocessing.shares[0].image_id == 1

    def test_ir_results_to_dataframe_with_modalities_and_shares(self):
        """Test that ir_results_to_dataframe includes modalities and share data when available."""
        from neurolabszia.utils import ir_results_to_dataframe

        # Create mock data with modalities and shares
        mock_result_data = {
            "uuid": "test-uuid",
            "task_uuid": "test-task",
            "image_url": "test-url",
            "status": "PROCESSED",
            "failure_reason": "",
            "duration": 10.0,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "postprocessing_results": {
                "shares": [
                    {
                        "image_id": 1,
                        "values": [
                            {
                                "group_by": "products",
                                "product_uuid": "test-product-uuid",
                                "count": 5,
                                "count_ratio": 0.25,
                                "area": 1000,
                                "area_ratio": 0.3
                            }
                        ]
                    }
                ]
            },
            "coco": {
                "info": {"year": "2025", "version": "1", "date_created": "2025-01-01"},
                "images": [{"id": 1, "width": 100, "height": 100, "license": 1, "file_name": "test.jpg"}],
                "licenses": [{"id": 1, "url": "", "name": ""}],
                "neurolabs": {},
                "categories": [
                    {
                        "id": 1,
                        "name": "Test Product",
                        "neurolabs": {
                            "productUuid": "test-product-uuid",
                            "name": "Test Product",
                            "brand": "Test Brand",
                            "barcode": "123456789",
                            "customId": "test-custom-id",
                            "label": "Test Label"
                        },
                        "supercategory": "test-category"
                    }
                ],
                "annotations": [
                    {
                        "id": 0,
                        "area": 1000,
                        "bbox": [0, 0, 10, 10],
                        "iscrowd": 0,
                        "image_id": 1,
                        "neurolabs": {
                            "modalities": {
                                "is-beer": [{"score": 1.0, "value": "True"}],
                                "orientation": [{"score": 1.0, "value": "FRONT_BACK"}],
                                "realogram:slot": [{"score": 1.0, "value": "1"}],
                                "realogram:shelf": [{"score": 1.0, "value": "2"}],
                                "realogram:stack": [{"score": 1.0, "value": "0"}]
                            },
                            "score": 0.95,
                            "alternative_predictions": [
                                {"category_id": 2, "score": 0.8}
                            ]
                        },
                        "category_id": 1,
                        "segmentation": []
                    }
                ]
            },
            "confidence_score": 0.95
        }

        result = NLIRResult.model_validate(mock_result_data)
        df = ir_results_to_dataframe([result], include_modalities=True, include_shares=True)

        # Should have only detection rows (no separate share rows)
        assert len(df) == 1
        
        # Check that detection row has modality data
        detection_row = df.iloc[0]
        assert detection_row["is_beer"] == "True"
        assert detection_row["is_beer_score"] == 1.0
        assert detection_row["orientation"] == "FRONT_BACK"
        assert detection_row["orientation_score"] == 1.0
        assert detection_row["realogram_slot"] == "1"
        assert detection_row["realogram_slot_score"] == 1.0
        assert detection_row["realogram_shelf"] == "2"
        assert detection_row["realogram_shelf_score"] == 1.0
        assert detection_row["realogram_stack"] == "0"
        assert detection_row["realogram_stack_score"] == 1.0
        
        # Check that detection row has share data as columns
        assert detection_row["share_count"] == 5
        assert detection_row["share_count_ratio"] == 0.25
        assert detection_row["share_area"] == 1000
        assert detection_row["share_area_ratio"] == 0.3

    def test_ir_results_to_dataframe_without_modalities_and_shares(self):
        """Test that ir_results_to_dataframe works without modalities and shares."""
        from neurolabszia.utils import ir_results_to_dataframe

        # Create mock data without modalities and shares
        mock_result_data = {
            "uuid": "test-uuid",
            "task_uuid": "test-task",
            "image_url": "test-url",
            "status": "PROCESSED",
            "failure_reason": "",
            "duration": 10.0,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "postprocessing_results": {"shares": []},
            "coco": {
                "info": {"year": "2025", "version": "1", "date_created": "2025-01-01"},
                "images": [{"id": 1, "width": 100, "height": 100, "license": 1, "file_name": "test.jpg"}],
                "licenses": [{"id": 1, "url": "", "name": ""}],
                "neurolabs": {},
                "categories": [
                    {
                        "id": 1,
                        "name": "Test Product",
                        "neurolabs": {
                            "productUuid": "test-product-uuid",
                            "name": "Test Product",
                            "brand": "Test Brand",
                            "barcode": "123456789",
                            "customId": "test-custom-id",
                            "label": "Test Label"
                        },
                        "supercategory": "test-category"
                    }
                ],
                "annotations": [
                    {
                        "id": 0,
                        "area": 1000,
                        "bbox": [0, 0, 10, 10],
                        "iscrowd": 0,
                        "image_id": 1,
                        "neurolabs": {
                            "modalities": {},
                            "score": 0.95,
                            "alternative_predictions": []
                        },
                        "category_id": 1,
                        "segmentation": []
                    }
                ]
            },
            "confidence_score": 0.95
        }

        result = NLIRResult.model_validate(mock_result_data)
        df = ir_results_to_dataframe([result], include_modalities=False, include_shares=False)

        # Should have only detection rows
        assert len(df) == 1
        
        # Check that modality columns are not present
        modality_columns = ["is_beer", "orientation", "realogram_slot", "realogram_shelf", "realogram_stack"]
        for col in modality_columns:
            assert col not in df.columns
        
        # Check that share columns are not present
        share_columns = ["share_count", "share_count_ratio", "share_area", "share_area_ratio"]
        for col in share_columns:
            assert col not in df.columns

    def test_modalities_parsing(self):
        """Test that modalities are correctly parsed from the JSON structure."""
        from neurolabszia.models.image_recognition import NLIRCOCONeurolabsAnnotation

        # Test modalities data structure
        modalities_data = {
            "is-beer": [{"score": 1.0, "value": "True"}],
            "orientation": [{"score": 1.0, "value": "FRONT_BACK"}],
            "realogram:slot": [{"score": 1.0, "value": "1"}],
            "realogram:shelf": [{"score": 1.0, "value": "2"}],
            "realogram:stack": [{"score": 1.0, "value": "0"}]
        }

        # Test that NLIRModalities.from_dict works
        from neurolabszia.models.image_recognition import NLIRModalities
        modalities = NLIRModalities.from_dict(modalities_data)
        
        assert modalities.is_beer is not None
        assert modalities.is_beer[0].value == "True"
        assert modalities.is_beer[0].score == 1.0
        
        assert modalities.orientation is not None
        assert modalities.orientation[0].value == "FRONT_BACK"
        assert modalities.orientation[0].score == 1.0
        
        assert modalities.realogram_slot is not None
        assert modalities.realogram_slot[0].value == "1"
        assert modalities.realogram_slot[0].score == 1.0
        
        assert modalities.realogram_shelf is not None
        assert modalities.realogram_shelf[0].value == "2"
        assert modalities.realogram_shelf[0].score == 1.0
        
        assert modalities.realogram_stack is not None
        assert modalities.realogram_stack[0].value == "0"
        assert modalities.realogram_stack[0].score == 1.0

        # Test that NLIRCOCONeurolabsAnnotation correctly parses modalities
        annotation_data = {
            "modalities": modalities_data,
            "score": 0.95,
            "alternative_predictions": []
        }
        
        annotation = NLIRCOCONeurolabsAnnotation.model_validate(annotation_data)
        
        assert annotation.modalities is not None
        assert annotation.modalities.is_beer is not None
        assert annotation.modalities.is_beer[0].value == "True"
        assert annotation.modalities.realogram_slot is not None
        assert annotation.modalities.realogram_slot[0].value == "1"
        assert annotation.score == 0.95

