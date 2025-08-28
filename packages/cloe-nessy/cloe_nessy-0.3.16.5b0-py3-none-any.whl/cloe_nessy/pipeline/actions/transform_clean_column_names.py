import json
import re
from typing import Any

import pyspark.sql.functions as F
import pyspark.sql.types as T

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformCleanColumnNamesAction(PipelineAction):
    """Fixes column names in the DataFrame to be valid.

    Removes invalid characters from the column names, including the fields of a struct and
    replaces a single leading underscore by a double underscore.

    Invalid characters include:
        - Any non-word character (anything other than letters, digits, and underscores).
        - A single leading underscore.

    Example:
        ```yaml
        Clean Column Names:
            action: TRANSFORM_CLEAN_COLUMN_NAMES
        ```
    """

    name: str = "TRANSFORM_CLEAN_COLUMN_NAMES"

    def run(
        self,
        context: PipelineContext,
        **_: Any,
    ) -> PipelineContext:
        """Fixes column names in the DataFrame to be valid.

        Removes invalid characters from the column names, including the fields of a struct and
        replaces a single leading underscore by a double underscore.

        Args:
            context: The context in which this Action is executed.

        Raises:
            ValueError: If the data from the context is None.

        Returns:
            The context after the execution of this Action, containing the DataFrame with cleaned column names.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        with_columns_renamed = {}
        with_columns_casted: dict[str, T.StructType | T.ArrayType | T.MapType] = {}

        single_underscrore_at_beginning = r"^_(?=[^_])"

        for c in context.data.schema:
            old_name = c.name
            new_name = re.sub(single_underscrore_at_beginning, "__", re.sub(r"\W", "_", old_name))
            with_columns_renamed[old_name] = new_name

            if isinstance(c.dataType, (T.StructType | T.ArrayType | T.MapType)):
                old_column_schema = c.dataType.json()
                new_column_schema = re.sub(
                    r'(?<="name":")[^"]+',
                    lambda m: re.sub(r"\W", "_", str(m.group())),
                    old_column_schema,
                )
                if isinstance(c.dataType, T.StructType):
                    with_columns_casted[new_name] = T.StructType.fromJson(json.loads(new_column_schema))
                elif isinstance(c.dataType, T.ArrayType):
                    with_columns_casted[new_name] = T.ArrayType.fromJson(json.loads(new_column_schema))
                elif isinstance(c.dataType, T.MapType):
                    with_columns_casted[new_name] = T.MapType.fromJson(json.loads(new_column_schema))

        df = context.data.withColumnsRenamed(with_columns_renamed)
        for c_name, c_type in with_columns_casted.items():
            df = df.withColumn(c_name, F.col(c_name).cast(c_type))

        return context.from_existing(data=df)  # type: ignore
