from plotly.graph_objects import Figure as Figure
from solas_disparity import const as const
from solas_disparity.types import Disparity as Disparity

def plot_wasserstein(disparity: Disparity, column: str = ...) -> Figure: ...
