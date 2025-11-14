# iSamples to PQG Conversion Guide

This guide provides detailed information about converting iSamples GeoParquet exports to PQG (Property Graph) format.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Schema Mapping](#schema-mapping)
- [Node Types](#node-types)
- [Edge Types](#edge-types)
- [Working with Converted Data](#working-with-converted-data)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

The PQG converter transforms the hierarchical, nested JSON-like structure of iSamples data into a property graph representation. This transformation enables:

- **Graph-based queries**: Traverse relationships between samples, sampling events, locations, and other entities
- **Network analysis**: Analyze connections between entities using graph algorithms
- **Flexible exploration**: Query the data using SQL, graph traversals, or Python
- **Data integration**: Combine iSamples data with other graph-based datasets

### Why PQG?

PQG (Property Graph in DuckDB) offers several advantages:

- **Simplicity**: Single-table design backed by DuckDB - no complex database setup
- **Performance**: Leverages DuckDB's columnar storage and query optimization
- **Portability**: Export to Parquet for easy sharing and archival
- **Python-native**: Direct integration with Python data science tools
- **SQL-compatible**: Query using familiar SQL syntax

## Installation

### Basic Installation

```bash
# Install export_client with PQG support
pip install "git+https://github.com/isamplesorg/export_client.git[pqg]"
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/isamplesorg/export_client.git
cd export_client

# Install with poetry including PQG extra
poetry install --extras pqg

# Or install PQG separately
poetry add pqg
```

## Quick Start

### 1. Export Data from iSamples

First, export data from iSamples in GeoParquet format:

```bash
# Login to get JWT token
isample login

# Export data (copy JWT from browser)
isample export -j $TOKEN -f geoparquet -d /tmp -q 'source:SMITHSONIAN'
```

### 2. Convert to PQG

Convert the exported GeoParquet file to PQG format:

```bash
isample convert-to-pqg \
  -i /tmp/isamples_export_2025_04_21_16_23_46_geo.parquet \
  -o /tmp/isamples_pqg.parquet \
  -d /tmp/isamples.duckdb
```

### 3. Query the Graph

Use Python to query the converted graph:

```python
from pqg import Graph

# Load the graph
graph = Graph("/tmp/isamples.duckdb")

# Query samples
samples = graph.db.execute("""
    SELECT pid, label, otype
    FROM node
    WHERE otype = 'Sample'
    LIMIT 10
""").fetchall()

for pid, label, otype in samples:
    print(f"{label}: {pid}")
```

## Schema Mapping

The converter maps the nested iSamples structure to a flat graph representation:

### Original iSamples Structure

```json
{
  "sample_identifier": "SMITHSONIAN:12345",
  "label": "Rock sample",
  "description": "Sedimentary rock sample",
  "produced_by": {
    "label": "Field collection 2023",
    "result_time": "2023-06-15",
    "sampling_site": {
      "label": "Grand Canyon",
      "place_name": ["Arizona", "USA"],
      "sample_location": {
        "latitude": 36.1069,
        "longitude": -112.1129,
        "elevation": 2134.5
      }
    }
  },
  "has_specimen_category": [
    {"label": "Rock"}
  ],
  "curation": {
    "label": "Smithsonian NMNH",
    "curation_location": "Washington, DC"
  }
}
```

### Converted PQG Structure

This becomes multiple nodes connected by edges:

```
Sample (SMITHSONIAN:12345)
  |
  +--[produced_by]--> SamplingEvent (event_abc123)
  |                      |
  |                      +--[sampling_site]--> SamplingSite (site_def456)
  |                                               |
  |                                               +--[sample_location]--> Location (location_ghi789)
  |
  +--[has_specimen_category]--> Category (category_specimen_rock)
  |
  +--[curation]--> Curation (curation_jkl012)
```

## Node Types

### Sample

**Purpose**: Represents a physical sample

**Fields**:
- `pid`: sample_identifier (e.g., "SMITHSONIAN:12345")
- `label`: Human-readable sample name
- `description`: Extended description
- `keywords`: Array of keyword strings
- `informal_classification`: Array of classification terms
- `source_collection`: Source collection identifier

**Example Query**:
```sql
SELECT * FROM node WHERE otype = 'Sample' LIMIT 10;
```

### SamplingEvent

**Purpose**: Represents the event that produced the sample

**Fields**:
- `pid`: Generated hash-based identifier (e.g., "event_a1b2c3d4e5f6")
- `label`: Event name
- `description`: Event description
- `identifier`: External identifier for the event
- `result_time`: Date/time when sample was collected

**Example Query**:
```sql
SELECT * FROM node WHERE otype = 'SamplingEvent';
```

### SamplingSite

**Purpose**: Represents the geographic site where sampling occurred

**Fields**:
- `pid`: Generated hash-based identifier
- `label`: Site name
- `description`: Site description
- `place_names`: Array of place name strings

**Example Query**:
```sql
SELECT label, place_names FROM node WHERE otype = 'SamplingSite';
```

### Location

**Purpose**: Represents precise geographic coordinates

**Fields**:
- `pid`: Generated hash-based identifier
- `label`: Auto-generated label with coordinates
- `latitude`: Decimal degrees
- `longitude`: Decimal degrees
- `elevation`: Meters above sea level

**Example Query**:
```sql
SELECT label, latitude, longitude, elevation
FROM node
WHERE otype = 'Location'
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL;
```

### Category

**Purpose**: Represents classification categories

**Fields**:
- `pid`: Derived from category type and label (e.g., "category_specimen_rock")
- `label`: Category name
- `category_type`: One of 'specimen', 'material', or 'context'

**Example Query**:
```sql
SELECT category_type, label, COUNT(*) as usage_count
FROM node
WHERE otype = 'Category'
GROUP BY category_type, label
ORDER BY usage_count DESC;
```

### Curation

**Purpose**: Represents curation and storage information

**Fields**:
- `pid`: Generated hash-based identifier
- `label`: Curation label
- `description`: Curation description
- `curation_location`: Physical location
- `access_constraints`: Array of constraint strings

**Example Query**:
```sql
SELECT label, curation_location FROM node WHERE otype = 'Curation';
```

### Agent

**Purpose**: Represents people or organizations

**Fields**:
- `pid`: Generated hash-based identifier
- `label`: Agent name
- `name`: Agent name
- `role`: Role in context (e.g., 'collector', 'registrant')

**Example Query**:
```sql
SELECT DISTINCT name, role FROM node WHERE otype = 'Agent';
```

## Edge Types

### produced_by

- **From**: Sample
- **To**: SamplingEvent
- **Meaning**: This sample was produced by this sampling event

### sampling_site

- **From**: SamplingEvent
- **To**: SamplingSite
- **Meaning**: The event occurred at this site

### sample_location

- **From**: SamplingSite
- **To**: Location
- **Meaning**: The site is at these geographic coordinates

### has_specimen_category

- **From**: Sample
- **To**: Category (category_type='specimen')
- **Meaning**: Sample is classified with this specimen category

### has_material_category

- **From**: Sample
- **To**: Category (category_type='material')
- **Meaning**: Sample is classified with this material category

### has_context_category

- **From**: Sample
- **To**: Category (category_type='context')
- **Meaning**: Sample is classified with this context category

### curation

- **From**: Sample
- **To**: Curation
- **Meaning**: Sample has this curation information

### registrant

- **From**: Sample
- **To**: Agent
- **Meaning**: Sample was registered by this agent

### responsibility_*

- **From**: SamplingEvent
- **To**: Agent
- **Meaning**: Agent has this role in the event (e.g., responsibility_collector)

## Working with Converted Data

### Basic Queries

#### Find samples by location

```sql
SELECT
    s.label as sample_label,
    loc.latitude,
    loc.longitude
FROM node s
JOIN node edge1 ON s.pid = edge1.s AND edge1.p = 'produced_by'
JOIN node event ON edge1.o[1] = event.row_id
JOIN node edge2 ON event.pid = edge2.s AND edge2.p = 'sampling_site'
JOIN node site ON edge2.o[1] = site.row_id
JOIN node edge3 ON site.pid = edge3.s AND edge3.p = 'sample_location'
JOIN node loc ON edge3.o[1] = loc.row_id
WHERE s.otype = 'Sample'
  AND loc.latitude BETWEEN 35.0 AND 37.0
  AND loc.longitude BETWEEN -113.0 AND -111.0;
```

#### Count samples by category

```sql
SELECT
    cat.label,
    COUNT(DISTINCT s.row_id) as sample_count
FROM node cat
JOIN node edge ON cat.row_id = ANY(edge.o)
JOIN node s ON edge.s = s.pid
WHERE cat.otype = 'Category'
  AND cat.category_type = 'specimen'
  AND s.otype = 'Sample'
GROUP BY cat.label
ORDER BY sample_count DESC;
```

#### Find all information about a specific sample

```sql
-- Get the sample
SELECT * FROM node WHERE pid = 'SMITHSONIAN:12345';

-- Get all outgoing edges
SELECT p, o FROM node WHERE s = 'SMITHSONIAN:12345';

-- Get related nodes
SELECT n.*
FROM node edge
JOIN node n ON edge.o[1] = n.row_id
WHERE edge.s = 'SMITHSONIAN:12345';
```

### Using PQG Python API

```python
from pqg import Graph

# Load graph
graph = Graph("isamples.duckdb")

# Get a sample
sample = graph.getNode("SMITHSONIAN:12345")
print(f"Sample: {sample.label}")

# Get related sampling event
events = graph.getRelations("SMITHSONIAN:12345", "produced_by")
if events:
    event = graph.getNode(events[0])
    print(f"Produced by: {event.label}")

# Get all samples of a certain type
samples = graph.db.execute("""
    SELECT s.*
    FROM node s
    JOIN node edge ON s.pid = edge.s
    JOIN node cat ON edge.o[1] = cat.row_id
    WHERE s.otype = 'Sample'
      AND edge.p = 'has_specimen_category'
      AND cat.label = 'Rock'
""").fetchdf()

print(f"Found {len(samples)} rock samples")
```

### Export Options

#### Export to Parquet

```python
graph.toParquet("isamples_subset.parquet")
```

#### Export to GeoJSON (for locations)

```python
# Export locations as GeoJSON
locations = graph.db.execute("""
    SELECT
        pid,
        label,
        longitude,
        latitude
    FROM node
    WHERE otype = 'Location'
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
""").fetchdf()

# Convert to GeoDataFrame
import geopandas as gpd
from shapely.geometry import Point

geometry = [Point(lon, lat) for lon, lat in zip(locations.longitude, locations.latitude)]
gdf = gpd.GeoDataFrame(locations, geometry=geometry, crs="EPSG:4326")
gdf.to_file("locations.geojson", driver="GeoJSON")
```

## Advanced Usage

### Programmatic Conversion

```python
from isamples_export_client.pqg_converter import ISamplesPQGConverter

# Create converter
converter = ISamplesPQGConverter(db_path="isamples.duckdb")

# Convert file
converter.convert_parquet_to_pqg(
    "input.parquet",
    "output_pqg.parquet"
)

# Get statistics
stats = converter.get_stats()
print(f"Created {sum(stats['nodes_by_type'].values())} nodes")
print(f"Created {sum(stats['edges_by_type'].values())} edges")

# Access the graph directly
graph = converter.graph

# Run custom queries
result = graph.db.execute("""
    SELECT COUNT(*) FROM node WHERE otype = 'Sample'
""").fetchone()[0]

print(f"Total samples: {result}")
```

### Batch Processing

```python
import glob
from pathlib import Path
from isamples_export_client.pqg_converter import convert_isamples_to_pqg

# Convert multiple files
parquet_files = glob.glob("/data/*.parquet")

for input_file in parquet_files:
    output_file = Path(input_file).stem + "_pqg.parquet"
    print(f"Converting {input_file}...")

    stats = convert_isamples_to_pqg(
        input_file,
        output_file,
        db_path=":memory:"
    )

    print(f"  Nodes: {sum(stats['nodes_by_type'].values())}")
    print(f"  Edges: {sum(stats['edges_by_type'].values())}")
```

### Custom Graph Analysis

```python
from pqg import Graph
import networkx as nx

# Load PQG graph
graph = Graph("isamples.duckdb")

# Export to NetworkX for analysis
edges = graph.db.execute("""
    SELECT s, p, o[1] as target
    FROM node
    WHERE s IS NOT NULL
""").fetchall()

# Create NetworkX directed graph
G = nx.DiGraph()
for source, predicate, target in edges:
    G.add_edge(source, target, relationship=predicate)

# Analyze
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")

# Find most connected nodes
top_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
for node, degree in top_nodes:
    print(f"  {node}: {degree} connections")
```

## Troubleshooting

### "PQG library not available" Error

**Problem**: PQG is not installed

**Solution**:
```bash
pip install pqg
# or
poetry add pqg
```

### Memory Issues with Large Files

**Problem**: Conversion runs out of memory

**Solution**: Use a persistent database file instead of in-memory:
```bash
isample convert-to-pqg \
  -i large_file.parquet \
  -o output.parquet \
  -d /path/to/persistent.duckdb
```

### Missing or Null Values

**Problem**: Some nodes have NULL values for expected fields

**Explanation**: The iSamples data is sparse - not all samples have all fields populated. The converter preserves this sparsity.

**Solution**: Use SQL COALESCE or NULL checks in queries:
```sql
SELECT
    COALESCE(description, 'No description') as description
FROM node
WHERE otype = 'Sample';
```

### Duplicate Nodes

**Problem**: Worried about duplicate nodes being created

**Explanation**: The converter uses content-based hashing for non-Sample nodes to ensure the same entity (e.g., same location coordinates) creates only one node, even if referenced by multiple samples.

### Performance Issues

**Problem**: Queries are slow

**Solutions**:
1. Create indexes:
```python
graph.db.execute("CREATE INDEX idx_otype ON node(otype)")
graph.db.execute("CREATE INDEX idx_s ON node(s)")
```

2. Use views for common queries:
```python
graph.db.execute("""
    CREATE VIEW sample_locations AS
    SELECT
        s.pid, s.label,
        loc.latitude, loc.longitude
    FROM node s
    JOIN node e1 ON s.pid = e1.s AND e1.p = 'produced_by'
    JOIN node ev ON e1.o[1] = ev.row_id
    JOIN node e2 ON ev.pid = e2.s AND e2.p = 'sampling_site'
    JOIN node site ON e2.o[1] = site.row_id
    JOIN node e3 ON site.pid = e3.s AND e3.p = 'sample_location'
    JOIN node loc ON e3.o[1] = loc.row_id
    WHERE s.otype = 'Sample'
""")
```

## Further Resources

- [PQG Documentation](https://github.com/isamplesorg/pqg)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [iSamples Export Service](https://github.com/isamplesorg/isamples_inabox/blob/develop/docs/export_service.md)
- [GeoParquet Specification](https://geoparquet.org/)

## Contributing

If you encounter issues or have suggestions for improving the PQG converter, please:

1. Check existing issues: https://github.com/isamplesorg/export_client/issues
2. Create a new issue with details about your use case
3. Submit pull requests with improvements

## License

Apache 2.0
