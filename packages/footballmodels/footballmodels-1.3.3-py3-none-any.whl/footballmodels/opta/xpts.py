from dbconnect.connector import Connection
from footballmodels.opta import functions as F
import pandas as pd
import numpy as np
from typing import List


def collapse_possessions(data: pd.DataFrame) -> pd.DataFrame:
    return data.groupby(
        [
            "possession_number",
            "period",
            "team",
            "teamId",
            "competition",
            "season",
            "matchId",
        ]
    ).agg({"xg": lambda xgs: 1 - np.prod(1 - xgs)})


def simulate(data: pd.DataFrame, trials: int, team_list: List[str]) -> pd.DataFrame:
    data = data.reset_index()
    team1 = data.loc[data["team"] == team_list[0]]
    if len(team1) > 0:
        m_1 = np.random.random((len(team1), trials))
        v_1 = (m_1 < team1["xg"].values.reshape((len(team1), 1))).astype(int)
        s_1 = v_1.sum(axis=0)

    else:
        s_1 = np.zeros(trials)

    team2 = data.loc[data["team"] == team_list[1]]
    if len(team2) > 0:
        m_2 = np.random.random((len(team2), trials))
        v_2 = (m_2 < team2["xg"].values.reshape((len(team2), 1))).astype(int)
        s_2 = v_2.sum(axis=0)

    else:
        s_2 = np.zeros(trials)

    t1_xpts = np.mean(np.where(np.sign(s_1 - s_2) + 1 == 2, 3, np.sign(s_1 - s_2) + 1))
    t2_xpts = np.mean(np.where(np.sign(s_2 - s_1) + 1 == 2, 3, np.sign(s_2 - s_1) + 1))
    return_df = pd.DataFrame(
        {
            "competition": [data["competition"].values[0]] * 2,
            "season": [data["season"].values[0]] * 2,
            "matchId": [data["matchId"].values[0]] * 2,
        }
    )
    return_df["team"] = team_list
    return_df["xpts"] = [t1_xpts, t2_xpts]
    return return_df
