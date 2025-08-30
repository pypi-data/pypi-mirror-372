from pathlib import Path
from typing import Any, Self

import yaml
import yaml.scanner
from jinja2 import TemplateNotFound
from pydantic import (
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

from ..logging import LoggerMixin
from ..utils.file_and_directory_handler import process_path
from .column import Column
from .constraint import Constraint
from .foreign_key import ForeignKey
from .mixins.read_instance_mixin import ReadInstancesMixin
from .mixins.template_loader_mixin import TemplateLoaderMixin
from .types import ValidationErrorType


class Table(TemplateLoaderMixin, ReadInstancesMixin, LoggerMixin):
    """A Class to represent a Table in Unity Catalog."""

    identifier: str
    columns: list[Column]
    is_external: bool | None = None
    partition_by: list[str] = Field(default_factory=list)
    liquid_clustering: bool | None = None
    composite_primary_key: list[str] = Field(default_factory=list)
    properties: dict[str, str] = Field(default_factory=dict)
    constraints: list[Constraint] = Field(default_factory=list)
    foreign_keys: list[ForeignKey] = Field(default_factory=list)
    storage_path: str | None = None
    business_properties: dict[str, str] = Field(default_factory=dict)
    comment: str | None = None
    data_source_format: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Post init method for the Table model."""
        self._console_logger = self.get_console_logger()
        self._tabular_logger = self.get_tabular_logger(uc_table_name="nessy_table_logs", log_type="nessy_table_logs")
        self._console_logger.debug(f"Model for table [ '{self.identifier}' ] has been initialized.")
        self._tabular_logger.debug(f"Message : Model for table [ '{self.identifier}' ] has been initialized.")

    @property
    def catalog(self):
        """The name of the Catalog of the Table."""
        return self.identifier.split(".")[0]

    @property
    def schema(self):
        """The name of the Schema of the Table."""
        return self.identifier.split(".")[1]

    @property
    def name(self):
        """The name of the Table."""
        return self.identifier.split(".")[2]

    @property
    def escaped_identifier(self):
        """The escaped identifier of the Table."""
        return f"`{self.catalog}`.`{self.schema}`.`{self.name}`"

    @field_validator("constraints", mode="before")
    def _validate_constraints(cls, raw: dict[str, dict[str, str]]) -> list[Constraint]:
        """The constraints are defined with the name as key or as a list and must therefore be transformed."""
        if isinstance(raw, dict):
            constraints = [Constraint(name=constraint, **raw[constraint]) for constraint in raw]
        elif isinstance(raw, list):
            constraints = []
            for item in raw:
                if isinstance(item, Constraint):
                    constraints.append(item)
                elif isinstance(item, dict):
                    constraints.append(Constraint(**item))
                else:
                    raise ValueError("Invalid constraint format")
        else:
            raise ValueError("Constraints must be either a list or a dictionary")
        return constraints

    @field_validator("foreign_keys", mode="after")
    def _validate_fk_columns(cls, v: list[ForeignKey], values: ValidationInfo):
        """Foreign keys need to be columns in the table as well."""
        column_names = [c.name for c in values.data.get("columns", [])]
        for fk in v:
            for column in fk.foreign_key_columns:
                if column not in column_names:
                    raise ValueError(f"Foreign key column '{column}' does not match any column in 'columns'")
        return v

    @model_validator(mode="after")
    def _validate_is_external(cls, table: Self):
        """If is_external is set to True, storage_path has to be set."""
        if table.is_external and table.storage_path is None:
            raise ValueError("is_external cannot be true while storage_path is None.")
        return table

    @classmethod
    def read_instances_from_directory(
        cls,
        instance_path: str | Path,
        fail_on_missing_subfolder: bool = True,
        catalog_name: str | None = None,
        schema_name: str | None = None,
        schema_storage_path: str | Path | None = None,
        **_: Any,
    ) -> tuple[list[Self], list[ValidationErrorType]]:
        """Reads instances from a directory containing YAML files.

        This method scans a specified directory for YAML files (.yaml or .yml),
        attempts to read and parse each file as an instance of the class, and
        collects any errors encountered during the process. If the directory
        does not exist or is not a directory, it either raises a
        FileNotFoundError (if fail_on_missing_subfolder is True) or returns
        empty lists.

        Args:
            instance_path: The path to the directory containing instance files.
            catalog_name: Name of the catalog to which these instances belong.
            schema_name: Name of the schema used for validating the instances.
            fail_on_missing_subfolder: Determines behavior when the specified
                    directory does not exist or is not a directory. Defaults to True,
                    which will raise a FileNotFoundError.
            schema_storage_path: Path to the storage location of the schema
                    these tables instances belong to.

        Returns:
            - The first list contains instances of the class that were
                successfully read and validated from the files.
            - The second list contains errors encountered during the
                process, which could be validation errors or YAML
                parsing/scanning errors.

        Raises:
            FileNotFoundError: If the specified directory does not exist or is
                               not a directory and fail_on_missing_subfolder is True.
            ValueError: If catalog_name or schema_name are not provided.
        """
        processed_instance_path = process_path(instance_path)
        schema_storage_path = process_path(schema_storage_path)
        errors: list[ValidationErrorType] = []

        if not catalog_name or not schema_name:
            errors.append(ValueError("catalog_name and schema_name must be provided."))
            return [], errors
        instances: list[Self] = []

        if not processed_instance_path or not processed_instance_path.exists() or not processed_instance_path.is_dir():
            if fail_on_missing_subfolder:
                raise FileNotFoundError(f"Directory not found: {processed_instance_path}")
            else:
                return instances, errors

        for instance_file in processed_instance_path.iterdir():
            sub_errors: list[ValidationErrorType] = []
            if instance_file.is_file() and instance_file.suffix in (".yaml", ".yml"):
                instance, sub_errors = cls.read_instance_from_file(
                    instance_file, catalog_name, schema_name, str(schema_storage_path)
                )
                instances += [] if instance is None else [instance]
            errors += sub_errors

        return instances, errors

    @classmethod
    def read_instance_from_file(
        cls,
        instance_path: str | Path,
        catalog_name: str | None = None,
        schema_name: str | None = None,
        schema_storage_path: str | Path | None = None,
        **_: Any,
    ) -> tuple[Self | None, list[ValidationErrorType]]:
        """Read a table instance from file.

        Args:
            instance_path: The path to the Schema definition YAML file.
            catalog_name: The name of the Catalog of the Table.
            schema_name: The name of the Schema of the Table.
            schema_storage_path: The storage path location of the Schema of the Table.

        Returns:
            - Instance of the class that was successfully instantiated and
                  validated
            - The second list contains errors encountered during the process,
                  which could be validation errors or YAML parsing/scanning errors.

        Raises:
            FileNotFoundError: If the specified directory does not exist or is
                not a directory and fail_on_missing_subfolder is
                True.
            ValueError: If catalog_name or schema_name are not provided.
        """
        processed_instance_path = process_path(instance_path)
        if not processed_instance_path:
            raise FileNotFoundError("Table file not found.")
        schema_storage_path = process_path(schema_storage_path)
        errors: list[ValidationErrorType] = []

        if not catalog_name or not schema_name:
            errors.append(ValueError("catalog_name and schema_name must be provided."))
            return None, errors

        try:
            with processed_instance_path.open("r") as file:
                data = yaml.safe_load(file)
                data["identifier"] = f"{catalog_name}.{schema_name}.{data['name']}"
                if data.get("is_external"):
                    if storage_path := data.get("storage_path"):
                        data["storage_path"] = storage_path
                    elif schema_storage_path:
                        data["storage_path"] = (schema_storage_path / data["name"]).as_posix()
                    else:
                        raise ValueError(
                            f"Neither storage path nor schema storage path of table {data['name']} has been provided."
                        )

                instance, sub_errors = cls.metadata_to_instance(data)
                errors += sub_errors
        except (
            ValidationError,
            yaml.parser.ParserError,
            yaml.scanner.ScannerError,
        ) as e:
            instance = None
            errors.append(e)
        return instance, errors

    def get_create_statement(
        self,
        replace: bool = True,
    ):
        """Get the create statement for the Table.

        Args:
            replace: Whether to use the REPLACE statement or not.

        Returns:
            The rendered create statement for the Table.

        Raises:
            TemplateNotFound: If the template file is not found.
        """
        templates = Path(__file__).parent / "templates"
        template_name = "create_table.sql.j2"

        try:
            template = self.get_template(templates, template_name)
        except TemplateNotFound as err:
            self._console_logger.error(f"Template [ {template_name} ] not found.")
            raise err
        render = template.render(table=self, replace=replace)
        return render

    def get_column_by_name(self, column_name: str) -> Column | None:
        """Get a column by name.

        Args:
            column_name: The name of the column to get.

        Returns:
            The column if found, else None.
        """
        for column in self.columns:
            if column.name == column_name:
                return column
        return None

    def update_column(self, column: Column) -> None:
        """Replaces a Column with a new Column object to update it.

        Args:
            column: The new column object, to replace the old one.
        """
        self.remove_column(column)
        self.add_column(column)

    def add_column(self, column: Column):
        """Adds a column to the table.

        Args:
            column: The column to be added.
        """
        self.columns.append(column)

    def remove_column(self, column: str | Column) -> None:
        """Remove a column from the Table.

        Args.
            column: The column to be removed.
        """
        if isinstance(column, Column):
            column_name = column.name
        else:
            column_name = column

        self.columns = [col for col in self.columns if col.name != column_name]
