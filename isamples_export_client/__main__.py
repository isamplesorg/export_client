import click
import logging
import multiprocessing
import os.path
import time
import typing
import webbrowser
from isamples_export_client.export_client import ExportClient
from isamples_export_client.fastapi_server import FastAPIServer
from isamples_export_client.pqg_converter import convert_isamples_to_pqg


token_option = click.option(
    "-j",
    "--jwt",
    type=str,
    default=None,
    help="The JWT for the authenticated user.",
    required=True
)


def getCurrentPyFolder(pyname: typing.Optional[str] = None) -> str:
    '''Return folder of specified file path.

    By default, returns the path to this script.
    '''
    if pyname is None:
        pyname = __file__
    return os.path.dirname(pyname)


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
@click.option(
    "-t",
    "--title",
    help="Human readable title for the generated STAC collection, if not specified one will be generated.",
)
@click.option(
    "-r",
    "--description",
    help="Human readable description for the generated STAC collection, if not specified one will be generated.",
)
def export(jwt: str, url: str, query: str, destination: str, format: str, title: str, description: str):
    """Export records from iSamples to a local copy.
    """
    client = ExportClient(query, destination, jwt, url, format, title, description)
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
    """Refresh an existing download by re-running the original query.
    """
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
    help=("The location with dataset viewer"),
    default=os.path.join(getCurrentPyFolder(), "ui")
)
@click.option(
    "-b",
    "--browser-dir",
    help=("The location with the stac browser files."),
    default="./stac-browser/dist/"
)
@click.option(
    "-p",
    "--port",
    help=("The port to start the server on."),
    default=8000
)
def server(download_dir: str, ui_dir: str, browser_dir: typing.Optional[str], port: int):
    """Run a local web server to view exported data."""
    def openBrowser():
        url = f"http://localhost:{port}/"
        logging.info(f"Opening browser at {url}...")
        time.sleep(2)
        webbrowser.open(url)

    if browser_dir is not None and not os.path.exists(browser_dir):
        browser_dir = None
    download_dir = os.path.abspath(download_dir)
    server = FastAPIServer(port, download_dir, ui_dir, browser_dir)
    logging.info(f"Starting server on port {port}, ui is available at http://localhost:{port}/")
    opener = multiprocessing.Process(target=openBrowser())
    opener.start()
    server.run()


@main.command("login")
@click.option(
    "-u",
    "--url",
    help="iSamples server URL",
    default="https://central.isample.xyz/isamples_central/"
)
def do_login(url: str):
    """Open a browser to login to the iSamples site.
    """
    url = url.rstrip("/")
    target = f"{url}/manage/login?raw_jwt=true"
    print("Opening for login. When complete, copy the JWT for use with this export client.")
    print('For example: export JWT="$(pbpaste)"')
    webbrowser.open(target)


@main.command("convert-to-pqg")
@click.option(
    "-i",
    "--input",
    "input_file",
    help="Path to input GeoParquet file",
    required=True,
    type=click.Path(exists=True)
)
@click.option(
    "-o",
    "--output",
    "output_file",
    help="Path to output PQG Parquet file",
    required=True,
    type=click.Path()
)
@click.option(
    "-d",
    "--db-path",
    help="Path to DuckDB database file (default: in-memory)",
    default=":memory:"
)
def convert_to_pqg(input_file: str, output_file: str, db_path: str):
    """Convert an iSamples GeoParquet export to PQG format.

    This command converts the nested iSamples data structure into PQG's
    property graph format, decomposing nested objects into separate nodes
    and creating edges to represent relationships.

    Example:
        isample convert-to-pqg -i data.parquet -o data_pqg.parquet
    """
    logging.info(f"Converting {input_file} to PQG format")
    logging.info(f"Output will be written to {output_file}")

    try:
        stats = convert_isamples_to_pqg(input_file, output_file, db_path)

        logging.info("Conversion completed successfully!")
        logging.info("\nGraph Statistics:")
        logging.info("\nNodes by type:")
        for otype, count in stats.get('nodes_by_type', {}).items():
            logging.info(f"  {otype}: {count}")

        logging.info("\nEdges by type:")
        for pred, count in stats.get('edges_by_type', {}).items():
            logging.info(f"  {pred}: {count}")

    except ImportError as e:
        logging.error("PQG library not installed. Install with: pip install pqg")
        raise click.ClickException("PQG library required but not installed")
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        raise


if __name__ == "__main__":
    main()
