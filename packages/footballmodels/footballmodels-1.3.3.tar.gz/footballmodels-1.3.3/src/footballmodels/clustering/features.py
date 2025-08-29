import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from footballmodels.opta.functions import col_get_qualifier_value
from footballmodels.opta.distance import progressive_distance
from footballmodels.model_files import load_model


def four_factor_model(data: pd.DataFrame) -> np.ndarray:
    """
    Returns an array of the four factor model features for each event in a dataframe
    The factors used are x coordinate of pass origin, y coordinate of pass origin, pass angle, and progressive distance of the pass

    Args:
        data (pd.DataFrame): The dataframe.  Must contain columns 'x', 'y', 'endX','endY', and
          'qualifiers', where the qualifiers column is a list of dicts of the form
        {
            "type": {"value": int, "displayName": str},
            "value": int
        }

    Returns:
        np.ndarray: An array of the four factor model features for each event in the dataframe
    """
    data_n = data.copy()
    data_n["pass_angle"] = col_get_qualifier_value(data, display_name="Angle")
    data_n["progressive_distance"] = progressive_distance(data)
    features = data_n[["x", "y", "progressive_distance", "pass_angle"]]
    scaler = load_model("pass_scaler")
    features_std = scaler.transform(features)
    return features_std
