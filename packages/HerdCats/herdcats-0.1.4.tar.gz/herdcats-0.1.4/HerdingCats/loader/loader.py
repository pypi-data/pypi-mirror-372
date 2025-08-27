import requests
import pandas as pd
import polars as pl
import duckdb
import boto3
import pyarrow as pa
import uuid
import urllib.parse
from ..errors.errors import OpenDataSoftExplorerError, FrenchCatDataLoaderError
from ..explorer.explore import CatSession
from ..config.source_endpoints import CkanApiPaths
from .loader_stores import (
    S3Uploader,
    DataFrameLoader,
    LocalUploader,
    DuckDBLoader,
    ResourceValidators,
)

from typing import Union, Optional, Literal, List, Dict, Any
from pandas.core.frame import DataFrame as PandasDataFrame
from polars.dataframe.frame import DataFrame as PolarsDataFrame
from io import BytesIO
from loguru import logger

# TODO: Start building proper data loader stores for different formats and locations
# TODO: further harmonise how the loader deal with the input data


# START TO WRANGLE / ANALYSE
# LOAD CKAN DATA RESOURCES INTO STORAGE / FORMATS
class CkanLoader:
    """A class to load data resources into various formats and storage systems."""

    STORAGE_TYPES = {"s3": S3Uploader, "local": LocalUploader}

    def __init__(self):
        self._validate_dependencies()
        self.df_loader = DataFrameLoader()

    def _validate_dependencies(self):
        """Validate that all required dependencies are available."""
        required_modules = {
            "pandas": pd,
            "polars": pl,
            "duckdb": duckdb,
            "boto3": boto3,
            "pyarrow": pa,
        }
        missing = [name for name, module in required_modules.items() if module is None]
        if missing:
            raise ImportError(f"Missing required dependencies: {', '.join(missing)}")

    def _fetch_data(self, url: str) -> BytesIO:
        """
        Fetch data from URL and return as BytesIO object.

        Args:
            url: URL to fetch data from

        Returns:
            BytesIO object containing the data
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(f"Error fetching data from URL: {e}")
            raise

    def ckan_sql_to_polars(
        self,
        session: CatSession,
        resource_name: str,
        filters: Optional[dict] = None,
        api_key: Optional[str] = None,
    ) -> pl.DataFrame:
        """
        Work with CKAN datasets that use the "datastore" extension to store their data.
        It allows you to query the data using SQL syntax
        and return the results as a Polars DataFrame.

        Args:
            session: CatSession object
            resource_name: str, name of the resource to query
            filters: Optional dict of filters to build WHERE clause
            api_key: Optional API key for private datasets

        Returns:
            Polars DataFrame with the query results
        """
        # Build SQL query using backticks for the table name
        sql_query = f"SELECT * FROM `{resource_name}`"

        if filters:
            where = " AND ".join(f"{k} = '{v}'" for k, v in filters.items())
            sql_query += f" WHERE {where}"

        api_call = (
            f"{session.base_url}{CkanApiPaths.DATASTORE_SQL_QUERY}"
            f"resource_id={resource_name}&"
            f"sql={urllib.parse.quote(sql_query)}"
        )
        headers = {"Authorization": api_key} if api_key else {}

        response = requests.get(api_call, headers=headers)
        response.raise_for_status()
        data = response.json()
        records = data["result"]["result"]["records"]
        return pl.DataFrame(records) if records else pl.DataFrame([])

    @ResourceValidators.validate_ckan_resource
    def get_sheet_names(self, resource_data: List) -> list[str]:
        """
        Get all sheet names from an Excel file.

        Args:
            resource_data: List of resources or single resource

        Returns:
            List of sheet names
        """
        if resource_data[0] != "spreadsheet":
            raise ValueError("Resource is not an Excel file")
        binary_data = self._fetch_data(resource_data[1])
        return self.df_loader.get_sheet_names(binary_data)

    @ResourceValidators.validate_ckan_resource
    def polars_data_loader(
        self,
        resource_data: List,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PolarsDataFrame:
        """
        Load a resource into a Polars DataFrame.

        Args:
            resource_data: List of resources or single resource
            sheet_name: Optional sheet name for Excel files
            skip_rows: Optional number of rows to skip at the beginning of the sheet

        Returns:
            Polars DataFrame with the loaded data
        """
        binary_data = self._fetch_data(resource_data[1])
        return self.df_loader.create_dataframe(
            binary_data,
            resource_data[0].lower(),
            sheet_name=sheet_name,
            loader_type="polars",
            skip_rows=skip_rows,
        )

    @ResourceValidators.validate_ckan_resource
    def pandas_data_loader(
        self,
        resource_data: List,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> PandasDataFrame:
        """
        Load a resource into a Pandas DataFrame.

        Args:
            resource_data: List of resources or single resource
            sheet_name: Optional sheet name for Excel files
            skip_rows: Optional number of rows to skip at the beginning of the sheet
        """
        binary_data = self._fetch_data(resource_data[1])
        return self.df_loader.create_dataframe(
            binary_data,
            resource_data[0].lower(),
            sheet_name=sheet_name,
            loader_type="pandas",
            skip_rows=skip_rows,
        )

    @ResourceValidators.validate_ckan_resource
    def upload_data(
        self,
        resource_data: List,
        bucket_name: str,
        custom_name: str,
        mode: Literal["raw", "parquet"],
        storage_type: Literal["s3"],
    ) -> str:
        """
        Upload data using specified uploader

        Args:
            resource_data: List of resources or single resource
            bucket_name: Name of the bucket to upload the data to
            custom_name: Custom name for the uploaded data
        """
        if not all(
            isinstance(x, str) and x.strip() for x in [bucket_name, custom_name]
        ):
            raise ValueError("Bucket name and custom name must be non-empty strings")

        UploaderClass = self.STORAGE_TYPES[storage_type]
        uploader = UploaderClass()

        file_format = resource_data[0].lower()
        binary_data = self._fetch_data(resource_data[1])

        key = f"{custom_name}-{uuid.uuid4()}"
        return uploader.upload(
            data=binary_data,
            bucket=bucket_name,
            key=key,
            mode=mode,
            file_format=file_format,
        )

    @ResourceValidators.validate_ckan_resource
    def duckdb_data_loader(
        self,
        resource_data: list,
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        _skip_validation: bool = False,
    ) -> bool:
        """
        Load data from a resource URL directly into DuckDB.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            api_key: Optional API key for the data source
            options: Optional loading parameters
            _skip_validation: Optional boolean to skip validation logic

        Returns:
            True if data was loaded successfully
        """
        # Initialise DuckDB loader
        self.duckdb_loader = DuckDBLoader()

        # Extract URL and load data (same for both code paths)
        file_format, url = resource_data

        return self.duckdb_loader.load_remote_data(
            url=url,
            table_name=table_name,
            file_format=format_type,
            api_key=api_key,
            options=options,
        )

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query against the DuckDB instance.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        return self.duckdb_loader.execute_query(query)

    @ResourceValidators.validate_ckan_resource
    def query_to_pandas(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PandasDataFrame:
        """
        Load data into DuckDB and return query results as pandas DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            pandas DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_pandas(query)

    @ResourceValidators.validate_ckan_resource
    def query_to_polars(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PolarsDataFrame:
        """
        Load data into DuckDB and return query results as polars DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            polars DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_polars(query)


# START TO WRANGLE / ANALYSE
# LOAD OPEN DATA SOFT DATA RESOURCES INTO STORAGE / FORMATS
class OpenDataSoftLoader:
    """A class to load OpenDataSoft resources into various formats and storage systems."""

    SUPPORTED_FORMATS = {
        "spreadsheet": ["xls", "xlsx"],
        "csv": ["csv"],
        "parquet": ["parquet"],
        "geopackage": ["gpkg", "geopackage"],
    }

    STORAGE_TYPES = {"s3": S3Uploader, "local": LocalUploader}

    def __init__(self) -> None:
        self._validate_dependencies()
        self.df_loader = DataFrameLoader()

    def _validate_dependencies(self):
        """Validate that all required dependencies are available."""
        required_modules = {
            "pandas": pd,
            "polars": pl,
            "duckdb": duckdb,
            "boto3": boto3,
            "pyarrow": pa,
        }
        missing = [name for name, module in required_modules.items() if module is None]
        if missing:
            raise ImportError(f"Missing required dependencies: {', '.join(missing)}")

    def _extract_resource_data(
        self, resource_data: Optional[List[Dict[str, str]]], format_type: str
    ) -> str:
        """Validate resource data and extract download URL."""
        if not resource_data:
            raise OpenDataSoftExplorerError("No resource data provided")

        # Get all supported formats
        all_formats = [
            fmt for formats in self.SUPPORTED_FORMATS.values() for fmt in formats
        ]

        # If the provided format_type is a category, get its format
        valid_formats = (
            self.SUPPORTED_FORMATS.get(format_type, [])
            if format_type in self.SUPPORTED_FORMATS
            else [format_type]
        )

        # Validate format type
        if format_type not in self.SUPPORTED_FORMATS and format_type not in all_formats:
            raise OpenDataSoftExplorerError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: csv, parquet, xls, xlsx, geopackage"
            )

        # Find matching resource
        url = next(
            (
                r.get("download_url")
                for r in resource_data
                if r.get("format", "").lower() in valid_formats
            ),
            None,
        )

        # If format provided does not have a url provide the formats that do
        if not url:
            available_formats = [r["format"] for r in resource_data]
            raise OpenDataSoftExplorerError(
                f"No resource found with format: {format_type}. "
                f"Available formats: {', '.join(available_formats)}"
            )

        return url

    def _fetch_data(self, url: str, api_key: Optional[str] = None) -> BytesIO:
        """Fetch data from URL and return as BytesIO object."""
        try:
            if api_key:
                url = f"{url}?apikey={api_key}"

            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            raise OpenDataSoftExplorerError(f"Failed to download resource: {str(e)}", e)

    def _verify_data(
        self, df: Union[pd.DataFrame, pl.DataFrame], api_key: Optional[str]
    ) -> None:
        """Verify that the DataFrame is not empty when no API key is provided."""
        is_empty = df.empty if isinstance(df, pd.DataFrame) else df.height == 0
        if is_empty and not api_key:
            raise OpenDataSoftExplorerError(
                "Received empty DataFrame. This likely means an API key is required. "
                "Please provide an API key and try again."
            )

    @ResourceValidators.validate_opendata_resource
    def polars_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pl.DataFrame:
        """Load data from a resource URL into a Polars DataFrame."""
        url = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "polars", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_opendata_resource
    def pandas_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pd.DataFrame:
        """Load data from a resource URL into a Pandas DataFrame."""
        url = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "pandas", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_opendata_resource
    def upload_data(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        bucket_name: str,
        custom_name: str,
        format_type: str,
        mode: Literal["raw", "parquet"],
        storage_type: Literal["s3"] = "s3",
        api_key: Optional[str] = None,
    ) -> str:
        """Upload data using specified uploader"""
        if not all(
            isinstance(x, str) and x.strip() for x in [bucket_name, custom_name]
        ):
            raise ValueError("Bucket name and custom name must be non-empty strings")

        UploaderClass = self.STORAGE_TYPES[storage_type]
        uploader = UploaderClass()

        # Extract the URL using the existing method
        url = self._extract_resource_data(resource_data, format_type)

        # Fetch the data with optional API key
        binary_data = self._fetch_data(url, api_key)

        # Generate a unique key and upload
        key = f"{custom_name}-{uuid.uuid4()}"
        return uploader.upload(
            data=binary_data,
            bucket=bucket_name,
            key=key,
            mode=mode,
            file_format=format_type,
        )

    @ResourceValidators.validate_opendata_resource
    def duckdb_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        _skip_validation: bool = False,
    ) -> bool:
        """
        Load data from a resource URL directly into DuckDB.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            api_key: Optional API key for the data source
            options: Optional loading parameters
            _skip_validation: Optional boolean to skip validation logic

        Returns:
            True if data was loaded successfully
        """
        # Initialise DuckDB loader
        self.duckdb_loader = DuckDBLoader()

        # Extract URL and load data (same for both code paths)
        url = self._extract_resource_data(resource_data, format_type)

        return self.duckdb_loader.load_remote_data(
            url=url,
            table_name=table_name,
            file_format=format_type,
            api_key=api_key,
            options=options,
        )

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query against the DuckDB instance.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        return self.duckdb_loader.execute_query(query)

    @ResourceValidators.validate_opendata_resource
    def query_to_pandas(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PandasDataFrame:
        """
        Load data into DuckDB and return query results as pandas DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            pandas DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_pandas(query)

    @ResourceValidators.validate_opendata_resource
    def query_to_polars(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PolarsDataFrame:
        """
        Load data into DuckDB and return query results as polars DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            polars DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_polars(query)


# START TO WRANGLE / ANALYSE
# LOAD FRENCH GOUV DATA RESOURCES INTO STORAGE / FORMATS
class FrenchGouvLoader:
    """A class to load French Gouv data resources into various formats and storage systems."""

    SUPPORTED_FORMATS = {
        "xls": ["xls"],
        "xlsx": ["xlsx"],
        "csv": ["csv"],
        "parquet": ["parquet"],
        "geopackage": ["gpkg", "geopackage"],
    }

    STORAGE_TYPES = {"s3": S3Uploader, "local": LocalUploader}

    def __init__(self) -> None:
        self._validate_dependencies()
        self.df_loader = DataFrameLoader()

    def _validate_dependencies(self):
        """Validate that all required dependencies are available."""
        required_modules = {
            "pandas": pd,
            "polars": pl,
            "duckdb": duckdb,
            "boto3": boto3,
            "pyarrow": pa,
        }
        missing = [name for name, module in required_modules.items() if module is None]
        if missing:
            raise ImportError(f"Missing required dependencies: {', '.join(missing)}")

    def _extract_resource_data(
        self, resource_data: Optional[List[Dict[str, str]]], format_type: str
    ) -> tuple[str, str]:
        """Validate resource data and extract download URL."""
        if not resource_data:
            raise FrenchCatDataLoaderError("No resource data provided")

        # Get all supported formats
        all_formats = [
            fmt for formats in self.SUPPORTED_FORMATS.values() for fmt in formats
        ]

        # If the provided format_type is a category, get its format
        valid_formats = (
            self.SUPPORTED_FORMATS.get(format_type, [])
            if format_type in self.SUPPORTED_FORMATS
            else [format_type]
        )

        # Validate format type
        if format_type not in self.SUPPORTED_FORMATS and format_type not in all_formats:
            raise FrenchCatDataLoaderError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: csv, parquet, xls, xlsx, geopackage"
            )

        # Find matching resource and its title
        matching_resource = next(
            (
                resource
                for resource in resource_data
                if resource.get("resource_format", "").lower() in valid_formats
            ),
            None,
        )

        if not matching_resource:
            available_formats = [r["resource_format"] for r in resource_data]
            raise FrenchCatDataLoaderError(
                f"No resource found with format: {format_type}. "
                f"Available formats: {', '.join(available_formats)}"
            )

        url = matching_resource.get("resource_url")
        title = matching_resource.get("resource_title", "Unnamed Resource")

        if not url:
            raise FrenchCatDataLoaderError("Resource URL not found in data")

        return url, title

    def _fetch_data(self, url: str, api_key: Optional[str] = None) -> BytesIO:
        """Fetch data from URL and return as BytesIO object."""
        try:
            if api_key:
                url = f"{url}?apikey={api_key}"

            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            raise OpenDataSoftExplorerError(f"Failed to download resource: {str(e)}", e)

    def _verify_data(
        self, df: Union[pd.DataFrame, pl.DataFrame], api_key: Optional[str]
    ) -> None:
        """Verify that the DataFrame is not empty when no API key is provided."""
        is_empty = df.empty if isinstance(df, pd.DataFrame) else df.height == 0
        if is_empty and not api_key:
            raise FrenchCatDataLoaderError(
                "Received empty DataFrame. This likely means an API key is required. "
                "Please provide an API key and try again."
            )

    @ResourceValidators.validate_french_gouv_resource
    def polars_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        format_type: Literal["csv", "parquet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pl.DataFrame:
        """Load data from a resource URL into a Polars DataFrame."""
        url, title = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "polars", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_french_gouv_resource
    def pandas_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pd.DataFrame:
        """Load data from a resource URL into a Pandas DataFrame."""
        url, title = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "pandas", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_french_gouv_resource
    def upload_data(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        bucket_name: str,
        custom_name: str,
        format_type: str,
        mode: Literal["raw", "parquet"],
        storage_type: Literal["s3"] = "s3",
        api_key: Optional[str] = None,
    ) -> str:
        """Upload data using specified uploader"""
        if not all(
            isinstance(x, str) and x.strip() for x in [bucket_name, custom_name]
        ):
            raise ValueError("Bucket name and custom name must be non-empty strings")

        # Define STORAGE_TYPES if not already defined
        if not hasattr(self, "STORAGE_TYPES"):
            self.STORAGE_TYPES = {"s3": S3Uploader}

        UploaderClass = self.STORAGE_TYPES[storage_type]
        uploader = UploaderClass()

        # Extract URL using the existing method
        url, _ = self._extract_resource_data(resource_data, format_type)

        # Fetch the data
        binary_data = self._fetch_data(url, api_key)

        # Generate a unique key and upload
        key = f"{custom_name}-{uuid.uuid4()}"
        return uploader.upload(
            data=binary_data,
            bucket=bucket_name,
            key=key,
            mode=mode,
            file_format=format_type,
        )

    @ResourceValidators.validate_french_gouv_resource
    def duckdb_data_loader(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        _skip_validation: bool = False,
    ) -> bool:
        """
        Load data from a resource URL directly into DuckDB.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            api_key: Optional API key for the data source
            options: Optional loading parameters
            _skip_validation: Optional boolean to skip validation logic

        Returns:
            True if data was loaded successfully
        """
        # Initialise DuckDB loader
        self.duckdb_loader = DuckDBLoader()

        # Extract URL and load data (same for both code paths)
        url, _ = self._extract_resource_data(resource_data, format_type)

        return self.duckdb_loader.load_remote_data(
            url=url,
            table_name=table_name,
            file_format=format_type,
            api_key=api_key,
            options=options,
        )

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query against the DuckDB instance.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        return self.duckdb_loader.execute_query(query)

    @ResourceValidators.validate_french_gouv_resource
    def query_to_pandas(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PandasDataFrame:
        """
        Load data into DuckDB and return query results as pandas DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            pandas DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_pandas(query)

    @ResourceValidators.validate_french_gouv_resource
    def query_to_polars(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PolarsDataFrame:
        """
        Load data into DuckDB and return query results as polars DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            polars DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_polars(query)


# START TO WRANGLE / ANALYSE
# LOAD ONS NOMIS DATA RESOURCES INTO STORAGE / FORMATS
# TODO: Add support for other formats
class ONSNomisLoader:
    """A class to load ONS Nomis data resources into various formats and storage systems."""

    STORAGE_TYPES = {"s3": S3Uploader, "local": LocalUploader}

    def __init__(self) -> None:
        self._validate_dependencies()
        self.df_loader = DataFrameLoader()

    def _validate_dependencies(self):
        """Validate that all required dependencies are available."""
        required_modules = {
            "pandas": pd,
            "polars": pl,
            "duckdb": duckdb,
            "boto3": boto3,
            "pyarrow": pa,
        }
        missing = [name for name, module in required_modules.items() if module is None]
        if missing:
            raise ImportError(f"Missing required dependencies: {', '.join(missing)}")

    def _fetch_data(self, url: str) -> BytesIO:
        """Fetch data from URL and return as BytesIO object."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(f"Error fetching data from URL: {e}")
            raise

    @ResourceValidators.validate_ons_nomis_resource
    def duckdb_data_loader(
        self,
        resource_data: str,
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        _skip_validation: bool = False,
    ) -> bool:
        """
        Load data from a resource URL directly into DuckDB.

        Args:
            url: Resource data from Nomis catalogue
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            api_key: Optional API key for the data source
            options: Optional loading parameters
            _skip_validation: Optional boolean to skip validation logic

        Returns:
            True if data was loaded successfully
        """
        # Initialise DuckDB loader
        self.duckdb_loader = DuckDBLoader()

        url = resource_data

        return self.duckdb_loader.load_remote_data(
            url=url,
            table_name=table_name,
            file_format=format_type,
            api_key=api_key,
            options=options,
        )

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query against the DuckDB instance.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        return self.duckdb_loader.execute_query(query)

    @ResourceValidators.validate_ons_nomis_resource
    def query_to_pandas(
        self,
        resource_data: str,
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PandasDataFrame:
        """
        Load data into DuckDB and return query results as pandas DataFrame.

        Args:
            url: Resource data from Nomis catalogue
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            pandas DataFrame with query results
        """

        url = resource_data
        self.duckdb_data_loader(
            resource_data=url,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_pandas(query)

    @ResourceValidators.validate_ons_nomis_resource
    def query_to_polars(
        self,
        resource_data: str,
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PolarsDataFrame:
        """
        Load data into DuckDB and return query results as polars DataFrame.

        Args:
            url: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            polars DataFrame with query results
        """

        url = resource_data

        self.duckdb_data_loader(
            resource_data=url,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_polars(query)

    @ResourceValidators.validate_ons_nomis_resource
    def upload_data(
        self,
        url: str,
        bucket_name: str,
        custom_name: str,
        mode: Literal["raw", "parquet"],
        storage_type: Literal["s3"] = "s3",
    ) -> str:
        """Upload data using specified uploader"""
        if not all(
            isinstance(x, str) and x.strip() for x in [bucket_name, custom_name]
        ):
            raise ValueError("Bucket name and custom name must be non-empty strings")

        # Define STORAGE_TYPES if not already defined
        if not hasattr(self, "STORAGE_TYPES"):
            self.STORAGE_TYPES = {"s3": S3Uploader}

        UploaderClass = self.STORAGE_TYPES[storage_type]
        uploader = UploaderClass()

        # Fetch the data
        binary_data = self._fetch_data(url)

        # For ONS Nomis, we know it's always XLSX format
        format_type = "csv"

        # Generate a unique key and upload
        key = f"{custom_name}-{uuid.uuid4()}"
        return uploader.upload(
            data=binary_data,
            bucket=bucket_name,
            key=key,
            mode=mode,
            file_format=format_type,
        )


# START TO WRANGLE / ANALYSE
# LOAD DATAPRESS DATA RESOURCES INTO STORAGE / FORMATS
class DataPressLoader:
    """A class to load DataPress resources into various formats and storage systems."""

    SUPPORTED_FORMATS = {
        "spreadsheet": ["spreadsheet"],
        "csv": ["csv"],
        "parquet": ["parquet"],
        "geopackage": ["gpkg", "geopackage"],
    }

    STORAGE_TYPES = {"s3": S3Uploader, "local": LocalUploader}

    def __init__(self) -> None:
        self._validate_dependencies()
        self.df_loader = DataFrameLoader()

    def _validate_dependencies(self):
        """Validate that all required dependencies are available."""
        required_modules = {
            "pandas": pd,
            "polars": pl,
            "duckdb": duckdb,
            "boto3": boto3,
            "pyarrow": pa,
        }
        missing = [name for name, module in required_modules.items() if module is None]
        if missing:
            raise ImportError(f"Missing required dependencies: {', '.join(missing)}")

    def _extract_resource_data(
        self, resource_data: Optional[List[List[str]]], format_type: str
    ) -> str:
        """Validate resource data and extract download URL."""
        if not resource_data:
            raise OpenDataSoftExplorerError("No resource data provided")

        # Get all supported formats
        all_formats = [
            fmt for formats in self.SUPPORTED_FORMATS.values() for fmt in formats
        ]

        # If the provided format_type is a category, get its format
        valid_formats = (
            self.SUPPORTED_FORMATS.get(format_type, [])
            if format_type in self.SUPPORTED_FORMATS
            else [format_type]
        )

        # Validate format type
        if format_type not in self.SUPPORTED_FORMATS and format_type not in all_formats:
            raise OpenDataSoftExplorerError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: csv, parquet, xls, xlsx, geopackage"
            )

        # Find matching resource - assuming each inner list has [format, url] structure
        url = next(
            (
                resource[1]  # The URL is at index 1
                for resource in resource_data
                if resource[0].lower() in valid_formats  # The format is at index 0
            ),
            None,
        )

        # If format provided does not have a url provide the formats that do
        if not url:
            available_formats = [resource[0] for resource in resource_data]
            raise OpenDataSoftExplorerError(
                f"No resource found with format: {format_type}. "
                f"Available formats: {', '.join(available_formats)}"
            )

        return url

    def _fetch_data(self, url: str, api_key: Optional[str] = None) -> BytesIO:
        """Fetch data from URL and return as BytesIO object."""
        try:
            if api_key:
                url = f"{url}?apikey={api_key}"

            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            raise OpenDataSoftExplorerError(f"Failed to download resource: {str(e)}", e)

    def _verify_data(
        self, df: Union[pd.DataFrame, pl.DataFrame], api_key: Optional[str]
    ) -> None:
        """Verify that the DataFrame is not empty when no API key is provided."""
        is_empty = df.empty if isinstance(df, pd.DataFrame) else df.height == 0
        if is_empty and not api_key:
            raise OpenDataSoftExplorerError(
                "Received empty DataFrame. This likely means an API key is required. "
                "Please provide an API key and try again."
            )

    @ResourceValidators.validate_datapress_resource
    def get_sheet_names(
        self,
        resource_data: Optional[List[List[str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
    ) -> list[str]:
        """
        Get all sheet names from an Excel file.

        Args:
            resource_data: List of resources or single resource

        Returns:
            List of sheet names
        """
        url = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url)
        return self.df_loader.get_sheet_names(binary_data)

    @ResourceValidators.validate_datapress_resource
    def polars_data_loader(
        self,
        resource_data: Optional[List[List[str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pl.DataFrame:
        """Load data from a resource URL into a Polars DataFrame."""
        url = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "polars", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_datapress_resource
    def pandas_data_loader(
        self,
        resource_data: Optional[List[List[str]]],
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        sheet_name: Optional[str] = None,
        skip_rows: Optional[int] = None,
    ) -> pd.DataFrame:
        """Load data from a resource URL into a Pandas DataFrame."""
        url = self._extract_resource_data(resource_data, format_type)
        binary_data = self._fetch_data(url, api_key)
        df = self.df_loader.create_dataframe(
            binary_data, format_type, "pandas", sheet_name, skip_rows
        )
        self._verify_data(df, api_key)
        return df

    @ResourceValidators.validate_datapress_resource
    def upload_data(
        self,
        resource_data: Optional[List[List[str]]],
        bucket_name: str,
        custom_name: str,
        format_type: str,
        mode: Literal["raw", "parquet"],
        storage_type: Literal["s3"] = "s3",
        api_key: Optional[str] = None,
    ) -> str:
        """Upload data using specified uploader"""
        if not all(
            isinstance(x, str) and x.strip() for x in [bucket_name, custom_name]
        ):
            raise ValueError("Bucket name and custom name must be non-empty strings")

        UploaderClass = self.STORAGE_TYPES[storage_type]
        uploader = UploaderClass()

        # Extract the URL using the existing method
        url = self._extract_resource_data(resource_data, format_type)

        # Fetch the data with optional API key
        binary_data = self._fetch_data(url, api_key)

        # Generate a unique key and upload
        key = f"{custom_name}-{uuid.uuid4()}"
        return uploader.upload(
            data=binary_data,
            bucket=bucket_name,
            key=key,
            mode=mode,
            file_format=format_type,
        )

    @ResourceValidators.validate_datapress_resource
    def duckdb_data_loader(
        self,
        resource_data: Optional[List[List[str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        _skip_validation: bool = False,
    ) -> bool:
        """
        Load data from a resource URL directly into DuckDB.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            api_key: Optional API key for the data source
            options: Optional loading parameters
            _skip_validation: Optional boolean to skip validation logic

        Returns:
            True if data was loaded successfully
        """
        # Initialise DuckDB loader
        self.duckdb_loader = DuckDBLoader()

        # Extract URL and load data (same for both code paths)
        url = self._extract_resource_data(resource_data, format_type)

        return self.duckdb_loader.load_remote_data(
            url=url,
            table_name=table_name,
            file_format=format_type,
            api_key=api_key,
            options=options,
        )

    def execute_query(self, query: str) -> Any:
        """
        Execute a SQL query against the DuckDB instance.

        Args:
            query: SQL query to execute

        Returns:
            DuckDB result object
        """
        return self.duckdb_loader.execute_query(query)

    @ResourceValidators.validate_datapress_resource
    def query_to_pandas(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PandasDataFrame:
        """
        Load data into DuckDB and return query results as pandas DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            pandas DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_pandas(query)

    @ResourceValidators.validate_datapress_resource
    def query_to_polars(
        self,
        resource_data: Optional[List[Dict[str, str]]],
        table_name: str,
        format_type: Literal["csv", "parquet", "spreadsheet", "xls", "xlsx"],
        query: str,
        api_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> PolarsDataFrame:
        """
        Load data into DuckDB and return query results as polars DataFrame.

        Args:
            resource_data: Resource data from OpenDataSoft catalog
            table_name: Name of table to create in DuckDB
            format_type: Format of the data
            query: SQL query to execute after loading data
            api_key: Optional API key for the data source
            options: Optional loading parameters

        Returns:
            polars DataFrame with query results
        """
        self.duckdb_data_loader(
            resource_data=resource_data,
            table_name=table_name,
            format_type=format_type,
            api_key=api_key,
            options=options,
            _skip_validation=True,
        )
        return self.duckdb_loader.to_polars(query)
