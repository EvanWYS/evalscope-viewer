# ETL Pipeline for EvalScope Viewer

This ETL (Extract-Transform-Load) pipeline converts evaluation framework output into standardized static JSON files for frontend visualization.

## Architecture

The ETL pipeline is designed with extensibility in mind:

```
┌─────────────────────────────────────┐
│  Framework-Specific Adapters        │
│  (evalscope, lm-harness, ...)      │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Standard Data Models               │
│  (Framework-agnostic)               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Static JSON Files                  │
│  (Frontend consumption)             │
└─────────────────────────────────────┘
```

## Directory Structure

```
etl/
├── core/                    # Framework-agnostic core
│   ├── schema.py           # JSON schema definitions
│   ├── models.py           # Standard data models
│   └── builder.py          # Static file builder
├── adapters/               # Framework-specific adapters
│   ├── base.py            # Abstract base class
│   └── evalscope/         # EvalScope adapter
│       └── adapter.py
├── build_static_data.py   # Main ETL script
├── utils.py               # Utility functions
└── requirements.txt       # Python dependencies
```

## Usage

### Basic Usage

```bash
python build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data
```

### Options

- `--framework`: Evaluation framework name (default: `evalscope`)
- `--raw-dir`: Directory containing framework output (required)
- `--out-dir`: Output directory for static JSON files (required)
- `--sample-limit`: Maximum samples per dataset (default: `100`)
- `--run-pattern`: Glob pattern for run directories (default: `*`)

### Example

```bash
# Process all runs in outputs/
python build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --sample-limit 200

# Process specific runs
python build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --run-pattern "20251124_*"
```

## Output Structure

The ETL pipeline generates the following structure:

```
web/public/data/
├── index.json                    # List of all runs
└── runs/
    └── <run_id>/
        ├── meta.json            # Run metadata
        ├── eval_summary.json    # Evaluation results
        └── samples/
            ├── mmlu_head.jsonl
            ├── gsm8k_head.jsonl
            └── ...
```

## Adding New Frameworks

To add support for a new evaluation framework:

1. **Create adapter directory:**
   ```bash
   mkdir -p adapters/myframework
   touch adapters/myframework/__init__.py
   ```

2. **Implement adapter class:**
   ```python
   # adapters/myframework/adapter.py
   from ..base import BaseAdapter
   from ...core.models import StandardRunMeta, StandardBenchmarkResult, StandardSample

   class MyFrameworkAdapter(BaseAdapter):
       def extract_meta(self) -> StandardRunMeta:
           # Parse framework-specific config
           ...

       def extract_results(self) -> List[StandardBenchmarkResult]:
           # Parse framework-specific reports
           ...

       def extract_samples(self, dataset: str, limit: int) -> List[StandardSample]:
           # Parse framework-specific predictions
           ...
   ```

3. **Register adapter:**
   ```python
   # adapters/__init__.py
   from .myframework import MyFrameworkAdapter

   ADAPTER_REGISTRY = {
       "evalscope": EvalScopeAdapter,
       "myframework": MyFrameworkAdapter,  # Add here
   }
   ```

4. **Use the new adapter:**
   ```bash
   python build_static_data.py --framework myframework --raw-dir ... --out-dir ...
   ```

## Development

### Installation

```bash
pip install -r requirements.txt
```

### Testing

```bash
# Test with sample data
python build_static_data.py \
  --framework evalscope \
  --raw-dir ../outputs/20251124_143025 \
  --out-dir ./test_output
```

## Standard Data Models

All adapters must convert framework-specific data to these standard models:

- **StandardRunMeta**: Run metadata (model, config, timestamps)
- **StandardBenchmarkResult**: Evaluation results (metrics, categories, subsets)
- **StandardSample**: Individual predictions (input, target, prediction, scores)

See `core/models.py` for detailed definitions.
