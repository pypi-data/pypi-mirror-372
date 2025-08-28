from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity

def plot_false_positive_rate(disparity: Disparity, column: str = ...) -> Figure: ...
