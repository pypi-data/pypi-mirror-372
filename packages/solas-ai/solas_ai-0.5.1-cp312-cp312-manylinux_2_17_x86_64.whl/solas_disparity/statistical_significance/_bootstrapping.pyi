from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity import const as const
from solas_disparity.types import StatSig as StatSig

def bootstrapping(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, sample_weight: Series | None = None, resamples: int = ..., sample: float | int = ..., seed: int | None = None, replace: bool = False) -> StatSig: ...
