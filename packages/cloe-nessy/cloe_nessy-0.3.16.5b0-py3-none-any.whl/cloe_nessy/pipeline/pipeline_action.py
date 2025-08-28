import logging
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..logging import LoggerMixin
from .pipeline_context import PipelineContext


@dataclass
class PipelineActionLogs:
    """Dataclass defining the pipeline action logs table."""

    table_name: str = "nessy_action_logs"
    log_type: str = "nessy_action_logs"
    columns: dict[str, str] = field(
        default_factory=lambda: {
            "action_name": "STRING",
            "message": "STRING",
        }
    )


class PipelineActionMeta(ABCMeta):
    """Metaclass for PipelineAction to ensure that all subclasses have a 'name' attribute."""

    def __init__(cls, name, bases, dct):
        if cls.__name__ != "PipelineAction" and "name" not in dct:
            raise TypeError(f"Class {name} is missing required 'name' attribute")
        super().__init__(name, bases, dct)


class PipelineAction(ABC, LoggerMixin, metaclass=PipelineActionMeta):
    """Models the operation being executed against an Input.

    Attributes:
        name: The name of the action.
    """

    name: str

    def __init__(self, tabular_logger: logging.Logger | None = None) -> None:
        """Initializes the PipelineAction object.

        Args:
            tabular_logger: The tabular logger to use for dependency injection.
        """
        self._console_logger = self.get_console_logger()
        self._tabular_logger = tabular_logger or self.get_tabular_logger(
            logger_name="Tabular:PipelineAction",
            uc_table_name=PipelineActionLogs().table_name,
            uc_table_columns=PipelineActionLogs().columns,
            log_type=PipelineActionLogs().log_type,
        )

    def __str__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def run(self, context: PipelineContext, **kwargs: Any) -> PipelineContext:
        """Execute the pipeline action."""
        pass
