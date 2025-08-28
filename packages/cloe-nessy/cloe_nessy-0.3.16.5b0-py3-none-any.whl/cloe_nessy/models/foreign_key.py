import os

from pydantic import BaseModel, field_validator


def _process_column_input(v):
    if isinstance(v, str):
        v = [col.strip() for col in v.split(",")]
    return v


class ForeignKey(BaseModel):
    """Represents a ForeignKey."""

    foreign_key_columns: list[str]
    parent_table: str
    parent_columns: list[str]
    foreign_key_option: list[str] | None = None

    @field_validator("foreign_key_columns", mode="before")
    def _validate_foreign_key_columns(cls, v):
        return _process_column_input(v)

    @field_validator("parent_columns", mode="before")
    def _validate_parent_columns(cls, v):
        return _process_column_input(v)

    @field_validator("parent_table", mode="before")
    def _validate_identifier(cls, v):
        if len(v.split(".")) != 3:
            raise ValueError("The 'parent_table' must be in the format 'catalog.schema.table'")
        if "<env>" in v:
            v = v.replace("<env>", os.environ["PROJECT_ENVIRONMENT"])
        return v
