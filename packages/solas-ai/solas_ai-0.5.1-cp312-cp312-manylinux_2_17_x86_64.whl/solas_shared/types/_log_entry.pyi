from ._log_level import LogLevel as LogLevel
from ._solas_type import SolasType as SolasType
from _typeshed import Incomplete
from datetime import datetime
from solas_shared import db as db

class LogEntry(SolasType):
    MIME_MARKDOWN: str
    __table__: Incomplete
    datetime: datetime
    text: str
    log_level: LogLevel
    solas_id: str | None
    for_display: bool
    group: str | None
    mimetype: str
    def to_dict(self) -> dict: ...
    def __init__(self, id, created, updated, user__, node__, version__, datetime, text, log_level, solas_id, for_display, group, mimetype) -> None: ...
    def __lt__(self, other): ...
    def __le__(self, other): ...
    def __gt__(self, other): ...
    def __ge__(self, other): ...
