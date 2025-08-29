import numpy as np


def cartesian_distance(point: np.ndarray, all_points: np.ndarray) -> np.ndarray:
    """Calculate the cartesian distance between a point and all other points in a set.

    Args:
        point (np.ndarray): The point to calculate the distance from.
        all_points (np.ndarray): The set of points to calculate the distance to.

    Returns:
        np.ndarray: The cartesian distance between the point and all other points in the set.
    """
    return np.linalg.norm(point - all_points, axis=1)


def weighted_cartesian_distance(
    point: np.ndarray, all_points: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    """Calculate the weighted cartesian distance between a point and all other points in a set.

    Args:
        point (np.ndarray): The point to calculate the distance from.
        all_points (np.ndarray): The set of points to calculate the distance to.
        weights (np.ndarray): The weights to apply to each dimension of the points.

    Returns:
        np.ndarray: The weighted cartesian distance between the point and all other points in the set.
    """
    return np.linalg.norm((point - all_points) * weights, axis=1)


def weighted_l1_distance(
    point: np.ndarray, all_points: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    """Calculate the weighted L1 distance between a point and all other points in a set.

    Args:
        point (np.ndarray): The point to calculate the distance from.
        all_points (np.ndarray): The set of points to calculate the distance to.
        weights (np.ndarray): The weights to apply to each dimension of the points.

    Returns:
        np.ndarray: The weighted L1 distance between the point and all other points in the set.
    """
    return np.sum(np.abs((point - all_points) * weights), axis=1)
