import logging
import os.path

import pandas as pd
import geopandas as gpd


def write_geoparquet_from_json_lines(filename: str) -> str:
    logging.info(f"Transforming json lines file at {filename} to geoparquet")
    filename_no_extension = os.path.splitext(filename)[0]
    with open(filename, "r") as json_file:
        df = pd.read_json(json_file, lines=True)
        normalized_produced_by = pd.json_normalize(df["produced_by"])
        df["sample_location_longitude"] = normalized_produced_by["sampling_site.sample_location.longitude"]
        df["sample_location_latitude"] = normalized_produced_by["sampling_site.sample_location.latitude"]
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(
                df.sample_location_longitude,
                df.sample_location_latitude),
            crs="EPSG:4326"
        )

    dest_file = f"{filename_no_extension}_geo.parquet"
    gdf.to_parquet(dest_file)
    logging.info(f"Wrote geoparquet file to {dest_file}")
    return dest_file
