# tests/conftest.py
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from neurolabszia import Config, Zia


@pytest.fixture(scope="session", autouse=True)
def load_environment():
    """
    Auto-load secrets for *all* tests.
    This runs automatically for every test session.
    """
    # Try to load from .env file manually if python-dotenv is available
    try:
        from dotenv import load_dotenv

        env_file = Path(".env.test") if Path(".env.test").exists() else Path(".env")
        if env_file.exists():
            print(f"📂 Loading environment from: {env_file}")
            load_dotenv(env_file, override=False)
        else:
            print(f"⚠️  No .env file found at: {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not available, using environment variables only")

    api_key = os.getenv("NEUROLABS_API_KEY")
    if api_key:
        print(f"🔑 Environment loaded. API Key: {api_key[:8]}...")
    else:
        print("⚠️  NEUROLABS_API_KEY not found in environment")


@pytest.fixture
def config():
    """Create a test configuration for unit tests."""
    return Config(
        api_key="test-api-key",
        base_url="https://api.test.com/v2",
        timeout=5.0,
        max_retries=1,
    )


@pytest.fixture
def client(config):
    """Create a test client for unit tests (mocked)."""
    return Zia(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries,
    )


@pytest.fixture
def api_key():
    load_dotenv()
    """Get API key from environment for integration tests."""
    key = os.getenv("NEUROLABS_API_KEY")
    if not key:
        pytest.skip("NEUROLABS_API_KEY environment variable not set")
    return key


@pytest.fixture
def integration_client():
    load_dotenv()
    """Create a real client for integration tests."""
    key = os.getenv("NEUROLABS_API_KEY")
    if not key:
        pytest.skip("NEUROLABS_API_KEY environment variable not set")

    print(f"🔧 Creating integration client with API key: {key[:8]}...")
    return Zia(api_key=key)


@pytest.fixture
def test_image_path():
    """Get path to test image."""
    image_path = (
        Path(__file__).parent.parent.parent / "data" / "display" / "pocm_ab.jpeg"
    )
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path


@pytest.fixture
def test_thumbnail_path():
    """Get path to test image."""
    image_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "display"
        / "bud_light_thumbnail.png"
    )
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path


@pytest.fixture
def sample_base_ir_result_data():
    """Sample IR result data matching the actual JSON structure."""
    return {
        "uuid": "43632c23-bbaf-4118-ab39-875a4db2de9c",
        "task_uuid": "f4c84578-ed86-45a0-ac89-930b4eeb63c3",
        "image_url": "https://storage.googleapis.com/nlb-dev-public/zia-sdk-python/demo.jpeg",
        "status": "PROCESSED",
        "failure_reason": "",
        "duration": 16.546352,
        "created_at": "2025-08-09T22:27:05.672621",
        "updated_at": "2025-08-09T22:27:21.647052",
        "postprocessing_results": {"realogram": None, "shares": []},
        "coco": {
            "info": {
                "url": "",
                "year": "2025",
                "version": "1",
                "contributor": "",
                "description": "",
                "date_created": "08/09/2025, 22:27:05",
            },
            "images": [
                {
                    "id": 1,
                    "width": None,
                    "height": None,
                    "license": 1,
                    "coco_url": "",
                    "file_name": "https://storage.googleapis.com/nlb-dev-public/zia-sdk-python/demo.jpeg",                    
                    "flickr_url": "",
                    "date_captured": "",
                }
            ],
            "licenses": [{"id": 1, "url": "", "name": ""}],
            "neurolabs": {},
            "categories": [
                {"id": 0, "name": "object", "neurolabs": None, "supercategory": ""},
                {
                    "id": 1,
                    "name": "Keystone Light 24/12C",
                    "neurolabs": {
                        "barcode": "71990480066",
                        "customId": "Keystone Light",
                        "label": "Keystone Light 24/12C",
                        "productUuid": "nb9cde09-2206-42d3-8323-567b01gf43a5",
                        "brand": "Keystone",
                        "name": "Keystone Light 24/12C",
                    },
                    "supercategory": "",
                },
                {
                    "id": 2,
                    "name": "Short's Locals Lager 12/12C",
                    "neurolabs": {
                        "barcode": "794028500436",
                        "customId": "Short's Locals Lager",
                        "label": "Short's Locals Lager 12/12C",
                        "productUuid": "acbdddb1-1a49-49f3-b73c-c54c224afe27",
                        "brand": "Short's",
                        "name": "Short's Locals Lager 12/12C",
                    },
                    "supercategory": "",
                },
                {
                    "id": 3,
                    "name": "Michelob Ultra 18/12C SC",
                    "neurolabs": {
                        "barcode": "18200967214",
                        "customId": "Michelob Ultra",
                        "label": "Michelob Ultra 18/12C SC",
                        "productUuid": "9df604aa-cf28-4fb4-8546-602d1924b400",
                        "brand": "Michelob Ultra",
                        "name": "Michelob Ultra 18/12C SC",
                    },
                    "supercategory": "",
                },
            ],
            "annotations": [
                {
                    "id": 0,
                    "area": 134676,
                    "bbox": [102, 440, 522, 258],
                    "iscrowd": 0,
                    "image_id": 1,
                    "neurolabs": {
                        "modalities": {},
                        "score": 0.869894652,
                        "alternative_predictions": [
                            {"category_id": 2, "score": 0.855113924},
                            {"category_id": 3, "score": 0.849582746},
                        ],
                    },
                    "category_id": 1,
                    "segmentation": [],
                },
                {
                    "id": 1,
                    "area": 185274,
                    "bbox": [579, 1233, 657, 282],
                    "iscrowd": 0,
                    "image_id": 1,
                    "neurolabs": {
                        "modalities": {},
                        "score": 0.981681682,
                        "alternative_predictions": [
                            {"category_id": 1, "score": 0.639585144},
                            {"category_id": 2, "score": 0.539767224},
                        ],
                    },
                    "category_id": 3,
                    "segmentation": [],
                },
            ],
        },
        "confidence_score": None,
    }


@pytest.fixture
def sample_ir_results_list_data(sample_base_ir_result_data):
    """Sample list of IR results data."""
    return {
        "items": [sample_base_ir_result_data],
        "total": 339601,
        "limit": 100,
        "offset": 0,
    }
