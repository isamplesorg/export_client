# Export Client
A CLI for the [iSamples Export Service](https://github.com/isamplesorg/isamples_inabox/blob/develop/docs/export_service.md).

## Authentication
All operations require a JWT.  The process to obtain one is described in [iSamples in a Box Documentation](https://github.com/isamplesorg/isamples_inabox/blob/develop/docs/authentication_and_identifiers.md).

## Usage
```
Usage: export_client_cli.py [OPTIONS]

Options:
  -q, --query TEXT          The solr query to execute.
  -d, --destination TEXT    The destination directory where the downloaded
                            content should be written.
  -r, --refresh-dir TEXT    If specified, will read the manifest.json out of
                            an existing directory and re-execute the query to
                            update results.
  -t, --jwt TEXT            The JWT for the authenticated user.
  -u, --url TEXT            The URL to the iSamples export service.
  -f, --format [jsonl|csv]  The format of the exported content.
  --help                    Show this message and exit.
  ```