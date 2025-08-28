from pydantic import BaseModel

class Config(BaseModel):
    LICENSE: str | None
    DEBUG_MODE: bool
    DB_ENGINE_URL: str | None
    DB_ALWAYS_REBUILD: bool
    DB_USE_TEST_CONFIG: bool
    DB_ECHO: bool
    APP_HOST: str
    APP_PORT: int
    APP_PATH: str
    OUTPUT_PATH: str
    PICKLE_STORE_PATH: str
    SHOW_CONSOLE_OUTPUT: bool
    SHOW_CONSOLE_DETAIL: bool
    SHOW_PROGRESS: bool
    CAPTURE_DEPENDENCY_LOGGING: bool
    LOG_LEVEL: str
    LOG_FILE: str
    LOG_FILE_RETENTION: str
    AVAILABLE_COLOR_PALLETE: list
    GROUP_COLOR_MAPPING: dict
    H2O_FILE_STORE_PATH: str
    SETTINGS_FILE_ID: str | None
    DEMOGRAPHIC_ESTIMATION_DATA_DIR: str
    SHRINK_STATSMODELS_OBJECTS: bool
    DISABLE_LIVE_EPOCH_SCATTER: bool
    HYPERPARAMETER_TUNING_DELTA: float
    EPSILON: float
