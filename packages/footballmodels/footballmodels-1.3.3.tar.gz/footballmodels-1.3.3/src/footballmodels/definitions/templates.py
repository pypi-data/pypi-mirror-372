from typing import Callable
import dataclasses
import enum
import pandas as pd
from footballmodels.utils.possession_adjustment import adj_possession_factors


def safe_divide(numer: pd.Series, denom: pd.Series, default: float = 0.0) -> pd.Series:
    """Element-wise safe division returning default where denominator is 0/NA.

    Ensures float output, aligns indices, and guards against inf.
    """
    numer, denom = numer.align(denom, fill_value=pd.NA)
    result = pd.Series(default, index=numer.index, dtype="float64")
    mask = denom.notna() & (denom != 0)
    if mask.any():
        result.loc[mask] = numer.loc[mask] / denom.loc[mask]
    # Clean any leftover inf values
    if result.isin([float("inf"), float("-inf")]).any():
        result.replace([float("inf"), float("-inf")], default, inplace=True)
    return result

class PossessionAdjustment(enum.IntEnum):
    NONE = 0
    OUT_OF_POSS = 1
    IN_POSS = 2


@dataclasses.dataclass
class TemplateAttribute:
    name: str
    calculation: Callable[[pd.DataFrame], pd.Series]
    ascending_rank: bool
    columns_used: list[str] = dataclasses.field(default_factory=list)
    possession_adjust: PossessionAdjustment = PossessionAdjustment.NONE
    sig_figs: int = 1
    per_90: bool = True

    def apply(self, df: pd.DataFrame):
        df = df.copy()
        if self.per_90:
            df[self.name] = safe_divide(self.calculation(df), df["minutes"]) * 90
        else:
            df[self.name] = self.calculation(df)
        df[self.name] = df[self.name].round(self.sig_figs)
        if self.possession_adjust == PossessionAdjustment.OUT_OF_POSS:
            df[self.name] = df[self.name] * df["out_of_possession_factor"]
        elif self.possession_adjust == PossessionAdjustment.IN_POSS:
            df[self.name] = df[self.name] * df["in_possession_factor"]

        return df[self.name]


ASSISTS = TemplateAttribute(
    "Assists",
    lambda df: df["assists"],
    True,
    columns_used=["assists"],
    sig_figs=2,
)
BLOCKS_PADJ = TemplateAttribute(
    "PAdj Blocks",
    lambda df: df["blocks"],
    True,
    columns_used=["blocks"],
    possession_adjust=PossessionAdjustment.OUT_OF_POSS,
)
CARRIES_INTO_FINAL_THIRD = TemplateAttribute(
    name="Carries Into Final Third",
    calculation=lambda df: df["carries_into_final_3rd"],
    ascending_rank=True,
    columns_used=["carries_into_final_3rd"],
    sig_figs=2,
)
CARRIES_INTO_PENALTY_BOX = TemplateAttribute(
    name="Carries Into Penalty Box",
    calculation=lambda df: df["carries_into_penalty_area"],
    ascending_rank=True,
    columns_used=["carries_into_penalty_area"],
    sig_figs=2,
)
CLEARANCES_PADJ = TemplateAttribute(
    "PAdj Clearances",
    lambda df: df["clearances"],
    True,
    columns_used=["clearances"],
    possession_adjust=PossessionAdjustment.OUT_OF_POSS,
)
DELIVERIES_INTO_PEN_AREA = TemplateAttribute(
    name="Deliveries Into Penalty Area",
    calculation=lambda df: df["crosses_into_penalty_area"]
    + df["passes_into_penalty_area"],
    ascending_rank=True,
    columns_used=["crosses_into_penalty_area", "passes_into_penalty_area"],
    sig_figs=2,
)

