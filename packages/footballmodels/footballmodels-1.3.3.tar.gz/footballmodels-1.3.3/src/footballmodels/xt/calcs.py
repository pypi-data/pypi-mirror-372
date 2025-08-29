import pandas as pd
import numpy as np
from footballmodels.xt import xt_grid
from footballmodels.opta.event_type import EventType


def net_xt(events: pd.DataFrame):
    xt_idx_x = pd.cut(events["x"], bins=np.linspace(0, 100, 13), labels=range(12))
    xt_idx_y = pd.cut(events["y"], bins=np.linspace(0, 100, 9), labels=range(8))
    xt_idx_x_end = pd.cut(
        events["endX"], bins=np.linspace(0, 100, 13), labels=range(12)
    )
    xt_idx_y_end = pd.cut(events["endY"], bins=np.linspace(0, 100, 9), labels=range(8))
    event_types = events["event_type"]
    xt_start = np.array(
        [
            (
                xt_grid[j][i]
                if i < 12 and j < 8 and event_type in [EventType.Pass, EventType.Carry]
                else 0
            )
            for i, j, event_type in zip(xt_idx_x, xt_idx_y, event_types)
        ]
    )

    xt_end = np.array(
        [
            (
                xt_grid[j][i]
                if i < 12 and j < 8 and event_type in [EventType.Pass, EventType.Carry]
                else 0
            )
            for i, j, event_type in zip(xt_idx_x_end, xt_idx_y_end, event_types)
        ]
    )
    xt_pass_net = xt_end - xt_start
    return xt_pass_net
