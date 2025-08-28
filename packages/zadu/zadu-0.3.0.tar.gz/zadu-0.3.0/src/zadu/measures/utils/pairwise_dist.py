from scipy.spatial.distance import cdist
import numpy as np
import numpy.typing as npt
from typing import Callable


def pairwise_distance_matrix(
    point: npt.NDArray, distance_function: str | Callable = "euclidean"
):
    """
    Compute the pairwise distance matrix of the point list.
    You can use any distance function from scipy.spatial.distance.cdist
    or specify a callable function.

    INPUT:
        ndarray: point: list of points
        str or callable: distance_function: distance function to use
    OUTPUT:
        ndarray: pairwise distance matrix
    """
    if callable(distance_function):
        distance_matrix = cdist(point, point, distance_function)
    elif distance_function.lower() == "snn":
        # TODO
        raise NotImplementedError(
            "snn has not yet been implemented as a distance function"
        )
    else:
        distance_matrix = cdist(point, point, distance_function)

    return distance_matrix


def distance_matrix_to_density(
    distance_matrix: npt.NDArray, sigma: float
) -> npt.NDArray:
    """
    Compute the density of each point based on the pairwise distance matrix.

    INPUT:
        ndarray: distance_matrix: pairwise distance matrix
        float: sigma: sigma parameter for the Gaussian kernel
    OUTPUT:
        ndarray: density
    """
    normalized_distance_matrix = distance_matrix / np.max(distance_matrix)
    density = np.sum(np.exp(-(normalized_distance_matrix**2) / sigma), axis=-1)
    density = density / np.sum(density)
    return density
