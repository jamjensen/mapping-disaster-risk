import json
import random
import pandas as pd
import numpy as np

from matplotlib import pyplot
import rasterio
from pyproj import Proj
from rasterio.mask import mask
from rasterio.plot import show
import raster_brick
import raster_bands


fpath_tiff = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/borde_rural_ortho-cog.tif'
fpath_geojson = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/train-borde_rural.geojson'
proj = Proj(init='epsg:32618')
dataset = rasterio.open(fpath_tiff)


def get_zonal_stats(roof_tif_file):
     ''' 
     Given a single roof tif file return the corresponding feature matrix
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



def go(limit=1):

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


