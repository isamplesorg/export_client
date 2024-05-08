import os
import geopandas as gpd
from isamples_export_client.geoparquet_utilities import write_geoparquet_from_json_lines


def test_geoparquet():
    dest_file = write_geoparquet_from_json_lines("./test_data/isamples_export_2024_05_08_08_57_12.jsonl")
    assert os.path.exists(dest_file)
    df = gpd.read_parquet(dest_file)
    assert df is not None