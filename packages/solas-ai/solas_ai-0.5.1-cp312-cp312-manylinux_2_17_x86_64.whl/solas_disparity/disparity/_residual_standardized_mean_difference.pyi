import pandas as pd
from ._standardized_mean_difference import standardized_mean_difference as standardized_mean_difference
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, ResidualSMDDenominator as ResidualSMDDenominator
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def residual_standardized_mean_difference(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], prediction: pd.Series, label: pd.Series, residual_smd_threshold: float, lower_score_favorable: bool = True, sample_weight: pd.Series | None = None, residual_smd_denominator: ResidualSMDDenominator | str = ...): ...
