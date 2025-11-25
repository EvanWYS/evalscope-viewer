"""
Base Adapter

Abstract base class that defines the interface all adapters must implement.
This ensures consistency across different evaluation framework adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from pathlib import Path

from ..core.models import (
    StandardRunMeta,
    StandardBenchmarkResult,
    StandardSample,
)


class BaseAdapter(ABC):
    """
    Abstract base class for evaluation framework adapters.

    Each adapter is responsible for:
    1. Reading framework-specific raw output files
    2. Parsing and extracting relevant data
    3. Converting to standard data models
    """

    def __init__(self, raw_dir: str):
        """
        Initialize adapter with raw output directory

        Args:
            raw_dir: Path to framework's raw output directory
        """
        self.raw_dir = Path(raw_dir)
        if not self.raw_dir.exists():
            raise FileNotFoundError(f"Raw directory not found: {raw_dir}")

    @abstractmethod
    def extract_meta(self) -> StandardRunMeta:
        """
        Extract run metadata from raw output

        Returns:
            StandardRunMeta: Standardized run metadata

        Raises:
            Exception: If metadata extraction fails
        """
        pass

    @abstractmethod
    def extract_results(self) -> List[StandardBenchmarkResult]:
        """
        Extract benchmark evaluation results from raw output

        Returns:
            List[StandardBenchmarkResult]: List of standardized benchmark results

        Raises:
            Exception: If results extraction fails
        """
        pass

    @abstractmethod
    def extract_samples(
        self, dataset: str, limit: int = 100
    ) -> List[StandardSample]:
        """
        Extract sample predictions for a specific dataset

        Args:
            dataset: Dataset name
            limit: Maximum number of samples to extract (default: 100)

        Returns:
            List[StandardSample]: List of standardized samples

        Raises:
            Exception: If sample extraction fails
        """
        pass

    def extract_all_samples(
        self, limit: int = 100
    ) -> Dict[str, List[StandardSample]]:
        """
        Extract samples for all datasets

        Args:
            limit: Maximum number of samples per dataset (default: 100)

        Returns:
            Dict[str, List[StandardSample]]: Dictionary mapping dataset name to samples

        Raises:
            Exception: If sample extraction fails
        """
        meta = self.extract_meta()
        samples_by_dataset = {}
        for dataset in meta.datasets:
            try:
                samples = self.extract_samples(dataset, limit)
                samples_by_dataset[dataset] = samples
            except Exception as e:
                print(f"Warning: Failed to extract samples for {dataset}: {e}")
                samples_by_dataset[dataset] = []
        return samples_by_dataset

    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Get the name of the evaluation framework

        Returns:
            str: Framework name (e.g., "evalscope")
        """
        pass

    @abstractmethod
    def get_framework_version(self) -> str:
        """
        Get the version of the evaluation framework

        Returns:
            str: Framework version (e.g., "1.0.0")
        """
        pass
