import pandas as pd
from ._custom_disparity_metric import custom_disparity_metric as custom_disparity_metric
from solas_disparity.types import DifferenceCalculation as DifferenceCalculation, Disparity as Disparity, DisparityCalculation as DisparityCalculation, RatioCalculation as RatioCalculation

def true_negative_rate(group_data: pd.DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: pd.Series, label: pd.Series, ratio_threshold: float, difference_threshold: float, sample_weight: pd.Series | None = None) -> Disparity: ...
