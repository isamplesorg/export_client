import click
import logging
from isamples_export_client.export_client import ExportClient


@click.command()
@click.option(
    "-q",
    "--query",
    help="The solr query to execute.",
)
@click.option(
    "-d",
    "--destination",
    help="The destination directory where the downloaded content should be written.",
)
@click.option(
    "-r",
    "--refresh-dir",
    help="If specified, will read the manifest.json out of an existing directory and re-execute the query to update results."
)
@click.option(
    "-t",
    "--jwt", prompt=True,
    help="The JWT for the authenticated user.",
)
@click.option(
    "-u",
    "--url",
    help="The URL to the iSamples export service.",
    default="https://central.isample.xyz/isamples_central/export"
)
@click.option(
    "-f",
    "--format",
    help="The format of the exported content.",
    type=click.Choice(["jsonl", "csv", "geoparquet"], case_sensitive=False),
    default="jsonl"
)
def main(query: str, destination: str, refresh_dir: str, jwt: str, url: str, format: str):
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s", level=logging.INFO)
    if refresh_dir is None:
        client = ExportClient(query, destination, jwt, url, format)
    else:
        client = ExportClient.from_existing_download(refresh_dir, jwt)
    client.perform_full_download()


if __name__ == "__main__":
    main()
