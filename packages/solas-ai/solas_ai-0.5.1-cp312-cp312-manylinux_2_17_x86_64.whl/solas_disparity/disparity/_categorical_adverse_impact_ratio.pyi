from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import Any

def categorical_adverse_impact_ratio(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, air_threshold: float, percent_difference_threshold: float, category_order: list[Any], label: Series | None = None, sample_weight: Series | None = None, max_for_fishers: int = ...) -> Disparity: ...
