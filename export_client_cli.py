import click
import logging
from isamples_export_client.export_client import ExportClient
from isamples_export_client.fastapi_server import FastAPIServer

token_option = click.option(
    "-t",
    "--jwt",
    type=str,
    default=None,
    help="The JWT for the authenticated user.",
    required=True
)


@click.group()
def main():
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s", level=logging.INFO)

@main.command("export")
@token_option
@click.option(
    "-u",
    "--url",
    help="The URL to the iSamples export service.",
    default="https://central.isample.xyz/isamples_central/export"
)
@click.option(
    "-q",
    "--query",
    help="The solr query to execute.",
    required=True
)
@click.option(
    "-d",
    "--destination",
    help="The destination directory where the downloaded content should be written.",
    required=True
)
@click.option(
    "-f",
    "--format",
    help="The format of the exported content.",
    type=click.Choice(["jsonl", "csv", "geoparquet"], case_sensitive=False),
    default="jsonl"
)
def export(jwt: str, url: str, query: str, destination: str, format: str):
    client = ExportClient(query, destination, jwt, url, format)
    client.perform_full_download()


@main.command("refresh")
@token_option
@click.option(
    "-r",
    "--refresh-dir",
    help=("If specified, will read the manifest.json out of an existing "
          "directory and re-execute the query to update results.")
)
def refresh(jwt: str, refresh_dir: str):
    client = ExportClient.from_existing_download(refresh_dir, jwt)
    logging.info(f"Going to refresh existing download at {refresh_dir}")
    client.perform_full_download()


@main.command("server")
@click.option(
    "-d",
    "--download-dir",
    help=("The location to read downloaded content from."),
    required=True
)
@click.option(
    "-u",
    "--ui-dir",
    help=("The location with the downloaded files."),
    default="./ui/"
)
@click.option(
    "-p",
    "--port",
    help=("The port to start the server on."),
    default=8000
)
def server(download_dir: str, ui_dir: str, port: int):
    server = FastAPIServer(port, download_dir, ui_dir)
    logging.info(f"Starting server on port {port}, ui is available at http://localhost:{port}/ui/index.html")
    server.run()


if __name__ == "__main__":
    main()
