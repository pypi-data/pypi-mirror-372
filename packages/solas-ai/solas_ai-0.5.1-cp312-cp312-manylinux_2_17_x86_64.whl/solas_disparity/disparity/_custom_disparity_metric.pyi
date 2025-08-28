from pandas import DataFrame, Series
from solas_disparity import const as const
from solas_disparity.statistical_significance import fishers_or_chi_squared as fishers_or_chi_squared
from solas_disparity.types import DifferenceCalculation as DifferenceCalculation, Disparity as Disparity, DisparityCalculation as DisparityCalculation, RatioCalculation as RatioCalculation, StatSig as StatSig, StatSigTest as StatSigTest
from solas_disparity.utils import pgrg_ordered as pgrg_ordered
from typing import Callable

def custom_disparity_metric(group_data: DataFrame, protected_groups: list[str], reference_groups: list[str], group_categories: list[str], outcome: Series, metric: Callable[..., int | float], label: Series | None = None, sample_weight: Series | None = None, difference_calculation: DifferenceCalculation | None = ..., difference_threshold: Callable[[int | float], bool] | None = ..., ratio_calculation: RatioCalculation | None = ..., ratio_threshold: Callable[[int | float], bool] | None = None) -> Disparity: ...
def resample(data: DataFrame | Series, resamples: int = ..., sample: float | int = ..., seed: int | None = None, replace: bool = True) -> DataFrame: ...
