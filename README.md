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