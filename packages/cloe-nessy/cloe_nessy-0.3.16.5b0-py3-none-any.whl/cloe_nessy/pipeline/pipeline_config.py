import logging
from collections import OrderedDict
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class PipelineConfigBaseModel(BaseModel):
    """The base model for Pipeline Config objects."""

    @classmethod
    def metadata_to_instance(cls, data: dict) -> Any:
        """Parses a Dictionary to an instance.

        Args:
            data: The data to parse.

        Returns:
            An instance and potentially a list of errors.
        """
        errors = []
        try:
            instance = cls(**data)
        except ValidationError as e:
            instance = None
            errors.append(e)
        if errors:
            PipelineConfig.handle_validation_errors(errors)
        return instance

    @staticmethod
    def handle_validation_errors(errors: list[ValidationError]) -> None:
        """Cleanly prints Pydantic validation errors and raises a ValueError.

        Args:
            errors: A list of Pydantic validation errors.

        Raises:
            ValueError: If any validation errors occurred.
        """
        logger = logging.getLogger(__name__)
        for error in errors:
            if isinstance(error, ValidationError):
                logger.error(f"Validation errors for {error.title}:")
                for err in error.errors():
                    loc = ".".join(map(str, err["loc"]))
                    msg = err["msg"]
                    err_type = err["type"]
                    input_value = err.get("input", "N/A")
                    logger.error(f"  Location: {loc}")
                    logger.error(f"  Error Message: {msg}")
                    logger.error(f"  Error Type: {err_type}")
                    logger.error(f"  Input Value: {input_value}")
                    logger.error(f"  Further information: {err.get('ctx', {}).get('url', 'N/A')}")
                    logger.error("")
            else:
                logger.error(error)
        if errors:
            raise ValueError(f"Validation errors occurred: {errors}")


class PipelineActionConfig(PipelineConfigBaseModel):
    """This class stores the configuration for a pipeline action."""

    name: str

    @model_validator(mode="before")
    def validate_action(cls, v):
        """The Pipeline Action must be a valid action type."""
        # This validation was removed in favor of custom validations in YAML
        # pipeline definitions.
        # if v not in PipelineActionType.__members__: # noqa: ERA001
        #     raise ValueError(f"Action '{v}' is not a valid action.") # noqa: ERA001
        action_config = {"name": v}
        return action_config


class PipelineStepConfig(PipelineConfigBaseModel):
    """This class stores the configuration for a pipeline step."""

    action: PipelineActionConfig
    is_successor: bool = True
    context: str | None = None
    table_metadata: str | None = None
    options: dict = Field(default_factory=dict)


class PipelineConfig(PipelineConfigBaseModel):
    """This class stores the configuration for a pipeline."""

    name: str
    steps: OrderedDict[str, PipelineStepConfig]
