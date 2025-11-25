#!/bin/bash
#
# Quick Start Script for EvalScope Adapter Demo
#
# This script automates the complete demo workflow:
# 1. Creates Python virtual environment (if not exists)
# 2. Installs dependencies
# 3. Runs the demo
# 4. Validates generated data
# 5. Shows sample output

set -e  # Exit on error

DEMO_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$DEMO_DIR")"

echo "========================================"
echo "EvalScope Adapter Demo - Quick Start"
echo "========================================"
echo ""

# Step 1: Check/Create virtual environment
if [ ! -d "$DEMO_DIR/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$DEMO_DIR/venv"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Step 2: Install dependencies
echo "📦 Installing dependencies..."
"$DEMO_DIR/venv/bin/pip3" install -q -r "$PROJECT_ROOT/tools/etl/requirements.txt"
echo "✅ Dependencies installed"
echo ""

# Step 3: Run demo
echo "🚀 Running demo..."
echo ""
"$DEMO_DIR/venv/bin/python3" "$DEMO_DIR/run_demo.py"
echo ""

# Step 4: Validate output
echo "🔍 Validating generated data..."
echo ""
"$DEMO_DIR/venv/bin/python3" "$DEMO_DIR/validate_output.py"
echo ""

# Step 5: Show sample outputs
echo "========================================"
echo "Sample Output Files"
echo "========================================"
echo ""

echo "📄 Index.json (first 10 lines):"
head -n 10 "$DEMO_DIR/output_data/index.json"
echo "..."
echo ""

echo "📄 Sample data (first 1 line):"
head -n 1 "$DEMO_DIR/output_data/runs/run_*/samples/mmlu_head.jsonl" | python3 -m json.tool
echo "..."
echo ""

echo "========================================"
echo "Next Steps"
echo "========================================"
echo ""
echo "1. View the generated files in: demo/output_data/"
echo "2. Copy to frontend: cp -r demo/output_data/* web/public/data/"
echo "3. Start frontend: cd web && npm run dev"
echo ""
echo "For more details, see: demo/README.md"
echo ""
