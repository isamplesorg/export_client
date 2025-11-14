# Export Client
Provides the command line client `isample` for retrieving content from the [iSamples Export Service](https://github.com/isamplesorg/isamples_inabox/blob/develop/docs/export_service.md).

```
Usage: isample [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  export   Export records from iSamples to a local copy.
  login    Open a browser to login to the iSamples site.
  refresh  Refresh an existing download by re-running the original query.
  server   Run a local web server to view exported data.
```

## Installation

The iSample client is currently under active development and the sources will be updated frequently.

The iSample client may be installed using `pipx`:

```
pipx install "git+https://github.com/isamplesorg/export_client.git"
```

or from a specific branch:

```
pipx install "git+https://github.com/isamplesorg/export_client.git@local_ui"
```

Alternatively, checkout the source from GitHub and install to a virtual environment using Poetry:

```
git clone https://github.com/isamplesorg/export_client.git
cd export_client
poetry install
poetry run isample
```


## login

```
Usage: isample login [OPTIONS]

  Open a browser to login to the iSamples site.

Options:
  -u, --url TEXT  iSamples server URL
  --help          Show this message and exit.
```

All data retrieval operations require a JWT which may be retrieved using
the `isample login` command or through the process described in [iSamples in a Box Documentation](https://github.com/isamplesorg/isamples_inabox/blob/develop/docs/authentication_and_identifiers.md).

The `login` command will open a browser to the iSamples ORCID authentication page and after authentication,
presents the raw JWT which may be copied and used for export and refresh operations.

After selecting and copying the JWT to the clipboard, the JWT can be assigned to an environment variable
for convenience. For example (on OS X):

```
export TOKEN="$(pbpaste)"
```

The JWT is then available for use in the same shell as the environment variable `${JWT}`.

## export

```
Usage: isample export [OPTIONS]

  Export records from iSamples to a local copy.

Options:
  -j, --jwt TEXT                  The JWT for the authenticated user.
                                  [required]
  -u, --url TEXT                  The URL to the iSamples export service.
  -q, --query TEXT                The solr query to execute.  [required]
  -d, --destination TEXT          The destination directory where the
                                  downloaded content should be written.
                                  [required]
  -f, --format [jsonl|csv|geoparquet]
                                  The format of the exported content.
  -t, --title TEXT                Human readable title for the generated STAC
                                  collection, if not specified one will be
                                  generated.
  -r, --description TEXT          Human readable description for the generated
                                  STAC collection, if not specified one will
                                  be generated.
  --help                          Show this message and exit.
```

The `isample export` command initiates retrieval of a subset of content from the iSamples central 
aggregation of physical specimen records. The subset of records is determined by a query which 
is expressed in Lucene or Solr query syntax. The query may be manually crafted or retrieved
from the iSamples web UI by navigating to the subset of interest and clicking on the `Export`.

For example, the following command initiates the retrieval of all the Smithsonian records in 
`geoparquet` format for the destination directory `/tmp`, using the JWT token in the `TOKEN` environment variable.

```
isample export -j $TOKEN -f geoparquet -d /tmp -q 'source:SMITHSONIAN'
```

## convert-to-pqg

```
Usage: isample convert-to-pqg [OPTIONS]

  Convert an iSamples GeoParquet export to PQG format.

  This command converts the nested iSamples data structure into PQG's
  property graph format, decomposing nested objects into separate nodes and
  creating edges to represent relationships.

Options:
  -i, --input PATH   Path to input GeoParquet file  [required]
  -o, --output PATH  Path to output PQG Parquet file  [required]
  -d, --db-path TEXT Path to DuckDB database file (default: in-memory)
  --help             Show this message and exit.
```

### What is PQG?

[PQG](https://github.com/isamplesorg/pqg) (Property Graph in DuckDB) is a Python library for constructing and querying property graphs using DuckDB as the backend. It provides a middle ground between full-featured graph databases and traditional relational databases.

### Installation with PQG Support

To use the PQG conversion feature, install the export client with PQG support:

```bash
# Using pipx
pipx install "git+https://github.com/isamplesorg/export_client.git[pqg]"

# Or using poetry
poetry install --extras pqg

# Or install pqg separately
pip install pqg
```

### How the Conversion Works

The converter transforms the nested iSamples data structure into a property graph by:

1. **Creating nodes** for each distinct entity:
   - Sample (main entity)
   - SamplingEvent (from `produced_by`)
   - SamplingSite (from `produced_by.sampling_site`)
   - Location (from geographic coordinates)
   - Category (from `has_*_category` fields)
   - Curation (from `curation`)
   - Agent (from `registrant` and `responsibility`)

2. **Creating edges** to represent relationships:
   - Sample → SamplingEvent (produced_by)
   - SamplingEvent → SamplingSite (sampling_site)
   - SamplingSite → Location (sample_location)
   - Sample → Category (has_specimen_category, has_material_category, has_context_category)
   - Sample → Curation (curation)
   - Sample → Agent (registrant)

3. **Preserving properties**: All relevant fields from the original data are preserved as node properties.

### Example Usage

Convert a GeoParquet export to PQG format:

```bash
# First, export data in geoparquet format
isample export -j $TOKEN -f geoparquet -d /tmp -q 'source:SMITHSONIAN'

# Then convert to PQG format
isample convert-to-pqg \
  -i /tmp/isamples_export_2025_04_21_16_23_46_geo.parquet \
  -o /tmp/isamples_pqg.parquet

# Optional: specify a persistent database file
isample convert-to-pqg \
  -i /tmp/isamples_export_2025_04_21_16_23_46_geo.parquet \
  -o /tmp/isamples_pqg.parquet \
  -d /tmp/isamples.duckdb
```

The conversion process will:
- Read the GeoParquet file
- Decompose nested structures into nodes and edges
- Create a PQG-compatible Parquet file
- Display statistics about the created graph (node counts by type, edge counts by predicate)

### Using the PQG Output

Once converted, you can use the PQG Python library to query and analyze the graph:

```python
from pqg import Graph

# Load the converted data
graph = Graph("isamples.duckdb")
graph.loadMetadata("isamples_pqg.parquet")

# Query samples
samples = graph.getNodesByType("Sample")

# Traverse relationships
for sample in samples[:10]:
    # Get the sampling event
    events = graph.getRelations(sample.pid, "produced_by")
    if events:
        event = graph.getNode(events[0])
        print(f"Sample {sample.label} was produced by {event.label}")
```

For more information about working with PQG, see the [PQG documentation](https://github.com/isamplesorg/pqg).

### Schema Mapping Reference

The converter provides **lossless conversion** - all iSamples fields are preserved in PQG:

| iSamples Field | PQG Mapping | Notes |
|---|---|---|
| sample_identifier | Sample (pid) | Used as the unique identifier |
| label | Sample (label) | Human-readable name |
| description | Sample (description) | Extended description |
| alternate_identifiers | Sample (altids) | Uses PQG's built-in altids field |
| produced_by | SamplingEvent node | Connected via produced_by edge |
| sampling_purpose | Sample property | Why sample was collected |
| produced_by.sampling_site | SamplingSite node | Nested decomposition |
| sampling_site.sample_location | Location node | Geographic coordinates (lat/lon/elevation) |
| has_specimen_category | Category nodes | Multiple edges created |
| has_material_category | Category nodes | Multiple edges created |
| has_context_category | Category nodes | Multiple edges created |
| keywords | Sample property | Stored as array |
| related_resource | RelatedResource nodes | Separate nodes with typed edges |
| complies_with | Sample property | Standards followed (array) |
| dc_rights | Sample property | Rights statement |
| curation | Curation node | Connected via curation edge |
| registrant | Agent node | Connected via registrant edge |
| informal_classification | Sample property | Stored as array |
| geometry | Sample property | Stored as WKT in geometry_wkt |
| source_collection | Named graph (n) | Used for organizational grouping |

**Note**: The converter creates 8 node types (Sample, SamplingEvent, SamplingSite, Location, Category, Curation, Agent, RelatedResource) and preserves all relationships through typed edges. All data from the GeoParquet export is preserved.