import numpy as np
import pandas as pd
from footballmodels.opta.event_type import EventType
from footballmodels.opta import functions as F
from footballmodels.opta.dimensions import opta_dims
from footballmodels.opta.distance import (
    progressive_distance,
    distance,
    MIDDLE_GOAL_COORDS,
    TOP_GOAL_COORDS,
    BOTTOM_GOAL_COORDS,
)
from footballmodels.opta.passes import is_open_play_pass


def open_play_second_ball(data):
    df = data.copy()
    df["Longball"] = F.col_has_qualifier(df, display_name="Longball")
    df["SetPieceTaken"] = ~open_play_event(df)
    df["Headpass"] = F.col_has_qualifier(df, display_name="HeadPass")
    second_balls = np.where(
        (df["isTouch"] == 1)
        & (open_play_event(df))
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) == df["teamId"])
            & (df["outcomeType"].shift(2) == 0)
            & (df["SetPieceTaken"].shift(2) == 0)
            & (df["SetPieceTaken"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(4) == True)
            & (df["teamId"].shift(4) == df["teamId"])
            & (df["outcomeType"].shift(4) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["SetPieceTaken"].shift(5) == 0)
            & (df["SetPieceTaken"].shift(6) == 0)
            & (df["endX"].shift(4) < 100)
            & (df["endY"].shift(4) < 100)
        )
        & (
            (df["event_type"].shift(3) == EventType.Aerial)
            & (df["outcomeType"].shift(3) == 1)
            & (df["teamId"].shift(3) != df["teamId"])
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 0)
            & (df["teamId"].shift(2) == df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(3) == True)
            & (df["teamId"].shift(3) == df["teamId"])
            & (df["outcomeType"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["SetPieceTaken"].shift(5) == 0)
            & (df["endX"].shift(3) < 100)
            & (df["endY"].shift(3) < 100)
        )
        & (
            (df["event_type"].shift(2) == EventType.BallRecovery)
            & (df["teamId"].shift(2) != df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) == df["teamId"])
            & (df["outcomeType"].shift(2) == 1)
            & (df["SetPieceTaken"].shift(2) == 0)
            & (df["SetPieceTaken"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (df["Headpass"].shift(1) == True)
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) == df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(4) == True)
            & (df["teamId"].shift(4) != df["teamId"])
            & (df["outcomeType"].shift(4) == 1)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["SetPieceTaken"].shift(5) == 0)
            & (df["SetPieceTaken"].shift(6) == 0)
            & (df["endX"].shift(4) < 100)
            & (df["endY"].shift(4) < 100)
        )
        & (
            (df["event_type"].shift(3) == EventType.Aerial)
            & (df["outcomeType"].shift(3) == 1)
            & (df["teamId"].shift(3) != df["teamId"])
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 0)
            & (df["teamId"].shift(2) == df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                & (df["outcomeType"].shift(1) == 0)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(3) == True)
            & (df["teamId"].shift(3) != df["teamId"])
            & (df["outcomeType"].shift(3) == 1)
            & (df["SetPieceTaken"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["SetPieceTaken"].shift(5) == 0)
            & (df["endX"].shift(3) < 100)
            & (df["endY"].shift(3) < 100)
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 1)
            & (df["teamId"].shift(2) != df["teamId"])
        )
        & (
            (df["event_type"].shift(1) == EventType.Aerial)
            & (df["outcomeType"].shift(1) == 0)
            & (df["teamId"].shift(1) == df["teamId"])
        ),
        1,
        0,
    )
    second_balls += np.where(
        (df["isTouch"] == True)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) != df["teamId"])
            & (df["outcomeType"].shift(2) == 0)
            & (df["SetPieceTaken"].shift(2) == 0)
            & (df["SetPieceTaken"].shift(3) == 0)
            & (df["SetPieceTaken"].shift(4) == 0)
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) == df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    return second_balls.astype(bool)


