import pandas as pd
from ._gender_estimation import GenderEstimation as GenderEstimation
from ._minority_estimation import MinorityEstimation as MinorityEstimation
from ._race_estimation import RaceEstimation as RaceEstimation
from solas_disparity import const as const
from solas_disparity.types import DemographicEstimation as DemographicEstimation

def demographic_estimation(input_data: pd.DataFrame, unique_id_column: str, last_name_column: str | None = None, first_name_column: str | None = None, zip9_column: str | None = None, geoid_column: str | None = None, latitude_column: str | None = None, longitude_column: str | None = None, zip5_column: str | None = None, census_year: int | None = None, adult_population_only: bool | None = None, use_surname_defaults: bool | None = None, estimate_race_proportion: bool = True, estimate_gender_proportion: bool = True, verbose: bool = False) -> DemographicEstimation: ...
def minority_estimation(input_data: pd.DataFrame, unique_id_column: str, zip9_column: str, census_year: int = ..., adult_population_only: bool = False, verbose: bool = False) -> DemographicEstimation: ...
