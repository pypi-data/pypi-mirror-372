# CKAN
class CkanApiPaths:
    BASE_PATH = "/api/3/action/{}"
    PACKAGE_LIST = BASE_PATH.format("package_list")
    PACKAGE_SEARCH = BASE_PATH.format("package_search")
    PACKAGE_INFO = BASE_PATH.format("package_show")
    CURRENT_PACKAGE_LIST_WITH_RESOURCES = BASE_PATH.format(
        "current_package_list_with_resources"
    )
    ORGANIZATION_LIST = BASE_PATH.format("organization_list")
    DATASTORE_SQL_QUERY = BASE_PATH.format("datastore_search_sql?")
    # Add more paths as needed...


# DataPress
class DataPressApiPaths:
    BASE_PATH = "/api/{}"
    PACKAGE_INFO = BASE_PATH.format("dataset/{}")
    SHOW_ALL_CATALOGUES = BASE_PATH.format("datasets/export.json")
    # Add more paths as needed...


# OPEN DATASOFT
class OpenDataSoftApiPaths:
    # Normal base paths...
    BASE_PATH = "/api/v2/catalog/{}"
    SHOW_DATASETS = BASE_PATH.format("datasets")
    SHOW_DATASET_INFO = BASE_PATH.format("datasets/{}")
    SHOW_DATASET_EXPORTS = BASE_PATH.format("datasets/{}/exports")

    # Alternative base paths...
    # TODO Sometimes these are needed - not sure why need to dig into this!
    BASE_PATH_2 = "/api/explore/v2.0/catalog/{}"
    SHOW_DATASETS_2 = BASE_PATH_2.format("datasets")
    SHOW_DATASET_INFO_2 = BASE_PATH_2.format("datasets/{}")
    SHOW_DATASET_EXPORTS_2 = BASE_PATH_2.format("datasets/{}/exports")
    # Add more paths as needed...


# DATA GOUV FR
class FrenchGouvApiPaths:
    BASE_PATH = "/api/1/{}"
    SHOW_DATASETS = BASE_PATH.format("datasets")
    SHOW_DATASETS_BY_ID = BASE_PATH.format("datasets/{}")
    SEARCH_DATASETS = BASE_PATH.format("datasets/")
    SHOW_DATASET_RESOURCE_BY_ID = BASE_PATH.format("datasets/{}/resources/")
    CATALOGUE = "5d13a8b6634f41070a43dff3"


# ONS NOMI
class ONSNomisApiPaths:
    BASE_PATH = "/api/v01/{}"
    SHOW_DATASETS = BASE_PATH.format("dataset/def.sdmx.json")
    SHOW_DATASET_INFO = BASE_PATH.format("dataset/{}/def.sdmx.json")
    SHOW_DATASET_OVERVIEW = BASE_PATH.format("dataset/{}.overview.json")
    GENERATE_LATEST_DATASET_DOWNLOAD_URL = BASE_PATH.format(
        "dataset/{}.data.csv?date=latest{}"
    )
    SHOW_CODELIST_DETAILS = BASE_PATH.format("codelist/{}.def.sdmx.json")
    # Add in codelists


class ONSNomisQueryParams:
    GEOGRAPHY = "&geography="


# DCAT
class DCATApiPaths:
    BASE_PATH = "/api/feed/dcat-ap/3.0.0.json"
