from ._difference_calculation import DifferenceCalculation as DifferenceCalculation
from ._disparity_calculation import DisparityCalculation as DisparityCalculation
from ._ratio_calculation import RatioCalculation as RatioCalculation
from ._residual_smd_denominator import ResidualSMDDenominator as ResidualSMDDenominator
from ._shortfall_method import ShortfallMethod as ShortfallMethod
from ._smd_denominator import SMDDenominator as SMDDenominator
from ._stat_sig import StatSig as StatSig
from ._stat_sig_test import StatSigTest as StatSigTest
from pandas import DataFrame
from pathlib import Path
from solas_disparity import const as const
from solas_disparity.utils import compare_pandas_objects as compare_pandas_objects
from typing import Callable

class Disparity:
    @property
    def plot(self): ...
    @plot.setter
    def plot(self, value) -> None: ...
    disparity_type: DisparityCalculation
    summary_table: DataFrame
    protected_groups: list[str]
    reference_groups: list[str]
    group_categories: list[str]
    statistical_significance: StatSig | None
    smd_threshold: float | None
    residual_smd_threshold: float | None
    smd_denominator: str | None
    residual_smd_denominator: str | None
    lower_score_favorable: bool | None
    odds_ratio_threshold: float | None
    air_threshold: float | None
    percent_difference_threshold: float | None
    max_for_fishers: int | None
    shortfall_method: ShortfallMethod | None
    fdr_threshold: float | None
    metric: Callable[..., int | float]
    difference_calculation: DifferenceCalculation | None
    difference_threshold: float | None
    ratio_calculation: RatioCalculation | None
    ratio_threshold: float | None
    statistical_significance_test: StatSigTest | None
    p_value_threshold: float
    shift_zeros: bool
    drop_small_groups: bool
    small_group_table: DataFrame
    unknown_table: DataFrame
    @property
    def affected_groups(self) -> list[str]: ...
    @property
    def affected_reference(self) -> list[str]: ...
    @property
    def affected_categories(self) -> list[str] | None: ...
    @property
    def report(self) -> tuple[DataFrame, DataFrame, DataFrame]: ...
    def to_excel(self, file_path: str | Path): ...
    def show(self) -> None: ...
    def __rich__(self) -> None: ...
    def __init__(self, disparity_type, summary_table, protected_groups, reference_groups, group_categories, statistical_significance, smd_threshold, residual_smd_threshold, smd_denominator, residual_smd_denominator, lower_score_favorable, odds_ratio_threshold, air_threshold, percent_difference_threshold, max_for_fishers, shortfall_method, fdr_threshold, metric, difference_calculation, difference_threshold, ratio_calculation, ratio_threshold, statistical_significance_test, p_value_threshold, shift_zeros, drop_small_groups, small_group_table, unknown_table) -> None: ...
    def __lt__(self, other): ...
    def __le__(self, other): ...
    def __gt__(self, other): ...
    def __ge__(self, other): ...
