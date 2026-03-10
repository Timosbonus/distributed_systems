#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=.
python -m src.main
