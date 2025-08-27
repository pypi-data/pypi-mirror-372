from enum import Enum


class CkanDataCatalogues(Enum):
    LONDON_DATA_STORE = "https://data.london.gov.uk"
    UK_GOV = "https://data.gov.uk"
    # Need to look into why Subak is currently not working
    # SUBAK = "https://data.subak.org"
    HUMANITARIAN_DATA_STORE = "https://data.humdata.org"
    OPEN_AFRICA = "https://open.africa"
    NATIONAL_GRID_DNO = "https://connecteddata.nationalgrid.co.uk"
    SSEN_DNO = "https://ckan-prod.sse.datopian.com"
    NHSBSA_OPEN_DATA = "https://opendata.nhsbsa.net"
    # OPEN_NET_ZERO = ""
    # Add more catalogues as needed...


class DataPressCatalogues(Enum):
    NORTHERN_DATA_MILL = "https://datamillnorth.org"
    LONDON_DATA_STORE = "https://data.london.gov.uk"


# OPEN DATASOFT
class OpenDataSoftDataCatalogues(Enum):
    UK_POWER_NETWORKS_DNO = "https://ukpowernetworks.opendatasoft.com"
    INFRABEL = "https://opendata.infrabel.be"
    PARIS = "https://opendata.paris.fr"
    TOULOUSE = "https://data.toulouse-metropole.fr"
    ELIA_BELGIAN_ENERGY = "https://opendata.elia.be"
    EDF_ENERGY = "https://opendata.edf.fr"
    CADENT_GAS_GDN = "https://cadentgas.opendatasoft.com"
    GRD_FRANCE = "https://opendata.agenceore.fr"
    NORTHERN_POWERGRID_DNO = "https://northernpowergrid.opendatasoft.com"
    ELECTRICITY_NORTH_WEST_DNO = "https://electricitynorthwest.opendatasoft.com"
    SSEN_TRANSMISSION = "https://ssentransmission.opendatasoft.com"
    SP_ENERGY_NETWORKS_DNO = "https://spenergynetworks.opendatasoft.com"
    # Add more catalogues as needed...


# DATA GOUV FR
class FrenchGouvCatalogue(Enum):
    GOUV_FR = "https://www.data.gouv.fr"


# ONS NOMI
class ONSNomisAPI(Enum):
    ONS_NOMI = "https://www.nomisweb.co.uk/"


# ONS Geo Portal
class ONSGeoPortal(Enum):
    ONS_GEO = "https://geoportal.statistics.gov.uk"
