from datetime import date
import os
import tempfile
from typing import List, Tuple
import argopy
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import json
import xarray
from argopy import DataFetcher, ArgoIndex, ArgoNVSReferenceTables  
from .json_cache import load_cache, save_cache, md5_hash

from . import misc

def get_data(
        exv: str,
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[date, date],
        depth: Tuple[float, float],
        cache: bool = True         
    ) -> xarray.Dataset:
    """ 
    Fetches Argo data using the Argopy python package.
    """
    misc.log_print("Fetching data from Argo using Argopy...")

    if not variables:
        misc.log_print("No variables")
        return None

    lon_east, lon_west, lat_north, lat_south = region
    depth_min, depth_max = depth
    date_min, date_max = time
    
    SELECTION = [
        lon_east, lon_west, lat_north, lat_south, 
        depth_min, depth_max,
        date_min, date_max    
    ]
    
    query_hash = md5_hash(json.dumps(SELECTION));
    
    filename = f"ARGO_{date_min}-{date_max}_{depth_min}-{depth_max}m_{query_hash}.nc"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    misc.log_print(f"Temporary file path: {filepath}")
    
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file...")
        
        dataset = xarray.open_dataset(filepath)
        
        return dataset
    
    else:
        misc.log_print(f"Downloading data...")
    
        try:
            f = DataFetcher(
                    ds='bgc', 
                    mode='expert', 
                    params=variables,
                    parallel=True, 
                    progress=True, 
                    cache=False,
                    chunks_maxsize={'time': 30},
            )
            
            f = f.region(SELECTION).load()
        
            df = f.to_xarray()
            
            # df[f"{exv}"] = df[variables].mean(axis=1)
            
            # Save to file
            df.to_netcdf(filepath)
            
            return df
        except Exception as e:
            misc.log_print("Something went wrong querying ARGO", e)
            