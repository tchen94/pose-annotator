#!/usr/bin/env bash
set -euo pipefail

# Always run from the repo root (directory of this script)
cd "$(dirname "$0")"

echo "▶ Starting Pose Annotator"

# --- Check Python ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Please install Python 3.12+."
  exit 1
fi

PYTHON_VERSION=$(python3 - <<EOF
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
EOF
)
echo "✔ Using Python $PYTHON_VERSION"

# --- Create virtual environment if missing ---
if [ ! -d ".venv" ]; then
  echo "▶ Creating virtual environment (.venv)"
  python3 -m venv .venv
fi

# --- Activate virtual environment ---
source .venv/bin/activate

# --- Upgrade pip ---
pip install --upgrade pip >/dev/null

# --- Install backend dependencies ---
echo "▶ Installing backend dependencies"
pip install -r backend/requirements.txt

# --- Verify frontend build exists ---
if [ ! -f "frontend/dist/index.html" ]; then
  echo "❌ frontend/dist/index.html not found."
  echo "This branch expects the frontend to already be built."
  exit 1
fi

# --- Start backend ---
echo "▶ Starting backend at http://localhost:8000"
echo "   (Press Ctrl+C to stop)"

cd backend
python api.py