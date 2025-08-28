import pandas as pd
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def odds_ratio(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, odds_ratio_threshold: float, percent_difference_threshold: float, lower_score_favorable: bool = False, label: pd.Series | None = None, sample_weight: pd.Series | None = None, max_for_fishers: int = ...) -> Disparity: ...
