# mapping-disaster-risk
MACS 40800: Unsupervised Machine Learning 

## About
This analysis was conducted by Tamara Glazer and James Jensen for the Unsupervised Machine Learning course at the University of Chicago. This study uses data provided by [DrivenData](https://www.drivendata.org/competitions/58/disaster-response-roof-type/data/), an organization working at the intersection of data science and social impact. The authors benefited greatly from computing resources made available by the [RCC](https://rcc.uchicago.edu/resources) at the University of Chicago. With the use of these resources, they were able to properly store, compare, and cluster satellite images by rooftop material across all seven TIF files present in the dataset. 

### Setup
This project assumes the use of Python 3.7+ and R 3.6+

* Run `pip install -requirements.txt` in the top level of the repository
* Run `install.packages("pacman")`. All additional packages will use pacman to install and load, if you do not already have them. 
* In total the tif files are over 35 GB, however, they are cloud optimzed. We recommend hosting them or downloading and working with a single file at a time. 

### Data Processing

The data consists of seven tif files, two from Guatemala, two from Colombia, and three from St. Lucia. The following files contain multiple methods that transform the images into numeric pixel values, creating datasets that can be used for clustering. The primary script used to generate a dataset is main_process.py and it calls the following: 

```
fourier_transform.py: handles all input image fourier transformations

image_segmentation.py: crops images to a set number of pixels and implements self-organizing maps for feature detection and color quantization.

raster_brick.py: takes crs projection and polygon coordinates to extract out a single rooftop
```

* Start in `processing/`
* View all possible dataset manipulations using `python3 main_process.py --help`
* Run `python3 main_process.py` with desired transformations
    * For example, run `python3 main_process.py --grayscale --crop_single --flatten` to transform all of the roofs to grayscale, crop a 60x60 pixel squre from the center each roof, then create an nx3600 dataset, where n is the number of roofs and 3600 represents each pixel in the cropped roof. 


#### Test Data
Several smaller datasets -- containing 400 or fewer processed roofs -- can be found in the data folder. They are examples of both flattened and zonal datasets, which can be passed to our clustering algorithms. 


### Analysis

The primary analysis script can be found in `analysis/`. Passing a dataset through this script will make use of the K-means, PAM, and Hierarchical Agglomerative Clustering algoritms. The output of this script will contain plots for each clustering method as well as csv files that display how the unsupervised methods compared to the actual labels. The results from our analysis can be found in `results/`.

This R script takes two parameters: (1) the path to the input csv and (2) the location to save the plots and tables.

* To run the analysis script: `Rscript RClusterScript.R --input --output`

We've also included the R Notebook --  `cluster_and_plot.Rmd` -- that, for a given dataset, walks through the process of  generating a feature matrix, passing it through the K-means, PAM, and Hierarchical Clustering Algorithms, and rendering the output. 





