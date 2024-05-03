import duckdb


class GeoFeaturesResult:
    def __init__(self, bbox: dict, geo_json: dict):
        self.geo_json = geo_json
        # This comes out of DuckDB as a dictionary with keys, but STAC expects an array like [min_x, min_y, max_x, max_y]
        self.bbox = [bbox["min_x"], bbox["min_y"], bbox["max_x"], bbox["max_y"]]

    def __repr__(self):
        return f"GeoFeaturesResult geo_json={self.geo_json}, bbox={self.bbox}"


def read_geo_features_from_jsonl(filename: str) -> GeoFeaturesResult:
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.read_json(filename, format="newline_delimited")
    results = con.sql(f"select * from '{filename}'")
    print(f"results are {results}")
    q = f"select ST_Extent(envelope)as bb, ST_AsGEOJSON(envelope) as poly from (select ST_Envelope_Agg(ST_Point(produced_by.sampling_site.latitude, produced_by.sampling_site.longitude)) as envelope from '{filename}' where produced_by.sampling_site.longitude is not null)"
    spatial_results = con.sql(q).fetchone()
    return GeoFeaturesResult(spatial_results[0], spatial_results[1])



if __name__ == "__main__":
    result = read_geo_features_from_jsonl("/tmp/isamples_export_2024_05_01_13_48_01.jsonl")
    print(f"result is {result}")