import numpy as np
import pandas as pd
import cv2
from matplotlib import pyplot as plt
import image_segmentation
import raster_brick
import raster_bands
import file_names as f

IMAGE_PATH = "BIGTST.TIF"


def read_image(image_path):
    '''
    Given a tif path, reads as grayscale and crops using the crop
    function in image_segmentation.py

    Input:
        image_path (tif): a geotif file for a single roof

    Output:
        crop (numpy array): a reduced size numpy array
    '''

    # reads with greyscale
    img = cv2.imread(image_path, 0)

    crop = image_segmentation.crop_center(img, 60, 60)
    # If percentage of zeros is less than 50, continue
    if (np.count_nonzero(crop) / crop.size) > .90:
        
        return crop



def fourier_transform(img, plt=False):
    '''
    Converts an input image from the spatial domain to the frequency
    domain, which provides a plot of high and low frequencies.
    Low frequencies are found in the center and high frequencies
    are scattered around.

    Input:
        img (array): cropped image

    Output:
        dft_shift (array): result of the FFT, but shifted so that low frequencies
            are in the center and high frequencies surround it
        magnitude_spectrum: represents the amount of each frequency present in the
            original image
    '''


    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    # shift so that low frequencies are in center of image
    dft_shift = np.fft.fftshift(dft)

    magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

    if plt:
        plt.subplot(2, 2, 1), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(2, 2, 2), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('After FFT'), plt.xticks([]), plt.yticks([])

    return dft_shift, magnitude_spectrum


def create_band_pass_filter(img):
    '''
    Creates a "Band Pass Filter", which is effectively a mask, that when 
    placed over the FFT image extracts only the attributes we're interested in. 
    High Frequencies depict a sudden change of image contrast from one pixel to another 
    in spatial domain. That’s why they correspond to edges in the spatial domain.  

    Returns:
        mask (array): A Band Pass Filter, same size as the original image, that consists of
            two concentric circles with the area between two circles as one's and rest all zeros.
            It allows a range of frequencies to pass, giving us balance of Low and High frequencies.

    '''

    rows, cols = img.shape
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)
    r_out = 80
    r_in = 10
    center = [crow, ccol]
    x, y = np.ogrid[:rows, :cols]
    mask_area = np.logical_and(((x - center[0]) ** 2 + (y - center[1]) ** 2 >= r_in ** 2),
                               ((x - center[0]) ** 2 + (y - center[1]) ** 2 <= r_out ** 2))
    mask[mask_area] = 1

    return mask

def create_high_pass_filter(img):

    # Circular HPF mask, center circle is 0, remaining all ones
    rows, cols = img.shape
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.ones((rows, cols, 2), np.uint8)
    r = 10
    center = [crow, ccol]
    x, y = np.ogrid[:rows, :cols]
    mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r*r
    mask[mask_area] = 0
    print('HIGH PASS FILTER r')

    return mask

def create_low_pass_filter(img):

    rows, cols = img.shape
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)
    r = 5
    center = [crow, ccol]
    x, y = np.ogrid[:rows, :cols]
    mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r*r
    mask[mask_area] = 1
    print('LOW PASS FILTER')

    return mask


def apply_mask_and_inverse_DFT(dft_shift, mask):
    '''
    Applies the Band Pass Filter to the transformed array and conducts the inverse
    fourier transformation so that we can reprint it as an image. 

    Returns:
        img_back (array): inverse fourier transformation
        fshift_mask_mag (array): transformed array with mask applied
    '''


    fshift = dft_shift * mask

    fshift_mask_mag = 2000 * np.log(cv2.magnitude(fshift[:, :, 0], fshift[:, :, 1]))

    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])


    return fshift_mask_mag, img_back


def print_transformation_single_rooftop():
    '''
    Conducts FFT on a single rooftop
    '''

    crop = read_image(IMAGE_PATH)

    dft_shift, magnitude_spectrum = fourier_transform(crop)
    #mask = create_band_pass_filter(crop)
    mask = create_high_pass_filter(crop)
    #mask = create_low_pass_filter(crop)

    fshift_mask_mag, img_back = apply_mask_and_inverse_DFT(dft_shift, mask)

    #img_back = image_segmentation.crop_center(img_back, 60, 60)
    print(magnitude_spectrum)

    plt.subplot(2, 2, 1), plt.imshow(crop, cmap='gray')
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(2, 2, 2), plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title('After FFT'), plt.xticks([]), plt.yticks([])
    plt.subplot(2, 2, 3), plt.imshow(fshift_mask_mag, cmap='gray')
    plt.title('FFT + Mask'), plt.xticks([]), plt.yticks([])
    plt.subplot(2, 2, 4), plt.imshow(img_back, cmap='gray')
    plt.title('After FFT Inverse'), plt.xticks([]), plt.yticks([])

    print(img_back)
    plt.show()


def go_multiple(limit=1,mask_filter=False):

    ''' 
    Applies FFT transformation to given number of cropped roofs, flattens them,
    and returns a feature matrix 
    '''

    count = 0
    outliers = 0
    label = []
    features = []

    geojson = raster_brick.load_geojson(f.fpath_geojson)
    polygons = raster_brick.make_polygons(geojson)

    for i, polygon in enumerate(polygons):
        if i < limit:
            polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], raster_brick.proj)
            img = raster_brick.get_rooftop_array_after_mask(f.fpath_tiff, polygon, raster_brick.proj)
            if img is not None:
                gray = (img[0] * 0.299) + (img[1] * 0.587) + (img[2] * 0.144)
                crop = image_segmentation.crop_center(gray, 60, 60)
                if (np.count_nonzero(crop) / crop.size) > .90:
                    dft_shift, magnitude_spectrum = fourier_transform(crop)
                    if mask_filter:
                        mask = create_band_pass_filter(crop)
                        fshift_mask_mag, img_back = apply_mask_and_inverse_DFT(dft_shift, mask) 
                    # Flatten                        
                        flat = img_back.flatten()
                    else:
                        flat = magnitude_spectrum.flatten()    
                    
                    label.append(polygon['roof_material'])
                    features.append(flat)
                else:
                    outliers += 1

    df = pd.DataFrame(features, label)

    return df, outliers



