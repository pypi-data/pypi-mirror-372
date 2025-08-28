import pandas as pd
from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def segmented_adverse_impact_ratio(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, air_threshold: float, percent_difference_threshold: float, fdr_threshold: float, segment: pd.Series, label: pd.Series | None = None, sample_weight: pd.Series | None = None, max_for_fishers: int = ..., shift_zeros: bool = True) -> Disparity: ...
