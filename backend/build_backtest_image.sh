#!/bin/bash
# Build Docker image for backtest execution

set -e

echo "Building backtest execution Docker image..."
echo "=========================================="

cd "$(dirname "$0")"

docker build \
    -f Dockerfile.backtest \
    -t backtest-executor:latest \
    .

echo ""
echo "✅ Image built successfully: backtest-executor:latest"
echo ""
echo "You can now run containerized backtests!"
