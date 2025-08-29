import pandas as pd
import geopandas as gpd
import pyarrow
from pathlib import Path



def check_extension(path):
    extension = path.suffix
      
    if extension == '.parquet':
        io_function = 'parquet'
        return io_function
    elif extension == '.feather':
        io_function = 'feather'
        return io_function
    else:
        io_function = 'file'
        return io_function


def open_vector_file(file):
    filepath = Path(file)
    
    io_func = check_extension(path=filepath)

    if io_func == 'file':
        gdf = gpd.read_file(filepath)
        return gdf
    elif io_func == 'parquet':
        gdf = gpd.read_parquet(filepath)
        return gdf
    elif io_func == 'feather':
        gdf = gpd.read_feather(filepath)
        return gdf

def save_vector_file(gdf, file):
    filepath = Path(file)
    
    io_func = check_extension(path=filepath)

    if io_func == 'file':
        gdf = gdf.to_file(filepath)
        return None
    elif io_func == 'parquet':
        gdf = gdf.to_parquet(filepath)
        return None
    elif io_func == 'feather':
        gdf = gdf.to_feather(filepath)
        return None
