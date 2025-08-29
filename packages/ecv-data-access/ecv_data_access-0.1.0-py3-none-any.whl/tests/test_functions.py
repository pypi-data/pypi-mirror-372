import ehnpy.functions as functions
import ehnpy.icos as icos
import matplotlib.pyplot as plt

from ehnpy import misc

if __name__ == "__main__":
    misc.log_print("Starting test_functions.py")
    
    # https://vocab.nerc.ac.uk/collection/EXV/current/
    exv = "EXV016" # Aerosol properties
    # exv = "EXV017" # Sea-surface temperature
    # exv = "EXV013" # Carbon dioxide, methane and other greenhouse gases 
    
    
    data = functions.get_data(
        exv_variable=exv,
        region=(-20, 10, 20, 55),
     
        time=("2018-01-01", "2020-12-31"),
        depth=(0, 100)
    )
    
    
    for source, datasets in data.items():
        print("\n\n")
        misc.log_print(f"=================== {source.upper()} ====================")

        misc.log_print(f"Dataset(s): {datasets}")

        misc.log_print(f"=================== {source.upper()} ====================\n\n")
    
    # data = {seadatanet: xarray.Dataset, argo: xarray.Dataset}
    
    # for source, ds in data.items():
    #     misc.log_print(f"Plotting dataset: {source}")
    #     misc.log_print(ds)
        
    # dump structure of the dataset:
    # functions.display_dataset(ds)
     
    # misc.log_print("EXV to P01 input:", exvs)
    # result = exv.exv_to_p01(exvs)
    # misc.log_print("EXV to P01 result:", result)
    
    # misc.log_print("EXV to P02 input:", exvs)
    # result = exv.exv_to_p02(exvs)
    # misc.log_print("EXV to P02 result:", result)
    
    # misc.log_print("EXV to P07 input:", exvs)
    # result = exv.exv_to_p07(exvs)
    # misc.log_print("EXV to P07 result:", result)
    
    # misc.log_print("EXV to R03 input:", exvs)
    # result = exv.exv_to_r03(exvs)
    # misc.log_print("EXV to R03 result:", result)

    # functions.get_data(
    #     variables=("NITROGEN", "PHOSPHATE", "SILICATE"),
    #     region=(-10, 10, 40, 50),
    #     time=("2020-01-01", "2020-12-31"),
    #     depth=(0, 100)
    # )



