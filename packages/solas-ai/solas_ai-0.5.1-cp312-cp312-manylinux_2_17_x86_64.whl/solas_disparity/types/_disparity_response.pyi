from ._disparity import Disparity as Disparity
from ._disparity_calculation import DisparityCalculation as DisparityCalculation
from ._shortfall_method import ShortfallMethod as ShortfallMethod
from ._smd_denominator import SMDDenominator as SMDDenominator
from sqlmodel import SQLModel

class DisparityResponse(SQLModel):
    disparity_type: DisparityCalculation
    summary_table_json: str
    summary_table_json_flat: str
    protected_groups: list[str]
    reference_groups: list[str]
    group_categories: list[str]
    outcome: str | None
    air_threshold: float | None
    percent_difference_threshold: float | None
    label: str | None
    sample_weight: str | None
    max_for_fishers: int | None
    shortfall_method: ShortfallMethod | None
    smd_threshold: float | None
    lower_score_favorable: bool | None
    smd_denominator: SMDDenominator | None
    plot_json: str | None
    @staticmethod
    def from_disparity(disparity: Disparity, *args, **kwargs) -> DisparityResponse: ...
