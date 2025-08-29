"""
GraphPlugin - Stage 3 of the Reasoning Kernel
==============================================

Generate and analyze conceptual dependency graphs from constraints.
Handles graph construction, analysis, and visualization support.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

try:
    from semantic_kernel.functions import kernel_function
except Exception:
    # semantic_kernel is optional for import-time; provide type stubs
    def kernel_function(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


try:
    import structlog

    logger = structlog.get_logger(__name__)
except Exception:
    # structlog is optional in some environments; fall back to stdlib logging
    import logging

    logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the dependency graph"""

    VARIABLE = "variable"
    CONSTRAINT = "constraint"
    PARAMETER = "parameter"
    OBSERVATION = "observation"


class EdgeType(Enum):
    """Types of edges in the dependency graph"""

    DEPENDS_ON = "depends_on"
    INFLUENCES = "influences"
    EQUALS = "equals"
    CONSTRAINS = "constrains"


@dataclass
class GraphNode:
    """A node in the dependency graph"""

    id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any]


@dataclass
class GraphEdge:
    """An edge in the dependency graph"""

    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    properties: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class GraphAnalysis:
    """Analysis results for a dependency graph"""

    node_count: int
    edge_count: int
    connected_components: int
    cycles: List[List[str]]
    critical_path: List[str]
    complexity_score: float


@dataclass
class GraphResult:
    """Result from graph construction and analysis"""

    success: bool
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    analysis: GraphAnalysis
    metadata: Dict[str, Any]
    error: Optional[str] = None


