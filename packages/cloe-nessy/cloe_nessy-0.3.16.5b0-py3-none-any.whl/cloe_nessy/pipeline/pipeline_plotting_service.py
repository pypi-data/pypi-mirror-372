"""Pipeline plotting service for visualizing pipeline graphs using matplotlib."""

import textwrap

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import networkx as nx

from ..logging import LoggerMixin


class PipelinePlottingService(LoggerMixin):
    """Service for plotting pipeline graphs using matplotlib.

    This service handles the visualization of pipeline DAGs, including node positioning,
    edge drawing, and proper layout management.
    """

    def __init__(self):
        """Initialize the plotting service."""
        self.context_colors = {
            "initialized": "lightgrey",
            "successful": "lightgreen",
            "failed": "red",
        }
        self._console_logger = self.get_console_logger()

    def plot_graph(self, pipeline, save_path: str | None = None):
        """Plot and save the pipeline graph as an image.

        Args:
            pipeline: The Pipeline object to visualize.
            save_path: Path where the graph image should be saved.
        """
        g: nx.DiGraph = nx.DiGraph()
        g.add_edges_from(self._generate_edges(pipeline))
        pos = self._determine_number_of_rows(g.nodes, 75, 5, pipeline)

        _, ax = plt.subplots(figsize=(16, 12))

        adjusted_pos = {}
        scaling_factor = 0.7

        for node, (x, y) in pos.items():
            text_length = len(node)
            node_width = max(7.5, text_length * 0.2)
            node_height = 2.0
            x_spacing = max(9.0, node_width * scaling_factor)
            y_spacing = max(4.5, node_height * scaling_factor)
            adjusted_pos[node] = (x * x_spacing, y * y_spacing)

        # Calculate bounds to set proper axis limits
        if adjusted_pos:
            x_coords = [pos[0] for pos in adjusted_pos.values()]
            y_coords = [pos[1] for pos in adjusted_pos.values()]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            # Add padding
            x_padding = (x_max - x_min) * 0.1 if x_max != x_min else 5
            y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 5

            ax.set_xlim(x_min - x_padding, x_max + x_padding)
            ax.set_ylim(y_min - y_padding, y_max + y_padding)

        self._draw_edges(ax, g, adjusted_pos)
        self._draw_nodes(ax, pipeline, adjusted_pos)
        self._add_legend(ax, adjusted_pos)

        ax.set_title(pipeline.name, fontsize=18, weight="bold", pad=20)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none", format="png")
            self._console_logger.info(f"Graph saved to {save_path}")
        else:
            plt.show()
        plt.close()

    def _generate_edges(self, pipeline):
        """Generate edges from pipeline steps."""
        input_collection = []
        for _, value in pipeline.steps.items():
            for predecessor in value._predecessors:
                input_collection.append((predecessor, value.name))
        return input_collection

    def _draw_edges(self, ax, graph, adjusted_pos):
        """Draw edges between nodes with proper arrow positioning."""
        for src, tgt in graph.edges():
            x0, y0 = adjusted_pos[src]
            x1, y1 = adjusted_pos[tgt]

            # Get the dimensions of the source and target nodes
            src_width = max(7.5, len(src) * 0.2) / 2  # Half width
            src_height = 1.7 / 2  # Half height
            tgt_width = max(7.5, len(tgt) * 0.2) / 2  # Half width
            tgt_height = 1.7 / 2  # Half height

            dx = x1 - x0
            dy = y1 - y0

            # Calculation of scaling factors so that the arrow starts/ends at rectangle boundary
            if abs(dx) < 0.001 and abs(dy) < 0.001:
                # Skip if nodes are at the same position
                continue
            if abs(dx) < 0.001:
                # Vertical line
                scale_src = src_height / abs(dy) if dy != 0 else 0
                scale_tgt = tgt_height / abs(dy) if dy != 0 else 0
            elif abs(dy) < 0.001:
                # Horizontal line
                scale_src = src_width / abs(dx)
                scale_tgt = tgt_width / abs(dx)
            else:
                # Diagonal line
                scale_x_src = src_width / abs(dx)
                scale_y_src = src_height / abs(dy)
                scale_src = min(scale_x_src, scale_y_src)

                scale_x_tgt = tgt_width / abs(dx)
                scale_y_tgt = tgt_height / abs(dy)
                scale_tgt = min(scale_x_tgt, scale_y_tgt)

            start_x = x0 + dx * scale_src
            start_y = y0 + dy * scale_src
            end_x = x1 - dx * scale_tgt
            end_y = y1 - dy * scale_tgt

            ax.annotate(
                "",
                xy=(end_x, end_y),
                xytext=(start_x, start_y),
                arrowprops={"arrowstyle": "->", "color": "gray", "lw": 2, "shrinkA": 0, "shrinkB": 0},
            )

    def _draw_nodes(self, ax, pipeline, adjusted_pos):
        """Draw nodes as rectangles with text labels."""
        for node, (x, y) in adjusted_pos.items():
            context = self._get_context_by_step_info(pipeline, node)
            fillcolor = self.context_colors.get(context, "lightgrey")

            text_length = len(node)
            node_width = max(7.5, text_length * 0.2)
            node_height = 2.0

            rect = patches.Rectangle(
                (x - node_width / 2, y - node_height / 2),
                node_width,
                node_height,
                linewidth=1,
                edgecolor="black",
                facecolor=fillcolor,
                zorder=2,
            )
            ax.add_patch(rect)

            wrapped_label = self._wrap_text(node).replace("<br>", "\n")
            ax.text(x, y, wrapped_label, ha="center", va="center", fontsize=10, weight="bold", zorder=3)

    def _add_legend(self, ax, adjusted_pos):
        """Add legend at the bottom of the graph."""
        legend_text = "Success = Light Green; Waiting = Light Grey; Failed = Bright Red"

        if adjusted_pos:
            y_coords = [pos[1] for pos in adjusted_pos.values()]
            legend_y = min(y_coords) - abs(max(y_coords) - min(y_coords)) * 0.2 - 3
            x_coords = [pos[0] for pos in adjusted_pos.values()]
            legend_x = (min(x_coords) + max(x_coords)) / 2
        else:
            legend_x, legend_y = 0, -5

        ax.text(
            legend_x,
            legend_y,
            legend_text,
            ha="center",
            va="center",
            fontsize=12,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.8},
        )

    def _determine_number_of_rows(self, nodes, max_row_length, max_nodes_in_row, pipeline):
        """Structure the node's position in a DAG-aware layout that better shows dependencies."""
        # Build the graph to understand dependencies
        graph = nx.DiGraph()
        graph.add_edges_from(self._generate_edges(pipeline))

        # Try to use a topological layout that respects dependencies
        try:
            # Use a hierarchical layout approach
            pos = self._create_hierarchical_layout(graph, pipeline)
        except Exception:
            # Fallback to the original layout if there are issues
            pos = self._create_simple_layout(nodes, max_row_length, max_nodes_in_row)

        pos = self._post_process_grouping(nodes, pos, pipeline)
        return pos

    def _create_hierarchical_layout(self, graph, pipeline):
        """Create a layout based on dependency levels to show parallel branches clearly."""
        levels = self._calculate_dependency_levels(graph)
        level_groups = self._group_nodes_by_level(levels)
        return self._position_nodes_in_levels(level_groups)

    def _calculate_dependency_levels(self, graph):
        """Calculate the dependency level for each node."""
        levels = {}
        remaining_nodes = set(graph.nodes())
        current_level = 0

        while remaining_nodes:
            current_level_nodes = self._find_nodes_without_dependencies(graph, remaining_nodes)

            if not current_level_nodes:
                # Circular dependency or other issue, place remaining nodes at current level
                current_level_nodes = list(remaining_nodes)

            # Assign level to these nodes
            for node in current_level_nodes:
                levels[node] = current_level
                remaining_nodes.remove(node)

            current_level += 1

        return levels

    def _find_nodes_without_dependencies(self, graph, remaining_nodes):
        """Find nodes that have no dependencies in the remaining nodes."""
        nodes_without_deps = []
        for node in remaining_nodes:
            predecessors = set(graph.predecessors(node))
            if not predecessors or predecessors.isdisjoint(remaining_nodes):
                nodes_without_deps.append(node)
        return nodes_without_deps

    def _group_nodes_by_level(self, levels):
        """Group nodes by their dependency level."""
        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
        return level_groups

    def _position_nodes_in_levels(self, level_groups):
        """Position nodes within their levels."""
        pos = {}
        for level, nodes_in_level in level_groups.items():
            for i, node in enumerate(nodes_in_level):
                # Spread parallel nodes vertically to show they can run in parallel
                y_pos = i - (len(nodes_in_level) - 1) / 2  # Center around 0
                pos[node] = (level, -y_pos)  # Negative y to match the original coordinate system
        return pos

    def _create_simple_layout(self, nodes, max_row_length, max_nodes_in_row):
        """Fallback to simple row-based layout."""
        pos = {}
        current_row = []
        current_row_length = 0
        row_index = 0
        left_to_right = True

        for node in nodes:
            node_length = len(node)
            if (current_row_length + node_length > max_row_length) or (len(current_row) >= max_nodes_in_row):
                self._position_row_nodes(pos, current_row, row_index, left_to_right)
                current_row = []
                current_row_length = 0
                row_index += 1
                left_to_right = not left_to_right

            current_row.append(node)
            current_row_length += node_length

        # Handle the last row
        self._position_row_nodes(pos, current_row, row_index, left_to_right)
        return pos

    def _position_row_nodes(self, pos, row_nodes, row_index, left_to_right):
        """Position nodes in a row, either left-to-right or right-to-left."""
        nodes_to_position = row_nodes if left_to_right else reversed(row_nodes)
        for i, row_node in enumerate(nodes_to_position):
            pos[row_node] = (i, -row_index)

    def _post_process_grouping(self, nodes, pos, pipeline):
        """Re-arrange the node's positions to fit more complex connections."""
        for node_name in nodes:
            predecessors = self._get_predecessors_by_step_info(pipeline, node_name)
            if predecessors is not None and len(predecessors) > 1:
                pos = self._shift_row_down(pos, node_name)
        return pos

    def _shift_row_down(self, pos, split_key):
        """Shift a node and subsequent nodes down by one row."""
        part1 = {}
        part2 = {}
        found_split_key = False

        for key, value in pos.items():
            if found_split_key:
                part2[key] = value
            else:
                if key == split_key:
                    found_split_key = True
                    part2[key] = value
                else:
                    part1[key] = value

        for key in part2:
            if key != split_key:
                new_tuple = (part2[key][0], part2[key][1] - 1)
                part2[key] = new_tuple

        part1.update(part2)
        return part1

    def _wrap_text(self, text, max_length=20):
        """Add line breaks to text if it exceeds max_length."""
        if len(text) <= max_length:
            return text

        wrapped_lines = textwrap.wrap(text, width=max_length)
        return "<br>".join(wrapped_lines)

    def _get_context_by_step_info(self, pipeline, step_name):
        """Get the context status of a step."""
        for _, step in pipeline.steps.items():
            if step.name == step_name:
                return step.context.status
        return None

    def _get_predecessors_by_step_info(self, pipeline, step_name):
        """Get predecessors of a step."""
        for _, step in pipeline.steps.items():
            if step.name == step_name:
                return step._predecessors
        return None
