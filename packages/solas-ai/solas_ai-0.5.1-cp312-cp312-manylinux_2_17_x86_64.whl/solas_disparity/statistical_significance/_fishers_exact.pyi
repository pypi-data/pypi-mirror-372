from ._fishers_or_chi_squared import fishers_or_chi_squared as fishers_or_chi_squared
from pandas import DataFrame as DataFrame, Series as Series
from solas_disparity.types import StatSig as StatSig, StatSigTest as StatSigTest

def fishers_exact(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, sample_weight: Series | None = None) -> StatSig: ...
