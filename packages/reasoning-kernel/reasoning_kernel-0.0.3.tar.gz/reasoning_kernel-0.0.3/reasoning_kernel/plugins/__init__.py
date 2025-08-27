"""
MSA Plugins Package - Complete 5-Stage Architecture
===================================================

Complete MSA 5-stage reasoning pipeline plugins with Semantic Kernel integration.

Stage 1: ParsingPlugin - Transform vignettes into structured constraints
Stage 2: KnowledgeRetrievalPlugin - Retrieve relevant background knowledge
Stage 3: GraphPlugin - Generate and analyze conceptual dependency graphs
Stage 4: ModelSynthesisPlugin - Generate probabilistic programs from graphs
Stage 5: ProbabilisticReasoningPlugin - Perform Bayesian inference and uncertainty quantification

Additional: EvaluationPlugin - Evaluate MSA reasoning results with comprehensive metrics
"""

from .evaluation_plugin import EvaluationPlugin, create_evaluation_plugin
from .graph_plugin import GraphPlugin, create_graph_plugin
from .knowledge_retrieval_plugin import (
    KnowledgeRetrievalPlugin,
    create_knowledge_retrieval_plugin,
)
from .model_synthesis_plugin import ModelSynthesisPlugin, create_model_synthesis_plugin
from .parsing_plugin import ParsingPlugin, create_parsing_plugin
from .probabilistic_reasoning_plugin import (
    ProbabilisticReasoningPlugin,
    create_probabilistic_reasoning_plugin,
)

# Import legacy plugins for backwards compatibility
from .inference_plugin import InferencePlugin, create_inference_plugin
from .knowledge_plugin import KnowledgePlugin, create_knowledge_plugin


__all__ = [
    # Core MSA Plugin Classes
    "EvaluationPlugin",
    "GraphPlugin",
    "KnowledgeRetrievalPlugin",
    "ModelSynthesisPlugin",
    "ParsingPlugin",
    "ProbabilisticReasoningPlugin",
    # Factory Functions
    "create_evaluation_plugin",
    "create_graph_plugin",
    "create_knowledge_retrieval_plugin",
    "create_model_synthesis_plugin",
    "create_parsing_plugin",
    "create_probabilistic_reasoning_plugin",
    # Legacy Plugin Support
    "InferencePlugin",
    "create_inference_plugin",
    "KnowledgePlugin",
    "create_knowledge_plugin",
]
