import os
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import networkx as nx

from ..logging.logger_mixin import LoggerMixin
from .pipeline_plotting_service import PipelinePlottingService
from .pipeline_step import PipelineStep


class Pipeline(LoggerMixin):
    """A Pipeline represents the logical unit of one ETL process.

    This class manages a directed acyclic graph (DAG) of steps, ensuring that
    each step is executed in the correct order based on dependencies.

    Attributes:
        name: The name of the pipeline.
        steps: An ordered dictionary of PipelineSteps that are part of the pipeline.
    """

    def __init__(self, name: str, steps: OrderedDict[str, "PipelineStep"] | None = None) -> None:
        self.name: str = name
        self.steps: OrderedDict[str, PipelineStep] = steps if steps is not None else OrderedDict()
        self._console_logger = self.get_console_logger()
        self._graph: nx.DiGraph = self._create_graph()
        self._lock: Lock = Lock()

    @property
    def graph(self) -> nx.DiGraph:
        """Get the pipeline graph."""
        return self._graph

    def _create_graph(self) -> nx.DiGraph:
        """Creates a directed acyclic graph (DAG) representing the pipeline steps and their dependencies.

        Each node in the graph represents a single step in the pipeline, and each edge represents a dependency.
        """
        g: nx.DiGraph = nx.DiGraph()
        g.add_nodes_from(set([s.name for s in self.steps.values()]))
        g.add_edges_from(set([(p, s.name) for s in self.steps.values() for p in s._predecessors if p]))

        self._console_logger.debug(f"Graph created with {g.number_of_nodes()} nodes and {g.number_of_edges()} edges.")
        return g

    def _run_step(self, step_name: str) -> None:
        """Executes the run method of the corresponding step in the pipeline."""
        step = self.steps[step_name]

        # Handle context and metadata references
        if step._context_ref:
            step.context = self.steps[step._context_ref].result
        if step._table_metadata_ref:
            step.context.table_metadata = self.steps[step._table_metadata_ref].result.table_metadata

        try:
            self._console_logger.info(f"Starting execution of step: {step.name}")
            step.run()
        except Exception as err:
            self._console_logger.error(f"Execution of step {step.name} failed with error: {str(err)}")
            raise err
        else:
            self._console_logger.info(f"Execution of step {step.name} succeeded.")

    def _get_ready_to_run_steps(self, remaining_steps: list[str], g: nx.DiGraph) -> set[str]:
        """Identifies and returns the steps that are ready to run.

        This method checks the directed acyclic graph (DAG) to find steps that have no predecessors,
        indicating that they are ready to be executed. It logs the remaining steps and the steps that
        are ready to run.

        Args:
            remaining_steps: A list of step IDs that are yet to be executed.
            g: The directed acyclic graph representing the pipeline.

        Returns:
            A set of step IDs that are ready to be executed.
        """
        with self._lock:
            ready_to_run = set([step for step in remaining_steps if g.in_degree(step) == 0])
            self._console_logger.debug(f"Remaining steps: {remaining_steps}")
            self._console_logger.debug(f"Ready to run: {ready_to_run}")
            return ready_to_run

    def _submit_ready_steps(
        self, ready_to_run: set[str], remaining_steps: list[str], executor: ThreadPoolExecutor, futures: dict
    ):
        """Submits the ready-to-run steps to the executor for execution.

        This method takes the steps that are ready to run, removes them from the list of remaining steps,
        and submits them to the executor for concurrent execution. It also updates the futures dictionary
        to keep track of the submitted tasks.

        Args:
            ready_to_run: A set of steps that are ready to be executed.
            remaining_steps: A list of steps that are yet to be executed.
            executor: The executor that manages the concurrent execution of steps.
            futures: A dictionary mapping futures to their corresponding step ID.
        """
        with self._lock:
            for step in ready_to_run:
                self._console_logger.debug(f"Submitting: {step}")
                remaining_steps.remove(step)
                future = executor.submit(self._run_step, step)
                futures[future] = step

    def _handle_completed_tasks(self, futures, g, remaining_steps):
        """Handles the completion of tasks in the pipeline.

        This method processes the futures that have completed execution. It removes the corresponding
        steps from the directed acyclic graph (DAG) and checks if new steps are ready to run. If new
        steps are ready, it returns True to indicate that the pipeline can continue execution.

        Args:
            futures: A dictionary mapping futures to their corresponding steps.
            g: The directed acyclic graph representing the pipeline.
            remaining_steps: A list of steps that are yet to be executed.

        Returns:
            True if new steps are ready to run, False otherwise.
        """
        # Wait for tasks to complete and free up dependencies
        for future in as_completed(futures):
            future.result()  # checks if the run was successful, otherwise throws an error and cancels remaining futures
            step = futures[future]
            del futures[future]
            with self._lock:
                g.remove_node(step)  # Mark the step as completed by removing it from the graph.
            if len(set([step for step in remaining_steps if g.in_degree(step) == 0])) > 0:
                self._console_logger.debug("New steps ready to run")
                return True
        self._console_logger.debug("No more steps to run")
        return False

    def _trim_graph(self, graph, until):
        """Trims the pipeline graph to only include steps up to the specified 'until' step (excluding).

        This method first verifies that the given step exists in the graph. It then finds all ancestors
        (i.e., steps that precede the 'until' step) and creates a subgraph consisting solely of those steps.

        Args:
            graph: The complete directed acyclic graph representing the pipeline.
            until: The identifier of the step up to which the graph should be trimmed.

        Returns:
            A subgraph containing only the steps leading to (and including) the 'until' step.

        Raises:
            ValueError: If the specified 'until' step is not found in the graph.
        """
        if until not in graph.nodes:
            raise ValueError(f"Step '{until}' not found in the pipeline.")

        predecessors = set(nx.ancestors(graph, until))
        predecessors.add(until)

        trimmed_graph = graph.subgraph(predecessors).copy()
        return trimmed_graph

    def run(self, until: str | None = None) -> None:
        """Executes the pipeline steps in the correct order based on dependencies.

        This method creates a directed acyclic graph (DAG) of the pipeline steps and, if specified, trims
        the graph to only include steps up to the given 'until' step (excluding: the step specified as 'until' will not be executed). It then concurrently executes steps
        with no pending dependencies using a ThreadPoolExecutor, ensuring that all steps are run in order.
        If a cyclic dependency is detected, or if any step fails during execution, the method raises an error.

        Args:
            until: Optional; the identifier of the step up to which the pipeline should be executed.

        Raises:
            RuntimeError: If a cyclic dependency is detected.
            Exception: Propagates any error raised during the execution of a step.
        """
        g = self._create_graph()

        if until is not None:
            g = self._trim_graph(g, until)

        remaining_steps = list(g.nodes())
        self._console_logger.info(f"Pipeline [' {self.name} '] started with {len(remaining_steps)} steps.")

        with ThreadPoolExecutor(max_workers=int(os.environ.get("NESSY_MAX_WORKERS", 1))) as executor:
            futures: dict = {}
            try:
                self._console_logger.debug(f"Remaining steps: {remaining_steps}")
                while remaining_steps:
                    ready_to_run = self._get_ready_to_run_steps(remaining_steps, g)
                    if not ready_to_run:
                        # If there are still steps to be executed, but all of them have predecessors there
                        # must be a cyclic dependency in the graph.
                        self._console_logger.error(
                            f"Cyclic dependency detected in the pipeline. Remaining steps: {remaining_steps}"
                        )
                        raise RuntimeError("Cyclic dependency detected in the pipeline!")

                    self._submit_ready_steps(ready_to_run, remaining_steps, executor, futures)

                    if self._handle_completed_tasks(futures, g, remaining_steps):
                        continue
            except RuntimeError as e:
                self._console_logger.error(f"Pipeline [' {self.name} '] failed due to cyclic dependency: {str(e)}")
                raise e
            except Exception as e:
                self._console_logger.error(f"Pipeline [' {self.name} '] failed: {str(e)}")
                raise e
            finally:
                # ensure that any futures are canceled (if successful, it finished anyway, if error, cancel still running futures)
                for future in futures:
                    future.cancel()  # Cancel remaining futures
                self._graph = self._create_graph()  # recreate the graph after the run
        self._console_logger.info(f"Pipeline [' {self.name} '] completed successfully.")

    def plot_graph(self, save_path: str | None = None) -> None:
        """Generates a visual representation of the pipeline steps and their dependencies.

        This method uses the PipelinePlottingService to create a plot of the pipeline graph. If a save path
        is specified, the plot will be saved to that location; otherwise, it will be displayed interactively.

        Args:
            save_path: Optional; the file path where the plot should be saved. If None, the plot is displayed interactively.
        """
        plotting_service = PipelinePlottingService()
        plotting_service.plot_graph(self, save_path)