class GraphPlugin:
    """
    Stage 3 Plugin: Generate and analyze conceptual dependency graphs.

    This plugin constructs dependency graphs from parsed constraints and
    performs structural analysis to identify relationships and dependencies.
    """

    def __init__(self):
        """Initialize the graph plugin"""
        self.node_id_counter = 0

    @kernel_function(
        description="Build dependency graph from constraints", name="build_graph"
    )
    async def build_graph(self, constraints: str, variables: str = "") -> str:
        """
        Build a dependency graph from constraints and variables.

        Args:
            constraints: JSON string of parsed constraints
            variables: Optional JSON string of variables

        Returns:
            JSON string containing the constructed graph and analysis
        """
        try:
            constraints_data = (
                json.loads(constraints) if isinstance(constraints, str) else constraints
            )
            variables_data = (
                json.loads(variables)
                if variables and isinstance(variables, str)
                else []
            )

            result = await self._build_dependency_graph(
                constraints_data, variables_data
            )

            return json.dumps(
                {
                    "success": result.success,
                    "nodes": [
                        {
                            "id": node.id,
                            "type": node.node_type.value,
                            "label": node.label,
                            "properties": node.properties,
                        }
                        for node in result.nodes
                    ],
                    "edges": [
                        {
                            "source": edge.source,
                            "target": edge.target,
                            "type": edge.edge_type.value,
                            "weight": edge.weight,
                            "properties": edge.properties,
                        }
                        for edge in result.edges
                    ],
                    "analysis": {
                        "node_count": result.analysis.node_count,
                        "edge_count": result.analysis.edge_count,
                        "connected_components": result.analysis.connected_components,
                        "cycles": result.analysis.cycles,
                        "critical_path": result.analysis.critical_path,
                        "complexity_score": result.analysis.complexity_score,
                    },
                    "metadata": result.metadata,
                    "error": result.error,
                }
            )

        except Exception as e:
            logger.error(f"Error building graph: {e}")
            return json.dumps(
                {
                    "success": False,
                    "nodes": [],
                    "edges": [],
                    "analysis": self._default_analysis(),
                    "metadata": {},
                    "error": str(e),
                }
            )

    async def _build_dependency_graph(
        self, constraints: List[Dict[str, Any]], variables: List[str]
    ) -> GraphResult:
        """Internal method to build dependency graph"""
        try:
            nodes = []
            edges = []

            # Create nodes for variables
            for variable in variables:
                node = GraphNode(
                    id=self._get_node_id(variable),
                    node_type=NodeType.VARIABLE,
                    label=variable,
                    properties={"name": variable},
                )
                nodes.append(node)

            # Create nodes and edges for constraints
            for constraint in constraints:
                constraint_id = self._get_node_id(
                    f"constraint_{constraint.get('type', 'unknown')}"
                )

                # Create constraint node
                constraint_node = GraphNode(
                    id=constraint_id,
                    node_type=NodeType.CONSTRAINT,
                    label=constraint.get("expression", ""),
                    properties={
                        "type": constraint.get("type"),
                        "expression": constraint.get("expression"),
                        "confidence": constraint.get("confidence", 0.8),
                    },
                )
                nodes.append(constraint_node)

                # Create edges from constraint to involved variables
                constraint_variables = constraint.get("variables", [])
                for var in constraint_variables:
                    var_id = self._get_node_id(var)

                    # Add variable node if not exists
                    if not any(node.id == var_id for node in nodes):
                        var_node = GraphNode(
                            id=var_id,
                            node_type=NodeType.VARIABLE,
                            label=var,
                            properties={"name": var},
                        )
                        nodes.append(var_node)

                    # Add edge from constraint to variable
                    edge = GraphEdge(
                        source=constraint_id,
                        target=var_id,
                        edge_type=EdgeType.CONSTRAINS,
                        weight=constraint.get("confidence", 0.8),
                    )
                    edges.append(edge)

            # Add dependency edges between variables
            self._add_variable_dependencies(nodes, edges, constraints)

            # Perform graph analysis
            analysis = self._analyze_graph(nodes, edges)

            metadata = {
                "construction_timestamp": "2025-08-25T11:30:00Z",
                "total_variables": len(variables),
                "total_constraints": len(constraints),
            }

            return GraphResult(
                success=True,
                nodes=nodes,
                edges=edges,
                analysis=analysis,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error in _build_dependency_graph: {e}")
            return GraphResult(
                success=False,
                nodes=[],
                edges=[],
                analysis=self._default_analysis(),
                metadata={},
                error=str(e),
            )

    def _get_node_id(self, name: str) -> str:
        """Generate unique node ID"""
        self.node_id_counter += 1
        return f"{name}_{self.node_id_counter}"

    def _add_variable_dependencies(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        constraints: List[Dict[str, Any]],
    ):
        """Add dependency edges between variables based on constraints"""

        # Group constraints by type to identify dependencies
        for constraint in constraints:
            constraint_type = constraint.get("type")
            variables = constraint.get("variables", [])

            if len(variables) >= 2:
                # For equality constraints, variables depend on each other
                if constraint_type == "equality":
                    var1, var2 = variables[0], variables[1]
                    var1_id = next(
                        (node.id for node in nodes if node.label == var1), None
                    )
                    var2_id = next(
                        (node.id for node in nodes if node.label == var2), None
                    )

                    if var1_id and var2_id:
                        # Add bidirectional dependency
                        edges.append(GraphEdge(var1_id, var2_id, EdgeType.EQUALS))
                        edges.append(GraphEdge(var2_id, var1_id, EdgeType.EQUALS))

                # For causal constraints, first variable influences second
                elif constraint_type == "causal":
                    var1, var2 = variables[0], variables[1]
                    var1_id = next(
                        (node.id for node in nodes if node.label == var1), None
                    )
                    var2_id = next(
                        (node.id for node in nodes if node.label == var2), None
                    )

                    if var1_id and var2_id:
                        edges.append(GraphEdge(var1_id, var2_id, EdgeType.INFLUENCES))

    def _analyze_graph(
        self, nodes: List[GraphNode], edges: List[GraphEdge]
    ) -> GraphAnalysis:
        """Analyze graph structure and compute metrics"""
        node_count = len(nodes)
        edge_count = len(edges)

        # Build adjacency list for analysis
        adjacency = {}
        for node in nodes:
            adjacency[node.id] = []

        for edge in edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge.target)

        # Count connected components (simplified)
        visited = set()
        components = 0

        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                dfs(neighbor)

        for node in nodes:
            if node.id not in visited:
                dfs(node.id)
                components += 1

        # Detect cycles (simplified DFS approach)
        cycles = self._detect_cycles(adjacency)

        # Find critical path (longest path)
        critical_path = self._find_critical_path(nodes, edges)

        # Compute complexity score
        complexity_score = self._compute_complexity(node_count, edge_count, len(cycles))

        return GraphAnalysis(
            node_count=node_count,
            edge_count=edge_count,
            connected_components=components,
            cycles=cycles,
            critical_path=critical_path,
            complexity_score=complexity_score,
        )

    def _detect_cycles(self, adjacency: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adjacency.get(node, []):
                dfs(neighbor, path.copy())

            rec_stack.remove(node)

        for node in adjacency:
            if node not in visited:
                dfs(node, [])

        return cycles[:5]  # Return up to 5 cycles to avoid huge output

    def _find_critical_path(
        self, nodes: List[GraphNode], edges: List[GraphEdge]
    ) -> List[str]:
        """Find the critical path (longest path) in the graph"""
        if not nodes:
            return []

        # Simple approach: find the longest chain
        adjacency = {}
        for node in nodes:
            adjacency[node.id] = []

        for edge in edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge.target)

        longest_path = []

        def dfs(node, current_path):
            nonlocal longest_path

            if len(current_path) > len(longest_path):
                longest_path = current_path.copy()

            for neighbor in adjacency.get(node, []):
                if neighbor not in current_path:  # Avoid cycles
                    dfs(neighbor, current_path + [neighbor])

        # Try starting from each node
        for node in nodes:
            dfs(node.id, [node.id])

        # Convert IDs back to labels
        id_to_label = {node.id: node.label for node in nodes}
        return [
            id_to_label[node_id] for node_id in longest_path if node_id in id_to_label
        ]

    def _compute_complexity(
        self, node_count: int, edge_count: int, cycle_count: int
    ) -> float:
        """Compute graph complexity score"""
        if node_count == 0:
            return 0.0

        # Normalize metrics
        density = (
            edge_count / (node_count * (node_count - 1) / 2) if node_count > 1 else 0
        )
        cycle_factor = min(cycle_count / node_count, 1.0)

        # Combine into complexity score
        complexity = density * 0.5 + cycle_factor * 0.3 + (node_count / 20) * 0.2
        return min(complexity, 1.0)

    def _default_analysis(self) -> GraphAnalysis:
        """Return default analysis when graph construction fails"""
        return GraphAnalysis(
            node_count=0,
            edge_count=0,
            connected_components=0,
            cycles=[],
            critical_path=[],
            complexity_score=0.0,
        )

    @kernel_function(
        description="Analyze graph structure and compute metrics", name="analyze_graph"
    )
    async def analyze_graph(self, graph_data: str) -> str:
        """Analyze graph structure"""
        try:
            graph = (
                json.loads(graph_data) if isinstance(graph_data, str) else graph_data
            )

            # Reconstruct nodes and edges from JSON data
            nodes = [
                GraphNode(
                    id=node_data["id"],
                    node_type=NodeType(node_data["type"]),
                    label=node_data["label"],
                    properties=node_data.get("properties", {}),
                )
                for node_data in graph.get("nodes", [])
            ]

            edges = [
                GraphEdge(
                    source=edge_data["source"],
                    target=edge_data["target"],
                    edge_type=EdgeType(edge_data["type"]),
                    weight=edge_data.get("weight", 1.0),
                    properties=edge_data.get("properties", {}),
                )
                for edge_data in graph.get("edges", [])
            ]

            analysis = self._analyze_graph(nodes, edges)

            return json.dumps(
                {
                    "node_count": analysis.node_count,
                    "edge_count": analysis.edge_count,
                    "connected_components": analysis.connected_components,
                    "cycles": analysis.cycles,
                    "critical_path": analysis.critical_path,
                    "complexity_score": analysis.complexity_score,
                }
            )

        except Exception as e:
            default_analysis = self._default_analysis()
            return json.dumps(
                {
                    "error": str(e),
                    "node_count": default_analysis.node_count,
                    "edge_count": default_analysis.edge_count,
                    "connected_components": default_analysis.connected_components,
                    "cycles": default_analysis.cycles,
                    "critical_path": default_analysis.critical_path,
                    "complexity_score": default_analysis.complexity_score,
                }
            )


def create_graph_plugin() -> GraphPlugin:
    """Factory function to create a GraphPlugin instance"""
    return GraphPlugin()
