import numpy as np
import pandas as pd
from footballmodels.opta.dimensions import Standardizer

MIDDLE_GOAL_COORDS = (100, 50)
TOP_GOAL_COORDS = (100, 56)
BOTTOM_GOAL_COORDS = (100, 44)


class Distance:
    """
    Computes actual distance between two points on a football pitch
    """

    def __init__(self):
        self._standardizer = Standardizer(pitch_from="opta", pitch_to="uefa")

    def __call__(
        self, x0: np.ndarray, y0: np.ndarray, x1: np.ndarray, y1: np.ndarray
    ) -> np.ndarray:
        """
        Computes the distance between two points on a football pitch

        Args:
            x0 (np.ndarray): The x coordinates of the first points
            y0 (np.ndarray): The y coordinates of the first points
            x1 (np.ndarray): The x coordinates of the second points
            y1 (np.ndarray): The y coordinates of the second points

        """
        if not isinstance(x0, np.ndarray):
            x0 = np.array([x0])
            y0 = np.array([y0])
            x1 = np.array([x1])
            y1 = np.array([y1])

        # xs, ys=self._standardizer.transform([x0, x1], [y0, y1])
        x0, y0 = self._standardizer.transform(x0, y0)
        x1, y1 = self._standardizer.transform(x1, y1)
        return np.sqrt(np.power(x1 - x0, 2) + np.power(y1 - y0, 2))


distance = Distance()


def progressive_distance(whoscored_df: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean series indicating whether each event in a dataframe is a progressive pass

    Args:
        whoscored_df (pd.DataFrame): The dataframe

    Returns:
        pd.Series: True if the event is a progressive pass, False otherwise

    """

    start_distance_to_goal_middle = distance(
        whoscored_df["x"],
        whoscored_df["y"],
        MIDDLE_GOAL_COORDS[0],
        MIDDLE_GOAL_COORDS[1],
    )
    start_distance_to_goal_top = distance(
        whoscored_df["x"],
        whoscored_df["y"],
        TOP_GOAL_COORDS[0],
        TOP_GOAL_COORDS[1],
    )
    start_distance_to_goal_bottom = distance(
        whoscored_df["x"],
        whoscored_df["y"],
        BOTTOM_GOAL_COORDS[0],
        BOTTOM_GOAL_COORDS[1],
    )
    start_distance = np.minimum(
        start_distance_to_goal_middle,
        np.minimum(start_distance_to_goal_top, start_distance_to_goal_bottom),
    )

    end_distance_to_goal_middle = distance(
        whoscored_df["endX"],
        whoscored_df["endY"],
        MIDDLE_GOAL_COORDS[0],
        MIDDLE_GOAL_COORDS[1],
    )
    end_distance_to_goal_top = distance(
        whoscored_df["endX"],
        whoscored_df["endY"],
        TOP_GOAL_COORDS[0],
        TOP_GOAL_COORDS[1],
    )
    end_distance_to_goal_bottom = distance(
        whoscored_df["endX"],
        whoscored_df["endY"],
        BOTTOM_GOAL_COORDS[0],
        BOTTOM_GOAL_COORDS[1],
    )
    end_distance = np.minimum(
        end_distance_to_goal_middle,
        np.minimum(end_distance_to_goal_top, end_distance_to_goal_bottom),
    )

    return start_distance[0] - end_distance[0]
