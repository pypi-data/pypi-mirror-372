import os
import re
from collections import OrderedDict
from enum import Enum
from pathlib import Path

import yaml

from ..logging import LoggerMixin
from ..session import SessionManager
from .actions import PipelineActionType, pipeline_actions
from .pipeline import Pipeline
from .pipeline_config import PipelineConfig
from .pipeline_step import PipelineStep


class PipelineParsingService:
    """A service class that parses a YAML document or string into a Pipeline object."""

    def __init__(self, custom_actions=None):
        if custom_actions is not None:
            for action in custom_actions:
                self.register_pipeline_action(action)

    @staticmethod
    def register_pipeline_action(pipeline_action_class):
        """Registers a custom pipeline action class.

        !!! note
            Registering an action enables the custom action to be used in the
            pipeline YAML definition. This is automatically called, when the
            PipelineParsingService is instantiated with (a list of) custom
            actions.
        """
        console_logger = LoggerMixin().get_console_logger()
        console_logger.info("Registering custom pipeline action [' %s ']", pipeline_action_class.name)
        pipeline_actions[pipeline_action_class.name] = pipeline_action_class

        global PipelineActionType
        PipelineActionType = Enum("PipelineActionType", pipeline_actions)

    @staticmethod
    def parse(path: Path | None = None, yaml_str: str | None = None) -> Pipeline:
        """Reads the YAML from a given Path and returns a Pipeline object.

        Args:
            path: Path to the YAML document.
            yaml_str: A string that can be parsed in YAML format.

        Raises:
            ValueError: If neither 'path' nor 'yaml_str' has been provided.

        Returns:
            Pipeline: The resulting Pipeline instance.
        """
        console_logger = LoggerMixin().get_console_logger()
        if not path and not yaml_str:
            raise ValueError("Neither 'file_path' nor 'yaml_str' was provided. Please supply one of them.")
        if path:
            path_obj = Path(path)
            with open(path_obj) as f:
                yaml_str = f.read()
        if not yaml_str:
            raise ValueError("YAML content is empty.")

        final_yaml_str = PipelineParsingService._replace_variables(yaml_str)
        config = yaml.safe_load(final_yaml_str)
        pipeline_config = PipelineConfig.metadata_to_instance(config)
        steps = PipelineParsingService._get_steps(pipeline_config.steps)
        pipeline = Pipeline(name=pipeline_config.name, steps=steps)  # type: ignore
        console_logger.info("Pipeline [ '%s' ] parsed successfully with %d steps.", pipeline.name, len(pipeline.steps))
        return pipeline

    @staticmethod
    def _replace_variables(yaml_str: str) -> str:
        """Replace variable placeholders in a YAML string.

        Replaces environment variables with the pattern `{{env:var-name}}`. Where
        the var-name is the name of the environment variable. Replaces secret
        references with the pattern `{{secret-scope-name:secret-key}}`. Where
        scope-name is the name of the secret scope and secret-key is the key of
        the secret.

        Args:
            yaml_str: A string that can be parsed in YAML format.

        Returns:
            The same YAML string with environment variable placeholders replaced.
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

    @staticmethod
    def _get_steps(step_configs, last_step_name: str | None = None):
        steps = OrderedDict()
        for step_name, step_config in step_configs.items():
            is_successor = step_config.is_successor
            context_ref = step_config.context
            if is_successor and not context_ref:
                context_ref = last_step_name
            action = PipelineActionType[step_config.action.name].value()
            step = PipelineStep(
                name=step_name,
                action=action,
                options=step_config.options,
                _context_ref=context_ref,
                _table_metadata_ref=step_config.table_metadata,
            )
            steps[step.name] = step
            last_step_name = step_name
        for step in steps.values():
            steps[step.name] = PipelineParsingService._replace_step_refs(steps, step)
        return steps

    @staticmethod
    def _replace_step_refs(steps: OrderedDict[str, PipelineStep], step: PipelineStep) -> PipelineStep:
        step_ref_pattern = r"\(\(step:([^)]+)\)\)"

        def _handle_string_value(value: str, option: str):
            if match := re.match(step_ref_pattern, value):
                dependency_step_name = match.group(1)
                dependency_step = steps.get(dependency_step_name)
                step.options[option] = dependency_step
                step._predecessors.add(dependency_step_name)

        def _handle_list_value(value: list, option: str):
            for i, v in enumerate(value):
                if isinstance(v, str):
                    if match := re.match(step_ref_pattern, v):
                        dependency_step_name = match.group(1)
                        dependency_step = steps.get(dependency_step_name)
                        step.options[option][i] = dependency_step
                        step._predecessors.add(dependency_step_name)

        if step.options:
            for option, value in step.options.items():
                if isinstance(value, str):
                    _handle_string_value(value, option)
                elif isinstance(value, list):
                    _handle_list_value(value, option)

        return step
