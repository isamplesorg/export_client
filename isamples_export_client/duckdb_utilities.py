import datetime
import json
import os.path
from typing import Optional

import duckdb

#Specifies the schema of the samples database created when loading the JSON
SOURCE_COLUMNS = '''{
sample_identifier: 'VARCHAR',
"label": 'VARCHAR',
source_collection: 'VARCHAR',
has_specimen_category: 'STRUCT("label" VARCHAR)[]',
has_material_category: 'STRUCT("label" VARCHAR)[]',
has_context_category: 'STRUCT("label" VARCHAR)[]',
informal_classification: 'VARCHAR[]',
keywords: 'STRUCT(keyword VARCHAR)[]',
produced_by: 'STRUCT(
    identifier VARCHAR, 
    "label" VARCHAR, 
    description VARCHAR, 
    result_time DATE, 
    sampling_site STRUCT(
        description VARCHAR, 
        "label" VARCHAR, 
        place_name VARCHAR[], 
        sample_location STRUCT(
            elevation DOUBLE, 
            latitude DOUBLE, 
            longitude DOUBLE
        )
    ), 
    responsibility STRUCT("role" VARCHAR, "name" VARCHAR)[]
)',
registrant: 'STRUCT("name" VARCHAR)',
curation: 'STRUCT(
    "label" VARCHAR, 
    description VARCHAR, 
    curation_location VARCHAR, 
    access_constraints VARCHAR[]
)'
}'''

class GeoFeaturesResult:
    def __init__(self, bbox: dict, geo_json: str):
        self.geo_json_dict = json.loads(geo_json)
        # This comes out of DuckDB as a dictionary with keys, but STAC expects an array like [min_x, min_y, max_x, max_y]
        self.bbox = [bbox["min_x"], bbox["min_y"], bbox["max_x"], bbox["max_y"]]

    def __repr__(self):
        return f"GeoFeaturesResult geo_json={self.geo_json}, bbox={self.bbox}"


class TemporalExtent(tuple):

    def __new__(self, t0: Optional[datetime.datetime], t1: Optional[datetime.datetime]):
        return tuple.__new__(TemporalExtent, (t0, t1))


def read_geo_features(con) -> Optional[GeoFeaturesResult]:
    location_prefix = "produced_by.sampling_site.sample_location."
    q = ("select ST_Extent(envelope)as bb, ST_AsGEOJSON(envelope) as poly "
         f"from (select ST_Envelope_Agg(ST_Point({location_prefix}longitude, {location_prefix}latitude)) as envelope "
         f"from samples where {location_prefix}longitude is not null)")
    spatial_results = con.sql(q).fetchone()
    if spatial_results is not None:
        return GeoFeaturesResult(spatial_results[0], spatial_results[1])
    else:
        return None


def get_temporal_extent(con) -> TemporalExtent:
    q = ("SELECT min(produced_by.result_time::TIMESTAMPTZ) as min_t, "
         "max(produced_by.result_time::TIMESTAMPTZ) as max_t "
         "from samples where produced_by.result_time is not null")
    result = con.sql(q).fetchone()
    if result is not None:
        return TemporalExtent(result[0], result[1])
    return TemporalExtent(None, None)


def load_db_from_jsonl(filename: str, dbcnstr:Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """
    Load the geojson file into the "samples" table in the database specified by dbcnstr.
    Default is to load in a memory database.
    """
    filename = os.path.abspath(filename)
    if dbcnstr is None:
        dbcnstr = ':memory:'
    con = duckdb.connect(dbcnstr)
    con.install_extension("spatial")
    con.load_extension("spatial")
    q = f"SET TimeZone='UTC'; CREATE TABLE samples AS SELECT * FROM read_json(?, format='newline_delimited', ignore_errors=true, columns={SOURCE_COLUMNS});"
    con.execute(q, [filename, ])
    return con
