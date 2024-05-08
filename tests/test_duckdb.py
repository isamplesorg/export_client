from isamples_export_client.duckdb_utilities import read_geo_features_from_jsonl


def test_duckdb_read_geo_features():
    geofeatures_result = read_geo_features_from_jsonl("./test_data/isamples_export_2024_05_08_08_57_12.jsonl")
    assert geofeatures_result is not None
    assert len(geofeatures_result.bbox) == 4
    geo_json_dict = geofeatures_result.geo_json_dict
    assert len(geo_json_dict) > 0
    assert geo_json_dict["type"] == "Polygon"
    assert geo_json_dict["coordinates"] is not None
