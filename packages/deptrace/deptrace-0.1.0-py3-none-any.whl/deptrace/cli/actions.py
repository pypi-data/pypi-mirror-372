from enum import Enum


class AnalysisAction(Enum):
    """Types of analysis that can be performed."""

    DEPENDENCIES = "dependencies"
    CALL_TREE = "call-tree"
