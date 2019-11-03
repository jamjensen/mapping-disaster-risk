import json
import numpy as np
import pandas as pd
import rasterio
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from rasterio.plot import show as s
from skimage.io import imread, imshow
from skimage.color import rgb2hsv
from skimage.transform import resize, rescale, rotate
from scipy import ndimage
import raster_brick as rb

'''
def convert_single_band_to_black_white(band_array):
    '''
    '''

    # Normalize and data
    flat = band_array.reshape(band_array.shape[0] * band_array.shape[1])

    for i in range(flat.shape[0]):
        if flat[i] > flat.mean():
            flat[i] = 1
        else:
            flat[i] = 0
    flat = flat.reshape(band_array.shape[0], band_array.shape[1])
    plt.imshow(flat, cmap='gray')
'''

def clustering_edges(out_image):

    # This is a version of color quantization I believe
    # Leaving out first band for now
    # In the future, just import out_image
    
    # USE TO GIVE YOU A RANDOM IMAGE
    #polygon, out_image = rb.go(return_polygon_and_image=True)

    # SELECT 3 BANDS
    out_image = out_image[1:4]

    # ROTATE IMAGES - still figuring out
    # if out_image.shape[2] > out_image.shape[1]:
        # out_image = rotate(out_image, angle=45)
    # rotate(image, angle=45, resize=True)

    # SCALE IMAGES
    #out_image = resize(out_image, (3, 115, 115)) # one option
    # out_image = rescale(out_image, scale=(1))

    
    # STANDARDIZE
    normalized = out_image / 255
    vertical = normalized.reshape(out_image.shape[1] *
                                  out_image.shape[2], out_image.shape[0])
    kmeans = KMeans(n_clusters=10, random_state=0).fit(vertical)
    show = kmeans.cluster_centers_[kmeans.labels_]
    cluster_pic = show.reshape(out_image.shape[0],
                               out_image.shape[1], out_image.shape[2])
    
    # Code to where I take the mean of values per band: not sure if sound
    # Otherwise use commented out code below

    show = np.min(cluster_pic, axis=0)
    s(show, cmap='gist_earth')


    '''
    # Code to see three bands:

    fig, (axr, axg, axb) = plt.subplots(1, 3, figsize=(21,7))
    bands = [axr, axg, axb]
    colors = ['gist_earth', 'gist_earth', 'gist_earth']
    mapping = dict(zip(bands, colors))
    for i, (k, v) in enumerate(mapping.items()):
        im = k.imshow(cluster_pic[i], cmap=v)
        fig.colorbar(im, ax=k)
        k.title.set_text(v)
     
    plt.show()
    '''



#NEXT STEPS: rotate, then flatten data into a single row so each pixel is a feature, then cluster


def rotate_and_resize_image():
    '''
    '''
    pass



