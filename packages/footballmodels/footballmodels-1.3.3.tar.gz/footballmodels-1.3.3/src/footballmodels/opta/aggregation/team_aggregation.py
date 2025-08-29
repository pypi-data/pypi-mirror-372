import pandas as pd
from footballmodels.opta import actions as A
from footballmodels.opta.event_type import EventType

from footballmodels.opta.functions import col_has_qualifier
from footballmodels.opta.actions import (
    in_attacking_box,
    is_shot,
    distance_to_goal,
    is_buildup,
    is_fast_break,
)
import numpy as np
from footballmodels.opta.distance import (
    progressive_distance,
    distance,
    MIDDLE_GOAL_COORDS,
    TOP_GOAL_COORDS,
    BOTTOM_GOAL_COORDS,
)


def eleven_v_eleven(data):
    red_cards = data[
        (data["event_type"] == EventType.Card)
        & col_has_qualifier(data, display_name="Red")
    ]
    # remove all the data that happens after the red card
    for i, row in red_cards.iterrows():
        data = data[
            (data["matchId"] != row["matchId"])
            | (data["match_seconds"] < row["match_seconds"])
        ].copy()
    return data


def calc_match_minutes(data: pd.DataFrame) -> float:
    period_starts = {1: 0, 2: 45, 3: 90, 4: 105}
    agg_data = data.groupby("period").agg({"minute": "max"}).reset_index()
    agg_data.columns = ["period", "max_minute"]
    agg_data["start_minute"] = agg_data["period"].map(period_starts)
    agg_data["end_minute"] = agg_data["max_minute"]
    agg_data["duration"] = agg_data["end_minute"] - agg_data["start_minute"]
    return agg_data["duration"].sum()


def get_team_match_data(data):
    data["attack"] = A.open_play_xg(data)
    data["set_piece_xg"] = A.set_piece_xg(data)
    data["ppda_qualifying_passes"] = A.ppda_qualifying_passes(data)
    data["ppda_qualifying_defensive_actions"] = A.ppda_qualifying_defensive_actions(
        data
    )
    data["box_efficiency"] = A.non_penalty_goal(data) - A.non_penalty_xg(data)
    data["physical_duels"] = A.ground_duels_won(data) + A.aerial_duels_won(data)
    data["touch"] = A.touch(data)
    data["shots"] = A.open_play_shot(data)
    data["counterattack_shots"] = A.counterattack_shot(data)
    data["attacking_touches"] = A.touch(data) & (data["x"] >= 66.6)
    match_length_data = data.groupby(["season", "competition", "matchId"]).apply(
        calc_match_minutes
    )
    match_length_data.name = "minutes"
    for_data = (
        data.groupby(["season", "competition", "matchId", "team", "teamId"])
        .agg(
            {
                "attack": "sum",
                "ppda_qualifying_defensive_actions": "sum",
                "set_piece_xg": "sum",
                "box_efficiency": "sum",
                "physical_duels": "sum",
                "touch": "sum",
                "shots": "sum",
                "counterattack_shots": "sum",
                "attacking_touches": "sum",
            }
        )
        .reset_index()
    )

    against_data = (
        data.groupby(
            [
                "season",
                "competition",
                "matchId",
                "opponent",
            ]
        )
        .agg(
            {
                "attack": "sum",
                "ppda_qualifying_passes": "sum",
                "set_piece_xg": "sum",
                "box_efficiency": "sum",
                "touch": "sum",
                "attacking_touches": "sum",
            }
        )
        .reset_index()
    )

    against_data["defense"] = against_data["attack"]
    against_data = against_data.drop(columns=["attack"])
    merged_data = pd.merge(
        for_data[
            [
                "season",
                "competition",
                "matchId",
                "team",
                "teamId",
                "attack",
                "ppda_qualifying_defensive_actions",
                "set_piece_xg",
                "box_efficiency",
                "physical_duels",
                "touch",
                "shots",
                "counterattack_shots",
                "attacking_touches",
            ]
        ],
        against_data[
            [
                "season",
                "competition",
                "matchId",
                "opponent",
                "defense",
                "ppda_qualifying_passes",
                "set_piece_xg",
                "box_efficiency",
                "touch",
                "attacking_touches",
            ]
        ],
        left_on=["season", "competition", "matchId", "team"],
        right_on=["season", "competition", "matchId", "opponent"],
        how="left",
        suffixes=("_for", "_against"),
    )

    merged_data = merged_data.drop(columns=["opponent"])
    merged_data["set_piece"] = (
        merged_data["set_piece_xg_for"] - merged_data["set_piece_xg_against"]
    )
    merged_data["box_efficiency"] = (
        merged_data["box_efficiency_for"] - merged_data["box_efficiency_against"]
    )
    merged_data = pd.merge(
        merged_data,
        match_length_data.reset_index(),
        on=["season", "competition", "matchId"],
    )
    return merged_data


