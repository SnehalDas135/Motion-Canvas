#!/bin/bash
# setup.sh -- FreeFace one-command setup
# Run: bash setup.sh

set -e

echo ""
echo "======================================"
echo "  FreeFace Setup"
echo "======================================"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 not found. Install from https://python.org"
  exit 1
fi

if ! command -v g++ >/dev/null 2>&1; then
  echo "ERROR: g++ not found."
  echo "  Ubuntu/Debian: sudo apt install g++"
  echo "  macOS:         xcode-select --install"
  exit 1
fi

echo "Python and g++ found"

echo ""
echo "Preparing virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "Upgrading pip tooling..."
python -m pip install --retries 8 --timeout 120 --upgrade pip setuptools wheel

echo ""
echo "Installing core Python dependencies..."
python -m pip install --retries 8 --timeout 120 -r requirements.txt
echo "Core dependencies installed"

echo ""
echo "Installing optional voice dependencies..."
if python -m pip install --retries 8 --timeout 120 -r requirements-voice.txt; then
  echo "Voice dependencies installed"
else
  echo "WARN: Optional voice dependencies could not be installed."
  echo "      Voice control will be disabled until PyAudio is available."
fi

echo ""
echo "Building C++ engine..."
make
echo "C++ engine built (engine.so)"

mkdir -p profiles
echo "Profiles directory ready"

echo ""
echo "======================================"
echo "  Setup complete"
echo ""
echo "  To run FreeFace:"
echo "  source venv/bin/activate"
echo "  cd python && python main.py"
echo ""
echo "  Controls:"
echo "  Q -> quit"
echo "  C -> recalibrate"
echo "======================================"