def set_piece_second_ball(data):
    df = data.copy()
    df["Longball"] = F.col_has_qualifier(df, display_name="Longball")
    df["SetPieceTaken"] = ~open_play_event(df)
    df["Headpass"] = F.col_has_qualifier(df, display_name="HeadPass")
    second_ball = np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) == df["teamId"])
            & (df["outcomeType"].shift(2) == 0)
            & (
                (df["SetPieceTaken"].shift(2) == 1)
                | (df["SetPieceTaken"].shift(3) == 1)
                | (df["SetPieceTaken"].shift(4) == 0)
            )
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(4) == True)
            & (df["teamId"].shift(4) == df["teamId"])
            & (df["outcomeType"].shift(4) == 0)
            & (
                (df["SetPieceTaken"].shift(4) == 1)
                | (df["SetPieceTaken"].shift(5) == 1)
                | (df["SetPieceTaken"].shift(6) == 1)
            )
            & (df["endX"].shift(4) < 100)
            & (df["endY"].shift(4) < 100)
        )
        & (
            (df["event_type"].shift(3) == EventType.Aerial)
            & (df["outcomeType"].shift(3) == 1)
            & (df["teamId"].shift(3) != df["teamId"])
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 0)
            & (df["teamId"].shift(2) == df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(3) == True)
            & (df["teamId"].shift(3) == df["teamId"])
            & (df["outcomeType"].shift(3) == 0)
            & (
                (df["SetPieceTaken"].shift(3) == 1)
                | (df["SetPieceTaken"].shift(4) == 1)
                | (df["SetPieceTaken"].shift(5) == 1)
            )
            & (df["endX"].shift(3) < 100)
            & (df["endY"].shift(3) < 100)
        )
        & (
            (df["event_type"].shift(2) == EventType.BallRecovery)
            & (df["teamId"].shift(2) != df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) == df["teamId"])
            & (df["outcomeType"].shift(2) == 1)
            & (
                (df["SetPieceTaken"].shift(2) == 1)
                | (df["SetPieceTaken"].shift(3) == 1)
                | (df["SetPieceTaken"].shift(4) == 1)
            )
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (df["Headpass"].shift(1) == True)
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) == df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(4) == True)
            & (df["teamId"].shift(4) != df["teamId"])
            & (df["outcomeType"].shift(4) == 1)
            & (
                (df["SetPieceTaken"].shift(4) == 1)
                | (df["SetPieceTaken"].shift(5) == 1)
                | (df["SetPieceTaken"].shift(6) == 1)
            )
            & (df["endX"].shift(4) < 100)
            & (df["endY"].shift(4) < 100)
        )
        & (
            (df["event_type"].shift(3) == EventType.Aerial)
            & (df["outcomeType"].shift(3) == 1)
            & (df["teamId"].shift(3) != df["teamId"])
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 0)
            & (df["teamId"].shift(2) == df["teamId"])
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                & (df["outcomeType"].shift(1) == 0)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) != df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == 1)
        & (df["SetPieceTaken"] == 0)
        & (df["event_type"] != EventType.BallTouch)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(3) == True)
            & (df["teamId"].shift(3) != df["teamId"])
            & (df["outcomeType"].shift(3) == 1)
            & (
                (df["SetPieceTaken"].shift(3) == 1)
                | (df["SetPieceTaken"].shift(4) == 1)
                | (df["SetPieceTaken"].shift(5) == 1)
            )
            & (df["endX"].shift(3) < 100)
            & (df["endY"].shift(3) < 100)
        )
        & (
            (df["event_type"].shift(2) == EventType.Aerial)
            & (df["outcomeType"].shift(2) == 1)
            & (df["teamId"].shift(2) != df["teamId"])
        )
        & (
            (df["event_type"].shift(1) == EventType.Aerial)
            & (df["outcomeType"].shift(1) == 0)
            & (df["teamId"].shift(1) == df["teamId"])
        ),
        1,
        0,
    )
    second_ball += np.where(
        (df["isTouch"] == True)
        & (df["SetPieceTaken"] == 0)
        & (
            ((df["event_type"] != EventType.BallRecovery) & (df["outcomeType"] == 1))
            | (
                (df["event_type"] == EventType.BallRecovery)
                & (df["outcomeType"].shift(-1) == 1)
                & (df["teamId"].shift(-1) == df["teamId"])
            )
        )
        & (
            (df["Longball"].shift(2) == True)
            & (df["teamId"].shift(2) != df["teamId"])
            & (df["outcomeType"].shift(2) == 0)
            & (
                (df["SetPieceTaken"].shift(2) == 1)
                | (df["SetPieceTaken"].shift(3) == 1)
                | (df["SetPieceTaken"].shift(4) == 1)
            )
            & (df["endX"].shift(2) < 100)
            & (df["endY"].shift(2) < 100)
        )
        & (
            (
                (df["event_type"].shift(1) == EventType.Pass)
                | (df["event_type"].shift(1) == EventType.Clearance)
                | (df["event_type"].shift(1) == EventType.Interception)
            )
            & (df["Longball"].shift(1) != True)
            & (df["teamId"].shift(1) == df["teamId"])
            & (df["SetPieceTaken"].shift(1) == 0)
            & (df["position"].shift(1) != "GK")
        ),
        1,
        0,
    )

    return second_ball.astype(bool)


