#!/usr/bin/env python3
"""
ETL Script: Build Static Data for EvalScope Viewer

This script converts evaluation framework output to static JSON files
that can be consumed by the frontend visualization tool.

Usage:
    python build_static_data.py --framework evalscope --raw-dir ./outputs --out-dir ./web/public/data

Supported frameworks:
    - evalscope (current)
    - lm-harness (future)
    - opencompass (future)
"""

import argparse
import sys
from pathlib import Path
from typing import List

from core import DataBuilder
from core.models import StandardIndexEntry
from adapters import get_adapter
from utils import scan_directories


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Build static data for evaluation visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--framework",
        type=str,
        default="evalscope",
        help="Evaluation framework name (default: evalscope)",
    )

    parser.add_argument(
        "--raw-dir",
        type=str,
        required=True,
        help="Directory containing framework output (e.g., ./outputs)",
    )

    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Output directory for static JSON files (e.g., ./web/public/data)",
    )

    parser.add_argument(
        "--sample-limit",
        type=int,
        default=100,
        help="Maximum number of samples per dataset (default: 100)",
    )

    parser.add_argument(
        "--run-pattern",
        type=str,
        default="*",
        help="Glob pattern to match run directories (default: *)",
    )

    return parser.parse_args()


def process_run(
    adapter_class: type,
    run_dir: Path,
    builder: DataBuilder,
    sample_limit: int,
) -> StandardIndexEntry:
    """
    Process a single evaluation run

    Args:
        adapter_class: Adapter class for the framework
        run_dir: Path to run directory
        builder: DataBuilder instance
        sample_limit: Maximum samples per dataset

    Returns:
        StandardIndexEntry for the processed run
    """
    print(f"\nProcessing: {run_dir}")

    # Initialize adapter
    adapter = adapter_class(str(run_dir))

    # Extract data using adapter
    print("  → Extracting metadata...")
    meta = adapter.extract_meta()

    print("  → Extracting evaluation results...")
    results = adapter.extract_results()

    print("  → Extracting samples...")
    samples_by_dataset = adapter.extract_all_samples(limit=sample_limit)

    # Build static JSON files
    print("  → Building static files...")
    builder.build_meta(meta)
    builder.build_eval_summary(meta.run_id, results)
    builder.build_samples(meta.run_id, samples_by_dataset)

    # Create index entry
    overall_score = (
        sum(r.overall_score for r in results) / len(results) if results else None
    )
    total_samples = sum(len(samples) for samples in samples_by_dataset.values())

    index_entry = StandardIndexEntry(
        run_id=meta.run_id,
        timestamp=meta.timestamp,
        framework=meta.framework,
        model={
            "name": meta.model.name,
            "type": meta.model.type or "unknown",
        },
        datasets=meta.datasets,
        overall_score=overall_score,
        num_samples=total_samples,
        start_time=meta.start_time,
        end_time=meta.end_time,
        duration_seconds=meta.duration_seconds,
        status=meta.status,
        tags=meta.tags,
    )

    print(f"  ✓ Completed: {meta.run_id}")
    return index_entry


def main():
    """Main ETL pipeline"""
    args = parse_args()

    print("=" * 60)
    print("EvalScope Viewer - ETL Pipeline")
    print("=" * 60)
    print(f"Framework:      {args.framework}")
    print(f"Raw directory:  {args.raw_dir}")
    print(f"Output directory: {args.out_dir}")
    print(f"Sample limit:   {args.sample_limit}")
    print("=" * 60)

    # Get adapter class
    try:
        adapter_class = get_adapter(args.framework)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Scan for run directories
    raw_dir = Path(args.raw_dir)
    if not raw_dir.exists():
        print(f"Error: Raw directory not found: {raw_dir}")
        sys.exit(1)

    run_dirs = scan_directories(raw_dir, args.run_pattern)
    if not run_dirs:
        print(f"Error: No run directories found in {raw_dir}")
        sys.exit(1)

    print(f"\nFound {len(run_dirs)} run(s)")

    # Initialize builder
    builder = DataBuilder(args.out_dir)

    # Process each run
    index_entries: List[StandardIndexEntry] = []
    failed_runs = []

    for run_dir in run_dirs:
        try:
            entry = process_run(adapter_class, run_dir, builder, args.sample_limit)
            index_entries.append(entry)
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed_runs.append((run_dir, str(e)))
            continue

    # Build index
    if index_entries:
        print("\nBuilding index...")
        index_path = builder.build_index(index_entries)
        print(f"  ✓ Index created: {index_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total runs:     {len(run_dirs)}")
    print(f"Successful:     {len(index_entries)}")
    print(f"Failed:         {len(failed_runs)}")

    if failed_runs:
        print("\nFailed runs:")
        for run_dir, error in failed_runs:
            print(f"  - {run_dir.name}: {error}")

    print(f"\nOutput directory: {args.out_dir}")
    print("=" * 60)

    # Exit with error code if any runs failed
    if failed_runs:
        sys.exit(1)


if __name__ == "__main__":
    main()
