from abc import ABC, abstractmethod
from typing import List
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import pandas as pd
from footballmodels.definitions.templates import TemplateAttribute
from footballmodels.utils.distance import (
    weighted_cartesian_distance,
    weighted_l1_distance,
)
import numpy as np


class SimilarityAlgorith(ABC):
    MINIMUM_MINUTES = 300

    def __init__(self, data: pd.DataFrame):
        self._data = data

    def _get_searched_player(
        self, data: pd.DataFrame, player: str, squad: str, season: int, comp: str
    ):
        return data[
            (data["player"] == player)
            & (data["squad"] == squad)
            & (data["season"] == season)
            & (data["comp"] == comp)
        ]

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def filter_data(self, data: pd.DataFrame, filter_kwargs: dict):
        for key, value in filter_kwargs.items():
            if isinstance(value, tuple):
                data = data[(data[key] >= value[0]) & (data[key] <= value[1])]
            else:
                data = data[data[key] == value]
        return data

    def find(
        self,
        player: str,
        squad: str,
        season: int,
        comp: str,
        n: int = 10,
        filter_kwargs: dict = None,
    ):
        data = self._data[self._data["minutes"] > self.MINIMUM_MINUTES]

        data = self.transform(data)

        search_data = self._find(data, player, squad, season, comp)
        if filter_kwargs:
            filtered_data = self.filter_data(search_data, filter_kwargs)
            if self._get_searched_player(
                filtered_data, player, squad, season, comp
            ).empty:
                player_data = self._get_searched_player(
                    search_data, player, squad, season, comp
                )
                filtered_data = pd.concat([filtered_data, player_data])
        return filtered_data.sort_values("distance").head(n)

    @abstractmethod
    def _find(
        self, data: pd.DataFrame, player: str, squad: str, season: int, comp: str
    ):
        pass


class TemplateSimilarityAlgorithm(SimilarityAlgorith):
    """
    Finds similar players based on features specified by
    positional tempate
    """

    def __init__(
        self,
        data: pd.DataFrame,
        template: List[TemplateAttribute],
        distance_metric: str = "cartesian",
    ):
        super().__init__(data)
        self._template = template
        if distance_metric == "cartesian":
            self._distance = weighted_cartesian_distance
        elif distance_metric == "l1":
            self._distance = weighted_l1_distance
        else:
            raise ValueError(f"Distance metric {distance_metric} not supported")

    def transform(self, orig_data: pd.DataFrame) -> pd.DataFrame:
        data = pd.DataFrame(
            {
                "player": orig_data["player"],
                "squad": orig_data["squad"],
                "season": orig_data["season"],
                "comp": orig_data["comp"],
                "age": orig_data["age"],
                "gender": orig_data["gender"],
                "minutes": orig_data["minutes"],
            }
        )
        for attr in self._template:
            data[attr.name] = attr.apply(orig_data)
            data[attr.name] = data[attr.name].rank(
                pct=True,
                ascending=attr.ascending_rank,
                method="min",
            )
        data[[attr.name for attr in self._template]] = MinMaxScaler().fit_transform(
            data[[attr.name for attr in self._template]]
        )
        return data

    def _find(
        self,
        data: pd.DataFrame,
        player: str,
        squad: str,
        season: int,
        comp: str,
        n: int = 10,
    ):
        player_data = data[
            (data["player"] == player)
            & (data["squad"] == squad)
            & (data["season"] == season)
            & (data["comp"] == comp)
        ]
        player_data = player_data.drop(
            ["player", "squad", "season", "comp", "age", "gender", "minutes"], axis=1
        )
        distances = self._distance(
            player_data.values,
            data[[attr.name for attr in self._template]].values,
            np.ones(player_data.shape),
        )
        data["distance"] = MinMaxScaler().fit_transform(distances.reshape(-1, 1))
        return data


class WeightedTemplateSimilarityAlgorithm(TemplateSimilarityAlgorithm):
    def _find(
        self,
        data: pd.DataFrame,
        player: str,
        squad: str,
        season: int,
        comp: str,
        n: int = 10,
    ):
        player_data = data[
            (data["player"] == player)
            & (data["squad"] == squad)
            & (data["season"] == season)
            & (data["comp"] == comp)
        ]
        player_data = player_data.drop(
            ["player", "squad", "season", "comp", "age", "gender", "minutes"], axis=1
        )
        distances = self._distance(
            player_data.values,
            data[[attr.name for attr in self._template]].values,
            player_data.values,
        )
        data["distance"] = MinMaxScaler().fit_transform(distances.reshape(-1, 1))
        return data
