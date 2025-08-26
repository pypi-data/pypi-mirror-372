import numpy as np


def normalize_vectors(vectors):
    """
    Normalizes an array of vectors.
    :param vectors: An numpy array of vectors
    :return:
    """
    abs_vectors = np.linalg.norm(vectors, axis=1, keepdims=True)
    abs_vectors = np.where(abs_vectors != 0, abs_vectors, 1)
    vectors = vectors / abs_vectors
    return vectors


def get_normalized_cross_product(center_point, point_a, point_b):
    """
    Returns the normalized cross product between three points.
    :param center_point:
    :param point_a:
    :param point_b:
    :return:
    """

    v1 = point_a - center_point
    v2 = point_b - center_point
    norm = np.cross(v1, v2)

    n = np.linalg.norm(norm, axis=0, keepdims=True)
    return norm / n
