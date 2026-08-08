#!/usr/bin/env bash
# run_analyze_7d.sh — runs weekly (Sunday 00:05 TW) via news_analyze_7d.timer.
# Processes the last 7 days of news; writes important.html / grouped.html /
# analysis.json AND analysis_7d_cache.json (used by 2-hour runs for the 7d tab).
# If Ollama is unreachable, analyze_news.py exits non-zero and leaves prior
# outputs untouched.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

echo "=== $(date '+%Y-%m-%d %H:%M:%S %Z') :: analyze start (7-day weekly) ==="
./venv/bin/python analyze_news.py --days 7
echo "=== $(date '+%Y-%m-%d %H:%M:%S %Z') :: analyze done ==="
