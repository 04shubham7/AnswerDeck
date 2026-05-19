#!/usr/bin/env bash
# Simple helper to create venv and install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Run 'python indexing.py --run' to build the index (if you have a PDF)."
echo "Run 'python chat.py' to query the index." 