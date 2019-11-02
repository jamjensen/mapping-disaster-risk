import json
import random
import pandas as pd

import rasterio
from pyproj import Proj
import numpy as np
from matplotlib import pyplot
import raster_brick



fpath_tiff = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/borde_rural_ortho-cog.tif'
fpath_geojson = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/train-borde_rural.geojson'

dataset = rasterio.open(fpath_tiff)

'''
The goal of this script is to extract the pixel matrix of a single roof in a given tif file, create 
a new tif file for the single roof, process the raster bands of the new tif file, and display each
band with a corresponding colorbar.

'''


def write_building_footprint_to_raster(dataset, out_image, polygon, name):
     '''
     Given numpy array with the pixel values for a given building footprint,
     writes the array back into a raster file so that we can work with each 
     individual frequency band. 

     Dataset (tiff file): the dataset from which the out_image was extracted from
     out_image (np array): an array whose coordinates align with the polygon building
          footprint and whose cell values are the image pixels.
     name (str): name of the output raster file, saved as .tif
     '''

     if len(out_image.shape) > 2:
          c = out_image.shape[0]
          h = out_image.shape[1]
          w = out_image.shape[2]
     else:
          c = 1
          h = out_image.shape[0]
          w = out_image.shape[1]


     with rasterio.Env():
          profile = dataset.profile 
          profile.update( 
              dtype=rasterio.uint8, 
              count=c, 
              height=h, 
              width=w, 
              compress='lzw') 

          with rasterio.open(name,'w', **profile) as dst:
               dst.update_tags(roof_material=polygon['roof_material'])
               dst.update_tags(bid=polygon['bid'])
               dst.write(out_image.astype(rasterio.uint8))




def open_and_plot_tif(tif_file):

     tif = rasterio.open(tif_file)

     # to see the entire image
     # show(tif.read())4
     fig, (axr, axg, axb) = pyplot.subplots(1,3, figsize=(21,7))

     bands = [axr,axg,axb]
     colors = ['inferno', 'gist_earth', 'Blues']
     mapping = dict(zip(bands,colors))

     for i, (k,v) in enumerate(mapping.items()):
          
          im = k.imshow(tif.read(i+1), cmap=v)
          fig.colorbar(im, ax=k)
          k.title.set_text(v)
     
     pyplot.show()




if __name__ == "__main__":

     proj = Proj(init='epsg:32618')

     geojson = raster_brick.load_geojson(fpath_geojson)
     polygons = raster_brick.make_polgyons(geojson)

     idx = random.randint(0,len(polygons))
     polygon = polygons[idx]

     polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], proj)
     out_image = raster_brick.get_rooftop_array_after_mask(polygon, proj, fpath_tiff)

     write_building_footprint_to_raster(dataset, out_image, polygon, 'BIGTST.tif')
     open_and_plot_tif('BIGTST.tif')















