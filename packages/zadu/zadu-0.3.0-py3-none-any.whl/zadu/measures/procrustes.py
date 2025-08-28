import numpy as np
import numpy.typing as npt
from numpy.linalg import svd
from .utils import knn


def measure(
    orig: npt.NDArray, emb: npt.NDArray, k: int = 20, knn_info: tuple | None = None
) -> dict:
    """
    Compute procrustes statistics
    INPUT:
            ndarray: orig: original data
            ndarray: emb: embedded data
          int: k: number of nearest neighbors to consider
    OUTPUT:
            Procrustes score
    """
    # k nearest neighbors in original space and embedded space each
    if knn_info is None:
        orig_knn_indices = knn.knn(orig, k)
        emb_knn_indices = knn.knn(emb, k)
    else:
        orig_knn_indices, emb_knn_indices = knn_info

    g_list = []

    for i in range(orig.shape[0]):
        origin_neighbors = orig[orig_knn_indices[i]]
        embedd_neighbors = emb[emb_knn_indices[i]]

        k = origin_neighbors.shape[0]
        I = np.eye(k)
        ones = np.ones((k, k))
        H = I - (1 / k) * ones

        U, _, V_T = svd(origin_neighbors.T @ H @ embedd_neighbors, full_matrices=False)
        A = U @ V_T
        A_T = A.T

        g = (
            np.linalg.norm(H @ (origin_neighbors - embedd_neighbors @ A_T), ord="fro")
            ** 2
        )
        g_normalized = g / np.linalg.norm(H @ origin_neighbors, ord="fro") ** 2
        g_list.append(g_normalized)

    procrustes = np.mean(g_list)

    return {"procrustes": procrustes}
