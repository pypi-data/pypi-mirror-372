from pathlib import Path

from jinja2 import FileSystemLoader
from jinja2 import Template as JinjaTemplate
from jinja2.environment import Environment


class TemplateLoaderMixin:
    """A Mixin to load Jinja Templates."""

    @staticmethod
    def get_template(template_path: Path, template_name: str) -> JinjaTemplate:
        """Load the specified template."""
        loader: FileSystemLoader = FileSystemLoader(template_path)

        env = Environment(loader=loader, keep_trailing_newline=True)

        return env.get_template(template_name)
