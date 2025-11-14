#!/usr/bin/env python3
"""
Example script demonstrating how to convert iSamples GeoParquet exports to PQG format.

This example shows how to:
1. Convert a GeoParquet file to PQG format
2. Query the resulting graph using PQG
3. Analyze the graph structure

Usage:
    python convert_to_pqg_example.py <input_parquet_file>
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    format="%(levelname)s %(asctime)s %(message)s",
    level=logging.INFO
)

try:
    from isamples_export_client.pqg_converter import convert_isamples_to_pqg
    from pqg import Graph
except ImportError as e:
    logging.error("Required libraries not installed.")
    logging.error("Install with: pip install pqg")
    logging.error(f"Error: {e}")
    sys.exit(1)


def main(input_file: str):
    """
    Convert an iSamples GeoParquet file to PQG and demonstrate basic queries.

    Args:
        input_file: Path to input GeoParquet file
    """
    # Define output paths
    input_path = Path(input_file)
    output_file = str(input_path.parent / f"{input_path.stem}_pqg.parquet")
    db_file = str(input_path.parent / f"{input_path.stem}.duckdb")

    logging.info(f"Converting {input_file} to PQG format")
    logging.info(f"Output: {output_file}")
    logging.info(f"Database: {db_file}")

    # Perform conversion
    stats = convert_isamples_to_pqg(input_file, output_file, db_file)

    # Display statistics
    print("\n" + "="*60)
    print("CONVERSION STATISTICS")
    print("="*60)

    print("\nNodes by type:")
    for otype, count in stats.get('nodes_by_type', {}).items():
        print(f"  {otype:20s}: {count:>6,}")

    print("\nEdges by type:")
    for pred, count in stats.get('edges_by_type', {}).items():
        print(f"  {pred:30s}: {count:>6,}")

    # Load and query the graph
    print("\n" + "="*60)
    print("SAMPLE QUERIES")
    print("="*60)

    graph = Graph(db_file)

    # Example 1: Get all samples
    print("\n1. First 5 samples:")
    result = graph.db.execute("""
        SELECT pid, label, otype
        FROM node
        WHERE otype = 'Sample'
        LIMIT 5
    """).fetchall()

    for pid, label, otype in result:
        print(f"   - {label[:50]:50s} ({pid})")

    # Example 2: Get samples with their sampling events
    print("\n2. Samples with sampling events:")
    result = graph.db.execute("""
        SELECT
            s.pid as sample_pid,
            s.label as sample_label,
            e.pid as event_pid,
            e.label as event_label
        FROM node s
        JOIN node edge ON s.pid = edge.s
        JOIN node e ON edge.o[1] = e.row_id
        WHERE s.otype = 'Sample'
          AND edge.p = 'produced_by'
          AND e.otype = 'SamplingEvent'
        LIMIT 5
    """).fetchall()

    for sample_pid, sample_label, event_pid, event_label in result:
        print(f"   - Sample: {sample_label[:40]:40s}")
        print(f"     Event:  {event_label[:40]:40s}")
        print()

    # Example 3: Get samples with locations
    print("\n3. Samples with geographic locations:")
    result = graph.db.execute("""
        SELECT
            s.label as sample_label,
            loc.latitude,
            loc.longitude,
            loc.elevation
        FROM node s
        JOIN node edge1 ON s.pid = edge1.s
        JOIN node event ON edge1.o[1] = event.row_id
        JOIN node edge2 ON event.pid = edge2.s
        JOIN node site ON edge2.o[1] = site.row_id
        JOIN node edge3 ON site.pid = edge3.s
        JOIN node loc ON edge3.o[1] = loc.row_id
        WHERE s.otype = 'Sample'
          AND event.otype = 'SamplingEvent'
          AND site.otype = 'SamplingSite'
          AND loc.otype = 'Location'
          AND loc.latitude IS NOT NULL
          AND loc.longitude IS NOT NULL
        LIMIT 5
    """).fetchall()

    for label, lat, lon, elev in result:
        elev_str = f"{elev:.1f}m" if elev is not None else "N/A"
        print(f"   - {label[:40]:40s}")
        print(f"     Location: ({lat:.4f}, {lon:.4f}), Elevation: {elev_str}")
        print()

    # Example 4: Count samples by category type
    print("\n4. Sample counts by category:")
    for cat_type in ['specimen', 'material', 'context']:
        result = graph.db.execute(f"""
            SELECT
                cat.label,
                COUNT(DISTINCT s.row_id) as sample_count
            FROM node cat
            JOIN node edge ON cat.row_id = ANY(edge.o)
            JOIN node s ON edge.s = s.pid
            WHERE cat.otype = 'Category'
              AND cat.category_type = '{cat_type}'
              AND s.otype = 'Sample'
            GROUP BY cat.label
            ORDER BY sample_count DESC
            LIMIT 5
        """).fetchall()

        print(f"\n   Top {cat_type} categories:")
        for label, count in result:
            print(f"      {label:30s}: {count:>6,} samples")

    print("\n" + "="*60)
    print("Example queries completed successfully!")
    print("="*60)
    print(f"\nDatabase file saved at: {db_file}")
    print(f"You can explore this graph further using PQG or DuckDB.")
    print("\nExample Python usage:")
    print("  from pqg import Graph")
    print(f"  graph = Graph('{db_file}')")
    print("  samples = graph.db.execute('SELECT * FROM node WHERE otype = \\'Sample\\' LIMIT 10').fetchall()")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_to_pqg_example.py <input_parquet_file>")
        print("\nExample:")
        print("  python convert_to_pqg_example.py /tmp/isamples_export_2025_04_21_16_23_46_geo.parquet")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    main(input_file)
