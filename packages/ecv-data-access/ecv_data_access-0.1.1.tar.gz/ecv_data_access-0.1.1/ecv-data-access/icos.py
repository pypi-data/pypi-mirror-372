import requests
import os
import sys
import tempfile
from datetime import date, datetime
from typing import List, Tuple
import xarray
from icoscp_core.icos import meta, data
from icoscp_core.metaclient import DataObject
from icoscp_core.icos import auth

from ecv-data-access import misc

def get_data(
        exv: str,
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[str, str],
        depth: Tuple[float, float],
        cache: bool = True         
    ) -> List[xarray.Dataset]:
    
    hasToken = False
    
    try:
        token = auth.get_token()  # make sure auth config is initialized
        if token:
            hasToken = True
    except Exception as e:
        hasToken = False

    if not hasToken:    
        auth.init_config_file() # make sure auth config is initialized
    
    misc.log_print("Fetching data from ICOS...")
    
    if not variables:
        misc.log_print("No variables provided. Please provide a list of variables to fetch data for.")
        return None
    
    dobjs = exec_icos_sparql_query(variables, region, time, depth)
    
    misc.log_print(f"Found {len(dobjs)} data objects.")
    
    if not dobjs:
        misc.log_print("No data objects found for the given query parameters.")
        return None
    
    # Exception: When requesting data from several data objects, all data objects must have a common dataset specification
    # datasets = list(data.batch_get_columns_as_arrays(dobjs))
    
    datasets = []
    
    for dobj in dobjs:
        datasets.append(data.get_columns_as_arrays(meta.get_dobj_meta(dobj)))
    
    return datasets
    
    


def exec_icos_sparql_query(
    variables: List[str],
    region: Tuple[float, float, float, float],
    time: Tuple[str, str],
    depth: Tuple[float, float],
) -> List[str]:
    time = (datetime.strptime(time[0], "%Y-%m-%d"), datetime.strptime(time[1], "%Y-%m-%d"))
    
    dt_min, dt_max = time
    sampling_height_min, sampling_height_max = depth
    longitude_min, longitude_max, latitude_min, latitude_max = region
    dt_format = "%Y-%m-%dT%H:%M:%SZ"
    
    spatial_filters = {
        "?lon > ": longitude_min, "?lon < ": longitude_max, "?lat > ": latitude_min, "?lat < ": latitude_max,
        "?height > ": sampling_height_min, "?height < ": sampling_height_max
    }
    
    filters = []
    
    if dt_min is not None:
        filters.append(f"?end > '{date.strftime(dt_min, dt_format)}'^^xsd:dateTime")
    if dt_max is not None:
        filters.append(f"?start < '{date.strftime(dt_max, dt_format)}'^^xsd:dateTime")
    for filter_str, filter_val in spatial_filters.items():
        if filter_val is not None:
            filters.append(f"{filter_str}{filter_val}")


    variables = [f"<http://vocab.nerc.ac.uk/collection/P07/current/{var}/>" for var in variables]
    p07_vars_str = " ".join(variables)
    filters_str = " && ".join(filters)
    
    query = f"""
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX cpmeta: <http://meta.icos-cp.eu/ontologies/cpmeta/>
    #PREFIX geo: <http://www.opengis.net/ont/geosparql#>

    SELECT ?dobj
    WHERE {{
        VALUES ?externalVar {{ {p07_vars_str} }}
        ?valueType skos:exactMatch ?externalVar .
        ?spec cpmeta:containsDataset/cpmeta:hasColumn/cpmeta:hasValueType ?valueType .
        ?spec cpmeta:hasDataLevel ?level .
        ?dobj cpmeta:hasObjectSpec ?spec .
        ?dobj cpmeta:wasAcquiredBy ?acq .
        ?dobj cpmeta:hasStartTime | (cpmeta:wasAcquiredBy/prov:startedAtTime) ?start .
        ?dobj cpmeta:hasEndTime | (cpmeta:wasAcquiredBy/prov:endedAtTime) ?end .
        ?acq prov:wasAssociatedWith ?station .
        ?acq cpmeta:hasSamplingHeight ?height .
        ?station cpmeta:hasLatitude ?lat .
        ?station cpmeta:hasLongitude ?lon .
        FILTER ( {filters_str} )
        FILTER NOT EXISTS {{[] cpmeta:isNextVersionOf ?dobj}}
        FILTER (?level = 2)
    }}
    """ 
    
    resp = requests.post("https://meta.icos-cp.eu/sparql", query)
    
    misc.log_print(f"SPARQL query status code: {resp.status_code}")
    
    bindings = resp.json()["results"]["bindings"]
    
    dobjs = [binding["dobj"]["value"] for binding in bindings]
    
    return dobjs
    
    
def meta_link_to_meta_obj(link: str) -> DataObject:
    """
    Converts a metadata link to a data link.
    """
    return meta.get_dobj_meta(link)
    # return link.replace("https://meta.icos-cp.eu/", "https://data.icos-cp.eu/") 

def create_temp_filepath(link: str) -> str:
    """
    Creates a temporary file path based on the link.
    """
    filename = link.split("/")[-1]
    return os.path.join(tempfile.gettempdir(), filename + ".nc")

def download_to_file(url: str, filename: str, filepath: str = "", cache = False):

	# add cookie: CpLicenseAcceptedFor=mXuWVqwoN6F2yYnyhgylY1_q
 
    cookies = {
        "CpLicenseAcceptedFor": filename
    }
    
    if not filepath:
        # use temp file if no filepath is provided
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file: {filepath}")
        return filepath
    
    misc.log_print(f"Downloading {url} to {filepath} with cookies: {cookies}")
    
    with requests.get(
        url,
        cookies=cookies,
        stream=True
    ) as resp:
        return misc.stream_to_file(resp, filepath)
















if __name__ == "__main__":
    
    from ecv-data-access import exv
    # Example usage
    exv_variable = "EXV013"
    region=(10, 20, 45, 65) 
    time=("2020-01-01", "2021-12-31")
    samplingheight=(0, 100)
    
    icos_variables = exv.exv_to_p07(exv_variable)

    
    datasets = get_data(
        exv=exv_variable,
        variables=icos_variables,
        region=region,
        time=time,
        depth=samplingheight
    )

    
    if datasets:
        print(datasets)
    else:
        print("No datasets found.")