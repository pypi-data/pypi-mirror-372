import requests
import json
import pandas as pd
import os
import sys
import tempfile
from datetime import date
from typing import List, Tuple

import xarray

from ecv-data-access import misc
from .json_cache import load_cache, save_cache, md5_hash

CDI_BEACON_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvZGF0YS5ibHVlLWNsb3VkLm9yZyIsImF1ZCI6Imh0dHBzOlwvXC9kYXRhLmJsdWUtY2xvdWQub3JnIiwiaWF0IjoxNzU1MTgxNjYzLCJleHAiOjE3ODY3MTc2NjMsInVzciI6MzIsImlkIjoicGF1bEBtYXJpcy5ubCIsImVwX29yZ2FuaXNhdGlvbiI6IkVudnJpLUh1YiBOZXh0In0.Rtk1moa6N9TsRGV6hhPveb4tOQROoh_DxE7CKdQkEkY"
CDI_BEACON = "https://beacon-cdi.maris.nl"

def get_data(
        exv: str,
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[date, date],
        depth: Tuple[float, float],
        cache: bool = True         
    ) -> xarray.Dataset:
    
    misc.log_print("Fetching data from SeaDataNet CDI Beacon API...")
    
    variables = filter_unavailable_columns(variables)
    
    misc.log_print(f"Variables: {variables}")
    
    if not variables:
        misc.log_print("No valid variables found. Please check the provided variables.")
        return None
    
    query_body = create_query_body(variables, region, time, depth)
    
    query_hash = md5_hash(json.dumps(query_body, sort_keys=True))
    
    mindate, maxdate = time
    mindepth, maxdepth = depth
    
    filename = f"SeaDataNet_{mindate}-{maxdate}_{mindepth}-{maxdepth}m_{query_hash}.arrow"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    misc.log_print(f"Temporary file path: {filepath}")
    
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file...")
    else:
        misc.log_print(f"Downloading data...")
        if download_to_file(query_body, filepath) is None:
            misc.log_print("Download failed. Please check the query parameters and try again.")
            return None
        
    cols_to_exclude = ['SDN_STATION', 'SDN_EDMO_CODE', 'SDN_LOCAL_CDI_ID']

    try:
        df = pd.read_feather(filepath)

        df = df.set_index("TIME").sort_index() 
        
        
        df[df.columns.difference(cols_to_exclude)] = df[df.columns.difference(cols_to_exclude)].apply(pd.to_numeric, errors='coerce')
        
        df[f"{exv}"] = df[variables].mean(axis=1)
        
        df.drop(columns=variables, inplace=True)
        
        return df.to_xarray()
    except Exception as e:
        misc.log_print(f"Error reading feather file: {e}")
        
    return None
    

def download_to_file(query_body, filepath: str):
        # send request with stream=True
    with requests.post(
        CDI_BEACON + "/api/query",
        data=json.dumps(query_body),
        headers={
            "Authorization": f"Bearer {CDI_BEACON_TOKEN}",
            "Content-Type": "application/json",
        },
        stream=True
    ) as resp:
        return misc.stream_to_file(resp, filepath)


def filter_unavailable_columns(variables: List[str]):
    """
    Filters the list of variables to only include those that are available in the CDI Beacon API.
    """
    
    misc.log_print("Filtering available columns...")
    
    cache_key = f"seadatanet_filter_unavailable_columns_{md5_hash('_'.join(variables))}"
    
    cache = load_cache(cache_key)
    
    if cache is not None:
        return cache
    
    
    
    response = requests.get(
        CDI_BEACON + "/api/query/available-columns",
        headers={
            "Authorization": f"Bearer {CDI_BEACON_TOKEN}",
        })
    
    if response.status_code != 200:
        misc.log_print("Error fetching available columns:", response.text)
        return []
    
    available_columns = response.json()

    matching_p01s = []
    
    for var in variables:
            if var in available_columns:
                matching_p01s.append(var)
                
    save_cache(cache_key, matching_p01s)

    return matching_p01s

def create_query_body(
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[date, date],
        depth: Tuple[float, float]         
    ):
    mindate, maxdate = time
    minlon, maxlon, minlat, maxlat = region
    mindepth, maxdepth = depth
    
    query_parameters = []
    query_parameters.append("LONGITUDE")
    query_parameters.append("LATITUDE")
    query_parameters.append("TIME")
    query_parameters.append({"function": "coalesce", "args": ["DEPTH", "PRES"], "alias": "DEPTH"})
    query_parameters.append("SDN_STATION")
    query_parameters.append("SDN_EDMO_CODE")
    query_parameters.append("SDN_LOCAL_CDI_ID")
    for p01 in variables:
        query_parameters.append(p01)

    filters = []
    filters.append({"for_query_parameter": "TIME", "min": f"{mindate}T00:00:00", "max": f"{maxdate}T00:00:00"})
    filters.append({"for_query_parameter": "DEPTH", "min": mindepth, "max": maxdepth})
    filters.append({"for_query_parameter": "LONGITUDE", "min": minlon, "max": maxlon})
    filters.append({"for_query_parameter": "LATITUDE", "min": minlat, "max": maxlat})


    parameter_or_filters = []
    for p01 in variables:
        parameter_or_filters.append({"is_not_null": {"for_query_parameter": p01}})
    or_filter = {
        "or" : parameter_or_filters
    }
    filters.append(or_filter)
    body = {
        "query_parameters": query_parameters,
        "filters": filters,
        "output": {"format": "ipc"},
    }
    return body



