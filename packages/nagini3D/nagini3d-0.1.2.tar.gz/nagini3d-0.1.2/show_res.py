from argparse import ArgumentParser
import numpy as np
from tifffile import imread
import napari 


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-p", "--points")
    parser.add_argument("-i", "--input")

    args = parser.parse_args()

    points_file = args.points
    img_file = args.input

    img = imread(img_file)[..., :200]

    contours = np.load(points_file)


    points = contours["points"]
    facets = contours["facets"]
    values = contours["values"]

    viewer = napari.view_labels(img, ndisplay=3)

    for point_cloud in points[0:50]:
        viewer.add_surface((point_cloud, facets, values), colormap="I Orange")

    napari.run()