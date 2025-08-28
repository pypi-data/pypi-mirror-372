import pandas as pd
from ._cache import Cache as Cache
from ._zip9_mixin import ZIP9MatchMixin as ZIP9MatchMixin
from _typeshed import Incomplete
from solas_disparity import const as const

class RaceEstimation(ZIP9MatchMixin):
    input_data: Incomplete
    unique_id_column: Incomplete
    last_name_column: Incomplete
    zip9_column: Incomplete
    geoid_column: Incomplete
    latitude_column: Incomplete
    longitude_column: Incomplete
    zip5_column: Incomplete
    census_year: Incomplete
    adult_population_only: Incomplete
    use_surname_defaults: Incomplete
    verbose: Incomplete
    geo_patterns: Incomplete
    report: Incomplete
    def __init__(self, input_data: pd.DataFrame, unique_id_column: str, last_name_column: str, zip9_column: str | None = None, geoid_column: str | None = None, latitude_column: str | None = None, longitude_column: str | None = None, zip5_column: str | None = None, census_year: int = ..., adult_population_only: bool = False, use_surname_defaults: bool = True, verbose: bool = False) -> None: ...
    surname_df: Incomplete
    geo_bisg_df: Incomplete
    def estimate(self): ...
