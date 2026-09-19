#!/bin/bash
set -e

cd "$(dirname "$0")"

nohup /Users/capanema/Projects/Jonas/.venv/bin/python dashboard_server.py >/tmp/brapci_dashboard_http.log 2>&1 &

sleep 1
open "http://localhost:8000"

echo "Dashboard em: http://localhost:8000"
