try:
    dinamica.inputs
except:
    from dinamicaClass import dinamicaClass
    dinamica = dinamicaClass({})
try:
    import rioxarray
except ModuleNotFoundError:
    dinamica.package('rioxarray')

try:
    import geopandas as gpd
except ModuleNotFoundError:
    dinamica.package('geopandas')
    dinamica.package('pyarrow')
    import geopandas as gpd

try:
    import pandas as pd
except ModuleNotFoundError:
    dinamica.package('pandas')

import numpy as np
try:
    import xarray as xr
except ModuleNotFoundError:
    dinamica.package('xarray')
    import xarray as xr

from dinamicarslib.utils import *
from pathlib import Path




def create_sample_points(vector_filepath , num_samples):
    gdf = open_vector_file(vector_filepath)
    samples_per_poly = num_samples
    points = gpd.GeoDataFrame(geometry=gdf.sample_points(size=samples_per_poly, rgn=64))
    points = points.explode(ignore_index=False, index_parts=False)
    points = points.reset_index().rename(columns={'index':'polygon_id'})
    points = points.reset_index().rename(columns={'index':'id'})
    points['id'] += 1
    points_gdf = points.merge(gdf.drop(columns='geometry'), how='left', right_index=True, left_on='polygon_id')
    return points_gdf

def create_dataset(points_fp, variables_fp):
    samples_points = open_vector_file(points_fp)
    iterable = samples_points.get_coordinates()
    x_points = xr.DataArray(iterable.x, dims=('points',))
    y_points = xr.DataArray(iterable.y, dims=('points',))
    for var in variables_fp[1:]:
        print(var)
        band_name = var[0]
        ds = rioxarray.open_rasterio(var[1], masked=True, chuncks='auto').assign_coords(band_name=band_name)
        values = ds.sel(x=x_points, y=y_points, method="nearest")
        samples_points.loc[:, band_name] = values.compute().values[0]

    return samples_points

def get_atributte_by_location(left_ds_fp, right_ds_fp, how, predicate, cols_to_get):


    gdf_left = open_vector_file(left_ds_fp)
    gdf_right = open_vector_file(right_ds_fp)
    
    
    cols_to_get.append(gdf_right.geometry.name)

    gdf_right = gdf_right.loc[:, cols_to_get]
    gdf_join = gdf_left.sjoin(gdf_right,how=how,predicate=predicate)
    gdf_join.drop(columns='index_right')

    return gdf_join


def query_table_by_atributte(dataset_fp, col_name, col_value, query=None):
    dataset = open_vector_file(dataset_fp)

    if query:
        if len(query) > 0:
            query_table=  dataset.query(query)
            return query_table

    query_table = dataset.loc[dataset[col_name]==col_value]

    return query_table

def union_vector_tables(files_table, id_column='id', keep_index=False):
    gdf_list = []
    for file in files_table[1:]:
        gdf = open_vector_file(file[1])
        gdf_list.append(gdf)

    gdf_concat = pd.concat(gdf_list, ignore_index=True)
    gdf_concat[id_column] = gdf_concat.index + 1
    
    return gdf_concat

try:
    from sklearn.model_selection import train_test_split
except ModuleNotFoundError:
    dinamica.package("scikit-learn",'scikit-learn', 'sklearn')
    from sklearn.model_selection import train_test_split

def create_samples_filename(base_folder, suffix, file_extension='.parquet', make_child_dirs=True):

    all_samples_dir = base_folder.joinpath('samples')
    test_samples_dir = base_folder.joinpath('test')
    train_samples_dir = base_folder.joinpath('train')
    
    if make_child_dirs:
        #All samples
        os.makedirs(all_samples_dir, exist_ok=True)
        #Test set
        os.makedirs(test_samples_dir, exist_ok=True)
        #Train samples
        os.makedirs(train_samples_dir, exist_ok=True)

    #Create file names
    all_samples = all_samples_dir.joinpath(suffix).with_suffix(file_extension)
    test_samples = test_samples_dir.joinpath(suffix).with_suffix(file_extension)
    train_samples = train_samples_dir.joinpath(suffix).with_suffix(file_extension)
    
    return all_samples, train_samples, test_samples

def split_dataset(dataset_fp, class_column, out_base_folder, suffix=None, test_size=0.3, random_state=0, stratify=False, grouped=False, group_cols=None):

    dataset = open_vector_file(dataset_fp)

    

    if grouped:
        if  isinstance(group_cols, list):
            unique_polygons = list(dataset.groupby(group_cols).groups.keys())
            samples_train, samples_test = train_test_split(unique_polygons, test_size=test_size ,random_state=0) #split train and test

            train_points = dataset.loc[dataset[group_cols].apply(tuple,axis=1).isin(samples_train)]
            test_points = dataset.loc[dataset[group_cols].apply(tuple,axis=1).isin(samples_test)]
        else:
            unique_polygons = dataset.loc[:,group_cols].unique()
            samples_train, samples_test = train_test_split(unique_polygons, test_size=test_size ,random_state=0) #split train and test

            train_points = dataset.loc[dataset[group_cols].isin(samples_train)]
            test_points = dataset.loc[dataset[group_cols].isin(samples_test)]
    else:
        unique_polygons = dataset.index
        samples_train, samples_test = train_test_split(unique_polygons, test_size=test_size ,random_state=0) #split train and test

        train_points = dataset.loc[dataset[group_cols].isin(samples_train)]
        test_points = dataset.loc[dataset[group_cols].isin(samples_test)]





    train_fp, test_fp = create_samples_filename(out_base_folder)
    


    train_points.to_parquet(train_fp)
    test_points.to_parquet(test_fp)

    
    
if __name__ == "__main__":
    points_fp = dinamica.inputs['s1']
    variables = dinamica.inputs['t1']

    dataset = create_dataset(points_fp, variables)
    out_filepath = dinamica.inputs['s2']
    dataset.to_parquet(out_filepath)

    print(dataset.head())
    print(dataset.info())