CROSSES_PCT = TemplateAttribute(
    name="Crosses %",
    calculation=lambda df: 100
    * safe_divide(df["crosses_into_penalty_area"], df["crosses"]),
    ascending_rank=True,
    columns_used=["crosses_into_penalty_area", "crosses"],
    per_90=False,
)
DISPOSSESSED = TemplateAttribute(
    "Dispossessed",
    lambda df: df["dispossessed"],
    False,
    columns_used=["dispossessed"],
)
FOULS = TemplateAttribute(
    "Fouls", lambda df: df["fouls"], False, columns_used=["fouls"]
)
HEADERS_WON = TemplateAttribute(
    "Headers Won",
    lambda df: df["aerials_won"],
    True,
    columns_used=["aerials_won"],
)
HEADERS_WON_PCT = TemplateAttribute(
    "Headers Won %",
    lambda df: 100
    * safe_divide(df["aerials_won"], (df["aerials_won"] + df["aerials_lost"])),
    True,
    columns_used=["aerials_won", "aerials_lost"],
    per_90=False,
)
INTERCEPTIONS_PADJ = TemplateAttribute(
    "PAdj Interceptions",
    lambda df: df["interceptions"],
    True,
    columns_used=["interceptions"],
    possession_adjust=PossessionAdjustment.OUT_OF_POSS,
)
INTS_TACKLES = TemplateAttribute(
    "Int+Tackles",
    lambda df: df["interceptions"] + df["tackles"],
    True,
    columns_used=["interceptions", "tackles"],
)
KEY_PASSES = TemplateAttribute(
    name="Key Passes",
    calculation=lambda df: df["assisted_shots"],
    ascending_rank=True,
    columns_used=["assisted_shots"],
)
NON_PENALTY_GOALS = TemplateAttribute(
    "Non-Penalty Goals",
    lambda df: df["goals"] - df["pens_made"],
    True,
    columns_used=["goals", "pens_made"],
    sig_figs=2,
)

NPXG = TemplateAttribute(
    "NPxG", lambda df: df["npxg"], True, columns_used=["npxg"], sig_figs=2
)

NPXG_PER_SHOT = TemplateAttribute(
    "NPxG/Shot",
    lambda df: safe_divide(df["npxg"], df["shots_total"]),
    True,
    columns_used=["npxg", "shots_total"],
    sig_figs=2,
)

PCT_DRIBBLERS_TACKLED = TemplateAttribute(
    "Pct of Dribblers Tackled",
    lambda df: 100
    * safe_divide(df["tackles_vs_dribbles_won"], df["tackles_vs_dribbles"]),
    True,
    columns_used=["tackles_vs_dribbles_won", "tackles_vs_dribbles"],
    per_90=False,
)

PASSING_PCT = TemplateAttribute(
    name="Passing %",
    calculation=lambda df: 100
    * safe_divide(df["passes_completed"], df["passes"]),
    ascending_rank=True,
    columns_used=["passes_completed", "passes"],
    per_90=False,
)
PASSES_INTO_PEN_AREA = TemplateAttribute(
    name="Passes Into Penalty Area",
    calculation=lambda df: df["passes_into_penalty_area"],
    ascending_rank=True,
    columns_used=["passes_into_penalty_area"],
    sig_figs=2,
)
PASSES_INTO_FINAL_THIRD = TemplateAttribute(
    name="Passes Into Final Third",
    calculation=lambda df: df["passes_into_final_third"],
    ascending_rank=True,
    columns_used=["passes_into_final_third"],
    sig_figs=2,
)

PASSES_PROGRESSIVE = TemplateAttribute(
    "Progressive Passes",
    lambda df: df["progressive_passes"],
    True,
    columns_used=["progressive_passes"],
)
PASSES_PROGRESSIVE_PCT = TemplateAttribute(
    "Progressive Passes %",
    lambda df: 100 * safe_divide(df["progressive_passes"], df["passes"]),
    True,
    columns_used=["progressive_passes", "passes"],
    per_90=False,
)
SCORING_CONTRIBUTIONS = TemplateAttribute(
    name="Scoring Contributions",
    calculation=lambda df: (df["goals"] - df["pens_made"] + df["assists"]),
    ascending_rank=True,
    columns_used=["goals", "assists", "pens_made"],
    sig_figs=2,
)
SHOOTING_PCT = TemplateAttribute(
    "Shooting %",
    lambda df: 100
    * safe_divide((df["goals"] - df["pens_made"]), df["shots_total"]),
    True,
    columns_used=["goals", "pens_made", "shots_total"],
    per_90=False,
)
SHOTS = TemplateAttribute(
    "Shots", lambda df: df["shots_total"], True, columns_used=["shots_total"]
)

SHOTS_CREATED_OPEN_PLAY = TemplateAttribute(
    "Open Play Shots Created",
    lambda df: df["sca"] - df["sca_passes_dead"],
    True,
    columns_used=["sca", "sca_passes_dead"],
)
SWITCHES = TemplateAttribute(
    "Switches",
    lambda df: df["passes_switches"],
    True,
    columns_used=["passes_switches"],
    sig_figs=2,
)

