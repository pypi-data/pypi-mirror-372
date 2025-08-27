import requests
import pandas as pd
import polars as pl
import duckdb

from typing import Any, Dict, Optional, Union, Literal, List, Tuple
from loguru import logger
from urllib.parse import urlencode


from ..config.source_endpoints import (
    CkanApiPaths,
    DataPressApiPaths,
    OpenDataSoftApiPaths,
    FrenchGouvApiPaths,
    ONSNomisApiPaths,
    ONSNomisQueryParams,
    DCATApiPaths,
)
from ..errors.errors import CatExplorerError, WrongCatalogueError
from ..session.session import CatSession, CatalogueType

# At the moment we have a lot of duplicate code between the explorers
# TODO: Find a better way to do this
# OR keep as is because each catalogue has a different API and different data structures.
# Could be a good idea to maintain a very strong separation between the explorers?


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For Ckan Catalogues Only
class CkanCatExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession.

        Allows user to start exploring data catalogue programatically.

        Make sure you pass a valid CkanCatSession in - it will check if the catalogue type is right.

        Args:
            CkanCatSession

        Returns:
            CkanCatExplorer

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = hc.CkanCatExplorer(session)

        if __name__ == "__main__":
            main()
        """

        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.CKAN),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.CKAN:
            raise WrongCatalogueError(
                "Invalid catalogue type. CkanCatExplorer requires a Ckan catalogue session.",
                expected_catalogue=str(CatalogueType.CKAN),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check CKAN site health
    # ----------------------------
    def check_site_health(self) -> None:
        """
        Make sure the Ckan endpoints are healthy and reachable.

        This calls the Ckan package_list endpoint to check if the site is still reacheable.

        Returns:
            Success message if the site is healthy
            Error message if the site is not healthy

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                health_check = explore.check_site_health()

        if __name__ == "__main__":
            main()
        """

        url: str = self.cat_session.base_url + CkanApiPaths.PACKAGE_LIST

        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    logger.success("Health Check Passed: CKAN is running and available")
                else:
                    logger.warning(
                        "Health Check Warning: CKAN responded with an empty dataset"
                    )
            else:
                logger.error(
                    f"Health Check Failed: CKAN responded with status code {response.status_code}"
                )

        except requests.RequestException as e:
            logger.error(f"Health Check Failed: Unable to connect to CKAN - {str(e)}")

    # ----------------------------
    # Basic Available package lists + metadata
    # ----------------------------
    def get_package_count(self) -> int:
        """
        A quick way to see how 'big' a data catalogue is.

        E.g how many datasets (packages) there are.

        Returns:
            package_count: int

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                package_count = explore.get_package_count()
                print(package_count)

        if __name__ == "__main__":
            main()
        """

        url: str = self.cat_session.base_url + CkanApiPaths.PACKAGE_LIST

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            package_count = response.json()
            return len(package_count["result"])
        except requests.RequestException as e:
            logger.error(f"Failed to get package count: {e}")
            raise CatExplorerError(f"Failed to get package count: {str(e)}")

    def get_package_list(self) -> dict:
        """
        Explore all packages that are available to query as a dictionary.

        Returns:
            Dictionary of all available packages to use for further exploration.

            It follows a {"package_name": "package_name"} structure so that you can use the package names for
            additional methods.

            {
            '--lfb-financial-and-performance-reporting-2021-22': '--lfb-financial-and-performance-reporting-2021-22',
            '-ghg-emissions-per-capita-from-food-and-non-alcoholic-drinks-': '-ghg-emissions-per-capita-from-food-and-non-alcoholic-drinks-',
            '100-west-cromwell-road-consultation-documents': '100-west-cromwell-road-consultation-documents',
            '19-year-olds-qualified-to-nvq-level-3': '19-year-olds-qualified-to-nvq-level-3',
            '1a---1c-eynsham-drive-public-consultation': '1a---1c-eynsham-drive-public-consultation',
            '2010-2013-gla-budget-detail': '2010-2013-gla-budget-detail',
            '2011-boundary-files': '2011-boundary-files',
            '2011-census-assembly': '2011-census-assembly',
            '2011-census-demography': '2011-census-demography'
            }

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                all_packages = explore.get_package_list()
                print(all_packages)

        if __name__ == "__main__":
            main()
        """

        url: str = self.cat_session.base_url + CkanApiPaths.PACKAGE_LIST

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()
            list_prep = data["result"]
            package_list = {item: item for item in list_prep}
            return package_list
        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_package_list_dataframe(
        self, df_type: Literal["pandas", "polars"]
    ) -> Union[pd.DataFrame, "pl.DataFrame"]:
        """
        Explore all packages that are available to query as a dataframe

        Args:
            pandas
            polars

        Returns:
            pd.DataFrame or pl.DataFrame with all dataset names

        Example ouput:
            shape: (68_995, 1)
            ┌─────────────────────
            │ column_0                        │
            │ ---                             │
            │ str                             │
            ╞═════════════════════
            │ 0-1-annual-probability-extents… │
            │ 0-1-annual-probability-extents… │
            │ 0-1-annual-probability-outputs… │
            │ 0-1-annual-probability-outputs… │
            │ 02a8c314-e726-44fb-88da-2e535e… │
            │ …                               │
            │ zoo-licensing-database          │
            │ zooplankton-abundance-data-der… │
            │ zooplankton-data-from-ring-net… │
            │ zoos-expert-committee-data      │
            │ zostera-descriptions-north-nor… │
            └─────────────────────

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                results = explore.get_package_list_dataframe('polars')
                print(results)

        if __name__ == "__main__":
            main()
        """
        if df_type.lower() not in ["pandas", "polars"]:
            raise ValueError(
                f"Invalid df_type: '{df_type}'. DataFrame type must be either 'pandas' or 'polars'."
            )

        url: str = self.cat_session.base_url + CkanApiPaths.PACKAGE_LIST

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()
            package_list: dict = data["result"]

            match df_type.lower():
                case "polars":
                    try:
                        return pl.DataFrame(package_list)
                    except ImportError:
                        raise ImportError(
                            "Polars is not installed. Please run 'pip install polars' to use this option."
                        )
                case "pandas":
                    try:
                        return pd.DataFrame(package_list)
                    except ImportError:
                        raise ImportError(
                            "Pandas is not installed. Please run 'pip install pandas' to use this option."
                        )
                case _:
                    raise ValueError(f"Unsupported DataFrame type: {df_type}")

        except (requests.RequestException, Exception) as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_organisation_list(self) -> Tuple[int, list]:
        """
        Returns the total number of organisations.

        Will return a list of maintainers if the org endpoint does not work.

        Returns:
            Tuple[int, list]

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                orgs_list = explore.get_organisation_list()
                print(orgs_list)

        if __name__ == "__main__":
            main()
        """
        url: str = self.cat_session.base_url + CkanApiPaths.ORGANIZATION_LIST

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()

            data = response.json()

            organisations: list = data["result"]
            length: int = len(organisations)

            return length, organisations
        except (requests.RequestException, Exception) as e:
            logger.warning(
                f"Primary organisation search method failed - attempting secondary method that fetches 'maintainers' only - this may still be useful but not as accurate: {e}"
            )
            try:
                # Secondary method using package endpoint
                package_url: str = (
                    self.cat_session.base_url
                    + CkanApiPaths.CURRENT_PACKAGE_LIST_WITH_RESOURCES
                )
                package_response = self.cat_session.session.get(package_url)
                package_response.raise_for_status()
                data = package_response.json()

                # Convert list of maintainers to a dictionary
                maintainers: list = list(
                    set(
                        entry.get("maintainer", "N/A")
                        for entry in data["result"]
                        if entry.get("maintainer")
                    )
                )
                length: int = len(maintainers)
                return length, maintainers

            except (requests.RequestException, Exception) as e:
                logger.error(f"Both organisation list methods failed: {e}")
                raise

    # ----------------------------
    # Show metadata using a package name
    # ----------------------------
    def show_package_info(
        self, package_name: Union[str, dict, Any], api_key=None
    ) -> List[Dict]:
        """
        Pass in a package name as a string or as a value from a dictionary.

        This will return package metadata including resource information and download links for the data.

        Args:
            package_name: Union[str, dict, Any]

        Returns:
            List[Dict]

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                all_packages = explore.package_list_dictionary()
                package = all_packages.get(insert_package_name)
                package_info = explore.show_package_info(package)
                print(package_info)

        if __name__ == "__main__":
            main()
        """

        if package_name is None:
            raise ValueError("package name cannot be none")

        base_url: str = self.cat_session.base_url + CkanApiPaths.PACKAGE_INFO

        params = {}
        if package_name:
            params["id"] = package_name

        url = f"{base_url}?{urlencode(params)}" if params else base_url

        try:
            headers = {}
            if api_key:
                headers["Authorization"] = api_key

            response = self.cat_session.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            result_data = data["result"]
            return self._extract_resource_data(result_data)

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def show_package_info_dataframe(
        self,
        package_name: Union[str, dict, Any],
        df_type: Literal["pandas", "polars"],
        api_key=None,
    ) -> pd.DataFrame | pl.DataFrame:
        """
        Pass in a package name as a string or as a value from a dictionary.

        This will return package metadata including resource information and download links for the data.

        Args:
            package_name: Union[str, dict, Any]
            df_type: Literal["pandas", "polars"]

        Returns:
            pd.DataFrame or pl.DataFrame

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = CkanCatExplorer(session)
                all_packages = explore.package_list_dictionary()
                package = all_packages.get("package_name")
                package_info = explore.show_package_info_dataframe(package, "pandas")
                print(package_info)

        if __name__ == "__main__":
            main()
        """

        if package_name is None:
            raise ValueError("package name cannot be none")

        base_url = self.cat_session.base_url + CkanApiPaths.PACKAGE_INFO
        params = {}
        if package_name:
            params["id"] = package_name
        url = f"{base_url}?{urlencode(params)}" if params else base_url

        try:
            headers = {}
            if api_key:
                headers["Authorization"] = api_key

            response = self.cat_session.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            result_data = data["result"]
            results = self._extract_resource_data(result_data)

            match df_type:
                case "pandas":
                    return pd.DataFrame(results)
                case "polars":
                    return pl.DataFrame(results)

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    # ----------------------------
    # Search Packages and store in DataFrames / or keep as Dicts.
    # Unpack data or keep it packed (e.g. don't split out resources into own columns)
    # ----------------------------
    def package_search(self, search_query: str, num_rows: int):
        """
        Returns all available data for a particular search query.

        Specify the number of rows if the 'count' is large.

        Args:
            search_query: str
            num_rows: int

        Returns:
            List[Dict]

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = hc.CkanCatExplorer(session)
                packages_search = explore.package_search("police", 50)
                print(packages_search)

        if __name__ =="__main__":
            main()
        """

        base_url = self.cat_session.base_url + CkanApiPaths.PACKAGE_SEARCH

        params = {}
        if search_query:
            params["q"] = search_query
            params["rows"] = num_rows

        url = f"{base_url}?{urlencode(params)}" if params else base_url

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()
            logger.success(f"Showing results for query: {search_query}")
            return data["result"]
        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def package_search_condense(
        self, search_query: str, num_rows: int
    ) -> Optional[List[Dict]]:
        """
        Args:
            search_query: str
            num_rows: int

        Returns:
            List[Dict]

        A more condensed view of package informaton focusing on:
            name
            number of resources
            notes
            resource:
                name
                created date
                format
                url to download

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.UK_GOV) as session:
                explore = hc.CkanCatExplorer(session)
                packages_search = explore.package_search_condense("police", 50)
                print(packages_search)

        if __name__ =="__main__":
            main()
        """
        base_url = self.cat_session.base_url + CkanApiPaths.PACKAGE_SEARCH

        params = {}
        if search_query:
            params["q"] = search_query
            params["rows"] = num_rows

        url = f"{base_url}?{urlencode(params)}" if params else base_url

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()

            # CKAN package_search returns: {"success": true, "result": {"count": X, "results": [...packages...]}}
            # Standard CKAN API uses "results" (plural) for the package list
            if "result" in data:
                if isinstance(data["result"], dict):
                    if "results" in data["result"]:
                        result_data = data["result"]["results"]
                    elif "result" in data["result"]:
                        result_data = data["result"]["result"]
                    else:
                        logger.warning(
                            f"Neither 'results' nor 'result' key found. Available keys: {list(data['result'].keys())}"
                        )
                        return []
                elif isinstance(data["result"], list):
                    result_data = data["result"]
                else:
                    logger.warning(f"Unexpected result type: {type(data['result'])}")
                    return []
            else:
                logger.warning("No 'result' key found in API response")
                return []

            logger.success(f"Showing results for query: {search_query}")

            return self._extract_condensed_package_data(
                result_data,
                ["name", "notes_markdown"],
                ["name", "created", "format", "url"],
            )

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def package_search_condense_dataframe(
        self,
        search_query: str,
        num_rows: int,
        df_type: Literal["pandas", "polars"] = "pandas",
    ) -> Union[pd.DataFrame, "pl.DataFrame"]:
        """
        Args:
            search_query: str
            num_rows: int
            df_type: Literal["pandas", "polars"]

        Returns:
            pd.DataFrame or pl.DataFrame

        A more condensed view of package informaton focusing on:
            name
            number of resources
            notes
            resource:
                name
                created date
                format
                url to download

        Specify the number of rows if the 'count' is large as the ouput is capped.

        The resources column is still nested.

        shape: (409, 4)
        ┌─────────────────────────────────┬────────────────┬───────────
        │ name                            ┆ notes_markdown ┆ num_resources ┆ resources                       │
        │ ---                             ┆ ---            ┆ ---           ┆ ---                             │
        │ str                             ┆ null           ┆ i64           ┆ list[struct[4]]                 │
        ╞═════════════════════════════════╪════════════════╪═══════════
        │ police-force1                   ┆ null           ┆ 3             ┆ [{"Police Force","2020-04-12T0… │
        │ police-stations-nsc             ┆ null           ┆ 5             ┆ [{null,"2015-05-29T16:11:17.58… │
        │ police-stations                 ┆ null           ┆ 2             ┆ [{"Police Stations","2016-01-1… │
        │ police-stations1                ┆ null           ┆ 8             ┆ [{"ArcGIS Hub Dataset","2019-0… │
        │ police-force-strength           ┆ null           ┆ 1             ┆ [{"Police force strength","202… │
        │ …                               ┆ …              ┆ …             ┆ …                               │
        │ crown_prosecution_service       ┆ null           ┆ 2             ┆ [{null,"2013-03-11T19:20:34.43… │
        │ register-of-geographic-codes-j… ┆ null           ┆ 1             ┆ [{"ArcGIS Hub Dataset","2024-0… │
        │ code-history-database-august-2… ┆ null           ┆ 1             ┆ [{"ArcGIS Hub Dataset","2024-0… │
        │ council-tax                     ┆ null           ┆ 3             ┆ [{"Council tax average per cha… │
        │ code-history-database-june-201… ┆ null           ┆ 1             ┆ [{"ArcGIS Hub Dataset","2024-0… │
        └─────────────────────────────────┴────────────────┴───────────

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.UK_GOV) as session:
                explorer = CkanCatExplorer(session)
                results = explorer.package_search_condense_dataframe('police', 500, "polars")
                print(results)

        if __name__ == "__main__":
            main()
        """
        if df_type.lower() not in ["pandas", "polars"]:
            raise ValueError(
                f"Invalid df_type: '{df_type}'. Must be either 'pandas' or 'polars'."
            )

        base_url = self.cat_session.base_url + CkanApiPaths.PACKAGE_SEARCH
        params = {}
        if search_query:
            params["q"] = search_query
            params["rows"] = num_rows

        url = f"{base_url}?{urlencode(params)}" if params else base_url
        logger.info(f"Making API request to: {url}")

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()

            # CKAN package_search returns: {"success": true, "result": {"count": X, "results": [...packages...]}}
            # Standard CKAN API uses "results" (plural) for the package list
            if "result" in data:
                if isinstance(data["result"], dict):
                    if "results" in data["result"]:
                        result_data = data["result"]["results"]
                    elif "result" in data["result"]:
                        result_data = data["result"]["result"]
                    else:
                        logger.warning(
                            f"Neither 'results' nor 'result' key found. Available keys: {list(data['result'].keys())}"
                        )
                        return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

                elif isinstance(data["result"], list):
                    result_data = data["result"]
                else:
                    logger.warning(f"Unexpected result type: {type(data['result'])}")
                    return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()
            else:
                logger.warning("No 'result' key found in API response")
                return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

            logger.success(f"Showing results for query: {search_query}")

            extracted_data = self._extract_condensed_package_data(
                result_data,
                ["name", "notes_markdown", "num_resources"],
                ["name", "created", "format", "url"],
            )

            if df_type.lower() == "polars":
                return pl.DataFrame(extracted_data)
            else:  # pandas
                return pd.DataFrame(extracted_data)

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def package_search_condense_dataframe_unpack(
        self,
        search_query: str,
        num_rows: int,
        df_type: Literal["pandas", "polars"] = "pandas",
    ) -> Union[pd.DataFrame, "pl.DataFrame"]:
        """
        Args:
            search_query: str
            num_rows: int
            df_type: Literal["pandas", "polars"]

        Returns:
            pd.DataFrame or pl.DataFrame

        A more condensed view of package informaton focusing on:
            name
            number of resources
            notes
            resource:
                name
                created date
                format
                url to download

        Specify the number of rows if the 'count' is large as the ouput is capped.

        The resources column is now unested so you can use specific dataset resources more easily.

        This will be a much larger df as a result - check the shape.

        shape: (2_593, 6)
        ┌─────────────────────────────┬────────────────┬─────────────────────────────┬─────────────────
        │ name                        ┆ notes_markdown ┆ resource_name               ┆ resource_created           ┆ resource_format ┆ resource_url               │
        │ ---                         ┆ ---            ┆ ---                         ┆ ---                        ┆ ---             ┆ ---                        │
        │ str                         ┆ null           ┆ str                         ┆ str                        ┆ str             ┆ str                        │
        ╞═════════════════════════════╪════════════════╪═════════════════════════════╪═════════════════
        │ police-force1               ┆ null           ┆ Police Force                ┆ 2020-04-12T08:28:35.449556 ┆ JSON            ┆ http://<div class="field   │
        │                             ┆                ┆                             ┆                            ┆                 ┆ field…                     │
        │ police-force1               ┆ null           ┆ List of neighbourhoods for  ┆ 2020-04-12T08:28:35.449564 ┆ JSON            ┆ http://<div class="field   │
        │                             ┆                ┆ the…                        ┆                            ┆                 ┆ field…                     │
        │ police-force1               ┆ null           ┆ Senior officers for the     ┆ 2020-04-12T08:28:35.449566 ┆ JSON            ┆ http://<div class="field   │
        │                             ┆                ┆ Cambri…                     ┆                            ┆                 ┆ field…                     │
        │ police-stations-nsc         ┆ null           ┆ null                        ┆ 2015-05-29T16:11:17.586034 ┆ HTML            ┆ http://data.n-somerset.gov │
        │                             ┆                ┆                             ┆                            ┆                 ┆ .uk/…                      │
        │ police-stations-nsc         ┆ null           ┆ null                        ┆ 2020-08-11T13:35:47.462440 ┆ CSV             ┆ http://data.n-somerset.gov │
        │                             ┆                ┆                             ┆                            ┆                 ┆ .uk/…                      │
        │ …                           ┆ …              ┆ …                           ┆ …                          ┆ …               ┆ …                          │
        │ code-history-database-augus ┆ null           ┆ ArcGIS Hub Dataset          ┆ 2024-05-31T19:06:58.646735 ┆ HTML            ┆ https://open-geography-por │
        │ t-2…                        ┆                ┆                             ┆                            ┆                 ┆ talx…                      │
        │ council-tax                 ┆ null           ┆ Council tax average per     ┆ 2017-07-20T08:21:23.185880 ┆ CSV             ┆ https://plymouth.thedata.p │
        │                             ┆                ┆ charge…                     ┆                            ┆                 ┆ lace…                      │
        │ council-tax                 ┆ null           ┆ Council Tax Band D amounts  ┆ 2017-07-20T08:26:28.314556 ┆ CSV             ┆ https://plymouth.thedata.p │
        │                             ┆                ┆ pai…                        ┆                            ┆                 ┆ lace…                      │
        │ council-tax                 ┆ null           ┆ Council Tax Collected as    ┆ 2017-07-20T15:23:26.889271 ┆ CSV             ┆ https://plymouth.thedata.p │
        │                             ┆                ┆ Perce…                      ┆                            ┆                 ┆ lace…                      │
        │ code-history-database-june- ┆ null           ┆ ArcGIS Hub Dataset          ┆ 2024-05-31T19:06:20.071480 ┆ HTML            ┆ https://open-geography-por │
        │ 201…                        ┆                ┆                             ┆                            ┆                 ┆ talx…                      │
        └─────────────────────────────┴────────────────┴─────────────────────────────┴─────────────────

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.UK_GOV) as session:
                explorer = CkanCatExplorer(session)
                results = explorer.package_search_condense_dataframe_unpacked('police', 500, "polars")
                print(results)

        if __name__ == "__main__":
            main()
        """
        if df_type.lower() not in ["pandas", "polars"]:
            raise ValueError(
                f"Invalid df_type: '{df_type}'. Must be either 'pandas' or 'polars'."
            )

        base_url = self.cat_session.base_url + CkanApiPaths.PACKAGE_SEARCH
        params = {}
        if search_query:
            params["q"] = search_query
            params["rows"] = num_rows
        url = f"{base_url}?{urlencode(params)}" if params else base_url

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()

            # CKAN package_search returns: {"success": true, "result": {"count": X, "results": [...packages...]}}
            # Standard CKAN API uses "results" (plural) for the package list
            if "result" in data:
                if isinstance(data["result"], dict):
                    if "results" in data["result"]:
                        result_data = data["result"]["results"]
                    elif "result" in data["result"]:
                        result_data = data["result"]["result"]
                    else:
                        logger.warning(
                            f"Neither 'results' nor 'result' key found. Available keys: {list(data['result'].keys())}"
                        )
                        return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

                elif isinstance(data["result"], list):
                    result_data = data["result"]
                else:
                    logger.warning(f"Unexpected result type: {type(data['result'])}")
                    return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()
            else:
                logger.warning("No 'result' key found in API response")
                return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

            logger.success(f"Showing results for query: {search_query}")

            extracted_data = self._extract_condensed_package_data(
                result_data,
                ["name", "notes_markdown"],
                ["name", "created", "format", "url"],
            )

            if df_type.lower() == "polars":
                return self._create_polars_dataframe(extracted_data)
            else:  # pandas
                return self._create_pandas_dataframe(extracted_data)

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    # ----------------------------
    # Extract information in preperation for Data Loader Class
    # TODO: Maybe we should move this to the data loader class itself???
    # ----------------------------
    def extract_resource_url(self, package_info: List[Dict]) -> List[str]:
        """
        Extracts the download inmformation for resources in a package.

        Tip: this accepts the output of show_package_info()

        Args:
            package_info: List[Dict]

        Returns:
            List[resource_name, resource_created, format, url]

        # Example:
        import HerdingCats as hc
        from pprint import pprint

        def main():
            with hc.CatSession(hc.CkanDataCatalogues.LONDON_DATA_STORE) as session:
                explore = hc.CkanCatExplorer(session)
                package = explore.show_package_info(insert_package_name)
                urls = explore.extract_resource_url(package)
                pprint(urls)

        if __name__ =="__main__":
            main()
        """

        results = []
        for item in package_info:
            resource_name = item.get("resource_name")
            created = item.get("resource_created")
            url = item.get("resource_url")
            format = item.get("resource_format")
            if all([resource_name, created, format, url]):
                logger.success(
                    f"Found URL for resource '{resource_name}'. Format is: {format}"
                )
                results.append([resource_name, created, format, url])
            else:
                logger.warning(
                    f"Resource '{resource_name}' found in package, but no URL available"
                )
        return results

    # ----------------------------
    # Helper Methods
    # Flatten nested data structures
    # Extract specific fields from a package
    # ----------------------------
    @staticmethod
    def _extract_condensed_package_data(
        data: List[Dict[str, Any]], base_fields: List[str], resource_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Static method to extract specified fields from Package Search dataset entries and their resources.

        Args:
            data (List[Dict[str, Any]]): List of dataset entries.
            base_fields (List[str]): List of field names to extract from each entry.
            resource_fields (List[str]): List of field names to extract from each resource section.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing extracted data.

        Example output:
            [{'name': 'police-force-strength',
            'notes_markdown': 'Numbers of police officers, police civilian staff, and '
                                'Police Community Support Officers in the Metropolitan '
                                "Police Force. Figures are reported by MOPAC to the GLA's "
                                'Police and Crime Committee each month. The figures are '
                                'full-time equivalent figures (FTE) in order to take '
                                'account of part-time working, job sharing etc, and do not '
                                'represent a measure of headcount.
                                'For more information, click here and here.',
            'num_resources': 1,
            'resources': [{'created': '2024-08-28T16:15:59.080Z',
                            'format': 'csv',
                            'name': 'Police force strength',
                            'url': 'https://airdrive-secure.s3-eu-west-1.amazonaws.com/
                            london/dataset/police-force-strength/2024-08-28T16%3A15%3A56/
                            Police_Force_Strength.csv'}]}
        """
        return [
            {
                **{field: entry.get(field) for field in base_fields},
                "resources": [
                    {
                        resource_field: resource.get(resource_field)
                        for resource_field in resource_fields
                    }
                    for resource in entry.get("resources", [])
                ],
            }
            for entry in data
        ]

    @staticmethod
    def _create_pandas_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Creates a pandas dataframe from the data.
        """
        df = pd.json_normalize(
            data,
            record_path="resources",
            meta=["name", "notes_markdown"],
            record_prefix="resource_",
        )
        return df

    @staticmethod
    def _create_polars_dataframe(data: List[Dict[str, Any]]) -> pl.DataFrame:
        """
        Creates a polars dataframe from the data.
        """
        df = pl.DataFrame(data)
        return (
            df.explode("resources")
            .with_columns(
                [
                    pl.col("resources").struct.field(f).alias(f"resource_{f}")
                    for f in ["name", "created", "format", "url"]
                ]
            )
            .drop("resources", "num_resources")
        )

    @staticmethod
    def _extract_resource_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts specific fields for a specific package and creates a list of dictionaries,
        one for each resource, containing the specified fields.

        Args:
        data (Dict[str, Any]): The input package data dictionary.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the specified fields for a resource.
        """

        group_names = (
            [group["name"] for group in data.get("groups", [])]
            if data.get("groups")
            else None
        )

        base_fields = {
            "name": data.get("name"),
            "maintainer": data.get("maintainer"),
            "maintainer_email": data.get("maintainer_email"),
            "notes_markdown": data.get("notes_markdown"),
            "groups": group_names,
        }

        resource_fields = ["url", "name", "format", "created", "last_modified"]

        result = []
        for resource in data.get("resources", []):
            resource_data = base_fields.copy()
            for field in resource_fields:
                resource_data[f"resource_{field}"] = resource.get(field)
            result.append(resource_data)

        return result


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For DataPress Catalogues Only
class DataPressCatExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession.

        Allows user to start exploring data catalogue programatically.

        Make sure you pass a valid DataPressCatSession in - it will check if the catalogue type is right.

        Args:
            DataPressCatSession

        Returns:
            DataPressCatExplorer

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.DataPressCatalogues.NORTHERN_DATA_MILL) as session:
                explore = hc.DataPressCatExplorer(session)

        if __name__ == "__main__":
            main()
        """

        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.DATA_PRESS),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.DATA_PRESS:
            raise WrongCatalogueError(
                "Invalid catalogue type. DataPressCatExplorer requires a DataPress catalogue session.",
                expected_catalogue=str(CatalogueType.DATA_PRESS),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check DataPress site health
    # ----------------------------
    def check_site_health(self) -> None:
        """
        Make sure the DataPress endpoints are healthy and reachable.

        This calls the DataPress package_list endpoint to check if the site is still reacheable.

        Returns:
            Success message if the site is healthy
            Error message if the site is not healthy

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.DataPressCatalogues.NORTHERN_DATA_MILL) as session:
                explore = hc.DataPressCatExplorer(session)
                health_check = explore.check_site_health()

        if __name__ == "__main__":
            main()
        """

        url: str = self.cat_session.base_url + DataPressApiPaths.PACKAGE_INFO.format(
            "20jl1"
        )

        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    logger.success(
                        "Health Check Passed: DataPress is running and available"
                    )
                else:
                    logger.warning(
                        "Health Check Warning: DataPress responded with an empty dataset"
                    )
            else:
                logger.error(
                    f"Health Check Failed: DataPress responded with status code {response.status_code}"
                )

        except requests.RequestException as e:
            logger.error(
                f"Health Check Failed: Unable to connect to DataPress - {str(e)}"
            )

    # ----------------------------
    # Get datasets available
    # ----------------------------
    def get_all_datasets(self) -> dict:
        """
        Fetch all datasets from a DataPress catalogue and return a dictionary of title:id.

        Returns:
            dict: Dictionary with dataset titles as keys and dataset IDs as values
        """
        try:
            endpoint = self.cat_session.base_url + DataPressApiPaths.SHOW_ALL_CATALOGUES

            response = self.cat_session.session.get(endpoint)
            response.raise_for_status()

            datasets = response.json()

            # Build the dictionary: title -> id
            return {
                dataset["title"]: dataset["id"]
                for dataset in datasets
                if "title" in dataset and "id" in dataset
            }

        except Exception as e:
            logger.error(f"Error fetching datasets from DataPress: {str(e)}")
            raise CatExplorerError(f"Error fetching datasets from DataPress: {str(e)}")

    def get_dataset_by_id(self, dataset_id: str) -> dict:
        """
        Fetch the metadata for the given dataset_id.

        Args:
            dataset_id: The dataset id to look up.

        Returns:
            dict: dataset object for that id

        Raises:
            CatExplorerError: if no dataset with that id is found.
        """

        url: str = self.cat_session.base_url + DataPressApiPaths.PACKAGE_INFO.format(
            dataset_id
        )

        try:
            response = requests.get(url)
            data = response.json()
            return data
        except Exception as e:
            logger.error(
                f"Error fetching dataset {dataset_id} from DataPress: {str(e)}"
            )
            raise CatExplorerError(
                f"Error fetching dataset {dataset_id} from DataPress: {str(e)}"
            )

    # ----------------------------
    # Get resources available
    # ----------------------------
    def get_resource_by_dataset_id(self, dataset_id: str):
        url: str = self.cat_session.base_url + DataPressApiPaths.PACKAGE_INFO.format(
            dataset_id
        )

        try:
            response = requests.get(url)
            data = response.json()
            resources = data["resources"]
            return resources
        except Exception as e:
            logger.error(
                f"Error fetching dataset {dataset_id} from DataPress: {str(e)}"
            )
            raise CatExplorerError(
                f"Error fetching dataset {dataset_id} from DataPress: {str(e)}"
            )

    # ----------------------------
    # Export resource links for a dataset
    # ----------------------------
    def get_resource_export_links(self, resource_info: dict) -> list[list[str]] | None:
        """
        Returns a list of resource export links for a dataset.

        Args:
            resource_info (dict): A dictionary containing resource information.

        Returns:
            list: A list of resource export links.
        """
        try:
            resources = resource_info
            export_links = [
                [resource["format"], resource["url"]] for resource in resources.values()
            ]
            return export_links
        except Exception as e:
            logger.error(f"Error fetching resource links: {str(e)}")


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For Open Datasoft Catalogues Only
class OpenDataSoftCatExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession

        Allows user to start exploring data catalogue programatically

        Make sure you pass a valid CkanCatSession in - checks if the right type.

        Args:
            CkanCatSession

        # Example usage...
        if __name__ == "__main__":
            with hc.CatSession(hc.OpenDataSoftDataCatalogues.UK_POWER_NETWORKS) as session:
                explore = CatExplorer(session)
        """

        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.OPENDATA_SOFT),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.OPENDATA_SOFT:
            raise WrongCatalogueError(
                "Invalid catalogue type. OpenDataSoft requires an OpenDataSoft catalogue session.",
                expected_catalogue=str(CatalogueType.OPENDATA_SOFT),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check OpenDataSoft site health
    # ----------------------------
    def check_site_health(self) -> None:
        """
        Make sure the Ckan endpoints are healthy and reachable

        This calls the Ckan package_list endpoint to check if site is still reacheable.

        # Example usage...
        if __name__ == "__main__":
            with hc.CatSession(hc.OpenDataSoftDataCatalogues.UK_POWER_NETWORKS) as session:
                explore = CkanCatExplorer(session)
                health_check = explore.check_site_health()
        """

        url = self.cat_session.base_url + OpenDataSoftApiPaths.SHOW_DATASETS
        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    logger.success(
                        "Health Check Passed: OpenDataSoft is running and available"
                    )
                else:
                    logger.warning(
                        "Health Check Warning: OpenDataSoft responded with an empty dataset"
                    )
            else:
                logger.error(
                    f"Health Check Failed: OpenDataSoft responded with status code {response.status_code}"
                )

        except requests.RequestException as e:
            logger.error(
                f"Health Check Failed: Unable to connect to OpenDataSoft - {str(e)}"
            )

    # ----------------------------
    # Get all datasets available on the catalogue
    # ----------------------------
    def fetch_all_datasets(self) -> dict | None:
        urls = [
            self.cat_session.base_url + OpenDataSoftApiPaths.SHOW_DATASETS,
            self.cat_session.base_url + OpenDataSoftApiPaths.SHOW_DATASETS_2,
        ]
        dataset_dict = {}
        total_count = 0

        for url in urls:
            offset = 0
            limit = 100

            try:
                while True:
                    params = {"offset": offset, "limit": limit}
                    response = self.cat_session.session.get(url, params=params)

                    if response.status_code == 400 and url == urls[0]:
                        logger.warning(
                            "SHOW_DATASETS endpoint returned 400 status. Trying SHOW_DATASETS_2."
                        )
                        break  # Break the inner loop to try the next URL

                    response.raise_for_status()
                    result = response.json()

                    for dataset_info in result.get("datasets", []):
                        if (
                            "dataset" in dataset_info
                            and "metas" in dataset_info["dataset"]
                            and "default" in dataset_info["dataset"]["metas"]
                            and "title" in dataset_info["dataset"]["metas"]["default"]
                            and "dataset_id" in dataset_info["dataset"]
                        ):
                            title = dataset_info["dataset"]["metas"]["default"]["title"]
                            dataset_id = dataset_info["dataset"]["dataset_id"]
                            dataset_dict[title] = dataset_id

                    # Update total_count if available
                    if "total_count" in result:
                        total_count = result["total_count"]

                    # Check if we've reached the end of the datasets
                    if len(result.get("datasets", [])) < limit:
                        break
                    offset += limit

                # If we've successfully retrieved datasets, no need to try the second URL
                if dataset_dict:
                    break

            except requests.RequestException as e:
                if url == urls[-1]:
                    logger.error(f"Failed to fetch datasets: {e}")
                    raise CatExplorerError(f"Failed to fetch datasets: {str(e)}")
                else:
                    logger.warning(
                        f"Failed to fetch datasets from {url}: {e}. Trying next URL."
                    )

        if dataset_dict:
            returned_count = len(dataset_dict)
            if returned_count == total_count:
                logger.success(f"Total Datasets Found: {total_count}")
            else:
                logger.warning(
                    f"WARNING MISMATCH: total_count = {total_count}, returned_count = {returned_count} - please raise an issue"
                )
            return dataset_dict
        else:
            logger.warning("No datasets were retrieved.")
            return None

    # ----------------------------
    # Get metadata about specific datasets in the catalogue
    # ----------------------------
    def show_dataset_info(self, dataset_id):
        urls = [
            self.cat_session.base_url
            + OpenDataSoftApiPaths.SHOW_DATASET_INFO.format(dataset_id),
            self.cat_session.base_url
            + OpenDataSoftApiPaths.SHOW_DATASET_INFO.format(dataset_id),
        ]
        last_error = []
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                return data
            except requests.RequestException as e:
                last_error = e
                continue
        error_msg = f"\033[91mFailed to fetch dataset: {str(last_error)}. Are you sure this dataset exists? Check again.\033[0m"
        raise CatExplorerError(error_msg)

    # ----------------------------
    # Show what export file types are available for a particular dataset
    # ----------------------------
    def show_dataset_export_options(self, dataset_id):
        urls = [
            self.cat_session.base_url
            + OpenDataSoftApiPaths.SHOW_DATASET_EXPORTS.format(dataset_id),
            self.cat_session.base_url
            + OpenDataSoftApiPaths.SHOW_DATASET_EXPORTS_2.format(dataset_id),
        ]
        last_error = []
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                # Extract download links and formats
                export_options = []
                for link in data["links"]:
                    if link["rel"] != "self":
                        export_options.append(
                            {"format": link["rel"], "download_url": link["href"]}
                        )

                return export_options

            except requests.RequestException as e:
                last_error = e
                continue

        error_msg = f"\033[91mFailed to fetch dataset: {str(last_error)}. Are you sure this dataset exists? Check again.\033[0m"
        raise CatExplorerError(error_msg)


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For French Gouv data catalogue Only
class FrenchGouvCatExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession

        Allows user to start exploring data catalogue programatically

        Make sure you pass a valid CkanCatSession in - checks if the right type.

        Args:
            CkanCatSession

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                explore = hc.FrenchGouvCatExplorer(session)
                dataset = explore.get_all_datasets()
                print(dataset)

        if __name__ =="__main__":
            main()
        """

        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.GOUV_FR),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.GOUV_FR:
            raise WrongCatalogueError(
                "Invalid catalogue type. FrenchGouvCatExplorer requires a French Government catalogue session.",
                expected_catalogue=str(CatalogueType.GOUV_FR),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check French Gouv site health
    # ----------------------------
    def check_health_check(self) -> None:
        """
        Check the health of the french government's opendata catalogue endpoint
        """

        url = self.cat_session.base_url + FrenchGouvApiPaths.SHOW_DATASETS
        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    logger.success(
                        "Health Check Passed: French Gouv is running and available"
                    )
                else:
                    logger.warning(
                        "Health Check Warning: French Gouv responded with an empty dataset"
                    )
            else:
                logger.error(
                    f"Health Check Failed: French Gouv responded with status code {response.status_code}"
                )

        except requests.RequestException as e:
            logger.error(
                f"Health Check Failed: Unable to connect to French Gouv - {str(e)}"
            )

    # ----------------------------
    # Get datasets available
    # ----------------------------
    def get_all_datasets(self) -> dict:
        """
        Uses DuckDB to read a Parquet file of whole French Gouv data catalogue and create a dictionary of slugs and IDs.

        Returns:
            dict: Dictionary with slugs as keys and dataset IDs as values

        Example usage:

            import HerdingCats as hc

            from pprint import pprint

            def main():
                with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                    explore = hc.FrenchGouvCatExplorer(session)
                    dataset = explore.get_all_datasets()
                    pprint(dataset)

            if __name__ =="__main__":
                main()
        """

        try:
            catalogue = FrenchGouvApiPaths.CATALOGUE
            catalogue_data = self.get_dataset_meta(catalogue)
            catalogue_resource = self.get_dataset_resource_meta(catalogue_data)

            if not catalogue_resource:
                logger.error("No resources found in the catalogue.")
                raise CatExplorerError("No resources found in the catalogue.")

            # Filter for Parquet resources so we get the most recent one
            # This has the most recent catalogue data
            parquet_resources = [
                resource
                for resource in catalogue_resource
                if resource.get("resource_extras", {}).get(
                    "analysis:parsing:parquet_url"
                )
            ]

            if not parquet_resources:
                logger.error("No Parquet resources found in the catalogue.")
                raise CatExplorerError("No Parquet resources found in the catalogue.")

            parquet_resources.sort(key=lambda x: x.get("resource_last_modified", ""))

            download_url = parquet_resources[0]["resource_extras"][
                "analysis:parsing:parquet_url"
            ]

            with duckdb.connect(":memory:") as con:
                # Install and load httpfs extension
                con.execute("INSTALL httpfs;")
                con.execute("LOAD httpfs;")

                # Query to select only id and slug, converting to dict format
                query = """
                SELECT DISTINCT slug, id
                FROM read_parquet(?)
                WHERE slug IS NOT NULL AND id IS NOT NULL
                """

                # Execute query and fetch results
                result = con.execute(query, parameters=[download_url]).fetchall()

                # Convert results to dictionary
                datasets = {slug: id for slug, id in result}
            return datasets

        except Exception as e:
            logger.error(f"Error processing parquet file: {str(e)}")
            raise CatExplorerError(f"Error processing parquet file: {str(e)}")

    def search_datasets(self, query: str) -> list[dict]:
        """
        Fetches a list of datasets using a search query.

        Args:
            query (str): Search query to fetch

        Returns:
            list[dict]: List of dataset details

        Example query:
            "population"

        # Example usage...
        import HerdingCats as hc
        from pprint import pprint

        def main():
            with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                explore = hc.FrenchGouvCatExplorer(session)
                datasets = explore.search_datasets("population")
                pprint(datasets)

        if __name__ =="__main__":
            main()
        """
        try:
            # Construct URL for specific dataset
            url = (
                self.cat_session.base_url
                + FrenchGouvApiPaths.SEARCH_DATASETS
                + f"?q={query}"
            )

            # Make request
            response = self.cat_session.session.get(url)

            # Handle response
            if response.status_code == 200:
                data = response.json()
                # Adjust the key as per actual API response structure
                results = data.get(
                    "data", data.get("results", data.get("datasets", []))
                )
                logger.success(f"Found {len(results)} datasets for query '{query}'")
                return results
            else:
                logger.error(
                    f"Failed to search datasets with status code {response.status_code}"
                )
                return []
        except Exception as e:
            logger.error(f"Error searching datasets with query '{query}': {str(e)}")
            return []

    # ----------------------------
    # Get metadata for a specific datasets
    # ----------------------------
    def get_dataset_meta(self, identifier: str) -> dict:
        """
        Fetches a metadata for a specific dataset using either its ID or slug.

        Args:
            identifier (str): Dataset ID or slug to fetch

        Returns:
            dict: Dataset details or empty dict if not found

        Example identifier:
            ID: "674de63d05a9bbeddc66bdc1"

        # Example usage...
        import HerdingCats as hc
        from pprint import pprint

        def main():
            with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                explore = hc.FrenchGouvCatExplorer(session)
                meta = explore.get_dataset_meta("5552083b88ee381e451c0bf3")
                pprint(meta)

        if __name__ =="__main__":
            main()
        """
        try:
            # Construct URL for specific dataset
            url = (
                self.cat_session.base_url
                + FrenchGouvApiPaths.SHOW_DATASETS_BY_ID.format(identifier)
            )

            # Make request
            response = self.cat_session.session.get(url)

            # Handle response
            if response.status_code == 200:
                data = response.json()
                resource_title = data.get("title")
                resource_id = data.get("id")
                logger.success(
                    f"Successfully retrieved dataset: {resource_title} - ID: {resource_id}"
                )
                return data
            elif response.status_code == 404:
                logger.warning(f"Dataset not found: {identifier}")
                return {}
            else:
                logger.error(
                    f"Failed to fetch dataset {identifier} with status code {response.status_code}"
                )
                return {}

        except Exception as e:
            logger.error(f"Error fetching dataset {identifier}: {str(e)}")
            return {}

    def get_dataset_meta_dataframe(
        self, identifier: str, df_type: Literal["pandas", "polars"]
    ) -> pd.DataFrame | pl.DataFrame:
        """
        Fetches a metadata for a specific dataset using either its ID or slug.

        Args:
            identifier (str): Dataset ID or slug to fetch

        Returns:
            dict: Dataset details or empty dict if not found

        Example identifier:
            ID: "674de63d05a9bbeddc66bdc1"

        # Example usage...
        import HerdingCats as hc
        from pprint import pprint

        def main():
            with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                explore = hc.FrenchGouvCatExplorer(session)
                meta = explore.get_dataset_meta_dataframe("5552083b88ee381e451c0bf3")
                pprint(meta)

        if __name__ =="__main__":
            main()
        """
        try:
            url = (
                self.cat_session.base_url
                + FrenchGouvApiPaths.SHOW_DATASETS_BY_ID.format(identifier)
            )
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                resource_title = data.get("title")
                resource_id = data.get("id")
                logger.success(
                    f"Successfully retrieved dataset: {resource_title} - ID: {resource_id}"
                )
                match df_type:
                    case "pandas":
                        return pd.DataFrame([data])
                    case "polars":
                        return pl.DataFrame([data])
            elif response.status_code == 404:
                logger.warning("Dataset not found")
                return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()
            else:
                logger.error(
                    f"Failed to fetch dataset with status code {response.status_code}"
                )
                return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching dataset: {str(e)}")
            return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

    def get_multiple_datasets_meta(self, identifiers: list) -> dict:
        """
        Fetches multiple datasets using a list of IDs or slugs.

        Args:
            identifiers (list): List of dataset IDs or slugs to fetch

        Returns:
            dict: Dictionary mapping identifiers to their dataset details

        import HerdingCats as hc
        from pprint import pprint

        def main():
            with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                explore = hc.FrenchGouvCatExplorer(session)
                identifiers = ['674de63d05a9bbeddc66bdc1', '5552083b88ee381e451c0bf3']
                meta = explore.get_multiple_datasets_meta(identifiers)
                pprint(meta)

        if __name__ =="__main__":
            main()
        """
        results = {}

        for identifier in identifiers:
            try:
                dataset = self.get_dataset_meta(identifier)
                if dataset:
                    results[identifier] = dataset
            except Exception as e:
                logger.error(f"Error processing identifier {identifier}: {str(e)}")
                results[identifier] = {}
        logger.success(f"Finished fetching {len(results)} datasets")
        return results

    # ----------------------------
    # Show available resource data for a particular dataset
    # ----------------------------
    def get_dataset_resource_meta(self, data: dict) -> List[Dict[str, Any]] | None:
        """
        Fetches metadata for a specific resource within a dataset.

        Args:
            Dict with dataset meta info

        Returns:
            dict: Resource details or empty dict if not found
        """
        if len(data) == 0:
            raise ValueError("Data can't be empty!")

        resource_title = data.get("resource_title")
        resource_id = data.get("resource_id")

        try:
            result = self._extract_resource_data(data)
            return result
        except Exception:
            logger.error(f"Error fetching {resource_title}. Id number: :{resource_id}")

    def get_dataset_resource_meta_dataframe(
        self, data: dict, df_type: Literal["pandas", "polars"]
    ) -> pd.DataFrame | pl.DataFrame:
        """
        Fetches export data for a specific resource within a dataset.

        Args:
            data (dict): Input data dictionary
            df_type (Literal["pandas", "polars"]): Type of DataFrame to return
        Returns:
            pd.DataFrame | pl.DataFrame: Resource details with resource_extras as a column
        """
        if len(data) == 0:
            raise ValueError("Data can't be empty!")

        resource_title = data.get("resource_title")
        resource_id = data.get("resource_id")

        try:
            # Get the extracted data
            result = self._extract_resource_data(data)
            # Create DataFrame based on type
            match df_type:
                case "pandas":
                    return pd.DataFrame(result)
                case "polars":
                    return pl.DataFrame(result)
        except Exception:
            logger.error(f"Error fetching {resource_title}. Id number: :{resource_id}")
            return pd.DataFrame() if df_type == "pandas" else pl.DataFrame()

    # ----------------------------
    # Show all organisation available
    # ----------------------------
    def get_all_organisations(self) -> dict:
        """
        Uses DuckDB to read a Parquet file of whole French Gouv data catalogue and create a dictionary of organisation names and IDs.

        Returns:
            dict: Dictionary with organisation names as keys and organisation IDs as values

        Example usage:

            import HerdingCats as hc

            from pprint import pprint

            def main():
                with hc.CatSession(hc.FrenchGouvCatalogue.GOUV_FR) as session:
                    explore = hc.FrenchGouvCatExplorer(session)
                    dataset = explore.get_all_datasets()
                    pprint(dataset)

            if __name__ =="__main__":
                main()
        """

        try:
            catalogue = FrenchGouvApiPaths.CATALOGUE
            catalogue_data = self.get_dataset_meta(catalogue)
            catalogue_resource = self.get_dataset_resource_meta(catalogue_data)

            if not catalogue_resource:
                logger.error("No resources found in the catalogue.")
                raise CatExplorerError("No resources found in the catalogue.")

            # Filter for Parquet resources so we get the most recent one
            # This has the most recent catalogue data
            parquet_resources = [
                resource
                for resource in catalogue_resource
                if resource.get("resource_extras", {}).get(
                    "analysis:parsing:parquet_url"
                )
            ]

            if not parquet_resources:
                logger.error("No Parquet resources found in the catalogue.")
                raise CatExplorerError("No Parquet resources found in the catalogue.")

            parquet_resources.sort(key=lambda x: x.get("resource_last_modified", ""))

            download_url = parquet_resources[0]["resource_extras"][
                "analysis:parsing:parquet_url"
            ]

            with duckdb.connect(":memory:") as con:
                # Install and load httpfs extension
                con.execute("INSTALL httpfs;")
                con.execute("LOAD httpfs;")

                query = """
                SELECT DISTINCT organization, organization_id
                FROM read_parquet(?)
                WHERE organization IS NOT NULL AND organization_id IS NOT NULL
                """
                # Execute query and fetch results
                result = con.execute(query, parameters=[download_url]).fetchall()
                # Convert results to dictionary
                organisations = {
                    organization: organization_id
                    for organization, organization_id in result
                }

            return organisations

        except Exception as e:
            logger.error(f"Error processing parquet file: {str(e)}")
            raise CatExplorerError(f"Error processing parquet file: {str(e)}")

    # ----------------------------
    # Helper function to flatten meta data
    # ----------------------------
    @staticmethod
    def _extract_resource_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts specific fields for a specific package and creates a list of dictionaries,
        one for each resource, containing the specified fields.

        Args:
        data (Dict[str, Any]): The input package data dictionary.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the specified fields for a resource.
        """
        try:
            base_fields = {
                "dataset_id": data.get("id"),
                "slug": data.get("slug"),
            }

            resource_fields = [
                "created_at",
                "id",
                "format",
                "url",
                "title",
                "latest",
                "last_modified",
                "frequency",
                "extras",
            ]

            result = []
            for resource in data.get("resources", []):
                resource_data = base_fields.copy()
                for field in resource_fields:
                    resource_data[f"resource_{field}"] = resource.get(field)
                result.append(resource_data)

            return result
        except Exception as e:
            raise e


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For ONS Nomis data catalogue Only
class ONSNomisCatExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession

        Allows user to start exploring data catalogue programatically
        """
        # Check if the CatSession has a catalogue_type attribute
        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.ONS_NOMIS),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.ONS_NOMIS:
            raise WrongCatalogueError(
                "Invalid catalogue type. ONSNomisCatExplorer requires a ONS Nomis catalogue session.",
                expected_catalogue=str(CatalogueType.ONS_NOMIS),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check Nomis site health
    # ----------------------------
    def check_health_check(self) -> bool:
        """Check the health of the Nomis catalogue endpoint"""

        url = self.cat_session.base_url + ONSNomisApiPaths.SHOW_DATASETS
        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                logger.success("Health Check Passed: Nomisis running and available")
                return True
            else:
                logger.error(
                    f"Health Check Failed: Nomis responded with status code {response.status_code}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Health Check Failed: Unable to connect to Nomis {str(e)}")
            return False

    # ----------------------------
    # Explore the Nomis data catalogue
    # ----------------------------
    def get_all_datasets(self) -> list[dict]:
        """
        Get all the datasets from the Nomis data catalogue

        Returns:
            list: List of dictionaries containing dataset information (id and name)
        """
        url: str = self.cat_session.base_url + ONSNomisApiPaths.SHOW_DATASETS
        datasets = []

        try:
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()

            if (
                "structure" in data
                and "keyfamilies" in data["structure"]
                and "keyfamily" in data["structure"]["keyfamilies"]
            ):
                key_families = data["structure"]["keyfamilies"]["keyfamily"]

                # Loop through each keyfamily
                for key_family in key_families:
                    # Extract the ID
                    dataset_id = key_family.get("id", "No ID available")

                    # Extract the name (if it exists)
                    name = "No name available"
                    if "name" in key_family and "value" in key_family["name"]:
                        name = key_family["name"]["value"]

                    # Add to our results list
                    datasets.append({"id": dataset_id, "name": name})

            return datasets
        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_dataset_info(self, dataset_id: str) -> dict:
        """
        Get the metadata for a specific dataset

        Args:
            dataset_id (str): The ID of the dataset to fetch

        Returns:
            dict: Dictionary containing dataset metadata
        """
        try:
            url: str = (
                self.cat_session.base_url
                + ONSNomisApiPaths.SHOW_DATASET_INFO.format(dataset_id)
            )
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    # ----------------------------
    # Get the codelists for a specific dataset and their values
    # ----------------------------
    def get_dataset_codelist(self, dataset_id: str) -> list:
        """
        Get the codelist values for a specific dataset

        Args:
            dataset_id (str): The ID of the dataset to fetch

        Returns:
            list: List of codelist values
        """

        # Final codelists values to return
        codelist_values = []

        try:
            url: str = (
                self.cat_session.base_url
                + ONSNomisApiPaths.SHOW_DATASET_INFO.format(dataset_id)
            )
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            data = response.json()

            structure = data.get("structure", {})
            keyfamilies = structure.get("keyfamilies", {}).get("keyfamily", [])

            if not isinstance(keyfamilies, list):
                keyfamilies = [keyfamilies]

            # Process each keyfamily
            for keyfamily in keyfamilies:
                components = keyfamily.get("components", {})

                dimensions = components.get("dimension", [])
                if not isinstance(dimensions, list):
                    dimensions = [dimensions]

                for dim in dimensions:
                    if "codelist" in dim:
                        codelist_values.append(dim.get("codelist"))

                attributes = components.get("attribute", [])
                if not isinstance(attributes, list):
                    attributes = [attributes]

                for attr in attributes:
                    if "codelist" in attr:
                        codelist_values.append(attr.get("codelist"))

                time_dimension = components.get("timedimension", {})
                if time_dimension and "codelist" in time_dimension:
                    codelist_values.append(time_dimension.get("codelist"))

            return codelist_values

        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_codelist_meta_info(self, codelist_id: str) -> dict:
        """
        Get the metadata for a specific codelist

        Args:
            codelist_id (str): The ID of the codelist to fetch

        Returns:
            dict: Dictionary containing codelist metadata
        """
        try:
            url: str = (
                self.cat_session.base_url
                + ONSNomisApiPaths.SHOW_CODELIST_DETAILS.format(codelist_id)
            )
            response = self.cat_session.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_codelist_values(self, data: Dict[str, Any]) -> Dict[str, List[int]]:
        """
        Extract all unique geography types and their corresponding value codes in one pass.

        Args:
            data: A dictionary containing the structured data

        Returns:
            A dictionary mapping geography types to their value codes
        """
        type_to_codes = {}

        try:
            if "structure" in data and "codelists" in data["structure"]:
                codelists = data["structure"]["codelists"].get("codelist", [])

                # Process each codelist
                for codelist in codelists:
                    # Get codes from the codelist
                    codes = codelist.get("code", [])

                    # Process each code
                    for code in codes:
                        if (
                            "annotations" in code
                            and "annotation" in code["annotations"]
                            and "value" in code
                        ):
                            annotations = code["annotations"]["annotation"]
                            geography_type = None

                            # Find the geography type in annotations
                            for annotation in annotations:
                                if annotation.get("annotationtitle") == "TypeName":
                                    geography_type = annotation.get("annotationtext")
                                    break

                            # If we found a geography type and have a value, add it to our mapping
                            if geography_type and "value" in code:
                                if geography_type not in type_to_codes:
                                    type_to_codes[geography_type] = []

                                value_code = code["value"]
                                if value_code not in type_to_codes[geography_type]:
                                    type_to_codes[geography_type].append(value_code)
        except (KeyError, TypeError) as e:
            print(f"Error processing data structure: {e}")

        return type_to_codes

    # ----------------------------
    # Generate download URLs
    # ----------------------------
    def generate_full_dataset_download_url(
        self,
        dataset_id: str,
        geography_codes: List[int] | None = None,
    ) -> str:
        """
        Generate a download URL for a specific dataset with optional geography codes or template.

        This will always download the latest data for the dataset.

        Args:
            dataset_id (str): The ID of the dataset to download
            geography_codes (List[int], optional): List of geography codes to filter the data
            geography_template (ONSNomisGeographyTemplates, optional):
            Geography template to filter the data (only used if geography_codes is None)

        Returns:
            str: The complete download URL

        Example:
            >>> # Using geography codes list
            >>> explorer.generate_full_dataset_download_url(
            ...     "NM_2077_1",
            ...     geography_codes=[2042626049, 2042626050, 2042626051]
            ... )
        """
        base_url: str = (
            self.cat_session.base_url
            + ONSNomisApiPaths.GENERATE_LATEST_DATASET_DOWNLOAD_URL.format(
                dataset_id, ""
            )
        )

        if geography_codes:
            # Convert list of codes to comma-separated string and add to URL
            geo_codes_str = ",".join(map(str, geography_codes))
            base_url += ONSNomisQueryParams.GEOGRAPHY + geo_codes_str
        return base_url


# FIND THE DATA YOU WANT / NEED / ISOLATE PACKAGES AND RESOURCES
# For ONS Geo Catalogue Only
class ONSGeoExplorer:
    def __init__(self, cat_session: CatSession):
        """
        Takes in a CatSession.

        Allows user to start exploring data catalogue programatically.

        Make sure you pass a valid ONSGeoSession in - it will check if the catalogue type is right.

        Args:
            ONSGeoSession

        Returns:
            ONSGeoExplorer

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                print("connected")
        if __name__ == "__main__":
            main()
        """

        if not hasattr(cat_session, "catalogue_type"):
            raise WrongCatalogueError(
                "CatSession missing catalogue_type attribute",
                expected_catalogue=str(CatalogueType.ONS_GEO_PORTAL),
                received_catalogue="Unknown",
            )

        if cat_session.catalogue_type != CatalogueType.ONS_GEO_PORTAL:
            raise WrongCatalogueError(
                "Invalid catalogue type. CkanCatExplorer requires a Ckan catalogue session.",
                expected_catalogue=str(CatalogueType.ONS_GEO_PORTAL),
                received_catalogue=str(cat_session.catalogue_type),
            )

        self.cat_session = cat_session

    # ----------------------------
    # Check CKAN site health
    # ----------------------------
    def check_site_health(self) -> bool:
        """
        Make sure the ONS Geo Portal endpoints are healthy and reachable.

        This calls the DCAT API endpoint to check if the site is still reachable.

        Returns:
            True if the site is healthy, False otherwise

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                explore = hc.ONSGeoExplorer(session)
                health_check = explore.check_site_health()

        if __name__ == "__main__":
            main()
        """

        url: str = self.cat_session.base_url + DCATApiPaths.BASE_PATH + "?q=ONSUD"

        try:
            response = self.cat_session.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    logger.success(
                        "Health Check Passed: ONS Geo Portal is running and available"
                    )
                    return True
                else:
                    logger.warning(
                        "Health Check Warning: ONS Geo Portal responded with an empty dataset"
                    )
                    return False
            else:
                logger.error(
                    f"Health Check Failed: ONS Geo Portal responded with status code {response.status_code}"
                )
                return False

        except requests.RequestException as e:
            logger.error(
                f"Health Check Failed: Unable to connect to ONS Geo Portal - {str(e)}"
            )
            return False

    # ----------------------------
    # Search datasets with query parameters
    # ----------------------------
    def _search_datasets(
        self, q: str, sort: Optional[str] = None, id: Optional[str] = None
    ) -> dict:
        """
        Search datasets in the ONS Geo Portal DCAT API.

        Args:
            q (str): Free text search query (required)
            sort (str, optional): Sort string in format like "Date Created|created|desc"
            id (str, optional): To include only a specific item id

        Returns:
            dict: JSON response from the API

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                explore = hc.ONSGeoExplorer(session)
                results = explore.search_datasets("ONSUD", sort="Date Created|created|desc")
                print(results)

        if __name__ == "__main__":
            main()
        """
        base_url = self.cat_session.base_url + DCATApiPaths.BASE_PATH

        params = {"q": q}

        if sort is not None:
            params["sort"] = sort

        if id is not None:
            params["id"] = id

        try:
            if sort is not None:
                if "sort" in params:
                    del params["sort"]
                query_string = urlencode(params)
                full_url = f"{base_url}?{query_string}&sort={sort}"
                response = self.cat_session.session.get(full_url)
            else:
                response = self.cat_session.session.get(base_url, params=params)

            response.raise_for_status()
            data = response.json()

            logger.success(f"Search completed for query: '{q}'. Found results.")
            return data

        except requests.RequestException as e:
            logger.error(f"Failed to search datasets: {str(e)}")
            raise CatExplorerError(f"Failed to search datasets: {str(e)}")

    def get_datasets_summary(
        self,
        q: str,
        sort: Optional[str] = None,
        id: Optional[str] = None,
        description: bool = False,
    ) -> List[Dict[str, str]]:
        """
        Search datasets and return only ID, title, and description for each dataset.

        Args:
            q (str): Free text search query (required)
            sort (str, optional): Sort string in format like "Date Created|created|desc"
            id (str, optional): To include only a specific item id
            description (bool, optional): Include description field in results (default True)

        Returns:
            List[Dict[str, str]]: List of dictionaries with 'id', 'title', and 'description' keys

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                explore = hc.ONSGeoExplorer(session)
                summary = explore.get_datasets_summary("ONSUD")
                for dataset in summary:
                    print(f"ID: {dataset['id']}")
                    print(f"Title: {dataset['title']}")
                    print(f"Description: {dataset['description'][:100]}...")
                    print("-" * 50)

        if __name__ == "__main__":
            main()
        """
        try:
            data = self._search_datasets(q, sort, id)
            datasets = data.get("dcat:dataset", [])

            summary = []

            match description:
                case True:
                    for dataset in datasets:
                        dataset_info = {
                            "id": dataset.get("@id", ""),
                            "title": dataset.get("dct:title", ""),
                            "description": dataset.get("dct:description", ""),
                        }
                        summary.append(dataset_info)

                    logger.success(f"Extracted summary for {len(summary)} datasets")
                    return summary
                case False:
                    for dataset in datasets:
                        dataset_info = {
                            "id": dataset.get("@id", ""),
                            "title": dataset.get("dct:title", ""),
                        }
                        summary.append(dataset_info)

                    logger.success(f"Extracted summary for {len(summary)} datasets")
                    return summary

        except Exception as e:
            logger.error(f"Failed to get datasets summary: {str(e)}")
            raise CatExplorerError(f"Failed to get datasets summary: {str(e)}")

    def _get_resource_metadata(self, dataset_id: str) -> dict:
        """
        Fetch detailed resource metadata including download links from ArcGIS REST API.

        Args:
            dataset_id (str): The dataset ID to fetch resource metadata for

        Returns:
            dict: Detailed resource metadata with download links

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                explore = hc.ONSGeoExplorer(session)
                # First get the dataset ID from search results
                summary = explore.get_datasets_summary("ONSUD")
                dataset_id = summary[0]['id']

                # Then get the detailed resource metadata
                resource_meta = explore.get_resource_metadata(dataset_id)
                print(resource_meta)

        if __name__ == "__main__":
            main()
        """
        base_url = "https://www.arcgis.com/sharing/rest/content/items"
        url = f"{base_url}/{dataset_id}"

        params = {"f": "json"}

        try:
            response = self.cat_session.session.get(url, params=params)
            logger.info(f"Request URL: {response.url}")
            response.raise_for_status()
            data = response.json()

            if data.get("error"):
                logger.error(f"ArcGIS API Error: {data['error']}")
                raise CatExplorerError(f"ArcGIS API Error: {data['error']}")

            logger.success(f"Retrieved resource metadata for dataset: {dataset_id}")
            return data

        except requests.RequestException as e:
            logger.error(f"Failed to get resource metadata: {str(e)}")
            raise CatExplorerError(f"Failed to get resource metadata: {str(e)}")

    def get_download_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get download information including direct download URLs for a dataset.

        Args:
            dataset_id (str): The dataset ID to get download info for

        Returns:
            Dict[str, Any]: Dictionary containing download URLs and file information

        # Example usage...
        import HerdingCats as hc

        def main():
            with hc.CatSession(hc.ONSGeoPortal.ONS_GEO) as session:
                explore = hc.ONSGeoExplorer(session)
                download_info = explore.get_download_info("b28cd21f0f274c77a2d556f0ee9ba594")
                print(f"Title: {download_info['title']}")
                print(f"Size: {download_info['size']} bytes")
                print(f"Download URL: {download_info['download_url']}")

        if __name__ == "__main__":
            main()
        """
        try:
            metadata = self._get_resource_metadata(dataset_id)
            download_info = {
                "id": metadata.get("id", ""),
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "size": metadata.get("size", 0),
                "type": metadata.get("type", ""),
                "owner": metadata.get("owner", ""),
                "created": metadata.get("created", ""),
                "modified": metadata.get("modified", ""),
                "access": metadata.get("access", ""),
                "tags": metadata.get("tags", []),
                "download_url": f"https://www.arcgis.com/sharing/rest/content/items/{dataset_id}/data",
            }

            if metadata.get("url"):
                download_info["item_url"] = metadata["url"]

            logger.success(f"Extracted download info for: {download_info['title']}")
            return download_info

        except Exception as e:
            logger.error(f"Failed to get download info: {str(e)}")
            raise CatExplorerError(f"Failed to get download info: {str(e)}")


# ----------------------------
# General catalogue info
# ----------------------------
def list_all_catalogues():
    """
    Simple function to list all available catalogues organized by type.

    Returns:
        dict: Dictionary containing all catalogues organized by type
    """
    from ..config.sources import (
        CkanDataCatalogues,
        DataPressCatalogues,
        OpenDataSoftDataCatalogues,
        FrenchGouvCatalogue,
        ONSNomisAPI,
    )

    catalogues = {
        "CKAN": [{"name": cat.name, "url": cat.value} for cat in CkanDataCatalogues],
        "DataPress": [
            {"name": cat.name, "url": cat.value} for cat in DataPressCatalogues
        ],
        "OpenDataSoft": [
            {"name": cat.name, "url": cat.value} for cat in OpenDataSoftDataCatalogues
        ],
        "FrenchGov": [
            {"name": cat.name, "url": cat.value} for cat in FrenchGouvCatalogue
        ],
        "ONSNomis": [{"name": cat.name, "url": cat.value} for cat in ONSNomisAPI],
    }

    return catalogues


def print_catalogues():
    """Print all available catalogues in a formatted way."""
    catalogues = list_all_catalogues()

    print("=" * 80)
    print("AVAILABLE DATA CATALOGUES")
    print("=" * 80)

    for cat_type, cat_list in catalogues.items():
        print(f"\n{cat_type} Catalogues:")
        print("-" * 40)
        for catalog in cat_list:
            print(f"  • {catalog['name']:30} → {catalog['url']}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("-" * 40)
    total = sum(len(cat_list) for cat_list in catalogues.values())
    for cat_type, cat_list in catalogues.items():
        print(f"  {cat_type:15}: {len(cat_list):3}")
    print(f"  {'─' * 23}")
    print(f"  Total:          {total:3}")
    print("=" * 80)
