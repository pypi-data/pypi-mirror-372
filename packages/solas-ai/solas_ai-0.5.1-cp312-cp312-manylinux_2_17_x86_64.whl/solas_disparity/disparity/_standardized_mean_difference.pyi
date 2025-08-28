import pandas as pd
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity, DisparityCalculation as DisparityCalculation, SMDDenominator as SMDDenominator, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered

def standardized_mean_difference(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, smd_threshold: float, lower_score_favorable: bool = True, label: pd.Series | None = None, sample_weight: pd.Series | None = None, smd_denominator: SMDDenominator = ...) -> Disparity: ...
