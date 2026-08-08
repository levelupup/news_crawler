#!/usr/bin/env bash
# Run a quick health check on representative crawlers.
# Usage: ./health_check.sh [crawler1 crawler2 ...]
# Default: checks 10 representative crawlers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV="$SCRIPT_DIR/venv"
[[ -d "$VENV" ]] || { echo "venv not found at $VENV" >&2; exit 1; }
source "$VENV/bin/activate"

DEFAULT_CRAWLERS=(36kr bloomberg reuters evertiq techwireasia dramx sohu chosunbiz nikkei)
if [[ $# -gt 0 ]]; then
    CRAWLERS=("$@")
else
    CRAWLERS=("${DEFAULT_CRAWLERS[@]}")
fi
TIMEOUT=30

printf "%-22s | %5s | %4s | %s\n" "crawler" "arts" "sec" "status"
printf '%0.s-' {1..48}; echo

PASS=0; FAIL=0
for c in "${CRAWLERS[@]}"; do
    f="${c}.py"
    if [[ ! -f "$f" ]]; then
        printf "%-22s | %5s | %4s | SKIP\n" "$c" "N/A" "-"
        continue
    fi
    START=$(date +%s)
    OUT=$(timeout "$TIMEOUT" python "$f" 2>/dev/null || true)
    END=$(date +%s)
    ELAPSED=$((END - START))
    COUNT=$(echo "$OUT" | grep -oP 'Found \K[0-9]+' | head -1 || true)
    COUNT="${COUNT:-0}"
    if [[ "$COUNT" -ge 5 ]]; then STATUS="PASS"; PASS=$((PASS+1)); else STATUS="FAIL"; FAIL=$((FAIL+1)); fi
    printf "%-22s | %5s | %3ds | %s\n" "$c" "$COUNT" "$ELAPSED" "$STATUS"
done

echo ""
echo "Result: $PASS PASS, $FAIL FAIL"
