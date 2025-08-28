import pandas as pd
from ._cache import Cache as Cache
from _typeshed import Incomplete
from solas_disparity import const as const

class GenderEstimation:
    data: Incomplete
    unique_id_column: Incomplete
    first_name_column: Incomplete
    verbose: Incomplete
    def __init__(self, input_data: pd.DataFrame, unique_id_column: str, first_name_column: str, verbose: bool = False) -> None: ...
    def estimate(self) -> tuple[pd.DataFrame, pd.DataFrame]: ...
