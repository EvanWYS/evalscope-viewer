"""
Adapters Module

This module contains adapters for different evaluation frameworks.
Each adapter implements the BaseAdapter interface to convert framework-specific
output to the standard data models.

Current implementations:
- EvalScopeAdapter: For evalscope framework

Future implementations:
- LMHarnessAdapter: For lm-evaluation-harness
- OpenCompassAdapter: For OpenCompass
- Custom adapters: User-defined adapters
"""

from .base import BaseAdapter
from .evalscope import EvalScopeAdapter

# Registry of available adapters
ADAPTER_REGISTRY = {
    "evalscope": EvalScopeAdapter,
    # Future: "lm-harness": LMHarnessAdapter,
    # Future: "opencompass": OpenCompassAdapter,
}


def get_adapter(framework: str) -> type:
    """
    Get adapter class by framework name

    Args:
        framework: Framework name (e.g., "evalscope")

    Returns:
        Adapter class

    Raises:
        ValueError: If framework is not supported
    """
    if framework not in ADAPTER_REGISTRY:
        available = ", ".join(ADAPTER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported framework: {framework}. Available: {available}"
        )
    return ADAPTER_REGISTRY[framework]


__all__ = ["BaseAdapter", "EvalScopeAdapter", "get_adapter", "ADAPTER_REGISTRY"]
