"""
Databricks metadata crawler for extracting catalog, schema, table, and column information.

This module provides the DatabricksCrawler class which connects to Databricks workspaces
and systematically extracts metadata from catalogs, schemas, tables, and columns.
The extracted metadata is stored in CLOE metadata format for further processing.
"""

import re
import uuid
from pathlib import Path

from cloe_logging import LoggerFactory
from cloe_metadata import base
from cloe_metadata.base.repository.database.column import Column
from cloe_metadata.base.repository.database.database import Database, Databases
from cloe_metadata.base.repository.database.schema import Schema
from cloe_metadata.base.repository.database.table import Table
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import CatalogInfo, SchemaInfo, TableInfo

logger = LoggerFactory.get_logger(handler_types=["console", "file"], filename="databricks_crawler.log")


class DatabricksCrawler:
    """
    A simple metadata crawler for Databricks workspaces.

    This class extracts metadata from Databricks workspaces by crawling through
    catalogs, schemas, tables, and columns. It provides flexible filtering options
    and can output results in CLOE metadata format either to disk or in memory.

    Attributes:
        client: WorkspaceClient instance for connecting to Databricks
        ignore_tables: If True, skips table-level metadata extraction
        ignore_columns: If True, skips column-level metadata extraction
        default_catalogs_to_ignore: Set of catalog names to always ignore
        catalog_filter: User-provided regex pattern for filtering catalogs
        catalog_regex: Compiled regex pattern for catalog filtering
        databases: Collection of extracted database metadata

    Example usage:
        >>> from databricks.sdk import WorkspaceClient
        >>> client = WorkspaceClient()
        >>> crawler = DatabricksCrawler(client=client, catalog_filter="prod_.*")
        >>> crawler.crawl(write_to_disk=True, output_path=Path("/tmp/metadata"))
    """

    client: WorkspaceClient
    ignore_tables: bool = False
    ignore_columns: bool = False
    default_catalogs_to_ignore: set[str] = {"system", "samples"}
    catalog_filter: str | None = None  # User-provided pattern
    catalog_regex: re.Pattern | None = None  # Compiled regex
    databases: base.Databases = base.Databases(databases=[])

    def __init__(
        self,
        client: WorkspaceClient,
        ignore_tables: bool = False,
        ignore_columns: bool = False,
        catalog_filter: str | None = None,
    ):
        """
        Initialize the DatabricksCrawler with configuration options.

        Args:
            client: Authenticated WorkspaceClient for Databricks API access
            ignore_tables: If True, skip table metadata extraction (default: False)
            ignore_columns: If True, skip column metadata extraction (default: False)
            catalog_filter: Regex pattern to filter catalogs by name (default: None)

        Raises:
            ValueError: If the provided catalog_filter is not a valid regex pattern

        Note:
            When ignore_tables is True, ignore_columns is automatically ignored
            since columns cannot exist without tables.
        """
        self.client = client
        self.ignore_tables = ignore_tables
        self.ignore_columns = ignore_columns
        self.catalog_filter = catalog_filter

        # Compile regex if a catalog pattern is provided
        if self.catalog_filter:
            try:
                self.catalog_regex = re.compile(self.catalog_filter, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern provided: {self.catalog_filter} - {e}") from e
        else:
            self.catalog_regex = None

    def crawl(self, write_to_disk: bool = True, output_path: Path | None = None) -> None:
        """
        Execute the complete metadata crawling process.

        This method orchestrates the entire crawling workflow, from connecting to
        Databricks to extracting metadata and optionally writing results to disk.

        Args:
            write_to_disk: If True, write extracted metadata to disk (default: True)
            output_path: Directory path for output files (required if write_to_disk=True)

        Raises:
            ValueError: If write_to_disk=True but output_path is None or not a directory
            PermissionError: If insufficient permissions to create output directory
            ConnectionError: If unable to connect to Databricks workspace

        Note:
            The output directory will be created if it doesn't exist.
            Existing files in the output directory may be overwritten.
        """
        if write_to_disk:
            logger.info("Prepare writing to disk.")
            if not output_path:
                logger.error("Please provide an output path to store the crawled metadata.")
                return

            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_path}")
            else:
                if not output_path.is_dir():
                    raise ValueError(f"The provided output path {output_path} is not a directory.")

        logger.info("Start crawling...")
        self.databases = Databases(databases=self._process_catalogs())
        logger.info("Finished crawling.")

        if write_to_disk:
            logger.info("Writing to disk...")
            self.databases.write_to_disk(output_path=output_path, delete_existing=True)  # type: ignore[arg-type]
            logger.info(f"Crawler output is now stored at: {output_path}")

    def _process_catalogs(self) -> list[Database]:
        """
        Fetch and process all catalogs from the Databricks workspace.

        This method retrieves all available catalogs, applies filtering based on
        the catalog_filter regex pattern, and processes each matching catalog
        to extract its metadata including schemas.

        Returns:
            List of Database objects representing the processed catalogs

        Note:
            System catalogs and catalogs in default_catalogs_to_ignore are automatically skipped.
            Catalogs without names are logged as warnings and skipped.
        """
        catalogs: list[Database] = []
        for catalog in self.client.catalogs.list():
            if not catalog.name:
                logger.warning("Catalog name is None, skipping this catalog.")
                continue

            # Regex filtering, skip system catalog and those that do not match the provided filter pattern
            if catalog.name in self.default_catalogs_to_ignore or (
                self.catalog_regex and not self.catalog_regex.match(catalog.name)
            ):
                continue

            # Retrieve catalog UUID from storage location
            catalog_id = self._get_catalog_uuid_from_storage_location(catalog.name)

            # Process schemas in the catalog and retrieve their metadata
            schemas: list[Schema] = self._process_schemas(catalog)

            # Create a CLOE Database instance for each catalog
            catalogs.append(
                Database(
                    id=catalog_id,
                    display_name=None,
                    name=catalog.name,
                    schemas=schemas,
                )
            )
        return catalogs

    def _process_schemas(self, catalog: CatalogInfo) -> list[Schema]:
        """
        Fetch and process all schemas within a specific catalog.

        Args:
            catalog: CatalogInfo object representing the parent catalog

        Returns:
            List of Schema objects representing the processed schemas

        Note:
            Schemas without names are logged as warnings and skipped.
            If a schema ID is missing, a UUID is generated automatically.
        """
        schemas: list[Schema] = []
        for schema in self.client.schemas.list(catalog.name):  # type: ignore[arg-type]
            # Check schema name and ID validity
            if not schema.name:
                logger.warning("Schema name is None, skipping this schema.")
                continue
            try:
                schema_id = uuid.UUID(schema.schema_id)
            except (AttributeError, TypeError, ValueError):
                logger.warning(f"Schema ID for schema {schema.name} is None, generating a UUID for this schema.")
                schema_id = uuid.uuid4()

            # Process tables within the schema and retrieve their metadata
            tables: list[Table] = self._process_tables(catalog, schema)

            # Create a CLOE Schema instance for each schema
            schemas.append(Schema(id=schema_id, name=schema.name, tables=tables))
        return schemas

    def _process_tables(self, catalog: CatalogInfo, schema: SchemaInfo) -> list[Table]:
        """
        Fetch and process all tables within a specific schema.

        Args:
            catalog: CatalogInfo object representing the parent catalog
            schema: SchemaInfo object representing the parent schema

        Returns:
            List of Table objects representing the processed tables

        Note:
            If ignore_tables is True, returns an empty list.
            Tables without names are logged as warnings and skipped.
            If a table ID is missing, a UUID is generated automatically.
        """
        tables: list[Table] = []
        if not self.ignore_tables:
            for table in self.client.tables.list(catalog.name, schema.name):  # type: ignore[arg-type]
                # Check table name and ID validity
                if not table.name:
                    logger.warning("Table name is None, skipping this table.")
                    continue
                try:
                    table_id = uuid.UUID(table.table_id)
                except (AttributeError, TypeError, ValueError):
                    logger.warning(f"Table ID for table {table.name} is None, generating a UUID for this table.")
                    table_id = uuid.uuid4()

                # Process columns of the table and retrieve their metadata
                columns: list[Column] = self._process_columns(table)

                # Create a CLOE Table instance for each table
                tables.append(Table(id=table_id, level=None, name=table.name, columns=columns))
        return tables

    def _process_columns(self, table: TableInfo) -> list[Column]:
        """
        Fetch and process all columns within a specific table.

        Args:
            table: TableInfo object representing the parent table

        Returns:
            List of Column objects representing the processed columns

        Note:
            If ignore_columns is True, returns an empty list.
            Tables without column information are logged as warnings.
            Columns without names or data types are logged as warnings and skipped.
        """
        columns: list[Column] = []
        if not self.ignore_columns:
            if not table.columns:
                logger.warning(f"No columns found for table {table.name}. Skipping column processing.")
                return columns

            for column in table.columns:
                # Check column name and data type validity
                if not column.name:
                    logger.warning("Column name is None, skipping this column.")
                    continue
                if not column.type_text:
                    logger.warning("Column data type is None, skipping this column.")
                    continue

                # Create a CLOE Column instance for each column
                columns.append(
                    Column(
                        comment=column.comment,
                        constraints=None,
                        data_type=column.type_text,
                        data_type_length=None,
                        data_type_numeric_scale=column.type_scale,
                        data_type_precision=column.type_precision,
                        is_key=None,
                        is_nullable=column.nullable,
                        labels=None,
                        name=column.name,
                        ordinal_position=None,
                    )
                )
        return columns

    def _get_catalog_uuid_from_storage_location(self, catalog_name: str) -> uuid.UUID:
        """
        Extract the catalog UUID from its storage location path.

        This method retrieves the catalog's storage location and extracts the UUID
        from the path. If no storage location exists or the UUID cannot be extracted,
        a new UUID is generated.

        Args:
            catalog_name: Name of the catalog to get UUID for

        Returns:
            UUID object representing the catalog identifier

        Note:
            If the storage location is unavailable or malformed, a warning is logged
            and a new UUID is generated to ensure consistency.
        """
        catalog: CatalogInfo = self.client.catalogs.get(catalog_name)
        storage_location: str | None = catalog.storage_location

        if not storage_location:
            logger.warning(
                f"No storage location found for catalog {catalog.name}. Using UUID instead of extracting \
                    Databricks' catalog UUID from storage location."
            )
            return uuid.uuid4()

        # Return the last part of the storage location path
        catalog_uuid: str = Path(storage_location).name

        if catalog_uuid == "":
            logger.warning(f"Could not extract ID from storage location: {storage_location}")
            return uuid.uuid4()

        return uuid.UUID(catalog_uuid)
