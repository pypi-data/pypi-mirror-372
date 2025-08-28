import re
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

COLUMN_DATA_TYPE_LIST = {
    "string",
    "decimal",
    "integer",
    "int",
    "smallint",
    "float",
    "boolean",
    "bool",
    "bigint",
    "long",
    "double",
    "date",
    "timestamp",
    "array",
    "map",
    "variant",
    "struct",
}


class Column(BaseModel):
    """Represents a Column of a Table."""

    name: str
    data_type: str
    nullable: bool
    default_value: Any = None
    generated: str | None = None
    business_properties: dict[str, Any] = Field(default_factory=dict)
    comment: str | None = None

    @field_validator("data_type", mode="before")
    def data_type_transform(cls, raw: str) -> str:
        """Map potential aliases to the correct SQL data type.

        Args:
            raw: The value for the data type.
        """
        val = raw.lower()
        base_data_types = re.findall(r"\b[a-z]+\b", val)
        forbidden_characters = re.findall(r"[^a-z0-9\(\)\<\>,\s]+", val)

        if forbidden_characters:
            raise ValueError(f"Forbidden characters in data type definition [ '{val}' ]: [' {forbidden_characters} ']")
        for base_data_type in base_data_types:
            if base_data_type not in COLUMN_DATA_TYPE_LIST:
                raise ValueError(f"Unknown data type used in data type definition [ '{val}' ]")
        return val

    @model_validator(mode="before")
    def _validate_generated_and_default_value(cls, v: Any) -> Any:
        """Check if a column has a default value and is generated.

        That doesn't make sense, so an error should be raised.
        """
        if v.get("default_value") and v.get("generated"):
            raise ValueError("A column can't have a default value and be generated.")
        if (v.get("default_value") or v.get("generated")) and v.get("nullable") is True:
            raise ValueError("A column can't have a default value or be generated and be nullable.")
        return v
