import json
import random
import pandas as pd
import numpy as np

from matplotlib import pyplot
import rasterio
import rasterstats
from pyproj import Proj
from rasterio.mask import mask
from rasterio.plot import show
import raster_brick
import raster_bands


fpath_tiff = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/borde_rural_ortho-cog.tif'
fpath_geojson = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/train-borde_rural.geojson'
PROJ = Proj(init='epsg:32618')
dataset = rasterio.open(fpath_tiff)


def get_zonal_stats_JJ_TEST(roof_tif_file):
     ''' 
     Given a single roof tif file return the corresponding feature matrix
     
     This is james' test version. I'm recreating the functionality of the zonal_stats function
     to see what it actually does -- by comparing the output of this function and that of 
     get_zonal_stats() you can see that the zonal_stats method from rasterstats package drops NO DATA,
     which is represented as a 0 in the array. 
     '''

     df = pd.DataFrame()
     tif = rasterio.open(roof_tif_file)

     for i in range(len(tif.colorinterp)):
          
          raster = tif.read(i+1)
          min = raster.min()
          max = raster.max()
          avg = np.mean(raster)
          med = np.median(raster)

          df[i] = pd.Series(med)

     df['roof'] = tif.tags()['roof_material']
     df.set_index('roof', inplace=True)

     return df



def get_zonal_stats(polygons, tif_file):
     ''' 
     Given a single roof tif file return the corresponding feature matrix
     '''
     rv = pd.DataFrame()

     for polygon in polygons:
          polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], PROJ)

          df = pd.DataFrame()

          for i in range(1,4):
          
               tats = rasterstats.zonal_stats(polygon,
                    tif_file,
                    stats=['min', 'max', 'median', 'majority', 'sum'],
                    band=i)

               df[i] = pd.Series(tats[0]['median'])

          df['roof'] = polygon['roof_material']
          df.set_index('roof', inplace=True)
          frames = [rv, df]
          rv = pd.concat(frames)

     return rv


def go(limit=1):
     '''
     Returns a feature matrix where a row represents a single roof and the columns
     represent the zonal statistic for each raster band. The limit determines the number
     of roofs to include in the matrix.
     '''

     geojson = raster_brick.load_geojson(fpath_geojson)
     polygons = raster_brick.make_polgyons(geojson)
     rv = pd.DataFrame()

     for i, polygon in enumerate(polygons):

          if i < limit:
               file_name = polygon['bid'] + '.tif'
               polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], proj)
               out_image = raster_brick.get_rooftop_array_after_mask(polygon, proj, fpath_tiff)
               raster_bands.write_building_footprint_to_raster(dataset, out_image, polygon, file_name)

               df = get_zonal_stats(file_name)
               frames = [rv, df]
               rv = pd.concat(frames)

     return rv


