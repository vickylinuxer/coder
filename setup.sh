#!/bin/bash
set -e

echo "Setting up coder..."

if [ "$(uname)" = "Linux" ]; then
    echo "Installing system dependencies..."
    sudo apt install -y wmctrl python3-xlib python3-venv
fi

python3 -m venv venv
# shellcheck source=/dev/null
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "Done. To run:"
echo "  source venv/bin/activate"
echo "  python3 coder.py"
