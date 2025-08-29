from dinamicarslib.dataset import create_sample_points, union_vector_tables
from dinamicarslib.utils import *
try:
    dinamica.inputs
except:
    from dinamicaClass import dinamicaClass
    dinamica = dinamicaClass({'s1':r"\\Nebula\homes\Pesquisa\Sensoriamento Remoto\Mappia\AC\Amostra\Poligonos\formacao_florestal.gpkg", 'v1':100, 's2':r"\\Nebula\homes\Pesquisa\Sensoriamento Remoto\Mappia\AC\Amostra\Poligonos\concat\sampples_concat.gpkg",
    't1': [['Indices', 'Filenames'], [1.0, '//Nebula/homes/Pesquisa/Sensoriamento Remoto/Mappia/AC/Amostra/Poligonos\\agua.gpkg'], [2.0, '//Nebula/homes/Pesquisa/Sensoriamento Remoto/Mappia/AC/Amostra/Poligonos\\formacao_florestal.gpkg'], [3.0, '//Nebula/homes/Pesquisa/Sensoriamento Remoto/Mappia/AC/Amostra/Poligonos\\formacao_n_florestal.gpkg'], [4.0, '//Nebula/homes/Pesquisa/Sensoriamento Remoto/Mappia/AC/Amostra/Poligonos\\silvicultura.gpkg'], [5.0, '//Nebula/homes/Pesquisa/Sensoriamento Remoto/Mappia/AC/Amostra/Poligonos\\uso_antropico.gpkg']],
    't2':[['Band_Name', 'Filenames'],
            ['B02',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B02\\B02_tile_1158.tif'],
            ['B03',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B03\\B03_tile_1158.tif'],
            ['B04',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B04\\B04_tile_1158.tif'],
            ['B05',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B05\\B05_tile_1158.tif'],
            ['B06',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B06\\B06_tile_1158.tif'],
            ['B07',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B07\\B07_tile_1158.tif'],
            ['B08',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B08\\B08_tile_1158.tif'],
            ['B8A',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B8A\\B8A_tile_1158.tif'],
            ['B11',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B11\\B11_tile_1158.tif'],
            ['B12',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\B12\\B12_tile_1158.tif'],
            ['P_B_01',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\P_B_01\\P_B_01_tile_1158.tif'],
            ['P_B_02',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\P_B_02\\P_B_02_tile_1158.tif'],
            ['P_B_03',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\P_B_03\\P_B_03_tile_1158.tif'],
            ['P_B_04',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\P_B_04\\P_B_04_tile_1158.tif'],
            ['MNDWI',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\MNDWI\\MNDWI_tile_1158.tif'],
            ['GNDVI',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\GNDVI\\GNDVI_tile_1158.tif'],
            ['AWEI_nsh',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\AWEI_nsh\\AWEI_nsh_tile_1158.tif'],
            ['AWEI_sh',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\AWEI_sh\\AWEI_sh_tile_1158.tif'],
            ['NDWI',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\NDWI\\NDWI_tile_1158.tif'],
            ['EVI',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\EVI\\EVI_tile_1158.tif'],
            ['NDVI',
            '//Nebula/homes/Pesquisa/Sensoriamento '
            'Remoto/Mappia/AC/Mosaicos/tiles\\NDVI\\NDVI_tile_1158.tif']]}
)
    

def test_concat(list_filenames, out_filename):
    concat = union_vector_tables(list_filenames, 'id', True)
    concat.to_file(out_filename)

    
if __name__ == '__main__':
    
    out_file = dinamica.inputs['s2']
    table = dinamica.inputs['t1']
    test_concat(table, out_file)