from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity

def plot_scoring_impact_ratio(disparity: Disparity, column: str = ..., group_category: str | float | None = None, separate: bool = False) -> Figure | list[Figure]: ...
