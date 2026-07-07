#!/bin/sh
set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

. venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt pytest

mkdir -p test-reports

echo "Running tests..."
python -m pytest test_*.py --junitxml=test-reports/results.xml
