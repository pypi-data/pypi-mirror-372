from typing import (
    Protocol,
    Literal,
    Optional,
    overload,
    Union,
    Callable,
    List,
    Dict,
    Any,
    TypeVar,
)

import boto3
import pandas as pd
import polars as pl
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import os

from functools import wraps
from io import BytesIO
from botocore.client import BaseClient as Boto3Client
from loguru import logger
from botocore.exceptions import ClientError

from pandas.core.frame import DataFrame as PandasDataFrame
from polars.dataframe.frame import DataFrame as PolarsDataFrame

from enum import IntEnum

# We can use protocols to define the methods that implementations must implement
# This is useful for having a more reusable pattern for defining shared behaviours
# TODO: Add enums for the other validation methods

# Use this type for the generic type parameter of the Traits below
T = TypeVar("T")


class ResourceValidators:
    """
    Centralised validators that can be used across different traits.

    This ensures that the resource data is in the correct format before it is passed to the loader.

    The `_skip_validation` flag can be used to skip validation if the resource data is already validated.
    This is especially useful for methods (such as DuckDB loaders) that may call themselves internally,
    to avoid running the validation logic multiple times on the same data.

    Usage:
        - When calling a decorated method directly, validation will run by default.
        - When calling the same method internally (e.g., from within itself), pass `_skip_validation=True`
          as a keyword argument to skip redundant validation.
    """

    @staticmethod
    def validate_ckan_resource(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to validate CKAN resource data and transform it into a simplified format.

        This decorator:
        1. Validates the structure of the resource data
        2. Handles both single resources and lists of resources
        3. Extracts and validates the format and URL using ResourceIndex enum
        4. Transforms the input into a simplified [format, url] list

        Input formats expected:
        - Single list: [name, date, format, url] indexed by ResourceIndex
        - List of lists: [[name, date, format, url], [...], ...]

        Output:
        - Simplified list: [format, url] that's passed to the decorated function
        """

        class ResourceIndex(IntEnum):
            NAME = 0
            DATE = 1
            FORMAT = 2
            URL = 3

        @wraps(func)
        def wrapper(
            self,
            resource_data: Optional[List],
            desired_format: Optional[str] = None,
            *args,
            **kwargs,
        ):
            # Check if _skip_validation is True
            if kwargs.get("_skip_validation", False):
                # Skip validation and just call the function
                return func(self, resource_data, *args, **kwargs)

            # First validate we have a list
            if not isinstance(resource_data, list) or not resource_data:
                logger.error("Invalid resource data: must be a non-empty list")
                raise ValueError("Resource data must be a non-empty list")

            # If we have multiple resources (list of lists)
            if isinstance(resource_data[0], list):
                if desired_format:
                    # Find the resource with matching format
                    target_resource = next(
                        (
                            resource
                            for resource in resource_data
                            if resource[ResourceIndex.FORMAT].lower()
                            == desired_format.lower()
                        ),
                        None,
                    )
                    if not target_resource:
                        available_formats = [
                            resource[ResourceIndex.FORMAT] for resource in resource_data
                        ]
                        logger.error(f"No resource found with format: {desired_format}")
                        raise ValueError(
                            f"No resource with format '{desired_format}' found. "
                            f"Available formats: {', '.join(available_formats)}"
                        )
                else:
                    # If no format specified, use first resource
                    target_resource = resource_data[0]
            else:
                # Single resource case
                target_resource = resource_data

            # Validate the resource has all required elements
            if len(target_resource) <= ResourceIndex.URL:
                logger.error(
                    f"Invalid resource format: resource must have at least {ResourceIndex.URL + 1} elements"
                )
                raise ValueError(
                    f"Resource must contain at least {ResourceIndex.URL + 1} elements"
                )

            # Extract format and URL using the enum
            format_type = target_resource[ResourceIndex.FORMAT].lower()
            url = target_resource[ResourceIndex.URL]

            # Validate URL format
            if not url.startswith(("http://", "https://")):
                logger.error(f"Invalid URL format: {url}")
                raise ValueError("Invalid URL format")

            # Create the modified resource in the expected format
            modified_resource = [format_type, url]
            logger.info("Resource data validated")

            return func(self, modified_resource, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_opendata_resource(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to validate OpenDataSoft resource data.

        Input format:
        - List of dictionaries with 'format' and 'download_url' keys

        Output format:
        - List of dictionaries with 'format' and 'download_url' keys
        """

        @wraps(func)
        def wrapper(self, resource_data: List[Dict[str, Any]], *args, **kwargs):
            # Check if _skip_validation is True
            if kwargs.get("_skip_validation", False):
                # Skip validation and just call the function
                return func(self, resource_data, *args, **kwargs)

            # Regular validation logic
            if not resource_data or not isinstance(resource_data, list):
                logger.error("Resource data must be a list")
                raise ValueError("Resource data must be a list of dictionaries")

            has_valid_item = any(
                isinstance(item, dict) and "format" in item and "download_url" in item
                for item in resource_data
            )

            if not has_valid_item:
                logger.error(
                    "Resource data must contain dictionaries with 'format' and 'download_url' keys"
                )
                raise ValueError("Invalid resource data format for OpenDataSoft")

            logger.info("Resource data validated")

            return func(self, resource_data, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_french_gouv_resource(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to validate French Government resource data.

        Input format:
        - List of dictionaries with 'resource_format' and 'resource_url' keys

        Output format:
        - List of dictionaries with 'resource_format' and 'resource_url' keys
        """

        @wraps(func)
        def wrapper(self, resource_data: List[Dict[str, Any]], *args, **kwargs):
            if kwargs.get("_skip_validation", False):
                return func(self, resource_data, *args, **kwargs)

            # Check if resource data exists and is non-empty
            if not resource_data or not isinstance(resource_data, list):
                logger.error("Resource data must be a list")
                raise ValueError("Resource data must be a list of dictionaries")

            # Check if at least one item has the expected resource_format and resource_url keys
            has_valid_item = any(
                isinstance(item, dict)
                and "resource_format" in item
                and "resource_url" in item
                for item in resource_data
            )

            if not has_valid_item:
                logger.error(
                    "Resource data must contain dictionaries with 'resource_format' and 'resource_url' keys"
                )
                raise ValueError(
                    "Invalid resource data format for French Government data"
                )

            logger.info("Resource data validated")

            return func(self, resource_data, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_ons_nomis_resource(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to validate ONS Nomis resource data.

        Input format:
        - String of the url

        Output format:
        - String of the url
        """

        @wraps(func)
        def wrapper(self, resource_data: str, *args, **kwargs):
            # Check if *skip*validation is True
            if kwargs.get("_skip_validation", False):
                # Skip validation and just call the function
                return func(self, resource_data, *args, **kwargs)

            if not resource_data or not isinstance(resource_data, str):
                logger.error("Resource data must be a string")
                raise ValueError("Resource data must be a string")
            logger.info("Resource data validated")
            return func(self, resource_data, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_datapress_resource(func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to validate DataPress resource data.
        Input format:
        - List of lists where each inner list contains [format, url]
        Output format:
        - Same as input (passes through)
        """

        @wraps(func)
        def wrapper(self, resource_data, *args, **kwargs):
            # Check if *skip*validation is True
            if kwargs.get("_skip_validation", False):
                # Skip validation and just call the function
                return func(self, resource_data, *args, **kwargs)

            # Regular validation logic
            if not isinstance(resource_data, list):
                logger.error("Resource data must be a list")
                raise ValueError("Resource data must be a list of format-URL pairs")

            # Check if all items in resource_data are valid format
            all_valid = all(
                isinstance(item, list)
                and len(item) == 2
                and isinstance(item[0], str)
                and isinstance(item[1], str)
                for item in resource_data
            )

            if not all_valid:
                logger.error(
                    "Each item in resource data must be a list with two string elements [format, url]"
                )
                raise ValueError("Invalid resource data format for DataPress")

            logger.info("Resource data validated")
            return func(self, resource_data, *args, **kwargs)

        return wrapper


class StorageTrait(Protocol):
    """Protocol defining the interface for remote storage uploaders."""

    def upload(
        self,
        data: BytesIO,
        bucket: str,
        key: str,
        mode: Literal["raw", "parquet"] = "parquet",
        file_format: Optional[str] = None,
    ) -> str: ...


class S3Uploader(StorageTrait):
    """S3 uploader implementation."""

    def __init__(self, client: Optional[Boto3Client] = None):
        self.client = client or boto3.client("s3")

    def _verify_s3_bucket(self, bucket_name: str) -> None:
        """Verify S3 bucket exists."""
        try:
            self.client.head_bucket(Bucket=bucket_name)
            logger.info("Bucket Found")
        except ClientError as error:
            error_code = int(error.response["Error"]["Code"])
            if error_code == 404:
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            raise

    def _convert_to_parquet(self, binary_data: BytesIO, file_format: str) -> BytesIO:
        """Convert input data to parquet format."""
        match file_format:
            case "spreadsheet" | "xlsx":
                df = pd.read_excel(binary_data)
            case "csv":
                df = pd.read_csv(binary_data)
            case "json":
                df = pd.read_json(binary_data)
            case _:
                raise ValueError(f"Unsupported format for Parquet: {file_format}")

        if df.empty:
            raise ValueError("No data was loaded from the source file")

        table = pa.Table.from_pandas(df)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)
        return parquet_buffer

    def upload(
        self,
        data: BytesIO,
        bucket: str,
        key: str,
        mode: Literal["raw", "parquet"] = "parquet",
        file_format: Optional[str] = None,
    ) -> str:
        """Upload data to S3 with support for raw and parquet modes."""
        if not all(isinstance(x, str) and x.strip() for x in [bucket, key]):
            raise ValueError("Bucket and key must be non-empty strings")

        self._verify_s3_bucket(bucket)
        logger.info(f"Uploading data to S3 bucket: {bucket}")

        try:
            match mode:
                case "raw":
                    filename = f"{key}.{file_format}" if file_format else key
                    self.client.upload_fileobj(data, bucket, filename)
                case "parquet":
                    if not file_format:
                        raise ValueError("file_format is required for parquet mode")
                    parquet_buffer = self._convert_to_parquet(data, file_format)
                    filename = f"{key}.parquet"
                    self.client.upload_fileobj(parquet_buffer, bucket, filename)

            logger.info(f"File uploaded successfully to S3 as {filename}")
            return filename

        except Exception as e:
            logger.error(f"AWS S3 upload error: {e}")
            raise


class LocalUploader(StorageTrait):
    """Local filesystem uploader implementation."""

    def __init__(self, base_directory: str = "./data"):
        """
        Initialize the local uploader.

        Args:
            base_directory: Base directory where files will be stored
        """
        self.base_directory = base_directory
        os.makedirs(self.base_directory, exist_ok=True)

    def _get_full_path(self, bucket: str, filename: str) -> str:
        """
        Get the full path for a file.

        Args:
            bucket: Directory name (simulating S3 bucket)
            filename: Name of the file

        Returns:
            Full path to the file
        """

        bucket_dir = os.path.join(self.base_directory, bucket)
        os.makedirs(bucket_dir, exist_ok=True)
        return os.path.join(bucket_dir, filename)

    def _convert_to_parquet(self, binary_data: BytesIO, file_format: str) -> BytesIO:
        """Convert input data to parquet format."""
        match file_format:
            case "spreadsheet" | "xlsx":
                df = pd.read_excel(binary_data)
            case "csv":
                df = pd.read_csv(binary_data)
            case "json":
                df = pd.read_json(binary_data)
            case _:
                raise ValueError(f"Unsupported format for Parquet: {file_format}")

        if df.empty:
            raise ValueError("No data was loaded from the source file")

        table = pa.Table.from_pandas(df)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)
        return parquet_buffer

    def upload(
        self,
        data: BytesIO,
        bucket: str,
        key: str,
        mode: Literal["raw", "parquet"] = "parquet",
        file_format: Optional[str] = None,
    ) -> str:
        """Upload data to local filesystem with support for raw and parquet modes."""
        if not all(isinstance(x, str) and x.strip() for x in [bucket, key]):
            raise ValueError("Bucket and key must be non-empty strings")

        logger.info(f"Saving data to local directory: {bucket}")

        try:
            match mode:
                case "raw":
                    filename = f"{key}.{file_format}" if file_format else key
                    full_path = self._get_full_path(bucket, filename)
                    with open(full_path, "wb") as f:
                        f.write(data.getvalue())
                case "parquet":
                    if not file_format:
                        raise ValueError("file_format is required for parquet mode")
                    parquet_buffer = self._convert_to_parquet(data, file_format)
                    filename = f"{key}.parquet"
                    full_path = self._get_full_path(bucket, filename)
                    with open(full_path, "wb") as f:
                        f.write(parquet_buffer.getvalue())

            logger.info(f"File saved successfully to {full_path}")
            return filename

        except Exception as e:
            logger.error(f"Local file save error: {e}")
            raise


class DuckDBTrait(Protocol):
    """Protocol defining the interface for DuckDB operations."""

    def execute_query(self, query: str) -> Any: ...

    def load_data(
        self,
        data: Union[BytesIO, str],
        table_name: str,
        file_format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> bool: ...

    def load_remote_data(
        self,
        url: str,
        table_name: str,
        file_format: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> bool: ...

    def to_pandas(self, query: str) -> PandasDataFrame: ...

    def to_polars(self, query: str) -> PolarsDataFrame: ...


class DuckDBLoader(DuckDBTrait):
    """DuckDB implementation for data loading and querying."""

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialise DuckDB connection.

        Args:
            database_path: Path to DuckDB database file. If None, uses in-memory database.
        """
        self.duckdb = duckdb
        db_path = database_path if database_path is not None else ":memory:"
        self.conn = duckdb.connect(database=db_path)
        logger.info(
            f"Connected to DuckDB {'in-memory database' if database_path is None else database_path}"
        )
        self._load_extensions()

    def _load_extensions(self) -> None:
        """Load required DuckDB extensions."""
        try:
            # Install and load httpfs for remote data access
            self.conn.execute("INSTALL httpfs;")
            self.conn.execute("LOAD httpfs;")

            # Install and load spatial extension
            self.conn.execute("INSTALL spatial;")
            self.conn.execute("LOAD spatial;")

            logger.info("DuckDB extensions loaded: httpfs, spatial")
        except Exception as e:
            logger.warning(f"Failed to load some DuckDB extensions: {e}")

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query in DuckDB.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        try:
            logger.info(f"Executing DuckDB query: {query[:100]}...")
            result = self.conn.execute(query)
            return result
        except Exception as e:
            logger.error(f"DuckDB query execution error: {e}")
            raise

    def load_data(
        self,
        data: Union[BytesIO, str],
        table_name: str,
        file_format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Load data into DuckDB from a BytesIO object or file path.

        Args:
            data: Data source (BytesIO object or file path)
            table_name: Name of table to create
            file_format: Format of the data ('csv', 'parquet', 'json', etc.)
            options: Optional loading parameters as dictionary

        Returns:
            True if successful
        """
        try:
            if options is None:
                options = {}

            temp_path = None

            if isinstance(data, BytesIO):
                import tempfile

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{file_format}"
                ) as temp_file:
                    temp_file.write(data.getvalue())
                    temp_path = temp_file.name
                file_path = temp_path
            else:
                file_path = data

            format_lower = file_format.lower()

            if format_lower in ("csv", "tsv"):
                options_str = ", ".join(
                    [
                        f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}"
                        for k, v in options.items()
                    ]
                )
                query = (
                    f"CREATE TABLE {table_name} AS SELECT * FROM read_csv('{file_path}'"
                )
                if options_str:
                    query += f", {options_str}"
                query += ")"

            elif format_lower == "parquet":
                query = f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')"

            elif format_lower == "json":
                query = f"CREATE TABLE {table_name} AS SELECT * FROM read_json('{file_path}')"

            elif format_lower in ("xlsx", "xls", "spreadsheet"):
                # Handle Excel with sheet name if provided
                sheet_name = options.get("sheet_name", None)
                sheet_option = f", sheet_name='{sheet_name}'" if sheet_name else ""
                query = f"CREATE TABLE {table_name} AS SELECT * FROM ST_Read('{file_path}'{sheet_option})"

            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            logger.info(f"Loading {file_format} data into table '{table_name}'")
            self.conn.execute(query)

            if temp_path is not None:
                import os

                os.unlink(temp_path)

            return True

        except Exception as e:
            logger.error(f"DuckDB data loading error: {e}")
            raise

    def load_remote_data(
        self,
        url: str,
        table_name: str,
        file_format: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Load data from a remote URL into DuckDB with optional API key support.

        Args:
            url: URL to load data from
            table_name: Name of table to create
            file_format: Format of the data ('csv', 'parquet', 'json', etc.)
            api_key: Optional API key to append to URL or include in headers
            options: Optional loading parameters as dictionary

        Returns:
            True if successful
        """
        try:
            if options is None:
                options = {}

            # Add API key to URL if provided
            if api_key is not None:
                if "?" in url:
                    url = f"{url}&apikey={api_key}"
                else:
                    url = f"{url}?apikey={api_key}"

            format_lower = file_format.lower()

            if format_lower in ("csv", "tsv"):
                options_str = ", ".join(
                    [
                        f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}"
                        for k, v in options.items()
                    ]
                )
                query = f"CREATE TABLE {table_name} AS SELECT * FROM read_csv('{url}'"
                if options_str:
                    query += f", {options_str}"
                query += ")"

            elif format_lower == "parquet":
                query = (
                    f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{url}')"
                )

            elif format_lower == "json":
                query = f"CREATE TABLE {table_name} AS SELECT * FROM read_json('{url}')"

            elif format_lower in ("xlsx", "xls", "spreadsheet"):
                # Handle Excel with sheet name if provided
                sheet_name = options.get("sheet_name", None)
                sheet_option = f", sheet_name='{sheet_name}'" if sheet_name else ""
                query = f"CREATE TABLE {table_name} AS SELECT * FROM st_read('{url}'{sheet_option})"

            elif format_lower == ("geojson", "geopackage"):
                query = f"CREATE TABLE {table_name} AS SELECT * FROM st_read('{url}')"

            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            # Execute the query
            logger.info(
                f"Loading {file_format} data from URL ('{url}') into table '{table_name}'"
            )
            self.conn.execute(query)

            return True

        except Exception as e:
            logger.error(f"DuckDB remote data loading error: {e}")
            raise

    def to_pandas(self, query: str) -> PandasDataFrame:
        """
        Execute query and return results as a pandas DataFrame.

        Args:
            query: SQL query to execute

        Returns:
            pandas DataFrame with query results
        """
        try:
            result = self.execute_query(query)
            return result.fetchdf()
        except Exception as e:
            logger.error(f"Error converting DuckDB result to pandas: {e}")
            raise

    def to_polars(self, query: str) -> PolarsDataFrame:
        """
        Execute query and return results as a polars DataFrame.

        Args:
            query: SQL query to execute

        Returns:
            polars DataFrame with query results
        """
        try:
            pandas_df = self.to_pandas(query)
            return pl.from_pandas(pandas_df)
        except Exception as e:
            logger.error(f"Error converting DuckDB result to polars: {e}")
            raise


class DataFrameLoaderTrait(Protocol):
    """Protocol defining the interface for DataFrame loaders."""

    @overload
    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["pandas"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PandasDataFrame: ...

    @overload
    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["polars"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PolarsDataFrame: ...

    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["pandas", "polars"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> Union[PandasDataFrame, PolarsDataFrame]: ...


class DataFrameLoader(DataFrameLoaderTrait):
    """DataFrame loading functionality with input validation."""

    def get_sheet_names(self, data: BytesIO) -> list:
        """
        Get all sheet names from an Excel file.

        Args:
            data (BytesIO): Excel file as BytesIO

        Returns:
            list[str]: List of sheet names

        Raises:
            ValueError: If the file is not an Excel file
        """
        try:
            # No need to create a new BytesIO object
            data.seek(0)  # Ensure we're at the start of the stream
            return pd.ExcelFile(data).sheet_names
        except Exception as e:
            logger.error(f"Failed to get sheet names: {str(e)}")
            raise ValueError("Could not read sheet names. Is this a valid Excel file?")

    @overload
    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["pandas"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PandasDataFrame: ...

    @overload
    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["polars"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PolarsDataFrame: ...

    def create_dataframe(
        self,
        data: BytesIO,
        format_type: str,
        loader_type: Literal["pandas", "polars"],
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> Union[PandasDataFrame, PolarsDataFrame]:
        """Load data into specified DataFrame type."""
        try:
            match (format_type.lower(), loader_type):
                case ("parquet", "pandas"):
                    return pd.read_parquet(data)

                case ("parquet", "polars"):
                    return pl.read_parquet(data)

                case (("xls" | "xlsx" | "spreadsheet"), "pandas"):
                    if skip_rows is not None:
                        return (
                            pd.read_excel(
                                data, sheet_name=sheet_name, skiprows=skip_rows
                            )
                            if sheet_name
                            else pd.read_excel(data, skiprows=skip_rows)
                        )
                    else:
                        return (
                            pd.read_excel(data, sheet_name=sheet_name)
                            if sheet_name
                            else pd.read_excel(data)
                        )

                case (("xls" | "xlsx" | "spreadsheet"), "polars"):
                    if skip_rows is not None:
                        return (
                            pl.read_excel(
                                data,
                                sheet_name=sheet_name,
                                read_options={"skip_rows": skip_rows},
                            )
                            if sheet_name
                            else pl.read_excel(
                                data, read_options={"skip_rows": skip_rows}
                            )
                        )
                    else:
                        return (
                            pl.read_excel(data, sheet_name=sheet_name)
                            if sheet_name
                            else pl.read_excel(data)
                        )

                case ("json", "pandas"):
                    return pd.read_json(data)

                case ("json", "polars"):
                    return pl.read_json(data)

                case (("geopackage" | "gpkg"), _):
                    raise ValueError("Geopackage format not implemented yet")

                case _:
                    raise ValueError(
                        f"Unsupported format {format_type} or loader type {loader_type}"
                    )

        except Exception as e:
            logger.error(f"Failed to load {loader_type} DataFrame: {str(e)}")
            raise