SUCCESSFUL_DRIBBLES = TemplateAttribute(
    "Successful Dribbles",
    lambda df: df["dribbles_completed"],
    True,
    columns_used=["dribbles_completed"],
)
TACKLES_PADJ = TemplateAttribute(
    "PAdj Tackles",
    lambda df: df["tackles"],
    True,
    columns_used=["tackles"],
    possession_adjust=PossessionAdjustment.OUT_OF_POSS,
)
THROUGHBALLS = TemplateAttribute(
    name="Throughballs",
    calculation=lambda df: df["through_balls"],
    ascending_rank=True,
    columns_used=["through_balls"],
    sig_figs=2,
)

TOUCHES_IN_MID_3RD = TemplateAttribute(
    "Touches in Mid 3rd",
    lambda df: df["touches_mid_3rd"],
    True,
    columns_used=["touches_mid_3rd"],
    sig_figs=2,
)

TURNOVERS = TemplateAttribute(
    name="Turnovers",
    calculation=lambda df: df["miscontrols"]
    + df["dispossessed"]
    + df["passes"]
    - df["passes_completed"]
    - (df["crosses"] - df["crosses_into_penalty_area"]),
    ascending_rank=False,
    columns_used=[
        "miscontrols",
        "dispossessed",
        "passes",
        "passes_completed",
        "crosses",
        "crosses_into_penalty_area",
    ],
)

XA = TemplateAttribute(
    "xA", lambda df: df["xag"], True, columns_used=["xag"], sig_figs=2
)

PROGRESSIVE_PASSES_RECEIVED = TemplateAttribute(
    "Progressive Passes Received",
    lambda df: df["progressive_passes_received"],
    True,
    columns_used=["progressive_passes_received"],
)

FOULS_WON = TemplateAttribute(
    "Fouls Won",
    lambda df: df["fouled"],
    True,
    columns_used=["fouled"],
)

TOUCHES_IN_PEN_AREA = TemplateAttribute(
    "Touches in Penalty Area",
    lambda df: df["touches_att_pen_area"],
    True,
    columns_used=["touches_att_pen_area"],
)

HEADED_SHOTS = TemplateAttribute(
    "Headed Shots",
    lambda df: df["shots_head"],
    True,
    columns_used=["shots_head"],
)
CARRY_PROGRESSIVE_DISTANCE = TemplateAttribute(
    "Progressive Carry Distance",
    lambda df: df["carry_progressive_distance"],
    True,
    columns_used=["carry_progressive_distance"],
)

SELF_CREATED_SHOT_PCT = TemplateAttribute(
    "Self-Created Shot %",
    lambda df: 100
    * safe_divide(df["self_created_shots"], df["shots_total"]),
    True,
    columns_used=["shots_total"],
    per_90=False,
)

OPEN_PLAY_SHOTS_FOR_OTHERS = TemplateAttribute(
    "Open Play Shots Created\nfor Others",
    lambda df: df["open_play_sca_for_others"],
    True,
    columns_used=[],
)


MFTemplate = [
    PASSING_PCT,
    KEY_PASSES,
    THROUGHBALLS,
    SCORING_CONTRIBUTIONS,
    SUCCESSFUL_DRIBBLES,
    CARRY_PROGRESSIVE_DISTANCE,
    TURNOVERS,
    FOULS,
    HEADERS_WON_PCT,
    PCT_DRIBBLERS_TACKLED,
    TACKLES_PADJ,
    INTERCEPTIONS_PADJ,
    PASSES_PROGRESSIVE,
]

