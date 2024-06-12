import datetime
import json
import os.path
import shutil
import uuid
from datetime import timezone, timedelta
from unittest.mock import MagicMock

import pytest
from stac_validator import stac_validator

from isamples_export_client.duckdb_utilities import GeoFeaturesResult, TemporalExtent
from isamples_export_client.export_client import ExportClient

MOCK_UUID = "abcdef"


@pytest.fixture
def geo_features_result() -> GeoFeaturesResult:
    bbox = {
        "min_x": 1.0,
        "min_y": 1.0,
        "max_x": 10.0,
        "max_y": 10.0
    }
    return GeoFeaturesResult(bbox, '{"type": "Polygon", "coordinates": [[[-149.91531, -27.1031], [-149.91531, 42.9989], [47.418, 42.9989], [47.418, -27.1031], [-149.91531, -27.1031]]]}')


@pytest.fixture
def temporal_extent() -> TemporalExtent:
    tz_info = timezone(timedelta(hours=0, minutes=0))
    datetime_0 = datetime.datetime.now(tz_info)
    datetime_1 = datetime.datetime.now(tz_info)
    return TemporalExtent(datetime_0, datetime_1)


@pytest.fixture()
def solr_query():
    return "foo:12345"


@pytest.fixture
def test_data_dir() -> str:
    return os.path.join(os.path.dirname(__file__), f"test_data/{uuid.uuid4()}")


@pytest.fixture
def export_client(solr_query: str, test_data_dir: str) -> ExportClient:
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    return ExportClient(solr_query, test_data_dir, "123456", "http://foo", "jsonl", "title", "description", None, MagicMock())


@pytest.fixture
def uuid_fixture() -> str:
    return str(uuid.uuid4())


def test_stac(geo_features_result: GeoFeaturesResult, temporal_extent: TemporalExtent, solr_query: str, export_client: ExportClient, uuid_fixture: str):
    stac_file = export_client.write_stac_item(uuid_fixture, datetime.datetime.now(), geo_features_result, temporal_extent, solr_query, "123456.jsonl", "123456.jsonl_geo.parquet")
    stac = stac_validator.StacValidate(stac_file, extensions=True)
    result = stac.run()
    print(stac.message)
    assert result is True


def test_stac_catalog(geo_features_result: GeoFeaturesResult, temporal_extent: TemporalExtent, solr_query: str, export_client: ExportClient):
    stac_file = export_client.write_stac_catalog()
    stac = stac_validator.StacValidate(stac_file, extensions=True)
    result = stac.run()
    print(stac.message)
    assert result is True


def test_write_manifest(solr_query: str, export_client: ExportClient, uuid_fixture: str):
    manifest_path = export_client.write_manifest(solr_query, uuid_fixture, datetime.datetime.now(), 100, export_client._destination_directory)
    with open(manifest_path, "r") as file:
        data = json.load(file)
        assert len(data) > 0


def _configure_mock_response_for_export_client(export_client: ExportClient, status_code: int, json_val: dict):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_val
    export_client._rsession.get.return_value = mock_response  # type: ignore


def test_create(export_client: ExportClient):
    _configure_mock_response_for_export_client(export_client, 200, {"uuid": MOCK_UUID})
    result = export_client.create()
    assert result == MOCK_UUID


def test_status(export_client: ExportClient):
    _configure_mock_response_for_export_client(export_client, 200, {"status": "completed"})
    result = export_client.status("abcdef")
    assert result["status"] == "completed"


def test_status_raise_invalid(export_client: ExportClient):
    _configure_mock_response_for_export_client(export_client, 400, {})
    with pytest.raises(Exception):
        export_client.status("abcdef")


def test_download(export_client: ExportClient):
    def mock_download_generator():
        yield """{"id":"123456"}"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = mock_download_generator
    export_client._rsession.get.return_value = mock_response  # type: ignore
    filename = export_client.download("abcdef")
    assert filename is not None
    assert os.path.exists(filename)
