from pandas import DataFrame
import pandas as pd
from typing import Optional, List
from collections import Counter


class IncomparableSchemasException(Exception):
    pass


def get_delta(
    history: DataFrame,
    latest: DataFrame,
    column_subset: Optional[List[str]] = None,
) -> DataFrame:
    """
    Returns the rows in latest that are not in history.
    """
    if Counter(history.columns) != Counter(latest.columns):
        raise IncomparableSchemasException(
            "Cannot compare dataframes with different schemas"
        )

    if not column_subset:
        column_subset = list(latest.columns)

    # Get the diff
    latest["key1"] = 1
    history["key2"] = 1
    merged = pd.merge(latest, history, on=column_subset, how="left")
    delta = (
        merged[~(merged.key2 == merged.key1)]
        .drop(["key1", "key2"], axis=1)
        .reset_index(drop=True)
    )

    return delta