def open_play_event(df: pd.DataFrame) -> pd.Series:
    """
    Determines if an event in the DataFrame represents an open play event.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the event data.

    Returns:
        pd.Series: A boolean Series indicating whether each event is an open play event.
    """
    return (
        ~F.col_has_qualifier(df, display_name="DirectFreekick")
        & ~F.col_has_qualifier(df, display_name="FromCorner")
        & ~F.col_has_qualifier(df, display_name="SetPiece")
        & ~F.col_has_qualifier(df, display_name="FreekickTaken")
        & ~F.col_has_qualifier(df, display_name="CornerTaken")
        & ~F.col_has_qualifier(df, display_name="ThrowIn")
    )


def in_attacking_box(df, start=True):
    """
    Determines if the given coordinates in the DataFrame `df` are within the attacking box.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the coordinates.
    - start (bool): If True, checks if the coordinates are within the attacking box at the start of the event.
                    If False, checks if the coordinates are within the attacking box at the end of the event.

    Returns:
    - pandas.Series: A boolean Series indicating whether each coordinate is within the attacking box.
    """
    x = "x" if start else "endX"
    y = "y" if start else "endY"
    dims = opta_dims()
    return df[x].between(dims.penalty_area_right, dims.right) & df[y].between(
        dims.penalty_area_bottom, dims.penalty_area_top
    )


def in_defensive_box(df, start=True):
    """
    Checks if the coordinates in the given DataFrame `df` are within the defensive box.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the coordinates.
    - start (bool, optional): If True, checks the starting coordinates (default). If False, checks the ending coordinates.

    Returns:
    - pandas.Series: A boolean Series indicating whether each coordinate is within the defensive box.
    """
    x = "x" if start else "endX"
    y = "y" if start else "endY"
    dims = opta_dims()
    return df[x].between(dims.left, dims.penalty_area_left) & df[y].between(
        dims.penalty_area_bottom, dims.penalty_area_top
    )


def is_shot(data: pd.DataFrame) -> pd.Series:
    """
    Determines if the given DataFrame `data` contains a shot event.

    Parameters:
    - data (pandas.DataFrame): The DataFrame containing the event data.

    Returns:
    - pandas.Series: A boolean Series indicating whether each event is a shot event.
    """
    return data["event_type"].isin(
        [
            EventType.Goal,
            EventType.ShotOnPost,
            EventType.MissedShots,
            EventType.SavedShot,
        ]
    )


