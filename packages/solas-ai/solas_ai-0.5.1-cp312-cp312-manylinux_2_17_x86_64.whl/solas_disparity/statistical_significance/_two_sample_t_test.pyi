from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity.types import StatSig as StatSig

def two_sample_t_test(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, sample_weight: Series | None = None) -> StatSig: ...