def circulation(data):
    data = data[data["event_type"] == EventType.Pass].copy()
    data["pass_progressive_distance"] = progressive_distance(data)
    data["pass_total_distance"] = distance(
        data["x"], data["y"], data["endX"], data["endY"]
    )[0]
    grouped_data = data.groupby(["season", "competition", "matchId", "teamId"]).agg(
        {"pass_progressive_distance": "sum", "pass_total_distance": "sum"}
    )
    grouped_data["circulation"] = (
        1
        - grouped_data["pass_progressive_distance"]
        / grouped_data["pass_total_distance"]
    )
    return grouped_data


def possession_operations(data):
    data = data[data["event_type"] != EventType.Carry].copy()

    data["is_valid"] = np.where(
        (data["event_type"] == EventType.Pass)
        & ((col_has_qualifier(data, qualifier_code=6) | data["kickoff"] == True)),
        0,
        1,
    )

    if (
        len(data[(data["event_type"] == EventType.Pass) & (data["outcomeType"] == 1)])
        == 0
    ):
        valid = False
    elif data.iloc[0]["is_valid"] != 1:
        valid = False
    else:
        valid = True
    start_event = data[data["possession_owner"] == data["teamId"]].iloc[0]
    end_event = data[data["possession_owner"] == data["teamId"]].iloc[-1]
    start_distance_to_goal = distance_to_goal(start_event["x"], start_event["y"])
    end_distance_to_goal = distance_to_goal(end_event["x"], end_event["y"])
    buildup_possession = is_buildup(data)
    fast_break = is_fast_break(data)
    return pd.DataFrame(
        {
            "valid": [valid],
            "start_possession_distance": [start_distance_to_goal],
            "end_possession_distance": [end_distance_to_goal],
            "buildup_possession": [buildup_possession],
            "fast_break": [fast_break],
        }
    )


def get_team_aggregation_2(data, possession_data):
    data_no_carry = data[data["event_type"] != EventType.Carry].copy()
    data_no_carry["second_ball_wins"] = A.open_play_second_ball(
        data_no_carry
    ) | A.set_piece_second_ball(data_no_carry)
    data["second_ball_wins"] = pd.merge(
        left=data, right=data_no_carry[["id", "second_ball_wins"]], on="id", how="left"
    )["second_ball_wins"].values
    data["open_play_box_entry"] = A.open_play_box_entry(data)

    normal_data_aggregation = data.groupby(
        ["season", "competition", "matchId", "teamId"]
    ).agg({"second_ball_wins": "sum", "open_play_box_entry": "sum"})
    grouped_data = data.groupby(
        ["season", "competition", "matchId", "possession_number"]
    ).agg({"possession_owner": "first"})
    possession_data = possession_data.copy()
    possession_data["start_possession_distance"] = possession_data[
        "start_possession_distance"
    ] * possession_data["valid"].astype(int)
    possession_data["end_possession_distance"] = possession_data[
        "end_possession_distance"
    ] * possession_data["valid"].astype(int)
    possession_data["pct_gained"] = np.maximum(
        (
            possession_data["start_possession_distance"]
            - possession_data["end_possession_distance"]
        )
        / possession_data["start_possession_distance"],
        0,
    )
    grouped_data = pd.merge(
        grouped_data, possession_data, left_index=True, right_index=True
    )
    grouped_data = grouped_data.groupby(
        ["season", "competition", "matchId", "possession_owner"]
    ).agg(
        {
            "start_possession_distance": "sum",
            "valid": "sum",
            "end_possession_distance": "sum",
            "pct_gained": "sum",
            "buildup_possession": "sum",
            "fast_break": "sum",
        }
    )
    grouped_data["pct_gained"] = grouped_data["pct_gained"] / grouped_data["valid"]
    grouped_data["start_possession_distance"] = (
        grouped_data["start_possession_distance"] / grouped_data["valid"]
    )
    grouped_data["end_possession_distance"] = (
        grouped_data["end_possession_distance"] / grouped_data["valid"]
    )
    grouped_data = (
        grouped_data.reset_index()
        .rename(columns={"valid": "valid_possessions", "possession_owner": "teamId"})
        .set_index(["season", "competition", "matchId", "teamId"])
    )
    grouped_data = pd.merge(
        left=grouped_data, right=circulation(data), left_index=True, right_index=True
    )
    grouped_data = pd.merge(
        left=grouped_data,
        right=normal_data_aggregation,
        left_index=True,
        right_index=True,
    )
    return grouped_data
