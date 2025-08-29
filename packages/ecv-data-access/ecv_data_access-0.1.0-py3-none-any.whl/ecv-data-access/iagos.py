import json
import requests
import os
import sys
import tempfile
from datetime import date, datetime
from typing import List, Tuple
import xarray

from . import misc

MAPPING_CF_TO_IAGOS = {'mole_fraction_of_carbon_monoxide_in_air' : ['CO'],
                   'mole_fraction_of_carbon_dioxide_in_air' : ['CO2']}

def get_data(
        exv: str, #ignored 
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[str, str],
        depth: Tuple[float, float], # ignored for IAGOS
        cache: bool = True         
    ) -> List[xarray.Dataset]:
    
    misc.log_print("Fetching data from IAGOS...")

    if not variables:
        misc.log_print("No variables provided. Please provide a list of variables to fetch data for.")
        return None
    
    
    # print(f"Variables: {variables}")

    iagos_variables = [MAPPING_CF_TO_IAGOS.get(var) for var in variables if var in MAPPING_CF_TO_IAGOS]
    iagos_variables = [item for sublist in iagos_variables for item in sublist]  # Flatten the list
    
    # print(iagos_variables)
    
    if not iagos_variables:
        misc.log_print("No valid IAGOS variables found. Please check the provided variables.")
        return None
    
    parameters = ','.join(iagos_variables)
    start, end = time
    bbox = ','.join(map(str, region))

    print(parameters)
    
    indexPage = 0
    sizePage = 20
    
    url = f"https://services.iagos-data.fr/prod/v2.0/airports/public?active=true&bbox={bbox}&from={start}&to={end}&cursor={indexPage}&size={sizePage}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        misc.log_print(f"Error fetching data from IAGOS: {response.text}")
        return None
    
    data = json.loads(response.text)
    
    airports = []
    
    for dataset in data:
        airports.append(dataset['iata_code'])
        
    airports = ",".join(airports)

    data_url = f"https://services.iagos-data.fr/prod/v2.0/l3/search?codes={airports}&from={start}&to={end}&level=2&parameters={parameters}"
    
    response = requests.get(data_url)
    
    if response.status_code != 200:
        misc.log_print(f"Error fetching data from IAGOS: {response.text}")
        return None
    
    data = json.loads(response.text)
    
    datasets = {}
    
    for dataset in data:
        datasets[dataset['title']] = dataset
        
    urls = []
    
    for dataset in datasets.values():
        for url_data in dataset['urls']:
            if url_data['type'].upper() == 'LANDING_PAGE':
                urls.append(url_data['url'])

    download_urls = {}
    
    for url in urls:
        filename = url.split("#")[-1]
        download_url = "https://services.iagos-data.fr/prod/v2.0/l3/loadNetcdfFile?fileId=" + url.replace("#", "%23")
        download_urls[filename] = download_url
        
    
    return_vals = []
    
    for filename, url in download_urls.items():
        
        filepath = download_to_file(filename, url, cache=cache)
        
        if filepath is None:
            misc.log_print(f"Failed to download dataset: {url}")
            continue
        
        misc.log_print(f"Downloaded to: {filepath}")
        
        dataset = xarray.open_dataset(filepath)
        return_vals.append(dataset)
    
    return return_vals

def download_to_file(filename: str, url: str, filepath: str = "", cache = False):
    if not filepath:
        # use temp file if no filepath is provided
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file: {filepath}")
        return filepath
    
    misc.log_print(f"Downloading {url} to {filepath}")
    
    with requests.get(
        url,
        stream=True
    ) as resp:
        return misc.stream_to_file(resp, filepath)   
        



