import pandas as pd
from ._adverse_impact_ratio import adverse_impact_ratio as adverse_impact_ratio
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, ShortfallMethod as ShortfallMethod

def scoring_impact_ratio(group_data: pd.DataFrame, race_ethnicity_groups: list[str], gender_groups: list[str], outcome: pd.Series, ratio_threshold: float, difference_threshold: float, sample_weight: pd.Series | None = None, max_for_fishers: int = ..., shortfall_method: ShortfallMethod | None = ..., drop_small_groups: bool | None = True) -> Disparity: ...
