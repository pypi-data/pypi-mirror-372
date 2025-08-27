# --- Constants for repeated strings and configurations ---
DEFAULT_CONFIDENCE = 0.8
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
PARTIAL_SUCCESS_CONFIDENCE = 0.5
HIGH_CONFIDENCE_THRESHOLD = 0.8
MODERATE_CONFIDENCE_THRESHOLD = 0.6

# Stage names for consistency
STAGE_PARSE = "parse"
STAGE_RETRIEVE = "retrieve"
STAGE_GRAPH = "graph"
STAGE_SYNTHESIZE = "synthesize"
STAGE_INFER = "infer"

# Confidence attribute names
CONFIDENCE_ATTR_PARSING = "parsing_confidence"
CONFIDENCE_ATTR_RETRIEVAL = "retrieval_confidence"
CONFIDENCE_ATTR_GRAPH = "graph_confidence"
CONFIDENCE_ATTR_GENERIC = "confidence"