import pandas as pd
import numpy as np
from typing import Dict, Any


def col_get_qualifier_value(
    dataframe: pd.DataFrame, display_name: str = "", qualifier_code: int = -1
) -> pd.Series:
    """
    Get a value of a specific qualifier from an opta dataframe.
    Dataframe must contain a column called 'qualifiers' which is a list of dict of form
    {
        "type": {"value": int, "displayName": str},
        "value": int
    }

    Args:
        dataframe (pd.DataFrame): Dataframe containing a column called 'qualifiers'
        display_name (str, optional): The display name of the qualifier. Defaults to "".
        qualifier_code (int, optional): The qualifier code. Defaults to -1.

    Returns:
        pd.Series: A series of the qualifier values
    """

    def _one(qs, display_name, qualifier_code):
        if display_name:
            try:
                q = next(d for d in qs if d["type"]["displayName"] == display_name)  # type: ignore

            except StopIteration:
                return np.nan

        else:
            try:
                q = next(d for d in qs if d["type"]["value"] == qualifier_code)  # type: ignore

            except StopIteration:
                return np.nan
        return q["value"] if "value" in q else np.nan

    return dataframe["qualifiers"].apply(
        lambda x: _one(x, display_name, qualifier_code)
    )


def has_qualifier(
    qs: Dict[str, Any], display_name: str = "", qualifier_code: int = -1
) -> bool:
    """
    Checks if a given qualifier is present in a dict of qualifiers

    Args:
        qs (Dict[str, Any]): The qualifiers dict
        display_name (str): The display name of the qualifier
        qualifier_code (int): The code of the qualifier

    Returns:
        bool: True if the qualifier is present, False otherwise

    """

    if display_name:
        try:
            next(d for d in qs if d["type"]["displayName"] == display_name)  # type: ignore
            return True
        except StopIteration:
            return False

    else:
        try:
            next(d for d in qs if d["type"]["value"] == qualifier_code)  # type: ignore

            return True
        except StopIteration:
            return False


def col_has_qualifier(
    df: pd.DataFrame, display_name: str = "", qualifier_code: int = -1
) -> pd.Series:
    """
    Checks if a given qualifier is present in each element of a  column of a dataframe

    Args:
        df (pd.DataFrame): The dataframe
        display_name (str): The display name of the qualifier
        qualifier_code (int): The code of the qualifier

    Returns:
        pd.Series: True if the qualifier is present, False otherwise

    """
    return df["qualifiers"].apply(
        lambda x: has_qualifier(x, display_name, qualifier_code)
    )
