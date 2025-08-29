import pandas as pd
from typing import Tuple
import numpy as np
from footballmodels.opta import functions as F
from footballmodels.opta.distance import distance
from footballmodels.opta.passes import is_open_play_pass


def filter_to_open_play_passes(data: pd.DataFrame) -> pd.DataFrame:
    print(data.shape[0])
    data_n = data.loc[is_open_play_pass(data)].copy()
    print(data_n.shape[0])
    data_n = data_n.loc[~F.col_has_qualifier(data_n, qualifier_code=123)].copy()
    print(data_n.shape[0])
    data_n = data_n.loc[~F.col_has_qualifier(data_n, qualifier_code=124)].copy()
    print(data_n.shape[0])
    return data_n


def x_pass_features(data: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    data_n = filter_to_open_play_passes(data)

    data_n["pass_angle"] = F.col_get_qualifier_value(
        data_n, display_name="Angle"
    ).astype(float)
    data_n["pass_length"] = distance(
        data_n["x"].values,
        data_n["y"].values,
        data_n["endX"].values,
        data_n["endY"].values,
    )
    data_n["is_chipped"] = F.col_has_qualifier(data_n, qualifier_code=155).astype(int)
    data_n["is_headpass"] = F.col_has_qualifier(data_n, qualifier_code=3).astype(int)
    data_n["is_throughball"] = F.col_has_qualifier(data_n, qualifier_code=4).astype(int)
    columns = [
        "x",
        "y",
        "pass_angle",
        "pass_length",
        "is_chipped",
        "is_headpass",
        "is_throughball",
    ]
    return (data_n[columns], data_n["outcomeType"].values)


def x_pass_features_v2(data, use_positions_as_features=False):
    data_n = data.copy()

    data_n["pass_angle"] = F.col_get_qualifier_value(
        data_n, display_name="Angle"
    ).astype(float)
    data_n["pass_length"] = distance(
        data_n["x"].values,
        data_n["y"].values,
        data_n["endX"].values,
        data_n["endY"].values,
    )
    data_n["is_free_kick"] = F.col_has_qualifier(data_n, qualifier_code=5).astype(int)
    data_n["is_corner"] = F.col_has_qualifier(data_n, qualifier_code=6).astype(int)
    data_n["is_throw_in"] = F.col_has_qualifier(data_n, qualifier_code=107).astype(int)
    data_n["is_goal_kick"] = F.col_has_qualifier(data_n, qualifier_code=123).astype(int)
    data_n["is_keeper_throw"] = F.col_has_qualifier(data_n, qualifier_code=124).astype(
        int
    )
    data_n["is_chipped"] = F.col_has_qualifier(data_n, qualifier_code=155).astype(int)
    data_n["is_headpass"] = F.col_has_qualifier(data_n, qualifier_code=3).astype(int)
    data_n["is_throughball"] = F.col_has_qualifier(data_n, qualifier_code=4).astype(int)
    data_n["is_long_pass"] = F.col_has_qualifier(data_n, qualifier_code=1).astype(int)
    data_n["is_gk"] = data_n["position"].apply(lambda x: x == "GK").astype(int)
    data_n["is_cross"] = F.col_has_qualifier(data_n, qualifier_code=2).astype(int)
    data_n["is_losing_big"] = (
        data_n["game_state"].apply(lambda x: x == "LosingBig").astype(int)
    )
    data_n["is_winning_big"] = (
        data_n["game_state"].apply(lambda x: x == "WinningBig").astype(int)
    )
    data_n["is_losing_small"] = (
        data_n["game_state"].apply(lambda x: x == "LosingSmall").astype(int)
    )
    data_n["is_winning_small"] = (
        data_n["game_state"].apply(lambda x: x == "WinningSmall").astype(int)
    )
    data_n["is_drawing"] = (
        data_n["game_state"].apply(lambda x: x == "Drawing").astype(int)
    )
    data_n["is_fwd"] = (
        data_n["position"].apply(lambda x: x in ["RF", "LF", "CF"]).astype(int)
    )
    data_n["is_att_mid"] = (
        data_n["position"]
        .apply(lambda x: x in ["RCAM", "RM", "LM", "LCAM", "CAM", "LWF", "RWF", "SS"])
        .astype(int)
    )
    data_n["is_mid"] = (
        data_n["position"]
        .apply(lambda x: x in ["RCM", "LCM", "RCDM", "LCDM", "CDM", "CM"])
        .astype(int)
    )
    data_n["is_cb"] = (
        data_n["position"].apply(lambda x: x in ["RCB", "LCB", "CB"]).astype(int)
    )
    data_n["is_fb"] = (
        data_n["position"].apply(lambda x: x in ["RB", "LB", "RWB", "LWB"]).astype(int)
    )

    columns = [
        "x",
        "y",
        "pass_angle",
        "pass_length",
        "is_chipped",
        "is_headpass",
        "is_throughball",
        "is_gk",
        "is_cross",
        "is_home_team",
        "is_winning_big",
        "is_losing_big",
        "is_winning_small",
        "is_losing_small",
        "is_drawing",
    ]
    if use_positions_as_features:
        columns += ["is_fwd", "is_att_mid", "is_mid", "is_cb", "is_fb"]

    return (data_n[columns], data_n["outcomeType"].values)
