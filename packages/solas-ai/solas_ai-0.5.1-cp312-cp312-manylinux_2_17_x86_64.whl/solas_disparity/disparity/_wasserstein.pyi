import pandas as pd
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def wasserstein(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, label: pd.Series | None = None, sample_weight: pd.Series | None = None, lower_score_favorable: bool = True) -> Disparity: ...
