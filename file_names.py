'''
Local tif names
'''
current_user = 'j'

tif_list = [{'tif':"borde_rural_ortho-cog.tif",
    'crs': 'epsg:32618',
    'geojson': 'train-borde_rural.geojson',
    'output': 'colombia_rural_zonal.csv'},
    {'tif':"borde_soacha_ortho-cog.tif",
    'crs': 'epsg:32618',
    'geojson':'train-borde_soacha.geojson',
    'output': 'colombia_soacha_zonal.csv'},
    {'tif':"mixco_1_and_ebenezer_ortho-cog.tif",
    'crs': 'epsg:32616',
    'geojson': 'train-mixco_1_and_ebenezer.geojson',
    'output': 'guatemala_mixco_1_zonal.csv'},
    {'tif':"mixco_3_ortho-cog.tif",
    'crs': 'epsg:32616',
    'geojson': 'train-mixco_3.geojson',
    'output': 'guatemala_mixco_3_zonal.csv'},
    {'tif':"castries_ortho-cog.tif",
    'crs': 'epsg:32620',
    'geojson': 'train-castries.geojson',
    'output': 'stlucia_castries_zonal.csv'},
    {'tif':"dennery_ortho-cog.tif",
    'crs': 'epsg:32620',
    'geojson': 'train-dennery.geojson',
    'output': 'stlucia_dennery_zonal.csv'},
    {'tif':"gros_islet_ortho-cog.tif",
    'crs': 'epsg:32620',
    'geojson': 'train-gros_islet.geojson',
    'output': 'stlucia_gros_islet_zonal.csv'}]

if current_user == 'tj':
    fpath_tiff = '/Users/Tammy/Documents/_MSCAPP/Fall 2019/Unsupervised ML/' \
                   'Final Project/stac/colombia/borde_rural/borde_rural_' \
                   'ortho-cog.tif'
    fpath_geojson = '/Users/Tammy/Documents/_MSCAPP/Fall 2019/Unsupervised ML/' \
                    'Final Project/stac/colombia/borde_rural/train-borde_rural' \
                    '.geojson'

if current_user == 'j':
    fpath_tiff = '/home/jamesjensen/castries_ortho-cog.tif'
    fpath_geojson = '/home/jamesjensen/train-castries.geojson'

crs = 'epsg:32620'
building_tif = 'BIGTST.tif' 
