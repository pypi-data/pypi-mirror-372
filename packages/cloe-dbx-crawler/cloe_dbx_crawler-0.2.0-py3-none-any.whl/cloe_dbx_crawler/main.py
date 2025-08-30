"""
Main entry point for the Databricks crawler CLI application.

This module provides a command-line interface for crawling Databricks instances
and extracting metadata from catalogs, schemas, tables, and columns.
"""

import os
import pathlib
from datetime import datetime
from typing import Annotated

import typer
from cloe_dbx_connector.config import AzureDatabricksConfig
from cloe_dbx_connector.connector import DatabricksConnector
from cloe_logging import LoggerFactory

from cloe_dbx_crawler.crawler import DatabricksCrawler

logger = LoggerFactory.get_logger(handler_types=["console", "file"], filename="databricks_crawler.log")


app = typer.Typer()
timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")


@app.command()
def crawl(
    output_path: Annotated[
        pathlib.Path,
        typer.Option(help="Path to save the crawled output to."),
    ] = pathlib.Path(f"./crawled_metadata/crawl_{timestamp_now}/"),
    ignore_columns: Annotated[
        bool,
        typer.Option(
            help="Ignore columns of tables and just retrieve information about the table itself.",
        ),
    ] = False,
    ignore_tables: Annotated[
        bool,
        typer.Option(
            help="Ignore tables and just retrieve information about the higher level objects.",
        ),
    ] = False,
    catalog_filter: Annotated[
        str | None,  # noqa: UP007
        typer.Option(
            help="Filters catalogs based on defined filter. Is used as regex pattern. \
                If no filter defined, all catalogs (except the system catalog) are retrieved.",
        ),
    ] = None,
) -> None:
    """
    Crawl a Databricks instance and extract metadata to disk.

    This command connects to a Databricks workspace and crawls through catalogs,
    schemas, tables, and columns to extract metadata. The extracted information
    is saved as JSON files in the specified output directory.

    Args:
        output_path: Directory path where the crawled metadata will be saved.
                    Defaults to a timestamped directory under ./crawled_metadata/
        ignore_columns: If True, skips column-level metadata extraction and only
                       retrieves table-level information and above.
        ignore_tables: If True, skips table-level metadata extraction and only
                      retrieves schema-level information and above.
        catalog_filter: Regular expression pattern to filter catalogs by name.
                       If None, all catalogs except system catalogs are crawled.

    Raises:
        ValueError: If the regex pattern in catalog_filter is invalid.
        ConnectionError: If unable to connect to the Databricks workspace.
        PermissionError: If insufficient permissions to access certain resources.

    Example:
        # Crawl all catalogs and save to default location
        python main.py crawl

        # Crawl specific catalogs matching pattern
        python main.py crawl --catalog-filter "prod_.*"

        # Crawl without column details to custom path
        python main.py crawl --ignore-columns --output-path /tmp/metadata/
    """
    host = os.getenv("CLOE_DBX_HOST")
    if not host:
        raise ValueError("CLOE_DBX_HOST environment variable is required")

    config = AzureDatabricksConfig(host=host)
    connector = DatabricksConnector(config)
    client = connector.client

    crawler = DatabricksCrawler(
        client=client, ignore_tables=ignore_tables, ignore_columns=ignore_columns, catalog_filter=catalog_filter
    )
    crawler.crawl(write_to_disk=True, output_path=output_path)


if __name__ == "__main__":
    app()
