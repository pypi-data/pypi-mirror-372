import logging

from pydantic import AnyUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_log_level(log_level: int | str) -> int:
    """Convert the log level to an integer.

    Args:
        log_level: The log level as a string or integer.

    Returns:
        The log level as an integer.
    """
    try:
        log_level = int(log_level)
    except ValueError:
        if isinstance(log_level, str):
            log_level = int(logging.getLevelName(log_level.upper()))
        else:
            log_level = 20
    return log_level


class LoggingSettings(BaseSettings):
    """This class defines the logging settings of the nessy Framework.

    Attributes:
        target_log_analytics: Whether to log to Azure Log Analytics.
        target_unity_catalog_table: Whether to log to the Unity Catalog Table.
        log_analytics_workspace_id: The workspace ID for Azure Log Analytics.
        log_analytics_shared_key: The shared key for Azure Log Analytics.
        uc_workspace_url: The workspace URL for the Unity Catalog Table.
        uc_warehouse_id: The warehouse ID for the Unity Catalog Table.
        uc_catalog_name: The catalog name for the Unity Catalog Table.
        uc_schema_name: The schema name for the Unity Catalog Table.
        log_level_console: The log level for the console logger.
        log_level_tabular: The log level for the tabular logger.
        log_format_console: The format of the console logger.
    """

    model_config = SettingsConfigDict(env_prefix="nessy_")

    target_log_analytics: bool = Field(default=False)
    target_unity_catalog_table: bool = Field(default=False)

    log_analytics_workspace_id: str | None = Field(default=None)
    log_analytics_shared_key: str | None = Field(default=None)
    # log_type is not implement on purpose, because separate loggers will
    # require different schemas, that can't be in the same table

    uc_workspace_url: AnyUrl | None = Field(default=None)
    uc_warehouse_id: str | None = Field(default=None)
    uc_catalog_name: str | None = Field(default=None)
    uc_schema_name: str | None = Field(default=None)
    # table is not implement on purpose, because separate logger will require
    # different schemas, that can't be in the same table

    log_level_console: int = Field(default=logging.INFO)
    log_level_tabular: int = Field(default=logging.INFO)

    log_format_console: str = "%(asctime)s - %(message)s"

    @model_validator(mode="before")
    def _convert_log_levels(cls, settings):
        """Convert the log levels to integers."""
        settings["log_level_console"] = get_log_level(settings.get("log_level_console", logging.INFO))
        settings["log_level_tabular"] = get_log_level(settings.get("log_level_tabular", logging.INFO))
        return settings

    @model_validator(mode="after")
    def _validate_log_analytics_settings(cls, settings):
        if settings.target_log_analytics is True:
            if not settings.log_analytics_workspace_id or not settings.log_analytics_shared_key:
                raise ValueError(
                    "`NESSY_LOG_ANALYTICS_WORKSPACE_ID` and `NESSY_LOG_ANALYTICS_SHARED_KEY` environment variables must be set if `NESSY_LOG_TO_LOG_ANALYTICS_WORKSPACE` is set to true."
                )
        return settings


class NessySettings(BaseSettings):
    """This class defines the settings of the nessy Framework.

    Attributes:
        logging: The logging settings of the nessy Framework.
    """

    model_config = SettingsConfigDict(env_prefix="nessy_")

    logging: LoggingSettings = Field(default_factory=LoggingSettings)
