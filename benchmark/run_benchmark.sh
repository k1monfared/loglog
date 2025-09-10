#!/bin/bash
# LogLog GUI Performance Benchmark Runner
# This script commits current changes and runs performance benchmarks

set -e

echo "🔬 LogLog GUI Performance Benchmark Runner"
echo "=========================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if there are uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "📝 Committing current changes for version tracking..."
    git add -A
    
    # Prompt for commit message
    read -p "Enter commit message (or press Enter for auto-generated): " commit_msg
    
    if [ -z "$commit_msg" ]; then
        commit_msg="Performance benchmark run at $(date)"
    fi
    
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
else
    echo "✅ No uncommitted changes found"
fi

# Get current commit hash
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "🔖 Current version: $COMMIT_HASH"

# Kill any existing GUI processes to ensure clean benchmark
echo "🧹 Cleaning up any existing GUI processes..."
pkill -f "python.*loglog_gui.py" || true
sleep 1

# Run benchmark
echo "🚀 Running performance benchmark..."
cd benchmark
python3 benchmark_runner.py

echo "📊 Benchmark complete!"
echo "📁 Results saved to: benchmark/performance_results.csv"
echo "🔗 Version tracked as: $COMMIT_HASH"