"""
Data Builder

Unified logic for building static JSON files from standard data models.
This layer is framework-agnostic and works with any adapter.
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from .schema import SCHEMA_VERSION
from .models import (
    StandardRunMeta,
    StandardBenchmarkResult,
    StandardSample,
    StandardIndexEntry,
)


class DataBuilder:
    """
    Builds static JSON files from standard data models.
    This class is framework-agnostic and works with any adapter output.
    """

    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Output directory for static JSON files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_meta(self, meta: StandardRunMeta) -> Path:
        """
        Build meta.json for a run

        Args:
            meta: Standard run metadata

        Returns:
            Path to the created meta.json file
        """
        run_dir = self.output_dir / "runs" / meta.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        meta_data = meta.to_dict()
        meta_data["schema_version"] = SCHEMA_VERSION

        meta_path = run_dir / "meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)

        return meta_path

    def build_eval_summary(
        self, run_id: str, results: List[StandardBenchmarkResult]
    ) -> Path:
        """
        Build eval_summary.json for a run

        Args:
            run_id: Run identifier
            results: List of standard benchmark results

        Returns:
            Path to the created eval_summary.json file
        """
        run_dir = self.output_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Calculate overall statistics
        total_samples = sum(
            list(r.metrics.values())[0].get("num_samples", 0) for r in results
        )
        avg_score = (
            sum(r.overall_score for r in results) / len(results) if results else 0.0
        )

        summary_data = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "datasets": [r.to_dict() for r in results],
            "overall": {
                "avg_score": avg_score,
                "total_samples": total_samples,
            },
        }

        summary_path = run_dir / "eval_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        return summary_path

    def build_samples(
        self, run_id: str, samples_by_dataset: Dict[str, List[StandardSample]]
    ) -> Dict[str, Path]:
        """
        Build samples JSONL files for each dataset

        Args:
            run_id: Run identifier
            samples_by_dataset: Dictionary mapping dataset name to list of samples

        Returns:
            Dictionary mapping dataset name to JSONL file path
        """
        samples_dir = self.output_dir / "runs" / run_id / "samples"
        samples_dir.mkdir(parents=True, exist_ok=True)

        created_files = {}
        for dataset_name, samples in samples_by_dataset.items():
            sample_path = samples_dir / f"{dataset_name}_head.jsonl"
            with open(sample_path, "w", encoding="utf-8") as f:
                for sample in samples:
                    json.dump(sample.to_dict(), f, ensure_ascii=False)
                    f.write("\n")
            created_files[dataset_name] = sample_path

        return created_files

    def build_index(self, entries: List[StandardIndexEntry]) -> Path:
        """
        Build index.json with all runs

        Args:
            entries: List of index entries

        Returns:
            Path to the created index.json file
        """
        index_data = {
            "runs": [entry.to_dict() for entry in entries],
            "total": len(entries),
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

        index_path = self.output_dir / "index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        return index_path
