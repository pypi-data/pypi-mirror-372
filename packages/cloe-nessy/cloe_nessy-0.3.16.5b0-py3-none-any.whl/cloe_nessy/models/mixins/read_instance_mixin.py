import os
import pathlib
import re
from typing import Any, Self

import yaml
import yaml.parser
import yaml.scanner
from pydantic import BaseModel, ValidationError

from ...session import SessionManager
from ..types import ValidationErrorType


class ReadInstancesMixin(BaseModel):
    """This class defines the methods to read, validate and parse metadata definitions."""

    @classmethod
    def metadata_to_instance(cls, data: dict) -> tuple[Self | None, list[ValidationError]]:
        """Parses a Dictionary to an instance.

        Returns:
            An instance and potentially a list of errors.
        """
        errors = []
        try:
            instance = cls(**data)
        except ValidationError as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def read_instance_from_file(
        cls,
        instance_path: pathlib.Path,
        **_: Any,  # allow subclasses to pass additional arguments
    ) -> tuple[Self | None, list[ValidationErrorType]]:
        """Read and instantiate a single YAML file for the given path.

        Arguments:
            instance_path: The path to the file to instantiate.

        Return:
            Returns a tuple of the instantiated model and errors.
        """
        errors: list[ValidationErrorType] = []
        try:
            with instance_path.open("r") as file:
                raw_string = file.read()
                yaml_str = cls._replace_variables(raw_string)
                data = yaml.safe_load(yaml_str)
                instance, sub_errors = cls.metadata_to_instance(data)
                errors += sub_errors
        except (ValidationError, yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
            instance = None
            errors.append(e)
        return instance, errors

    @classmethod
    def read_instances_from_directory(
        cls,
        instance_path: pathlib.Path,
        fail_on_missing_subfolder: bool = True,
        **_: Any,  # allow subclasses to pass additional arguments
    ) -> tuple[list[Self], list[ValidationErrorType]]:
        """Read and instantiate all *.yaml files for the given path.

        Arguments:
            instance_path: Path to the directory containing the instance definitions as YAML files.
            fail_on_missing_subfolder: If False return a tuple with 2 empty
                    lists. Otherwise raise a FileNotFoundError.

        Return:
            Returns a tuple of the instantiated models and errors.
        """
        instances: list[Self] = []
        errors: list[ValidationErrorType] = []

        if not instance_path.exists() or not instance_path.is_dir():
            if fail_on_missing_subfolder:
                raise FileNotFoundError(f"Directory not found: {instance_path}")
            else:
                return instances, errors

        for instance_file in instance_path.iterdir():
            sub_errors: list[ValidationErrorType] = []
            if instance_file.is_file() and instance_file.suffix in (".yaml", ".yml"):
                instance, sub_errors = cls.read_instance_from_file(instance_file)
                instances += [] if instance is None else [instance]
            errors += sub_errors

        return instances, errors

    @staticmethod
    def _replace_variables(yaml_str: str) -> str:
        """Replace variable placeholders in a YAML string.

        Replaces environment variables with the pattern `{{env:var-name}}`. Where
        the var-name is the name of the environment variable.

        Args:
            yaml_str (str): A string that can be parsed in YAML format.

        Returns:
            The same YAML string with environment variable placeholders
            replaced.
        """
        env_var_pattern = r"\{\{env:([^}]+)\}\}"
        secret_ref_pattern = r"\{\{(?!step|env)([^}]+):([^}]+)\}\}"

        def replace_with_env_var(match):
            env_var_name = match.group(1)
            env_var_value = os.getenv(env_var_name)
            return env_var_value

        def replace_with_secret(match):
            secret_scope_name = match.group(1)
            secret_key = match.group(2)
            return SessionManager.get_utils().secrets.get(scope=secret_scope_name, key=secret_key)

        env_replaced_yaml_string = re.sub(env_var_pattern, replace_with_env_var, yaml_str)
        final_yaml_string = re.sub(secret_ref_pattern, replace_with_secret, env_replaced_yaml_string)
        return final_yaml_string