CBTemplate = [
    PASSING_PCT,
    PCT_DRIBBLERS_TACKLED,
    TACKLES_PADJ,
    INTERCEPTIONS_PADJ,
    BLOCKS_PADJ,
    CLEARANCES_PADJ,
    FOULS,
    HEADERS_WON,
    HEADERS_WON_PCT,
    PASSES_PROGRESSIVE,
    PASSES_PROGRESSIVE_PCT,
]
FBTemplate = [
    PASSING_PCT,
    TACKLES_PADJ,
    INTERCEPTIONS_PADJ,
    PCT_DRIBBLERS_TACKLED,
    KEY_PASSES,
    DELIVERIES_INTO_PEN_AREA,
    CROSSES_PCT,
    OPEN_PLAY_SHOTS_FOR_OTHERS,
    SUCCESSFUL_DRIBBLES,
    CARRY_PROGRESSIVE_DISTANCE,
    DISPOSSESSED,
    SCORING_CONTRIBUTIONS,
    FOULS,
]
AttackerTemplate = [
    NON_PENALTY_GOALS,
    SHOTS,
    SHOOTING_PCT,
    PASSING_PCT,
    ASSISTS,
    XA,
    OPEN_PLAY_SHOTS_FOR_OTHERS,
    INTS_TACKLES,
    TURNOVERS,
    SUCCESSFUL_DRIBBLES,
    CARRIES_INTO_PENALTY_BOX,
    SELF_CREATED_SHOT_PCT,
    NPXG,
    NPXG_PER_SHOT,
]

TargetmanTemplate = [
    NON_PENALTY_GOALS,
    NPXG,
    HEADERS_WON,
    HEADERS_WON_PCT,
    HEADED_SHOTS,
    PROGRESSIVE_PASSES_RECEIVED,
    PASSES_PROGRESSIVE,
    PASSING_PCT,
    FOULS_WON,
    TOUCHES_IN_PEN_AREA,
    OPEN_PLAY_SHOTS_FOR_OTHERS,
    NPXG_PER_SHOT,
]

BuildUpIndexTemplate = [
    TURNOVERS,
    CARRY_PROGRESSIVE_DISTANCE,
    PASSES_PROGRESSIVE,
    PASSES_INTO_FINAL_THIRD,
    CARRIES_INTO_FINAL_THIRD,
    TOUCHES_IN_MID_3RD,
    SWITCHES,
    THROUGHBALLS,
]

GoalkeeperTemplate = [
    TemplateAttribute(
        "Goals Conceded",
        lambda df: df["goals_conceded"],
        False,
        columns_used=["goals_conceded"],
        sig_figs=2,
    ),
    TemplateAttribute(
        "Save %",
    lambda df: 100
    * safe_divide(df["saves"], df["shots_on_target_against"]),
        True,
        columns_used=["shots_on_target_against", "saves"],
        per_90=False,
    ),
    TemplateAttribute("Saves", lambda df: df["saves"], True, columns_used=["saves"]),
    TemplateAttribute(
        "Shot Stopping Value Added",
        lambda df: df["psxg_gk"] - df["goals_conceded"],
        True,
        columns_used=["psxg_gk", "goals_conceded"],
        sig_figs=2,
    ),
    TemplateAttribute(
        "SSVA per 100 Shots",
        lambda df: 100
        * safe_divide(
            (df["psxg_gk"] - df["goals_conceded"]), df["shots_on_target_against"]
        ),
        True,
        columns_used=["psxg_gk", "goals_conceded", "shots_on_target_against"],
        per_90=False,
        sig_figs=2,
    ),
    TemplateAttribute(
        "Crosses Collected",
        lambda df: df["crosses_stopped_gk"],
        True,
        columns_used=["crosses_stopped_gk"],
    ),
    TemplateAttribute(
        "Sweeper Actions",
        lambda df: df["sweeper_actions"],
        True,
        columns_used=["sweeper_actions"],
    ),
    TemplateAttribute(
        "Sweeper Action Distance",
        lambda df: df["sweeper_action_avg_distance"],
        True,
        columns_used=["sweeper_action_avg_distance"],
    ),
    TemplateAttribute(
        "Thrown Passes",
        lambda df: df["passes_thrown"],
        True,
        columns_used=["passes_thrown"],
    ),
    TemplateAttribute(
        "Long Passes",
        lambda df: df["passes_long"],
        True,
        columns_used=["passes_long"],
    ),
    TemplateAttribute(
        "Long Pass % Completed",
    lambda df: 100
    * safe_divide(df["passes_completed_long"], df["passes_long"]),
        True,
        columns_used=["passes_completed_long", "passes_long"],
        per_90=False,
    ),
    TemplateAttribute(
        "Mistakes In Possession",
        lambda df: (df["passes_short"] + df["passes_medium"])
        - (df["passes_completed_short"] + df["passes_completed_medium"])
        + df["miscontrols"]
        + df["dispossessed"],
        False,
        columns_used=[
            "passes_completed_short",
            "passes_completed_medium",
            "passes_short",
            "passes_medium",
            "miscontrols",
            "dispossessed",
        ],
        sig_figs=2,
    ),
]

