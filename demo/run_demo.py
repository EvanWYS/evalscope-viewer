#!/usr/bin/env python3
"""
Demo Script: EvalScope Adapter Demo

This script demonstrates the complete ETL pipeline:
1. Mock evalscope raw data -> 2. Adapter extraction -> 3. Standard protocol JSON

Usage:
    python demo/run_demo.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.etl.adapters.evalscope.adapter import EvalScopeAdapter
from tools.etl.core.builder import DataBuilder
from tools.etl.core.models import StandardIndexEntry


def main():
    print("=" * 80)
    print("EvalScope Adapter Demo")
    print("=" * 80)
    print()

    # Paths
    demo_dir = Path(__file__).parent
    raw_data_dir = demo_dir / "mock_evalscope_output" / "20251124_143025"
    output_dir = demo_dir / "output_data"

    print(f"📂 Raw data directory: {raw_data_dir}")
    print(f"📂 Output directory: {output_dir}")
    print()

    # Step 1: Initialize adapter
    print("Step 1: Initializing EvalScope Adapter...")
    adapter = EvalScopeAdapter(str(raw_data_dir))
    print("✅ Adapter initialized")
    print()

    # Step 2: Extract metadata
    print("Step 2: Extracting run metadata...")
    meta = adapter.extract_meta()
    print(f"  Run ID: {meta.run_id}")
    print(f"  Model: {meta.model.name}")
    print(f"  Datasets: {', '.join(meta.datasets)}")
    print(f"  Status: {meta.status}")
    print(f"  Duration: {meta.duration_seconds:.2f}s")
    print("✅ Metadata extracted")
    print()

    # Step 3: Extract benchmark results
    print("Step 3: Extracting benchmark results...")
    results = adapter.extract_results()
    print(f"  Found {len(results)} datasets")
    for result in results:
        print(f"    - {result.dataset_pretty_name}: {result.overall_score:.2%}")
        print(f"      Metrics: {', '.join(result.metrics.keys())}")
        if result.categories:
            print(f"      Categories: {len(result.categories)}")
    print("✅ Benchmark results extracted")
    print()

    # Step 4: Extract samples
    print("Step 4: Extracting samples...")
    samples_by_dataset = {}
    for dataset in meta.datasets:
        samples = adapter.extract_samples(dataset, limit=10)
        samples_by_dataset[dataset] = samples
        print(f"  - {dataset}: {len(samples)} samples")
        # Show a sample
        if samples:
            sample = samples[0]
            print(f"    Example: ID={sample.id}, Scores={sample.scores}")
    print("✅ Samples extracted")
    print()

    # Step 5: Build standard protocol files
    print("Step 5: Building standard protocol JSON files...")
    builder = DataBuilder(str(output_dir))

    # Build meta.json
    meta_path = builder.build_meta(meta)
    print(f"  ✅ Created: {meta_path}")

    # Build eval_summary.json
    summary_path = builder.build_eval_summary(meta.run_id, results)
    print(f"  ✅ Created: {summary_path}")

    # Build samples JSONL files
    sample_paths = builder.build_samples(meta.run_id, samples_by_dataset)
    for dataset, path in sample_paths.items():
        print(f"  ✅ Created: {path}")

    # Build index.json
    # Calculate overall score (average of all datasets)
    overall_score = sum(r.overall_score for r in results) / len(results) if results else 0.0
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
    index_path = builder.build_index([index_entry])
    print(f"  ✅ Created: {index_path}")
    print()

    # Step 6: Summary
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print(f"  - Run ID: {meta.run_id}")
    print(f"  - Model: {meta.model.name}")
    print(f"  - Datasets: {len(results)}")
    print(f"  - Total samples: {total_samples}")
    print(f"  - Overall score: {overall_score:.2%}")
    print()
    print("📁 Generated files:")
    print(f"  - {output_dir / 'index.json'}")
    print(f"  - {output_dir / 'runs' / meta.run_id / 'meta.json'}")
    print(f"  - {output_dir / 'runs' / meta.run_id / 'eval_summary.json'}")
    for dataset in meta.datasets:
        print(f"  - {output_dir / 'runs' / meta.run_id / 'samples' / f'{dataset}_head.jsonl'}")
    print()
    print("🎉 You can now use these JSON files with the visualization frontend!")
    print()


if __name__ == "__main__":
    main()
