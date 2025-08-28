from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def fishers_or_chi_squared(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, sample_weight: Series | None = None, max_for_fishers: int | float = ...) -> StatSig: ...
