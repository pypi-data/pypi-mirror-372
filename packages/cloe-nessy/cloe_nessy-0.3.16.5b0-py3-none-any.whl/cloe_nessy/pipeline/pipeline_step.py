from dataclasses import dataclass, field
from typing import Any

from .pipeline_action import PipelineAction
from .pipeline_context import PipelineContext


@dataclass
class PipelineStep:
    """A PipelineStep is a logical step within a Pipeline.

    The step stores the PipelineContext and offers an interface to interact with
    the Steps DataFrame.

    Attributes:
        name: The name of the step.
        action: The action to be executed.
        is_successor: A boolean indicating if the step is a successor and takes
            the previous steps context.
        context: The context of the step.
        options: Additional options for the step
        _predecessors: A list of names of the steps that are predecessors to this step.
        _context_ref: Reference to the previous steps context
        _table_metadata_ref: Reference to the previous steps metadata
    """

    name: str
    action: PipelineAction
    context: PipelineContext = field(default_factory=lambda: PipelineContext())
    options: dict[str, Any] = field(default_factory=lambda: {})
    result: PipelineContext = field(default_factory=lambda: PipelineContext())
    _predecessors: set[str] = field(default_factory=lambda: set())
    _context_ref: str | None = None
    _table_metadata_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action, PipelineAction):
            raise ValueError("action must be a PipelineAction subclass.")
        if self._context_ref:
            self._predecessors.add(self._context_ref)
        if self._table_metadata_ref:
            self._predecessors.add(self._table_metadata_ref)
        if self.options:
            for val in self.options.values():
                if isinstance(val, PipelineStep):
                    self._predecessors.add(val.name)

    def run(self) -> None:
        """Execute the action on the context."""
        self.result = self.action.run(context=self.context, **self.options)