TeamTemplate = [
    TemplateAttribute(
        "Open Play NPxG/Shot",
        lambda df: safe_divide(df["live_xg_team"], df["shots_total_team"]),
        True,
        columns_used=[],
        sig_figs=3,
    ),
    TemplateAttribute(
        "Open Play NPxG",
        lambda df: safe_divide(df["live_xg_team"], df["matches"]),
        True,
        columns_used=[],
        sig_figs=2,
    ),
    TemplateAttribute(
        "Open Play NPxGA",
        lambda df: safe_divide(df["live_xg_opp"], df["matches"]),
        False,
        columns_used=[],
        sig_figs=2,
    ),
    TemplateAttribute(
        "Set Piece NPxGD",
        lambda df: safe_divide(
            (df["setpiece_xg_team"] - df["setpiece_xg_opp"]), df["matches"]
        ),
        True,
        columns_used=[],
        sig_figs=2,
    ),
    TemplateAttribute(
        "Big Chance Created",
        lambda df: safe_divide(df["big_chance_team"], df["matches"]),
        True,
        columns_used=[],
    ),
    TemplateAttribute(
        "Shots",
        lambda df: safe_divide(df["shots_total" + "_team"], df["matches"]),
        True,
        columns_used=["shots_total"],
    ),
    TemplateAttribute(
        "Shots Conceded",
        lambda df: safe_divide(df["shots_total" + "_opp"], df["matches"]),
        False,
        columns_used=["shots_total"],
    ),
    TemplateAttribute(
        "Cross % Box Entries",
        lambda df: 100
        * safe_divide(
            df["crosses_into_penalty_area" + "_team"],
            df["crosses_into_penalty_area" + "_team"]
            + df["passes_into_penalty_area" + "_team"]
            + df["carries_into_penalty_area" + "_team"],
        ),
        True,
        columns_used=[
            "crosses_into_penalty_area",
            "passes_into_penalty_area",
            "carries_into_penalty_area",
        ],
    ),
    TemplateAttribute(
        "Long Ball %",
        lambda df: 100
        * safe_divide(df["passes_long" + "_team"], df["passes" + "_team"]),
        True,
        columns_used=["passes_long", "passes"],
    ),
    TemplateAttribute(
        "Possession %",
        lambda df: 100
        * safe_divide(
            df["touches" + "_team"],
            (df["touches" + "_opp"] + df["touches" + "_team"]),
        ),
        True,
        columns_used=["touches"],
    ),
    TemplateAttribute(
        "PAdj Final 3rd Tackles",
        lambda df: safe_divide(
            safe_divide(df["tackles_att_3rd" + "_team"], df["matches"]),
            safe_divide(
                df["touches" + "_opp"],
                (df["touches" + "_opp"] + df["touches" + "_team"]),
            ),
        )
        * 0.5,
        True,
        columns_used=["tackles_att_3rd", "touches"],
    ),
    TemplateAttribute(
        "PPDA",
        lambda df: safe_divide(
            df["passes_opp"],
            (df["tackles_team"] + df["interceptions_team"] + df["fouls_team"]),
        ),
        False,
        columns_used=["passes", "tackles", "interceptions", "fouls"],
    ),
    TemplateAttribute(
        "PAdj Fouls Committed",
        lambda df: safe_divide(
            safe_divide(df["fouls" + "_team"], df["matches"]),
            safe_divide(
                df["touches" + "_opp"],
                (df["touches" + "_opp"] + df["touches" + "_team"]),
            ),
        )
        * 0.5,
        False,
        columns_used=["fouls", "touches"],
    ),
    TemplateAttribute(
        "PAdj Dribbles",
        lambda df: safe_divide(
            safe_divide(df["dribbles" + "_team"], df["matches"]),
            safe_divide(
                df["touches" + "_team"],
                (df["touches" + "_opp"] + df["touches" + "_team"]),
            ),
        )
        * 0.5,
        True,
        columns_used=["dribbles", "touches"],
    ),
    TemplateAttribute(
        "PAdj Offsides",
        lambda df: safe_divide(
            safe_divide(df["offsides" + "_team"], df["matches"]),
            safe_divide(
                df["touches" + "_team"],
                (df["touches" + "_opp"] + df["touches" + "_team"]),
            ),
        )
        * 0.5,
        False,
        columns_used=["offsides", "touches"],
    ),
]
