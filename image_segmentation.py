import json
import numpy as np
import pandas as pd
import rasterio
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from rasterio.plot import show as s
from skimage.io import imread, imshow
from skimage.color import rgb2hsv, rgb2gray
from skimage.transform import resize, rescale, rotate, AffineTransform, warp
from skimage.util import crop
from scipy import ndimage
import raster_brick as rb
import cv2
import os



# Step 1) Convert to grayscale
def convert_to_gray(out_image):
    '''
    Converts from 3 layers into a single, transformed gray layer.
    '''
    img = cv2.imread(out_image, 0)

    return img


# Step 2) Extract center given size
def crop_center(img, cropx, cropy):
    '''
    Crops center of image based on given parameters.
    '''
    y,x = img.shape
    startx = x//2 - (cropx//2)
    starty = y//2 - (cropy//2)    

    return img[starty:starty + cropy, startx:startx + cropx]


# Loop through tifs
def loop_and_print():


    count = 1
    while count < 30:
        for filename in os.listdir('/Users/Tammy/Documents/_MSCAPP/Fall 2019/Unsupervised ML/Final Project/mapping-disaster-risk/data/colombia_rural_tifs'):
            img = convert_to_gray(filename)
            crop = crop_center(img, 62, 62)
            plt.subplot(10, 10, count), plt.imshow(crop, cmap='gray')
            count += 1




# Working through this function
def clustering_edges(out_image):
    '''
    Color Quantization, assuming we can leave out the 4th band
    '''

    out_image = out_image[0:3]

    '''
    Step 1) Figure out how to rotate images using rotate(out_image, angle=X)
    
    test = 0
    for i in range(3):
        a = np.count_nonzero(out_image[i, :, 1])
        if a > test:
            test = a

    if test < 10:
        out_image = rotate(out_image, angle=45, cval=1)
    '''

    '''
    Step 2) Figure out how to scale images correctly, or pick an arbitrary scale

    out_image = rescale(out_image, scale=(1))
    out_image = resize(out_image, (3, 100, 100))
    '''

    # Standardize
    normalized = out_image / 255
    vertical = normalized.reshape(out_image.shape[1] *
                                  out_image.shape[2], out_image.shape[0])
    kmeans = KMeans(n_clusters=10, random_state=0).fit(vertical)
    show = kmeans.cluster_centers_[kmeans.labels_]
    cluster_pic = show.reshape(out_image.shape[0],
                               out_image.shape[1], out_image.shape[2])
    
    # Take the most extreme values per band: not sure if sound
    show = np.min(cluster_pic, axis=0)
    s(show, cmap='gist_earth')

    # NEXT STEPS: rotate, flatten data into a single row so each pixel is a feature, cluster



def rotate_and_scale():

    pass


# Probably won't use this
def convert_single_band_to_black_white(band_array):
    '''
    '''

    out_image = out_image[0:3]
    flat = band_array.reshape(band_array.shape[0] * band_array.shape[1])

    for i in range(flat.shape[0]):
        if flat[i] > flat.mean():
            flat[i] = 1
        else:
            flat[i] = 0
    flat = flat.reshape(band_array.shape[0], band_array.shape[1])
    plt.imshow(flat, cmap='gray')



# Probably won't use this
def convert_to_gray(out_image):
    '''
    '''

    out_image = out_image[0:3]
    final = (out_image[0] * 0.299) + (out_image[1] * 0.587) + (out_image[2] * 0.144)
    s(final, cmap='gray')





