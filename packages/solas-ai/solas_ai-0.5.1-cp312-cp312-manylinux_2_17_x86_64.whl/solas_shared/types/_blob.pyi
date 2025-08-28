import pandas as pd
from ._types_shared import get_new_id as get_new_id
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel
from typing import Any

class BlobDataType(str, Enum):
    ANY = 'any'
    DATAFRAME = 'dataframe'
    SERIES = 'series'

class Blob(SQLModel, table=True):
    id: str
    expires: datetime | None
    data: Any | None
    content_type: str | None
    filename: str | None
    extension: str | None
    def as_dataframe(self) -> pd.DataFrame: ...
    def as_series(self) -> pd.Series: ...

class BlobResponse(SQLModel):
    id: str
    expires: datetime | None
    content_type: str | None
    filename: str | None
    extension: str | None
    uri: str | None
    rows: int | None
    cols: int | None
    column_names: list[str] | None
