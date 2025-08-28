import pandas as pd
from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def adverse_impact_ratio_by_quantile(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, air_threshold: float, percent_difference_threshold: float, quantiles: list[float], label: pd.Series | None = None, sample_weight: pd.Series | None = None, max_for_fishers: int = ..., lower_score_favorable: bool = True, merge_bins: bool = True) -> Disparity: ...
