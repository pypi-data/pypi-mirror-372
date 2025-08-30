import logging
import logging.handlers
from typing import cast

from cloe_logging import LoggerFactory

from ..settings import LoggingSettings, NessySettings

factory = LoggerFactory()

DEFAULT_COLUMN_SPLIT_CHAR = "|"
DEFAULT_KEY_VALUE_SPLIT_CHAR = ":"


class LoggerMixin:
    """LoggingMixin class to add logging functionality to classes."""

    def get_console_logger(
        self,
        level: int | None = None,
        log_format: str | None = None,
    ) -> logging.Logger:
        """Adds a console logger to the class.

        Args:
            level: The logging level for the console logger.
            log_format: The format for the console logger.

        Returns:
            The logger with the console handler.
        """
        logging_settings: LoggingSettings = NessySettings().logging
        logger = LoggerFactory.get_logger(
            handler_types=["console"],
            logger_name=f"Console:{self.__class__.__name__}",
            logging_level=level if level is not None else logging_settings.log_level_console,
            log_format=log_format if log_format is not None else logging_settings.log_format_console,
        )
        return cast(logging.Logger, logger)

    def get_tabular_logger(
        self,
        logger_name: str | None = None,
        handlers: list[str] | None = None,
        level: int | None = None,
        add_log_analytics_logger: bool | None = None,
        add_unity_catalog_logger: bool | None = None,
        # LAW
        log_type: str | None = None,
        workspace_id: str | None = None,
        shared_key: str | None = None,
        # UC
        uc_workspace_url: str | None = None,
        uc_warehouse_id: str | None = None,
        uc_catalog_name: str | None = None,
        uc_schema_name: str | None = None,
        uc_table_name: str | None = None,
        uc_table_columns: dict[str, str] | None = None,
        column_split_char: str = DEFAULT_COLUMN_SPLIT_CHAR,
        key_value_split_char: str = DEFAULT_KEY_VALUE_SPLIT_CHAR,
    ) -> logging.Logger:
        """Adds a tabular logger to the class.

        Args:
            logger_name: The name of the logger.
            handlers: The list of handlers to add.
            level: The logging level for the tabular logger. If not provided, the value from the settings will be used.
            add_log_analytics_logger: Whether to add a LogAnalyticsHandler to the logger. If not provided, the value from the settings will be used.
            add_unity_catalog_logger: Whether to add a UnityCatalogHandler to the logger. If not provided, the value from the settings will be used.
            log_type: The log type for the Log Analytics workspace.
            workspace_id: The workspace id for the Log Analytics workspace. If not provided, the value from the settings will be used.
            shared_key: The shared key for the Log Analytics workspace.
            uc_workspace_url: The workspace url for the Unity Catalog. If not provided, the value from the settings will be used.
            uc_warehouse_id: The warehouse id for the Unity Catalog. If not provided, the value from the settings will be used.
            uc_catalog_name: The catalog name for the Unity Catalog. If not provided, the value from the settings will be used.
            uc_schema_name: The schema name for the Unity Catalog. If not provided, the value from the settings will be used.
            uc_table_name: The table name for the Unity Catalog.
            uc_table_columns: The columns for the Unity Catalog Table.
            column_split_char: The column split character for the Log Analytics workspace and Unity Catalog. Defaults to "|".
            key_value_split_char: The key value split character for the Log Analytics workspace and Unity Catalog. Defaults to ":".

        Returns:
            The logger with the added tabular handlers.
        """
        if handlers is None:
            handlers = []
        logging_settings = NessySettings().logging

        if self.should_add_log_analytics_handler(logging_settings, add_log_analytics_logger):
            handlers.append("log_analytics")

        if self.should_add_unity_catalog_handler(logging_settings, add_unity_catalog_logger):
            handlers.append("unity_catalog")

        logger = LoggerFactory.get_logger(
            handler_types=handlers,
            logger_name=logger_name or f"Tabular:{self.__class__.__name__}",
            level=level,
            column_split_char=column_split_char,
            key_value_split_char=key_value_split_char,
            # UC Settings
            uc_table_name=uc_table_name,
            uc_catalog_name=uc_catalog_name or logging_settings.uc_catalog_name,
            uc_schema_name=uc_schema_name or logging_settings.uc_schema_name,
            uc_table_columns=uc_table_columns,
            workspace_url=uc_workspace_url or logging_settings.uc_workspace_url,
            warehouse_id=uc_warehouse_id or logging_settings.uc_warehouse_id,
            # LAW Settings
            workspace_id=workspace_id or logging_settings.log_analytics_workspace_id,
            shared_key=shared_key or logging_settings.log_analytics_shared_key,
            log_type=log_type,
            test_connectivity=False,
        )
        return cast(logging.Logger, logger)

    @staticmethod
    def should_add_log_analytics_handler(
        logging_settings: LoggingSettings,
        add_log_analytics_logger: bool | None,
        **kwargs,  # noqa: ARG004
    ) -> bool:
        """Determines if a LogAnalyticsHandler should be added to the logger.

        The Logger will be added if the `target_log_analytics` setting is set to True or if the `add_log_analytics_logger`
        argument is set to True.

        Setting `target_log_analytics` to False will prevent the handler from being added.

        Args:
            logging_settings: The logging settings to use for the logger.
            add_log_analytics_logger: Whether to add a LogAnalyticsHandler to the logger.
            **kwargs: Additional keyword arguments. Not used.

        Returns:
            bool: True if the LogAnalyticsHandler should be added, False otherwise.
        """
        disable_overwrite = logging_settings.target_log_analytics is False
        enable_logger = logging_settings.target_log_analytics or add_log_analytics_logger
        return cast(bool, enable_logger and not disable_overwrite)

    @staticmethod
    def should_add_unity_catalog_handler(
        logging_settings: LoggingSettings,
        add_unity_catalog_logger: bool | None,
    ) -> bool:
        """Determines if a UnityCatalogHandler should be added to the logger.

        The Logger will be added if the `target_unity_catalog_table` setting is set to True or if the `add_unity_catalog_logger`
        argument is set to True.

        Setting `target_unity_catalog_table` to False will prevent the handler from being added.

        Args:
            logging_settings: The logging settings to use for the logger.
            add_unity_catalog_logger: Whether to add a UnityCatalogHandler to the logger.

        Returns:
            bool: True if the UnityCatalogHandler should be added, False otherwise.
        """
        disable_overwrite = logging_settings.target_unity_catalog_table is False
        enable_logger = logging_settings.target_unity_catalog_table or add_unity_catalog_logger
        return cast(bool, enable_logger and not disable_overwrite)
