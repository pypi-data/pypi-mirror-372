"""
The `PipelinePayloadBuilder` class is responsible for constructing standardized data payloads for each stage of the reasoning pipeline. As the system progresses through parsing, retrieval, graph creation, synthesis, and inference, this builder gathers key metrics and results from each stage. For example, it captures the number of entities identified during parsing, the number of documents retrieved, and the number of nodes in the dependency graph. These payloads serve as structured records of each stage's output, ensuring that data is consistently formatted and easily accessible for subsequent processing and analysis.
"""
from typing import Dict, Any

from .. import constants


class PipelinePayloadBuilder:
    def build_parse_payload(self, parsed) -> Dict[str, Any]:
        """Build payload for parse stage completion."""
        entities_count = getattr(parsed, "entities_count",
                               len(getattr(parsed, "entities", [])) if hasattr(parsed, "entities") else 0)
        constraints_count = getattr(parsed, "constraints_count",
                                   len(getattr(parsed, "constraints", [])) if hasattr(parsed, "constraints") else 0)

        return {
            "confidence": getattr(parsed, constants.CONFIDENCE_ATTR_PARSING, 0),
            "entities_count": entities_count,
            "constraints_count": constraints_count,
        }

    def build_retrieve_payload(self, retrieval) -> Dict[str, Any]:
        """Build payload for retrieve stage completion."""
        documents = getattr(retrieval, "documents", []) or []
        return {
            "confidence": getattr(retrieval, constants.CONFIDENCE_ATTR_RETRIEVAL, getattr(retrieval, constants.CONFIDENCE_ATTR_GENERIC, 0)),
            "documents_count": len(documents),
        }

    def build_graph_payload(self, graph) -> Dict[str, Any]:
        """Build payload for graph stage completion."""
        nodes = getattr(graph, "nodes", []) or []
        edges = getattr(graph, "edges", []) or []
        return {
            "confidence": getattr(graph, constants.CONFIDENCE_ATTR_GRAPH, getattr(graph, constants.CONFIDENCE_ATTR_GENERIC, 0)),
            "nodes_count": getattr(graph, "nodes_count", len(nodes)),
            "edges_count": getattr(graph, "edges_count", len(edges)),
        }

    def build_synthesize_payload(self, program) -> Dict[str, Any]:
        """Build payload for synthesize stage completion."""
        code = getattr(program, "program_code", "") or ""
        variables = getattr(program, "variables", []) or []
        return {
            "confidence": getattr(program, constants.CONFIDENCE_ATTR_GENERIC, 0),
            "lines_count": len(code.split("\n")) if code else 0,
            "variables_count": getattr(program, "variables_count", len(variables)),
            "validation_status": getattr(program, "validation_status", None),
        }

    def build_infer_payload(self, inference) -> Dict[str, Any]:
        """Build payload for infer stage completion."""
        posterior_samples = getattr(inference, "posterior_samples", {}) or {}
        inference_status = getattr(inference, "inference_status", None)
        status_name = getattr(inference_status, "name", str(inference_status)) if inference_status else None

        return {
            "confidence": getattr(inference, constants.CONFIDENCE_ATTR_GENERIC, 0),
            "samples_count": getattr(inference, "num_samples", 0),
            "parameters_count": len(posterior_samples),
            "inference_status": status_name,
        }