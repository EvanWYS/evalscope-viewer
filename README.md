# EvalScope Viewer

A lightweight, static visualization platform for LLM evaluation results. Designed for evalscope with extensibility for other evaluation frameworks.

## 🎯 Features

- **Framework-Agnostic Architecture**: Currently supports evalscope with easy extensibility for other frameworks (lm-harness, OpenCompass, etc.)
- **Static-First Design**: No backend required - pure static files deployed anywhere
- **Comprehensive Visualization**:
  - Run listings with metadata
  - Detailed benchmark results with category breakdowns
  - Sample-level prediction inspection
- **Modern UI**: Built with Next.js 14, TypeScript, and Tailwind CSS
- **Extensible**: Adapter pattern for easy integration of new evaluation frameworks

## 📁 Project Structure

```
evalscope-viewer/
├── tools/etl/              # ETL pipeline (Python)
│   ├── core/              # Framework-agnostic core
│   ├── adapters/          # Framework-specific adapters
│   │   ├── base.py       # Abstract adapter interface
│   │   └── evalscope/    # EvalScope adapter
│   └── build_static_data.py
│
├── web/                   # Frontend (Next.js)
│   ├── app/              # Pages
│   ├── components/       # React components
│   ├── lib/              # Utilities & types
│   └── public/data/      # Generated static JSON
│
├── outputs/              # EvalScope raw output (not in git)
└── dcos/                 # Design documents
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Step 1: Install Dependencies

```bash
# Install ETL dependencies
pip install -r tools/etl/requirements.txt

# Install frontend dependencies
cd web
npm install
```

### Step 2: Generate Data

Place your evalscope output in the `outputs/` directory, then run:

```bash
python tools/etl/build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data
```

### Step 3: Start Development Server

```bash
cd web
npm run dev
```

Visit http://localhost:3000 to view your evaluation results.

### Step 4: Build for Production

```bash
cd web
npm run build
```

The static site will be generated in `web/out/`. Deploy this directory to any static hosting service.

## 📊 Data Flow

```
EvalScope Evaluation
        ↓
   Raw Output Files
   (configs, reports, predictions)
        ↓
   ETL Pipeline
   (Extract → Transform → Load)
        ↓
   Standard JSON Protocol
   (meta.json, eval_summary.json, samples/*.jsonl)
        ↓
   Next.js Frontend
   (Static visualization)
```

## 🔧 ETL Pipeline

The ETL pipeline converts framework-specific output to a standard JSON protocol:

### Architecture

```
┌─────────────────────────────────┐
│  Adapter Layer (Framework-Specific)  │
│  - evalscope adapter            │
│  - Future: lm-harness adapter   │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│  Core Layer (Framework-Agnostic)     │
│  - Standard data models         │
│  - JSON schema definitions      │
└─────────────────────────────────┘
              ↓
┌─────────────────────────────────┐
│  Output (Static JSON)           │
└─────────────────────────────────┘
```

### Usage

```bash
# Basic usage
python tools/etl/build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data

# Custom sample limit
python tools/etl/build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --sample-limit 200

# Process specific runs
python tools/etl/build_static_data.py \
  --framework evalscope \
  --raw-dir ./outputs \
  --out-dir ./web/public/data \
  --run-pattern "20251124_*"
```

## 📝 Standard JSON Protocol

The ETL pipeline generates these files:

### index.json
```json
{
  "runs": [
    {
      "run_id": "run_20251124_143025_a1b2c3d4",
      "framework": "evalscope",
      "model": { "name": "Qwen/Qwen2.5-7B", "type": "openai_api" },
      "datasets": ["mmlu", "gsm8k"],
      "overall_score": 0.68,
      "status": "completed"
    }
  ]
}
```

### runs/<run_id>/meta.json
Run metadata including model config, timestamps, and environment.

### runs/<run_id>/eval_summary.json
Aggregated evaluation results with metrics and category breakdowns.

### runs/<run_id>/samples/<dataset>_head.jsonl
Sample-level predictions (JSONL format).

See `dcos/ETL Data Protocol.md` for complete specification.

## 🔌 Adding New Frameworks

To add support for a new evaluation framework:

1. **Create adapter directory**:
   ```bash
   mkdir -p tools/etl/adapters/myframework
   ```

2. **Implement adapter**:
   ```python
   # tools/etl/adapters/myframework/adapter.py
   from ..base import BaseAdapter
   from ...core.models import StandardRunMeta, StandardBenchmarkResult

   class MyFrameworkAdapter(BaseAdapter):
       def extract_meta(self) -> StandardRunMeta:
           # Parse framework-specific config
           ...

       def extract_results(self) -> List[StandardBenchmarkResult]:
           # Parse framework-specific results
           ...
   ```

3. **Register adapter**:
   ```python
   # tools/etl/adapters/__init__.py
   from .myframework import MyFrameworkAdapter

   ADAPTER_REGISTRY = {
       "evalscope": EvalScopeAdapter,
       "myframework": MyFrameworkAdapter,
   }
   ```

4. **Use it**:
   ```bash
   python tools/etl/build_static_data.py --framework myframework --raw-dir ... --out-dir ...
   ```

## 🎨 Frontend

Built with modern web technologies:

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: ECharts (for future enhancements)
- **Deployment**: Static export (no server required)

### Key Pages

- `/` - List all evaluation runs
- `/runs/[runId]` - Run details with benchmark results
- `/runs/[runId]/samples` - Sample predictions viewer

## 📖 Documentation

- [Evaluation Visualization System Design](dcos/Evaluation%20Visualization%20System%20Design.md)
- [ETL Data Protocol](dcos/ETL%20Data%20Protocol.md)
- [ETL README](tools/etl/README.md)

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- ✅ ETL pipeline with evalscope adapter
- ✅ Frontend with runs list, details, and samples
- ✅ Standard JSON protocol

### Phase 2: Enhanced Visualization
- ⏳ ECharts integration for metrics visualization
- ⏳ Category comparison charts
- ⏳ Multi-run comparison view

### Phase 3: Multi-Framework Support
- ⏳ lm-evaluation-harness adapter
- ⏳ OpenCompass adapter
- ⏳ Plugin system for custom adapters

### Phase 4: Advanced Features
- ⏳ Error analysis dashboard
- ⏳ Filtering and search
- ⏳ Export reports

## 🤝 Contributing

Contributions are welcome! Areas of interest:

- New framework adapters
- Visualization components
- Documentation improvements
- Bug fixes and optimizations

## 📄 License

MIT License

## 🙏 Acknowledgments

- Built for evalscope evaluation framework
- Designed for extensibility to support the broader LLM evaluation ecosystem
