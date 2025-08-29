import pandas as pd
from footballmodels.opta.functions import col_get_qualifier_value, col_has_qualifier


def is_open_play_pass(data: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean series indicating whether each event in a dataframe is an open play pass

    Args:
        data (pd.DataFrame): The dataframe

    Returns:
        pd.Series: True if the event is an open play pass, False otherwise

    """
    return (
        data["event_type"].apply(
            lambda x: x == 1 if isinstance(x, int) else x.value == 1
        )
        & ~col_has_qualifier(data, qualifier_code=5)
        & ~col_has_qualifier(data, qualifier_code=6)
        & ~col_has_qualifier(data, qualifier_code=107)
    )
