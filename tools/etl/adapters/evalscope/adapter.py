"""
EvalScope Adapter Implementation

Converts evalscope-specific output format to standard data models.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

from ...core.models import (
    StandardRunMeta,
    StandardBenchmarkResult,
    StandardSample,
    StandardModel,
    StandardCategory,
    StandardSubset,
)
from ..base import BaseAdapter


class EvalScopeAdapter(BaseAdapter):
    """
    Adapter for evalscope evaluation framework.

    Expected directory structure:
    raw_dir/
        ├── configs/
        │   └── task_config_*.yaml
        ├── logs/
        │   └── eval_log.log
        ├── predictions/
        │   └── <model_name>/
        │       └── <dataset_name>.jsonl
        ├── reviews/
        │   └── <model_name>/
        │       └── <dataset_name>.jsonl
        └── reports/
            └── <model_name>/
                └── <dataset_name>.json
    """

    def __init__(self, raw_dir: str):
        super().__init__(raw_dir)
        self._config = None
        self._run_id = None

    def get_framework_name(self) -> str:
        return "evalscope"

    def get_framework_version(self) -> str:
        # Try to detect version from config or use default
        return "1.0.0"

    def _load_config(self) -> dict:
        """Load evalscope configuration file"""
        if self._config is not None:
            return self._config

        configs_dir = self.raw_dir / "configs"
        if not configs_dir.exists():
            raise FileNotFoundError(f"Configs directory not found: {configs_dir}")

        # Find first task_config_*.yaml file
        config_files = list(configs_dir.glob("task_config_*.yaml"))
        if not config_files:
            raise FileNotFoundError(f"No task_config_*.yaml found in {configs_dir}")

        with open(config_files[0], "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        return self._config

    def _generate_run_id(self) -> str:
        """Generate unique run_id from timestamp and model name"""
        if self._run_id is not None:
            return self._run_id

        config = self._load_config()
        timestamp = self.raw_dir.name
        model_id = config.get("model", {}).get("model_id", "unknown")

        # Create short hash of model_id
        model_hash = hashlib.md5(model_id.encode()).hexdigest()[:8]
        self._run_id = f"run_{timestamp}_{model_hash}"

        return self._run_id

    def _parse_log_timestamps(self) -> tuple[str, str, float]:
        """
        Parse start and end timestamps from log file

        Returns:
            Tuple of (start_time, end_time, duration_seconds)
        """
        log_file = self.raw_dir / "logs" / "eval_log.log"
        if not log_file.exists():
            # Return defaults if log doesn't exist
            return (
                datetime.utcnow().isoformat() + "Z",
                datetime.utcnow().isoformat() + "Z",
                0.0,
            )

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                raise ValueError("Log file is empty")

            # Parse first and last timestamp
            first_line = lines[0]
            last_line = lines[-1]

            # Expected format: "2025-11-24 14:30:25,123 - INFO - ..."
            start_time_str = first_line.split(" - ")[0].strip()
            end_time_str = last_line.split(" - ")[0].strip()

            # Convert to ISO format
            start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S,%f")
            end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S,%f")

            duration = (end_dt - start_dt).total_seconds()

            return (
                start_dt.isoformat() + "Z",
                end_dt.isoformat() + "Z",
                duration,
            )
        except Exception as e:
            print(f"Warning: Failed to parse log timestamps: {e}")
            return (
                datetime.utcnow().isoformat() + "Z",
                datetime.utcnow().isoformat() + "Z",
                0.0,
            )

    def extract_meta(self) -> StandardRunMeta:
        """Extract run metadata from evalscope config"""
        config = self._load_config()
        run_id = self._generate_run_id()
        timestamp = self.raw_dir.name

        # Parse model information
        model_config = config.get("model", {})
        model = StandardModel(
            name=model_config.get("model_id", "unknown"),
            revision=model_config.get("model_revision", "master"),
            type=config.get("eval_type", "unknown"),
            metadata=model_config.get("generation_config", {}),
        )

        # Parse eval configuration
        eval_config = config.get("eval", {})
        datasets = eval_config.get("datasets", [])

        # Parse timestamps from log
        start_time, end_time, duration = self._parse_log_timestamps()

        # Build standard meta
        meta = StandardRunMeta(
            run_id=run_id,
            timestamp=timestamp,
            framework=self.get_framework_name(),
            framework_version=self.get_framework_version(),
            model=model,
            datasets=datasets,
            config={
                "eval_batch_size": eval_config.get("eval_batch_size", 1),
                "seed": eval_config.get("seed"),
                "limit": eval_config.get("limit"),
                "generation_config": model_config.get("generation_config", {}),
            },
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            status="completed",
            tags=[],
            environment={},
        )

        return meta

    def extract_results(self) -> List[StandardBenchmarkResult]:
        """Extract benchmark results from evalscope reports"""
        reports_dir = self.raw_dir / "reports"
        if not reports_dir.exists():
            raise FileNotFoundError(f"Reports directory not found: {reports_dir}")

        results = []

        # Find all report JSON files
        for report_file in reports_dir.rglob("*.json"):
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)

                result = self._parse_report(report)
                results.append(result)
            except Exception as e:
                print(f"Warning: Failed to parse report {report_file}: {e}")
                continue

        return results

    def _parse_report(self, report: dict) -> StandardBenchmarkResult:
        """Parse a single evalscope report JSON"""
        dataset = report.get("dataset_name", "unknown")
        dataset_pretty_name = report.get("dataset_pretty_name", dataset)
        overall_score = report.get("score", 0.0)

        # Parse metrics
        metrics = {}
        for metric in report.get("metrics", []):
            metric_name = metric.get("name", "unknown")
            metrics[metric_name] = {
                "score": metric.get("score", 0.0),
                "macro_score": metric.get("macro_score", 0.0),
                "num_samples": metric.get("num", 0),
            }

        # Parse categories
        categories = []
        if report.get("metrics"):
            primary_metric = report["metrics"][0]
            for cat in primary_metric.get("categories", []):
                category = self._parse_category(cat)
                categories.append(category)

        result = StandardBenchmarkResult(
            dataset=dataset,
            dataset_pretty_name=dataset_pretty_name,
            metrics=metrics,
            overall_score=overall_score,
            categories=categories,
            metadata={},
        )

        return result

    def _parse_category(self, cat_data: dict) -> StandardCategory:
        """Parse category data from evalscope report"""
        name = cat_data.get("name", ["unknown"])
        if not isinstance(name, list):
            name = [name]

        subsets = []
        for subset_data in cat_data.get("subsets", []):
            subset = StandardSubset(
                name=subset_data.get("name", "unknown"),
                score=subset_data.get("score", 0.0),
                num=subset_data.get("num", 0),
                metadata={},
            )
            subsets.append(subset)

        category = StandardCategory(
            name=name,
            score=cat_data.get("score", 0.0),
            macro_score=cat_data.get("macro_score", 0.0),
            num_samples=cat_data.get("num", 0),
            subsets=subsets,
        )

        return category

    def extract_samples(
        self, dataset: str, limit: int = 100
    ) -> List[StandardSample]:
        """Extract samples for a specific dataset"""
        predictions_dir = self.raw_dir / "predictions"
        reviews_dir = self.raw_dir / "reviews"

        # Find prediction and review files
        pred_files = list(predictions_dir.rglob(f"{dataset}.jsonl"))
        review_files = list(reviews_dir.rglob(f"{dataset}.jsonl"))

        if not pred_files:
            raise FileNotFoundError(f"No predictions found for dataset: {dataset}")

        # Load predictions
        predictions = self._load_jsonl(pred_files[0])

        # Load reviews (optional)
        reviews_dict = {}
        if review_files:
            reviews = self._load_jsonl(review_files[0])
            reviews_dict = {r["id"]: r for r in reviews}

        # Merge and convert to standard format
        samples = []
        for pred in predictions[:limit]:
            sample_id = pred.get("id", 0)
            review = reviews_dict.get(sample_id, {})

            sample = StandardSample(
                id=sample_id,
                input=pred.get("input", ""),
                target=pred.get("target", ""),
                prediction=pred.get("prediction", ""),
                scores=review.get("sample_scores", {}),
                metadata={
                    **pred.get("metadata", {}),
                    **review.get("metadata", {}),
                },
                choices=pred.get("choices"),
            )
            samples.append(sample)

        return samples

    def _load_jsonl(self, file_path: Path) -> List[dict]:
        """Load JSONL file"""
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        return data
