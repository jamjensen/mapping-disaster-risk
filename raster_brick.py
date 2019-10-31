import json
import random

from matplotlib import pyplot
import rasterio
from pyproj import Proj
from rasterio.mask import mask
from rasterio.plot import show

# if importing into iypthon you need to run the magic command so that
# you can print out the roof: 
    # %matplotlib osx

fpath_tiff = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/borde_rural_ortho-cog.tif'
fpath_geojson = '/Users/jamesjensen/Documents/harris/q1_20/UML/Project/stac/colombia/borde_rural/train-borde_rural.geojson'

dataset = rasterio.open(fpath_tiff)
proj = Proj(init='epsg:32618')


def load_geojson(file_path):
    '''
    Given path to geojson file returns the geojson, which is of type
    dictionary and stores the building id, roof material and cooridinates
    of the building
    '''

    with open(file_path) as geojson:
        geojson = json.load(geojson)

    return geojson
    

def make_polgyons(geojson):
    '''
    Given geojson dictionary returns a list of buildings mapped by their coordinates
    '''

    polygons = []
    polygon = {}

    for feature in geojson['features']:
        polygon = {}
        polygon['type'] = feature['geometry']['type']
        polygon['bid'] = feature['id']
        polygon['roof_material'] = feature['properties']['roof_material']
        polygon['coordinates'] = feature['geometry']['coordinates']
        polygons.append(polygon)

    return polygons


def transform_coordinates(coordinates_lists, transform):
    """Transform the coordinates with the provided `affine_transform`
    
    :param coordinates_lists: list of lists of coordinates
    :type coordinates_lists: list[list[int]]
    :param transform: transformation to apply
    :type: pyproj.Proj
    """
    
    transformed_coordinates_lists = []
    for coordinates_list in coordinates_lists:
        transformed_coordinates_list = []
        for coordinate in coordinates_list:
            coordinate = tuple(coordinate)
            transformed_coordinate = list(transform(coordinate[0], coordinate[1]))
            transformed_coordinates_list.append(transformed_coordinate)
        transformed_coordinates_lists.append(transformed_coordinates_list)
    
    return transformed_coordinates_lists


def get_rooftop_array_after_mask(polygon, projection, tiff_path):
    '''
    returns:
        out_image (numpy array): array of pixel values for the given polygon 
    '''

    with rasterio.open(tiff_path) as tiff:
        out_image, out_transform = mask(tiff, [polygon], crop=True)

    return out_image



    
def display_single_roof(out_image):
    '''
    takes numpy array for a single roof and displays it using matplot
    '''

    show(out_image)
        


if __name__ == "__main__":

    # prints single rooftop at random
    geojson = load_geojson(fpath_geojson)
    polygons = make_polgyons(geojson)

    idx = random.randint(0,len(polygons))
    polygon = polygons[idx]

    polygon['coordinates'] = transform_coordinates(polygon['coordinates'], proj)
    out_image = get_rooftop_array_after_mask(polygon, proj, fpath_tiff)

    display_single_roof(out_image)
