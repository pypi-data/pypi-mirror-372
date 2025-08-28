from pathlib import Path
from typing import Any, Self

from pydantic import Field

from ..utils.file_and_directory_handler import process_path
from .mixins.read_instance_mixin import ReadInstancesMixin
from .table import Table
from .types import ValidationErrorType


class Schema(ReadInstancesMixin):
    """A Class to represent a Schema in Unity Catalog."""

    catalog: str
    name: str
    storage_path: str | None = None
    tables: list[Table] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
    comment: str | None = None

    @classmethod
    def read_instance_from_file(
        cls,
        instance_path: str | Path,
        fail_on_missing_subfolder: bool = True,
        table_dir_name: str = "tables",
        **_: Any,
    ) -> tuple[Self | None, list[ValidationErrorType]]:
        """Read a schema from file.

        Adds the table objects from a path relative to the schema definition.

        Args:
            instance_path: The path to the Schema definition YAML file.
            fail_on_missing_subfolder: If False return a tuple with 2 empty
                    lists. Otherwise raise a FileNotFoundError.
            table_dir_name: The name of the directory containing the Table
                    definitions related to this schema. Can be a relative path.
        """
        processed_instance_path = process_path(instance_path)
        if not processed_instance_path:
            raise FileNotFoundError("Schema file not found.")

        schema, schema_errors = super().read_instance_from_file(processed_instance_path)
        table_errors: list[ValidationErrorType] = []
        if schema:
            schema.storage_path = "" if not schema.storage_path else schema.storage_path
            tables, table_errors = Table.read_instances_from_directory(
                instance_path=processed_instance_path.parents[0] / table_dir_name,
                catalog_name=schema.catalog,
                schema_name=schema.name,
                schema_storage_path=schema.storage_path,
                fail_on_missing_subfolder=fail_on_missing_subfolder,
            )
            schema.tables = tables
        return schema, schema_errors + table_errors

    def get_table_by_name(self, table_name: str) -> Table:
        """Return table in schema.

        Filters tables in schema for table_name and returns Table object.

        Args:
            table_name: Name of table to return from schema.

        Raises:
            ValueError: If table not found in schema metadata.

        Returns:
            The table.
        """
        table = next((table for table in self.tables if table.name == table_name), None)

        if not table:
            raise ValueError(f"Table {table_name} not found in {self.catalog}.{self.name} metadata.")

        return table

    def add_table(self, table: Table):
        """Adds a table to the schema and sets the table identifier accordingly.

        Args:
            table: A Table object that is added to the Schema tables.
        """
        table.identifier = f"{self.catalog}.{self.name}.{table.name}"
        self.tables.append(table)

    def add_tables(self, tables: list[Table]) -> None:
        """Adds tables to the schema.

        Args:
            tables: A list of Table objects that are added to the Schema tables.
        """
        for table in tables:
            self.add_table(table)
