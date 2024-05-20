import json
from typing import Optional

import duckdb


class GeoFeaturesResult:
    def __init__(self, bbox: dict, geo_json: str):
        self.geo_json_dict = json.loads(geo_json)
        # This comes out of DuckDB as a dictionary with keys, but STAC expects an array like [min_x, min_y, max_x, max_y]
        self.bbox = [bbox["min_x"], bbox["min_y"], bbox["max_x"], bbox["max_y"]]

    def __repr__(self):
        return f"GeoFeaturesResult geo_json={self.geo_json}, bbox={self.bbox}"


def read_geo_features_from_jsonl(filename: str) -> Optional[GeoFeaturesResult]:
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.read_json(filename, format="newline_delimited")
    location_prefix = "produced_by.sampling_site.sample_location."
    q = ("select ST_Extent(envelope)as bb, ST_AsGEOJSON(envelope) as poly "
         f"from (select ST_Envelope_Agg(ST_Point({location_prefix}longitude, {location_prefix}latitude)) as envelope "
         f"from '{filename}' where {location_prefix}longitude is not null)")
    spatial_results = con.sql(q).fetchone()
    if spatial_results is not None:
        return GeoFeaturesResult(spatial_results[0], spatial_results[1])
    else:
        return None


def get_temporal_extent_from_jsonl(filename: str) -> tuple[Optional[str], Optional[str]]:
    con = duckdb.connect()
    con.read_json(filename, format="newline_delimited")
    q = f"SET TimeZone='UTC'; CREATE TABLE samples AS SELECT * FROM read_json('{filename}', format='newline_delimited');"
    con.sql(q)
    q = ("SELECT min(produced_by.result_time::TIMESTAMPTZ) as min_t, "
         "max(produced_by.result_time::TIMESTAMPTZ) as max_t "
         "from samples where produced_by.result_time is not null")
    result = con.sql(q).fetchone()
    return (result[0], result[1])
