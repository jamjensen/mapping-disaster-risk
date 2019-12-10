import numpy as np
import pandas as pd
import raster_brick
import raster_bands
import image_segmentation
from minisom import MiniSom
import file_names as f
from pyproj import Proj
from sklearn.preprocessing import StandardScaler



def go(width=3, height=3, layers=3, sigma=0.1, learning_rate=0.2, limit=10):

    tif = f.fpath_tiff
    proj = Proj(init=f.crs)
    geojson = raster_brick.load_geojson(f.fpath_geojson)
    polygons = raster_brick.make_polygons(geojson)
    rv = pd.DataFrame()
    outliers = 0

    for i, polygon in enumerate(polygons):
        if i < limit:
            # For now, get an image, and perform grayscale/crop/flatten
            polygon['coordinates'] = raster_brick.transform_coordinates(polygon['coordinates'], proj)
            img = raster_brick.get_rooftop_array_after_mask(f.fpath_tiff, polygon, proj)
            if img:
                img = image_segmentation.crop_multi_bands(img, 60, 60)
                pixels = np.reshape(img, (3, img.shape[1] * img.shape[2]))
                standardized_data = StandardScaler().fit_transform(pixels.T)
                som = MiniSom(width, height, layers, sigma, learning_rate)
                som.random_weights_init(standardized_data)
                som.train_random(standardized_data, 100)
                qnt = som.quantization(standardized_data)
                if qnt.T.size == 10800 and (np.count_nonzero(qnt.T) / qnt.T.size > .90):
                    new_img = qnt.T.reshape(3,60,60)
                    #gray = (new_img[0] * 0.299) + (new_img[1] * 0.587) + (new_img[2] * 0.144)
                    #gray = gray.flatten()
                    gray = new_img.flatten()
                    label = []
                    features = []
                    label.append(polygon['roof_material'])
                    features.append(gray)
                    df = pd.DataFrame(features, label)
                    rv = pd.concat([rv, df])
                else:
                    outliers +=1

    rv.to_csv('guatemala_3layer_alldata.csv')
    return outliers

