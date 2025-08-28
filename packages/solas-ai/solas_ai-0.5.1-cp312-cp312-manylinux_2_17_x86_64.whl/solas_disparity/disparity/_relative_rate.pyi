import pandas as pd
from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, ShortfallMethod as ShortfallMethod

def relative_rate(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, ratio_threshold: float, percent_difference_threshold: float, label: pd.Series | None = None, sample_weight: pd.Series | None = None, max_for_fishers: int = ..., shortfall_method: ShortfallMethod | None = ...) -> Disparity: ...
