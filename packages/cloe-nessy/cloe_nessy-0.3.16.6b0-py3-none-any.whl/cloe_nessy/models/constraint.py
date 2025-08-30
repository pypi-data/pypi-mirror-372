from pydantic import BaseModel


class Constraint(BaseModel):
    """Represents a Constraint on a Table."""

    name: str
    expression: str
    description: str | None = None
