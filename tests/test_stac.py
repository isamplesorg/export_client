import datetime
import uuid
from datetime import tzinfo, timezone, timedelta

import pytest
from stac_validator import stac_validator

from isamples_export_client.duckdb_utilities import GeoFeaturesResult, TemporalExtent
from isamples_export_client.export_client import ExportClient


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
    tz_info = timezone(timedelta(hours = 0, minutes = 0))
    datetime_0 = datetime.datetime.now(tz_info)
    datetime_1 = datetime.datetime.now(tz_info)
    return TemporalExtent(datetime_0, datetime_1)


@pytest.fixture()
def solr_query():
    return "foo:12345"


def test_stac(geo_features_result: GeoFeaturesResult, temporal_extent: TemporalExtent, solr_query: str):
    export_client = ExportClient(solr_query, "./test_data/", "123456", "http://foo", "jsonl")
    stac_file = export_client.write_stac(str(uuid.uuid4()), datetime.datetime.now(), geo_features_result, temporal_extent, solr_query, "123456.jsonl", "123456.jsonl_geo.parquet")
    stac = stac_validator.StacValidate(stac_file, extensions=True)
    result = stac.run()
    print(stac.message)
    assert result is True