def xg(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected goals for each event in the given DataFrame `data`.

    Parameters:
    - data (pandas.DataFrame): The DataFrame containing the event data.

    Returns:
    - pandas.Series: A Series containing the expected goals for each event.
    """
    return is_shot(data) * data["xg"]


def in_final_third(data: pd.DataFrame) -> pd.Series:
    """
    Check if the x-coordinate of each data point is in the final third of the field.

    Parameters:
    data (pd.DataFrame): The input data containing the x-coordinate.

    Returns:
    pd.Series: A boolean series indicating whether each data point is in the final third.
    """
    return data["x"] >= 200 / 3


def ppda_qualifying_passes(data: pd.DataFrame) -> pd.Series:
    """
    Filters the given DataFrame to select only the qualifying passes for PPDA calculation.

    Args:
        data (pd.DataFrame): The DataFrame containing the football event data.

    Returns:
        pd.Series: A boolean Series indicating the qualifying passes.
    """
    return (
        open_play_event(data)
        & (data["event_type"].isin([EventType.Pass]))
        & (data["x"] < 60)
    )


def open_play_shot(data: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean Series indicating whether each row in the input DataFrame represents an open play shot.
    An open play shot is defined as a shot that is not from a corner, set piece, penalty, own goal, throw-in set piece, or direct free kick.

    Parameters:
    - data: pd.DataFrame
        The input DataFrame containing the data.

    Returns:
    - pd.Series
        A boolean Series indicating whether each row represents an open play shot.
    """
    return is_shot(data) & (
        ~F.col_has_qualifier(data, display_name="FromCorner")
        & ~F.col_has_qualifier(data, display_name="SetPiece")
        & ~F.col_has_qualifier(data, display_name="Penalty")
        & ~F.col_has_qualifier(data, display_name="OwnGoal")
        & ~F.col_has_qualifier(data, display_name="ThrowinSetPiece")
        & ~F.col_has_qualifier(data, display_name="DirectFreekick")
    )


def set_piece_shot(data: pd.DataFrame) -> pd.Series:
    """
    Determines if a given data represents a set piece shot.

    Args:
        data (pd.DataFrame): The data to be checked.

    Returns:
        pd.Series: True if the data represents a set piece shot, False otherwise.
    """
    return (
        is_shot(data)
        & ~(
            ~F.col_has_qualifier(data, display_name="FromCorner")
            & ~F.col_has_qualifier(data, display_name="SetPiece")
            & ~F.col_has_qualifier(data, display_name="ThrowinSetPiece")
            & ~F.col_has_qualifier(data, display_name="DirectFreekick")
        )
        & (~F.col_has_qualifier(data, display_name="Penalty"))
        & (~F.col_has_qualifier(data, display_name="OwnGoal"))
    )


def open_play_xg(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected goals (xG) for open play shots.

    Parameters:
        data (pd.DataFrame): The input data containing shot information.

    Returns:
        pd.Series: The calculated expected goals for open play shots.
    """
    return xg(data) * open_play_shot(data)


def open_play_box_goal(data: pd.DataFrame) -> pd.Series:
    """
    Determines if a goal occurred from an open play within the attacking box.

    Args:
        data (pd.DataFrame): The input DataFrame containing football event data.

    Returns:
        pd.Series: A boolean Series indicating whether each event is a goal from open play within the attacking box.
    """
    return (
        (data["event_type"] == EventType.Goal)
        & in_attacking_box(data)
        & open_play_shot(data)
    )


def non_penalty_goal(data: pd.DataFrame) -> pd.Series:
    """
    Determines if a goal occurred from an open play within the attacking box.

    Args:
        data (pd.DataFrame): The input DataFrame containing football event data.

    Returns:
        pd.Series: A boolean Series indicating whether each event is a goal from open play within the attacking box.
    """
    return (data["event_type"] == EventType.Goal) & ~F.col_has_qualifier(
        data, display_name="Penalty"
    )


def open_play_box_xg(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected goals (xG) for open play shots inside the attacking box.

    Parameters:
        data (pd.DataFrame): The input data containing shot information.

    Returns:
        pd.Series: The expected goals (xG) for open play shots inside the attacking box.
    """
    return open_play_xg(data) * in_attacking_box(data)


def non_penalty_xg(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected goals (xG) for open play shots inside the attacking box.

    Parameters:
        data (pd.DataFrame): The input data containing shot information.

    Returns:
        pd.Series: The expected goals (xG) for open play shots inside the attacking box.
    """
    return xg(data) * ~F.col_has_qualifier(data, display_name="Penalty") * is_shot(data)


def set_piece_xg(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the expected goals (xG) for set piece actions.

    Parameters:
        data (pd.DataFrame): The input data containing set piece action information.

    Returns:
        pd.Series: The calculated expected goals (xG) for each set piece action.
    """
    return xg(data) * set_piece_shot(data)


def ppda_qualifying_defensive_actions(data: pd.DataFrame) -> pd.Series:
    """
    Filters defensive actions that qualify for PPDA calculation
    in the given DataFrame based on specific criteria.

    Parameters:
        data (pd.DataFrame): The DataFrame containing the defensive actions data.

    Returns:
        pd.Series: A boolean Series indicating whether each action qualifies as a defensive action.
    """
    return (
        data["event_type"].isin(
            [EventType.Tackle, EventType.Interception, EventType.Challenge]
        )
        | ((data["event_type"] == EventType.Foul) & (data["outcomeType"] == 0))
    ) & (data["x"] >= 40)


def ground_duels_won(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the ground duels won based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing event_type and outcomeType columns.

    Returns:
    pd.Series: A series indicating whether each row represents a ground duel won or not.
    """
    return (
        (
            data["event_type"].isin(
                [EventType.Tackle, EventType.TakeOn, EventType.Smother]
            )
        )
        & (data["outcomeType"] == 1)
    ) | (
        (data["event_type"] == EventType.Foul)
        & (data["outcomeType"] == 1)
        & (~F.col_has_qualifier(data, qualifier_code=264))
    )


def ground_duels_total(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the total number of ground duels based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing event_type and outcomeType columns.

    Returns:
    pd.Series: A series indicating whether each row represents a ground duel or not.
    """
    return data["event_type"].isin(
        [
            EventType.Tackle,
            EventType.TakeOn,
            EventType.Smother,
            EventType.Dispossessed,
            EventType.Challenge,
        ]
    ) | (
        (data["event_type"] == EventType.Foul)
        & (~F.col_has_qualifier(data, qualifier_code=264))
    )


def defensive_duel_total(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the total number of defensive duels based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing the events.

    Returns:
    pd.Series: A series indicating whether each event is a defensive duel or not.
    """
    return data["event_type"].isin(
        [
            EventType.Tackle,
            EventType.Smother,
            EventType.Challenge,
        ]
    ) | (
        (data["event_type"] == EventType.Foul)
        & (~F.col_has_qualifier(data, qualifier_code=264))
        & (data["outcomeType"] == 0)
    )


def defensive_duel_won(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the number of defensive duels won based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing the events.

    Returns:
    pd.Series: A series indicating whether each event is a defensive duel won or not.
    """
    return (data["event_type"].isin([EventType.Tackle, EventType.Smother])) & (
        data["outcomeType"] == 1
    )


def aerial_duels_won(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the number of aerial duels won based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing the events.

    Returns:
    pd.Series: A series indicating whether each event is an aerial duel won or not.
    """
    return ((data["event_type"] == EventType.Aerial) & (data["outcomeType"] == 1)) | (
        (data["event_type"] == EventType.Foul)
        & (data["outcomeType"] == 1)
        & (F.col_has_qualifier(data, qualifier_code=264))
    )


def aerial_duels_total(data: pd.DataFrame) -> pd.Series:
    """
    Calculates the total number of aerial duels based on the given data.

    Parameters:
    data (pd.DataFrame): The input data containing the events.

    Returns:
    pd.Series: A series indicating whether each event is an aerial duel or not.
    """
    return (data["event_type"] == EventType.Aerial) | (
        (data["event_type"] == EventType.Foul)
        & (F.col_has_qualifier(data, qualifier_code=264))
    )


def touch(data: pd.DataFrame) -> pd.Series:
    """
    Determines if an event in the given DataFrame represents a touch.

    Parameters:
    data (pd.DataFrame): The DataFrame containing the event data.

    Returns:
    pd.Series: A boolean Series indicating whether each event represents a touch.
    """
    TOUCH_IDS = [
        EventType(id)
        for id in [
            1,
            2,
            3,
            7,
            8,
            9,
            10,
            11,
            2,
            13,
            14,
            15,
            16,
            41,
            42,
            50,
            54,
            61,
            73,
            74,
        ]
    ]

    return (data["event_type"].isin(TOUCH_IDS)) | (
        (data["event_type"] == EventType.Foul) & (data["outcomeType"] == 1)
    )


def counterattack_shot(data: pd.DataFrame) -> pd.Series:
    """
    Checks if a shot is a result of a counterattack.

    Args:
        data (pd.DataFrame): The input DataFrame containing shot data.

    Returns:
        pd.Series: A boolean Series indicating whether each shot is a counterattack shot.
    """
    return is_shot(data) & F.col_has_qualifier(data, display_name="FastBreak")


def is_kickoff(data):
    """
    marks the kickoff events in the data
    """
    data = data.copy()
    rel_data = data[data["event_type"].isin([EventType.Pass, EventType.Goal])].copy()
    rel_data["kickoff"] = False
    rel_values = np.where(
        (rel_data["event_type"] == EventType.Pass)
        & ((rel_data.shift(1)["event_type"] == EventType.Goal)),
        True,
        False,
    )
    rel_data["kickoff"] = rel_values
    data.loc[rel_data.index, "kickoff"] = rel_data["kickoff"]
    data.loc[
        data["id"].isin(data.groupby(["matchId", "period"]).first()["id"]), "kickoff"
    ] = True
    return data["kickoff"].fillna(False).infer_objects(copy=False).astype(bool).values


def assign_possession_team_id(data):

    valid_events = [
        EventType.Pass,
        EventType.GoodSkill,
        EventType.TakeOn,
        EventType.ShotOnPost,
        EventType.BallRecovery,
        EventType.Goal,
        EventType.MissedShots,
        EventType.KeeperPickup,
        EventType.SavedShot,
        EventType.Claim,
    ]
    filtered_data = data[
        (data["event_type"].isin(valid_events))
        | ((data["event_type"] == EventType.Foul) & (data["outcomeType"] == 1))
    ]
    if len(filtered_data) == 0:
        return data.iloc[0]["teamId"]
    team = filtered_data.iloc[0]["teamId"]
    return team


def has_shot_and_touch_in_box(data):
    return (
        len(
            data[
                data["event_type"].isin(
                    [
                        EventType.ShotOnPost,
                        EventType.Goal,
                        EventType.MissedShots,
                        EventType.SavedShot,
                    ]
                )
            ]
        )
        > 0
        or in_attacking_box(data[data["teamId"] == data["possession_owner"]]).sum() > 0
    )


def is_buildup(data):
    if len(data[data["event_type"] == EventType.Pass]) < 8:
        return False
    # partition frame into before and after 8 passes
    idx = data[data["event_type"] == EventType.Pass].index[7]
    after = data.loc[idx:]

    if has_shot_and_touch_in_box(after):

        return True
    return False


def is_fast_break(data):
    data = data[data["teamId"] == data["possession_owner"]].copy()
    if len(data[data["x"] <= 40]) == 0:

        return False
    last_starting_qualifying_event = data[data["x"] <= 40].iloc[-1]
    qualifying = data[is_shot(data) | (in_attacking_box(data))]
    if len(qualifying) == 0:

        return False
    return (
        qualifying.iloc[0]["match_seconds"]
        - last_starting_qualifying_event["match_seconds"]
    ) <= 15


def distance_to_goal(x, y):
    start_distance_to_goal_middle = distance(
        x,
        y,
        MIDDLE_GOAL_COORDS[0],
        MIDDLE_GOAL_COORDS[1],
    )[0]
    start_distance_to_goal_top = distance(
        x,
        y,
        TOP_GOAL_COORDS[0],
        TOP_GOAL_COORDS[1],
    )[0]
    start_distance_to_goal_bottom = distance(
        x,
        y,
        BOTTOM_GOAL_COORDS[0],
        BOTTOM_GOAL_COORDS[1],
    )[0]

    distance_to_goal = np.minimum(
        start_distance_to_goal_middle,
        np.minimum(start_distance_to_goal_top, start_distance_to_goal_bottom),
    )
    return distance_to_goal


def open_play_box_entry(data):
    return (
        (in_attacking_box(data, start=False) & ~in_attacking_box(data, start=True))
        & (data["outcomeType"] == 1)
        & ((is_open_play_pass(data)) | (data["event_type"] == EventType.Carry))
    )
