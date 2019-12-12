import numpy as np
import pandas as pd
import cv2
from matplotlib import pyplot as plt
from pyproj import Proj
import image_segmentation
import raster_brick
import raster_bands
import fourier_transform
import file_names as f
import argparse


def go(args):


    # tif = f.fpath_tiff
    # proj = Proj(init=f.crs)
    # geojson = raster_brick.load_geojson(f.fpath_geojson)
    
    home_dir = "/home/jamesjensen/"
    tif_list = f.tif_list

    for tif_dictionary in tif_list:

        crs = tif_dictionary['crs']

        tif = home_dir + tif_dictionary['tif']
        proj = Proj(init=crs)
        geo_path = home_dir + tif_dictionary['geojson']
        geojson = raster_brick.load_geojson(geo_path)
        output_name = args.output_dir + tif_dictionary['output']

        polygons = raster_brick.make_polygons(geojson)
        #print(polygons)
        rv = pd.DataFrame()


        count = 0
        outliers = 0


        for i, polygon in enumerate(polygons):
            if i < args.limit:
                polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], proj)
                img = raster_brick.get_rooftop_array_after_mask(tif, polygon, proj)
                #print(img)
                # Invalid input checks
                if img is None:
                    continue
                if img.size < (args.pixels * args.pixels):
                    continue
                # Crop image when > 1 layer
                if args.crop_multiple:
                    img = image_segmentation.crop_multi_bands(img, args.pixels, args.pixels)
                # Self-organizing map feature reduction
                if args.SOM:
                    img = image_segmentation.SOM(img=img)
                # Convert to gray
                if args.grayscale:
                    img = (img[0] * 0.299) + (img[1] * 0.587) + (img[2] * 0.144)
                # Crop image down
                if args.crop_single:
                    img = image_segmentation.crop_center(img, args.pixels, args.pixels)
                # Excess whitespace check
                if args.whitespace:
                    if (np.count_nonzero(img) / img.size) < .90:
                        outliers += 1
                        continue
                if args.fourier:
                    dft_shift, magnitude_spectrum = fourier_transform.fourier_transform(img)
                if args.mask:
                    mask = fourier_transform.create_band_pass_filter(img)
                    fshift_mask_mag, img = fourier_transform.apply_mask_and_inverse_DFT(dft_shift, mask)
                if args.zonal:
                    df = pd.DataFrame()
                    if args.grayscale:
                        df[0] = pd.Series(np.median(img))
                    else:
                        for i in range(img.shape[0] - 1):
                            df[i] = pd.Series(np.median(img[i]))
                    df['roof'] = polygon['roof_material']
                    df.set_index('roof', inplace=True)
                if args.flatten:
                    label = []
                    features = []
                    if args.mask:
                        flat = magnitude_spectrum.flatten()
                    else:
                        flat = img.flatten()
                    label.append(polygon['roof_material'])
                    features.append(flat)
                    df = pd.DataFrame(features, label)
                    #print(df)

                rv = pd.concat([rv, df])
                #print(rv)
        
        #print(rv)
        #rv.to_csv(args.csv)
        #return rv
        rv.to_csv(output_name)



if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description='processing dem roofs')

    argparser.add_argument('--grayscale', action='store_true', help='converting tif to grayscale')
    argparser.add_argument('--whitespace', action='store_true', help='get ride of bad whitespace ones')
    argparser.add_argument('--crop_single', action='store_true', help='crop single raster layer')
    argparser.add_argument('--crop_multiple', action='store_true', help='crop raster brick')
    argparser.add_argument('-p', '--pixels', type=int, default=60, help='The number of pixels to crop')
    argparser.add_argument('--flatten', action='store_true', help='Flatten matrix')
    argparser.add_argument('--zonal', action='store_true', help='calculate zonal statistics')
    argparser.add_argument('--fourier', action='store_true', help='conduct fourier transformation')
    argparser.add_argument('-l', '--limit', type=int, default=1, help='Set limit to number of roofs')
    argparser.add_argument('--output_dir', action='store', dest='output_dir', help='"/home/jamesjensen/data/...')
    #argparser.add_argument('-c', '--csv', action='store', dest='csv', help='Name of the stored csv')
    argparser.add_argument('--mask', action='store_true', help='Add filter to FFT')
    argparser.add_argument('--SOM', action='store_true', help='implement a self-organizing map')

    args = argparser.parse_args()

    go(args)
