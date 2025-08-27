# fastpluggy/core/view_builer/components/debug_panel.py
import time
import traceback
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Set, Annotated

from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.core.widgets import AbstractWidget


@dataclass
class ComponentNode:
    """Represents a node in the component tree for debugging."""
    name: str
    type_name: str
    obj_id: int
    depth: int
    parent_id: Optional[int] = None
    is_cycle: bool = False
    children: List['ComponentNode'] = None
    attributes: Dict[str, Any] = None
    context: Dict[str, Any] = None
    warnings: List[str] = None

    icon: str = None
    category: str = None
    widget_type: str = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.attributes is None:
            self.attributes = {}
        if self.warnings is None:
            self.warnings = []


class DebugPanelWidget(AbstractWidget):
    """
    A debug panel component that analyzes and displays the component tree structure.
    """
    widget_type = "debug_panel"
    template_name = "debug_tools/widgets/debug/debug_panel.html.j2"

    category = "debug"
    description = "Development tool for analyzing widget hierarchy and detecting issues"
    icon = "bug"

    def __init__(
            self,
            items: Annotated[List[AbstractWidget], InjectDependency],
            title: str = "Component Debug Panel",
            max_depth: int = 10,
            show_attributes: bool = True,
            show_warnings: bool = True,
            show_context: bool = True,
            auto_expand: bool = False,
            **kwargs
    ):
        """
        Initialize the debug panel.

        Args:
            items: List of components to analyze
            title: Panel title
            max_depth: Maximum tree depth to analyze
            show_attributes: Whether to show component attributes
            show_warnings: Whether to show warnings and issues
            auto_expand: Whether to auto-expand all tree nodes
        """
        kwargs['collapsed'] = True
        kwargs['title_css_class'] = 'bg-info text-white'
        kwargs['title_icon'] = 'fas fa-bug me-2'

        super().__init__(**kwargs)
        self.items = items or []
        self.title = title
        self.max_depth = max_depth
        self.show_attributes = show_attributes
        self.show_warnings = show_warnings
        self.show_context = show_context
        self.auto_expand = auto_expand

        # Analysis results
        self.component_tree: List[ComponentNode] = []
        self.stats: Dict[str, Any] = {}
        self.warnings: List[Dict[str, Any]] = []

    def process(self, **kwargs) -> None:
        """Analyze the component tree and prepare debug information."""
        start_time = time.time()

        try:
            # Reset previous analysis
            self.component_tree = []
            self.warnings = []

            # Build tree for each root item, skipping any None returns
            for i, item in enumerate(self.items):
                root_node = self._analyze_component(
                    component=item,
                    name=f"Root[{i}]",
                    depth=0,
                    visited=set(),
                    parent_id=None
                )
                if root_node is not None:
                    self.component_tree.append(root_node)

            # Generate statistics
            analysis_time = time.time() - start_time
            self.stats = self._generate_stats(analysis_time)

        except Exception as e:
            self.warnings.append({
                'type': 'error',
                'message': f"Debug analysis failed: {str(e)}",
                'traceback': traceback.format_exc()
            })

    def is_visible(self):
        from ...config import DebugToolsConfig
        debug_config = DebugToolsConfig()
        return debug_config.show_debug_panel_widget

    def _analyze_component(
            self,
            component: Any,
            name: str,
            depth: int,
            visited: Set[int],
            parent_id: Optional[int]
    ) -> Optional[ComponentNode]:
        """Recursively analyze a component and its children."""
        # 0) Skip the panel itself if encountered
        if isinstance(component, DebugPanelWidget):
            return None

        obj_id = id(component)
        widget_type = getattr(component, 'widget_type', 'unknown')
        icon = getattr(component, 'icon', 'fas fa-cube text-secondary')
        category = getattr(component, 'category', 'unknown')
        class_name = component.__class__.__name__

        # 1) Create the node
        node = ComponentNode(
            name=name,
            type_name=f"{class_name} ({widget_type})",
            obj_id=obj_id,
            depth=depth,
            parent_id=parent_id,
            icon=icon,
            category=category,
            widget_type=widget_type
        )

        # 2) Check for cycles
        if obj_id in visited:
            node.is_cycle = True
            node.warnings.append("Circular reference detected!")
            return node

        # 3) Check depth limit
        if depth > self.max_depth:
            node.warnings.append(f"Maximum depth ({self.max_depth}) exceeded")
            return node

        # 4) Mark as visited
        visited.add(obj_id)

        # 5) Gather attributes & context
        if self.show_attributes:
            node.attributes = self._get_component_attributes(component)

        if self.show_context:
            try:
                node.context = component.get_context()  # assume get_context() returns a dict
            except Exception:
                node.context = {}

        # 6) Analyze children via context‐only logic (skipping any DebugPanelWidget)
        self._analyze_children(component, node, visited, depth)

        # 7) Add deep‐nesting warning if needed
        if depth > 5:
            node.warnings.append(f"Deep nesting (depth: {depth})")

        # 8) Unmark visited before returning
        visited.remove(obj_id)
        return node

    def _analyze_children(
            self,
            component: Any,
            node: ComponentNode,
            visited: Set[int],
            depth: int
    ):
        """
        Analyze child widgets by scanning component.get_context() for any
        AbstractWidget (or list of them). We explicitly skip DebugPanelWidget
        instances so that the panel never re‐enters itself.
        """
        try:
            context_dict = component.get_context() or {}
        except Exception:
            context_dict = {}

        for key, value in context_dict.items():
            # 1) Skip the debug panel if it appears
            if isinstance(value, DebugPanelWidget):
                continue

            # 2) Single widget in context
            if isinstance(value, AbstractWidget):
                candidate = self._analyze_component(
                    component=value,
                    name=f"context[{key}]",
                    depth=depth + 1,
                    visited=visited.copy(),
                    parent_id=node.obj_id
                )
                if candidate is not None:
                    node.children.append(candidate)

            # 3) List of widgets in context
            elif isinstance(value, list):
                for idx, element in enumerate(value):
                    # Skip any DebugPanelWidget inside a list
                    if isinstance(element, DebugPanelWidget):
                        continue
                    if isinstance(element, AbstractWidget):
                        candidate = self._analyze_component(
                            component=element,
                            name=f"context[{key}][{idx}]",
                            depth=depth + 1,
                            visited=visited.copy(),
                            parent_id=node.obj_id
                        )
                        if candidate is not None:
                            node.children.append(candidate)

    def _get_component_attributes(self, component: Any) -> Dict[str, Any]:
        """Extract relevant attributes from a component for debugging."""
        attributes: Dict[str, Any] = {}

        # Common attributes to show
        interesting_attrs = [
            'widget_type', 'title', 'css_class', 'collapsed', 'template_name',
            'col_xs', 'col_sm', 'col_md', 'col_lg', 'col_xl', 'col_xxl'
        ]

        for attr in interesting_attrs:
            value = getattr(component, attr, None)
            if value is not None:
                attributes[attr] = str(value)

        # Special handling for GridItem
        if hasattr(component, 'get_column_classes'):
            try:
                attributes['column_classes'] = component.get_column_classes()
            except Exception:
                attributes['column_classes'] = 'Error getting classes'

        return attributes

    def _generate_stats(self, analysis_time: float) -> Dict[str, Any]:
        """Generate statistics about the component tree."""

        def count_nodes(nodes: List[ComponentNode]) -> int:
            count = len(nodes)
            for node in nodes:
                count += count_nodes(node.children)
            return count

        def max_depth(nodes: List[ComponentNode], current_depth: int = 0) -> int:
            if not nodes:
                return current_depth
            return max(max_depth(node.children, current_depth + 1) for node in nodes)

        def count_cycles(nodes: List[ComponentNode]) -> int:
            count = 0
            for node in nodes:
                if node.is_cycle:
                    count += 1
                count += count_cycles(node.children)
            return count

        def count_warnings(nodes: List[ComponentNode]) -> int:
            count = 0
            for node in nodes:
                count += len(node.warnings)
                count += count_warnings(node.children)
            return count

        total_components = count_nodes(self.component_tree)
        max_tree_depth = max_depth(self.component_tree)
        cycle_count = count_cycles(self.component_tree)
        warning_count = count_warnings(self.component_tree)

        return {
            'total_components': total_components,
            'max_depth': max_tree_depth,
            'cycle_count': cycle_count,
            'warning_count': warning_count,
            'analysis_time_ms': round(analysis_time * 1000, 2),
            'root_components': len(self.component_tree)
        }
