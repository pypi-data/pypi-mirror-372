from typing import Any

from pyspark.sql import DataFrame

from ..models import Table


class PipelineContext:
    """A class that models the context of a pipeline.

    The context consists of Table Metadata (the Table definition) and the actual data
    as a DataFrame.

    Attributes:
        table_metadata: The Nessy-Table definition.
        data: The data of the context.
        runtime_info: Additional runtime information, e.g. streaming status.
        status: The status of the context. Can be "initialized", "successful" or
            "failed".

    Note:
        This is not a pydantic class, because Fabric does not support the type ConnectDataFrame.
    """

    def __init__(
        self,
        table_metadata: Table | None = None,
        data: DataFrame | None = None,
        runtime_info: dict[str, Any] | None = None,
        status: str = "initialized",
    ) -> None:
        self.table_metadata = table_metadata
        self.data = data
        self.runtime_info = runtime_info if runtime_info is not None else {}
        self.status = status

    def from_existing(
        self,
        table_metadata: Table | None = None,
        data: DataFrame | None = None,
        runtime_info: dict[str, Any] | None = None,
    ) -> "PipelineContext":
        """Creates a new PipelineContext from an existing one.

        Args:
            table_metadata: The metadata of the new context.
            data: The data of the new context.
            runtime_info: The runtime_info of the new context.

        Returns:
            The new PipelineContext.
        """
        final_metadata = table_metadata or self.table_metadata
        final_data = data or self.data
        final_runtime_info = runtime_info or self.runtime_info or {}
        return PipelineContext(table_metadata=final_metadata, data=final_data, runtime_info=final_runtime_info)
