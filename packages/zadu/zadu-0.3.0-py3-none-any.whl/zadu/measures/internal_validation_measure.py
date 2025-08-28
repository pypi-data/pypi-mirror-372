from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)
import numpy.typing as npt


def measure(emb: npt.NDArray, label: npt.NDArray, measure: str = "silhouette") -> dict:
    """
    Compute internal validation measure of the embedding
    INPUT:
        ndarray: emb: embedded data
        str: measure: internal validation measure to compute (Optional) Currently supports "silhouette", "calinski_harabasz", "davies_bouldin"
    OUTPUT:
        dict: internal validation measure value
    """

    measure = measure.lower()

    if measure == "silhouette":
        score = silhouette_score(emb, label)
    elif measure == "calinski_harabasz":
        score = calinski_harabasz_score(emb, label)
    elif measure == "davies_bouldin":
        score = davies_bouldin_score(emb, label)

    return {measure: score}
