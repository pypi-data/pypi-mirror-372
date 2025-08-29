from datetime import date
from typing import List, Tuple, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
import xarray as xr
import matplotlib.pyplot as plt

from . import argo
from . import seadatanet
from . import icos
from . import iagos
from . import actris
from . import exv
from . import misc


def get_data(
        exv_variable: str,
        region: Tuple[float, float, float, float],
        time: Tuple[date, date],
        samplingheight: Tuple[float, float],
        cache: bool = True
    ) -> Dict[str, List]:
    
    """ Get data from all Envri Hub Next partners with data access services."""
    
    # Check if variables exists in the NERC vocab:
    exvs = exv.get_exvs()

    if exv_variable not in exvs:
        misc.log_print(f"Variable {exv_variable} not found in NERC vocab EXV list. Available variables are:")
        for k, v in exvs.items():
            misc.log_print(f"\t{k}: {v}")
        return None
    
    results: Dict[str, List] = {}
    
    seadatanet_variables = exv.exv_to_p01(exv_variable)
    results["seadatanet"] = seadatanet.get_data(exv_variable, variables=seadatanet_variables, region=region, time=time, depth=samplingheight, cache=cache)
    
    argo_variables = exv.exv_to_r03(exv_variable)
    results["argo"] = argo.get_data(exv_variable, variables=argo_variables, region=region, time=time, depth=samplingheight, cache=cache)

    icos_variables = exv.exv_to_p07(exv_variable)
    results["icos"] = icos.get_data(exv_variable, variables=icos_variables, region=region, time=time, depth=samplingheight, cache=cache)
    
    iagos_variables = exv.exv_to_p07(exv_variable, True)
    results["iagos"] = iagos.get_data(exv_variable, variables=iagos_variables, region=region, time=time, depth=samplingheight, cache=cache)
    
    actris_variables = actris.exv_to_actris(exv_variable)
    results["actris"] = actris.get_data(exv_variable, variables=actris_variables, region=region, time=time, depth=samplingheight, cache=cache)

    return results





def display_dataset(ds: xr.Dataset, max_points: int = 5000):
    """
    Very simple display of an xarray.Dataset:
      - prints ds
      - plots latitude vs longitude (first max_points points) using coords only
      - plots the first data‐variable over time using coords only

    Assumes ds.coords contains fields named 'latitude'/'lat', 'longitude'/'lon', and 'time'.
    """
    # 1) summary
    misc.log_print(ds)
    
    # 2) helper: find coord by common names
    def _find_coord(names):
        for name in ds.coords:
            if name.lower() in names:
                return ds.coords[name]
        return None

    lat = _find_coord(('latitude','lat'))
    lon = _find_coord(('longitude','lon'))
    time = _find_coord(('time',))
    
    # 3) spatial scatter (coords only)
    if lat is not None and lon is not None:
        n = min(lat.size, max_points)
        plt.figure(figsize=(6,4))
        plt.scatter(lon.values[:n], lat.values[:n], s=1)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(f'Spatial distribution (first {n} points)')
        plt.tight_layout()
        plt.show()
    else:
        misc.log_print("⚠️ Could not find latitude/longitude in coords.")
    
    # 4) first data‐variable vs time (time from coords only)
    if time is not None and ds.data_vars:
        var = list(ds.data_vars)[0]
        arr = ds[var]
        # match along same dimension as time if possible
        dim = time.dims[0]
        if dim in arr.dims:
            idx = slice(0, min(arr.sizes[dim], max_points))
            x = time.sel({dim: time.coords[dim][:max_points]})
            y = arr.isel({dim: idx})
        else:
            # fallback: index 0-axis
            n = min(arr.shape[0], max_points)
            x = time.values[:n]
            y = arr.values[:n]
        
        try:
            plt.figure(figsize=(6,3))
            plt.plot(x, y, marker='.', linestyle='none', markersize=2)
            plt.xlabel('Time')
            plt.ylabel(var)
            plt.title(f"{var!r} over time (first {len(x)} points)")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            misc.log_print(f"⚠️ Failed to plot {var!r} vs time:", e)
    else:
        misc.log_print("⚠️ Could not find time in coords or no data-variables.")
