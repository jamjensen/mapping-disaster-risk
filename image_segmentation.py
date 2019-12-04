'''
NOTE: currently this only works correctly when functions are copied into
ipython and you are in the directory with the tif images.

Not entirely sure why!
'''
import numpy as np
import pandas as pd
from pyproj import Proj
import rasterio
from matplotlib import pyplot as plt
from rasterio.plot import show as s
from skimage.io import imread, imshow
import raster_brick
import raster_bands
import file_names as f
import cv2
import os

tif_path = f.fpath_tiff
proj = Proj(init=f.crs)


# Step 1) Convert to grayscale (reduces to a single layer)
def convert_to_gray(out_image):
    '''
    Converts image from multiple layers into a single, transformed gray
    image using a linear transformation.

    Input:
        out_image (tif): a geotif file for a single roof

    Output:
        img (numpy array): a 1 dimensional numpy array
    '''
    img = cv2.imread(out_image, 0)

    return img



# Step 2) Extract center given specified size (eg. 60 x 60)
def crop_center(img, cropx, cropy):
    '''
    Crops an image down to it's center given a specified size.

    Inputs:
        img (numpy array): numpy array representing an image
        cropx (int): specified number of rows
        cropy (int): specified number of columns

    Output:
        img (numpy array): a reduced size numpy array
    '''
    y, x = img.shape
    startx = x//2 - (cropx//2)
    starty = y//2 - (cropy//2)    
    endx = startx + cropx
    endy = starty + cropy

    return img[starty:endy, startx:endx]


# Step 3) Loop through tifs and print processed images as a grid to inspect
def loop_and_print(how_many, grid_rows, grid_cols):
    '''
    Loops through tif files, converts to grayscale, crops to 60x60, and
    outputs the images of each of the tifs. Drops any tifs with greater than
    5% whitespace.

    Inputs:
        how_many (int): number of images to loop through
        grid_rows (int): number of rows in final output file
        grid_cols (int): number of cols in final output file

    Output:
        outliers (int): number of images with >5% whitespace after processing
    '''
    count = 0
    outliers = 0
    fig = plt.figure(figsize=(grid_rows, grid_cols))

    for filename in os.listdir(tif_path):
        img = convert_to_gray(filename)
        crop = crop_center(img, 60, 60)
        # If percentage of zeros is less than 50, continue
        if (np.count_nonzero(crop) / crop.size) > .90:
            count += 1
            fig.add_subplot(10, 10, count)
            plt.imshow(crop)
        else:
            outliers += 1
        if count >= how_many:
            continue
    
    return outliers


# Step 4) Loop through all tiffs, process, and include in a dataframe
def go(limit=1):
    '''

    '''
    tif = f.fpath_tiff
    geojson = raster_brick.load_geojson(f.fpath_geojson)
    polygons = raster_brick.make_polygons(geojson)

    count = 0
    outliers = 0
    label = []
    features = []

    for i, polygon in enumerate(polygons):
        if i < limit:
            polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], proj)
            img = raster_brick.get_rooftop_array_after_mask(f.fpath_tiff, polygon, proj)
            # Convert to gray
            gray = (img[0] * 0.299) + (img[1] * 0.587) + (img[2] * 0.144)
            # Crop image down
            crop = crop_center(gray, 60, 60)
            if (np.count_nonzero(crop) / crop.size) > .90:
                count += 1
                # Flatten
                flat = crop.flatten()
                label.append(polygon['roof_material'])
                features.append(flat)
            else:
                outliers += 1
    df = pd.DataFrame(features, label)
    
    return df, outliers

# Step 5) Save to CSV
def save_df_as_csv(file_name, limit=1):

    df, outliers = go(limit=limit)
    df.to_csv(file_name)

