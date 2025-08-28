from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity

def plot_segmented_adverse_impact_ratio(disparity: Disparity, column: str = ..., segment: str | None = None, separate: bool = False, group: str | None = None) -> Figure | list[Figure]: ...
