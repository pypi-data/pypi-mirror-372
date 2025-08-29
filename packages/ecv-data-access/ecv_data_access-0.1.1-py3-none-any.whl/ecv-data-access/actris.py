# Library for working with netCDF files
import sys
import tempfile
import xarray as xr

# Libraries for working with JSON files, making HTTP requests, and handling file system operations
import json
import requests
import os

# Library for plotting data
import matplotlib.pyplot as plt

# Library for querying SPARQL endpoints
from SPARQLWrapper import SPARQLWrapper, JSON
import xarray
from typing import List, Tuple

from ecv-data-access import misc
from requests.exceptions import HTTPError

MAPPING_EXV_TO_ACTRIS = {
    "EXV016": True,
    "EXV011": True
}

def get_data(
        exv: str, #ignored
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[str, str],
        depth: Tuple[float, float],
        cache: bool = True         
    ) -> List[xarray.Dataset]:
    
    misc.log_print("Fetching data from ACTRIS...")
    
    if not variables:
        misc.log_print("No valid ACTRIS variables found. Please check the provided variables.")
        return None
    
    start_time, end_time = time
    west_bound_longitude, east_bound_longitude, south_bound_latitude, north_bound_latitude = region
    
    url = "https://prod-actris-md2.nilu.no/metadata/query/envri"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    actris_query_body = {
        "time_range": [start_time, end_time],
        "bounding_box": {
            "west_bound_longitude": west_bound_longitude,
            "east_bound_longitude": east_bound_longitude,
            "south_bound_latitude": south_bound_latitude,
            "north_bound_latitude": north_bound_latitude
        },
        "variables": variables,  # Only if observed_properties is a JSON string
        "page": 0
    }
    
    
    #misc.log_print(f"ACTRIS query body: {actris_query_body}")
    
    metadata_list = []
    
    while True:
        response = requests.post(url, headers=headers, data=json.dumps(actris_query_body))

        text = response.text
      
        try:
            response_json = response.json()
            metadata_list.extend(response_json)
        except ValueError:
            misc.log_print("Non-JSON response:", response.text)

        if response.status_code != 200 or not response.json(): 
            break

        #misc.log_print(f'Response Status: {response.status_code} - Response Reason: {response.reason} - Page: {actris_query_body["page"]}')
        actris_query_body["page"] += 1

    #misc.log_print(f"Number of metadata elements retrieved: {len(metadata_list)}")
    
    data_files = []
    
    for element in metadata_list: 
        url = element['md_distribution_information'][0]['dataset_url']
        filename = "ACTRIS_"+element['md_metadata']['file_identifier']
        filepath = download_to_file(url, filename, cache=cache)

        if filepath is None:
            misc.log_print(f"Skipping {url} due to failed download.")
            continue  # Skip this entry and move to the next one

        try:
            dataset = xarray.open_dataset(filepath)
            data_files.append(dataset)
        except Exception as err:
            misc.log_print(f"Failed to open dataset from {filepath}: {err}")

        # dataset = xarray.open_dataset(filepath)
        # data_files.append(dataset)

    return data_files




def download_to_file(url: str, filename: str, filepath: str = "", cache: bool = False):
    if not filepath:
        # use temp file if no filepath is provided
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file: {filepath}")
        return filepath
    
    misc.log_print(f"Downloading {url} to {filepath} ")
    
    # with requests.get(
    #     url,
    #     stream=True
    # ) as resp:
    #     return misc.stream_to_file(resp, filepath)

    try:
        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()  
            return misc.stream_to_file(resp, filepath)

    except HTTPError as http_err:
        misc.log_print(f"HTTP error occurred: {http_err} Skipping download for URL: {url}")
        return None
    except Exception as err:
        misc.log_print(f"Unexpected error occurred: {err} Skipping download for URL: {url}")
        return None


def exv_to_actris(exv: str) -> List[str]:
    """
    Convert an EXV variable to ACTRIS variables.
    
    Args:
        exv (str): The EXV variable code.
        
    Returns:
        List[str]: A list of ACTRIS variable URIs.
    """
    
    if exv not in MAPPING_EXV_TO_ACTRIS.keys():
        return []
    
    return EXV_iadopt()

def EXV_iadopt():
    # SPARQL endpoint
    endpoint_url = "https://vocabulary.actris.nilu.no/fuseki/skosmos/sparql"

    # Construct full identifier
    # exv_identifier = f"SDN:EXV::{exv_code}"

    # Create the query with the user input
    query = """
    prefix skos: <http://www.w3.org/2004/02/skos/core#>
    prefix iop: <https://w3id.org/iadopt/ont/>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix ACTRIS_vocab: <https://vocabulary.actris.nilu.no/actris_vocab/>

    SELECT DISTINCT ?aerosol_variable_url ?aerosol_variable_ParticlePhase
    from <https://vocabulary.actris.nilu.no/actris_vocab/>
    WHERE {
        ?aerosol_variable_url iop:hasMatrix ACTRIS_vocab:aerosolparticlephase;
            skos:prefLabel ?aerosol_variable_ParticlePhase
    }
    """

    # Set up the SPARQL request
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Run the query and parse results
    results = sparql.query().convert()

    observed_properties = []

    # Show results
    for result in results["results"]["bindings"]:
        uri = result.get("aerosol_variable_ParticlePhase", {}).get("value", "")
        observed_properties.append(uri)
        
    return observed_properties


if __name__ == "__main__":
    misc.log_print("Starting ecv-data-access.actris.py")
    
    #exv = 'EXV011'
    exv = "EXV016"  # Aerosol properties
    # exv = "EXV017"  # Sea-surface temperature
    # exv = "EXV013"  # Carbon dioxide, methane and other greenhouse gases
     
    actris_variables = exv_to_actris(exv)
    
    data = get_data(
        exv=exv,
        variables=actris_variables,
        region=(8.59, 8.66, 45.75, 45.85),
        time=("2023-02-01T00:00:00", "2023-02-01T23:59:59"),
        depth=(0, 100)
    )
    
    misc.log_print(data)