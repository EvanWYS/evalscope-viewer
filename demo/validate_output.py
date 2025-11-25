#!/usr/bin/env python3
"""
Validation Script for Generated Data

Validates that the generated standard protocol JSON files
are correct and complete.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


class bcolors:
    """Terminal colors"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def check(condition: bool, message: str):
    """Check a condition and print result"""
    if condition:
        print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} {message}")
        return True
    else:
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} {message}")
        return False


def validate_index(index_path: Path) -> bool:
    """Validate index.json"""
    print(f"\n{bcolors.BOLD}Validating index.json{bcolors.ENDC}")

    if not index_path.exists():
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} File not found: {index_path}")
        return False

    with open(index_path) as f:
        data = json.load(f)

    checks = [
        check("runs" in data, "Has 'runs' field"),
        check("total" in data, "Has 'total' field"),
        check("last_updated" in data, "Has 'last_updated' field"),
        check(len(data["runs"]) == data["total"], "Run count matches total"),
    ]

    if data["runs"]:
        run = data["runs"][0]
        checks.extend([
            check("run_id" in run, "Run has 'run_id'"),
            check("framework" in run, "Run has 'framework'"),
            check("model" in run, "Run has 'model'"),
            check("datasets" in run, "Run has 'datasets'"),
            check("status" in run, "Run has 'status'"),
        ])

    return all(checks)


def validate_meta(meta_path: Path) -> bool:
    """Validate meta.json"""
    print(f"\n{bcolors.BOLD}Validating meta.json{bcolors.ENDC}")

    if not meta_path.exists():
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} File not found: {meta_path}")
        return False

    with open(meta_path) as f:
        data = json.load(f)

    checks = [
        check("schema_version" in data, "Has 'schema_version'"),
        check(data.get("schema_version") == "1.0", "Schema version is 1.0"),
        check("run_id" in data, "Has 'run_id'"),
        check("timestamp" in data, "Has 'timestamp'"),
        check("framework" in data, "Has 'framework'"),
        check("model" in data, "Has 'model'"),
        check("datasets" in data, "Has 'datasets'"),
        check("config" in data, "Has 'config'"),
        check("start_time" in data, "Has 'start_time'"),
        check("end_time" in data, "Has 'end_time'"),
        check("duration_seconds" in data, "Has 'duration_seconds'"),
        check("status" in data, "Has 'status'"),
    ]

    # Validate model structure
    if "model" in data:
        model = data["model"]
        checks.extend([
            check("name" in model, "Model has 'name'"),
            check("revision" in model, "Model has 'revision'"),
            check("type" in model, "Model has 'type'"),
        ])

    return all(checks)


def validate_eval_summary(summary_path: Path) -> bool:
    """Validate eval_summary.json"""
    print(f"\n{bcolors.BOLD}Validating eval_summary.json{bcolors.ENDC}")

    if not summary_path.exists():
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} File not found: {summary_path}")
        return False

    with open(summary_path) as f:
        data = json.load(f)

    checks = [
        check("schema_version" in data, "Has 'schema_version'"),
        check(data.get("schema_version") == "1.0", "Schema version is 1.0"),
        check("run_id" in data, "Has 'run_id'"),
        check("datasets" in data, "Has 'datasets'"),
        check("overall" in data, "Has 'overall'"),
        check(len(data.get("datasets", [])) > 0, "Has at least one dataset"),
    ]

    # Validate dataset structure
    if data.get("datasets"):
        dataset = data["datasets"][0]
        checks.extend([
            check("dataset" in dataset, "Dataset has 'dataset'"),
            check("metrics" in dataset, "Dataset has 'metrics'"),
            check("overall_score" in dataset, "Dataset has 'overall_score'"),
        ])

        # Check for categories (optional but should be present in demo)
        if "categories" in dataset and dataset["categories"]:
            category = dataset["categories"][0]
            checks.extend([
                check("name" in category, "Category has 'name'"),
                check("score" in category, "Category has 'score'"),
                check("num_samples" in category, "Category has 'num_samples'"),
            ])

    return all(checks)


def validate_samples(samples_dir: Path) -> bool:
    """Validate samples JSONL files"""
    print(f"\n{bcolors.BOLD}Validating samples{bcolors.ENDC}")

    if not samples_dir.exists():
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} Directory not found: {samples_dir}")
        return False

    sample_files = list(samples_dir.glob("*.jsonl"))
    checks = [
        check(len(sample_files) > 0, f"Found {len(sample_files)} sample files"),
    ]

    # Validate first sample file
    if sample_files:
        sample_file = sample_files[0]
        with open(sample_file) as f:
            first_line = f.readline()
            if first_line:
                sample = json.loads(first_line)
                checks.extend([
                    check("id" in sample, "Sample has 'id'"),
                    check("input" in sample, "Sample has 'input'"),
                    check("target" in sample, "Sample has 'target'"),
                    check("prediction" in sample, "Sample has 'prediction'"),
                    check("scores" in sample, "Sample has 'scores'"),
                ])

    return all(checks)


def main():
    output_dir = Path(__file__).parent / "output_data"

    print("=" * 80)
    print("Data Validation Script")
    print("=" * 80)
    print(f"\nOutput directory: {output_dir}")

    if not output_dir.exists():
        print(f"\n{bcolors.FAIL}Error:{bcolors.ENDC} Output directory does not exist.")
        print("Please run 'demo/run_demo.py' first.")
        sys.exit(1)

    # Find run directory
    runs_dir = output_dir / "runs"
    run_dirs = list(runs_dir.glob("run_*")) if runs_dir.exists() else []

    if not run_dirs:
        print(f"\n{bcolors.FAIL}Error:{bcolors.ENDC} No run directories found.")
        sys.exit(1)

    run_dir = run_dirs[0]
    print(f"Run directory: {run_dir.name}")

    # Validate each component
    results = [
        validate_index(output_dir / "index.json"),
        validate_meta(run_dir / "meta.json"),
        validate_eval_summary(run_dir / "eval_summary.json"),
        validate_samples(run_dir / "samples"),
    ]

    # Summary
    print("\n" + "=" * 80)
    if all(results):
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}✓ All validations passed!{bcolors.ENDC}")
        print("\nThe generated data is valid and ready to use with the frontend.")
        sys.exit(0)
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}✗ Some validations failed.{bcolors.ENDC}")
        print("\nPlease check the errors above and regenerate the data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
