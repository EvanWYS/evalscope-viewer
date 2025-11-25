"""
ETL Core Module

This module provides framework-agnostic abstractions for evaluation data processing.
Future adapters for different evaluation frameworks should implement these interfaces.
"""

from .schema import SCHEMA_VERSION
from .models import (
    StandardRunMeta,
    StandardBenchmarkResult,
    StandardMetric,
    StandardSample,
)
from .builder import DataBuilder

__all__ = [
    "SCHEMA_VERSION",
    "StandardRunMeta",
    "StandardBenchmarkResult",
    "StandardMetric",
    "StandardSample",
    "DataBuilder",
]
