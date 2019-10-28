import json

import rasterio
from pyproj import Proj
from rasterio.mask import mask
from rasterio.plot import show

# if importing into iypthon you need to run the magic command so that
# you can print out the roof: 
    # %matplotlib osx

fpath_tiff = 'stac/colombia/borde_rural/borde_rural_ortho-cog.tif'
fpath_geojson = 'stac/colombia/borde_rural/train-borde_rural.geojson'

unread_tiff = rasterio.open(fpath_tiff)
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
    

def make_polgyons(geojson, n=1):
    '''
    Given geojson dictionary returns a list of buildings mapped by their coordinates
    I've included the n so that you can cut off the number of building footprints
    '''

    polygons = []
    for i, feature in enumerate(geojson['features']):
        if i < n:
            polygons.append(feature['geometry'])

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

    
def display_single_roof(polygon, projection, tiff_path):

    polygon['coordinates'] = transform_coordinates(polygon['coordinates'], proj)
    
    with rasterio.open(tiff_path) as tiff:
        out_image, out_transform = mask(tiff, [polygon], crop=True)
        show(out_image)


if __name__ == "__main__":

    geojson = load_geojson(fpath_geojson)
    polygon0 = make_polgyons(geojson, 1)[0]
    # polygon0['coordinates'] = transform_coordinates(polygon0['coordinates'], proj)
    display_single_roof(polygon0, proj, fpath_tiff)

