#!/bin/bash
set -e

cd "$(dirname "$0")"

/Users/capanema/Projects/Jonas/.venv/bin/python brapci_visualization.py
nohup /Users/capanema/Projects/Jonas/.venv/bin/python -m http.server 8000 >/tmp/brapci_dashboard_http.log 2>&1 &

sleep 1
open "http://localhost:8000"

echo "Dashboard em: http://localhost:8000"
