"""
Standard Data Models

Defines Python data classes representing the standard JSON protocol.
These models are framework-agnostic and used by all adapters.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class StandardModel:
    """Standard model information"""
    name: str
    revision: Optional[str] = None
    type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardMetric:
    """Standard metric representation"""
    name: str
    value: float
    num_samples: int
    aggregation: str = "mean"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardSubset:
    """Standard subset (finest granularity)"""
    name: str
    score: float
    num: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardCategory:
    """Standard category breakdown"""
    name: List[str]
    score: float
    macro_score: float
    num_samples: int
    subsets: List[StandardSubset] = field(default_factory=list)


@dataclass
class StandardBenchmarkResult:
    """Standard benchmark evaluation result"""
    dataset: str
    dataset_pretty_name: str
    metrics: Dict[str, Dict[str, Any]]
    overall_score: float
    categories: List[StandardCategory] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert categories to dict format
        result["categories"] = [
            {
                "name": cat.name,
                "score": cat.score,
                "macro_score": cat.macro_score,
                "num_samples": cat.num_samples,
                "subsets": [
                    {"name": s.name, "score": s.score, "num": s.num}
                    for s in cat.subsets
                ],
            }
            for cat in self.categories
        ]
        return result


@dataclass
class StandardRunMeta:
    """Standard run metadata"""
    run_id: str
    timestamp: str
    framework: str
    framework_version: str
    model: StandardModel
    datasets: List[str]
    config: Dict[str, Any]
    start_time: str
    end_time: str
    duration_seconds: float
    status: str
    tags: List[str] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        return result


@dataclass
class StandardSample:
    """Standard sample representation"""
    id: Any
    input: Any
    target: Any
    prediction: Any
    scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    choices: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "id": self.id,
            "input": self.input,
            "target": self.target,
            "prediction": self.prediction,
            "scores": self.scores,
            "metadata": self.metadata,
        }
        if self.choices is not None:
            result["choices"] = self.choices
        return result


@dataclass
class StandardIndexEntry:
    """Standard index entry for a run"""
    run_id: str
    timestamp: str
    framework: str
    model: Dict[str, str]
    datasets: List[str]
    overall_score: Optional[float]
    num_samples: int
    start_time: str
    end_time: str
    duration_seconds: float
    status: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
