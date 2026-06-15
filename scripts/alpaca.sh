#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"
API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"
H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"
cmd="${1:-}"; shift || true
case "$cmd" in
  account) curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/account" ;;
  positions) curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions" ;;
  position) sym="${1:?usage: position SYM}"; curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions/$sym" ;;
  quote) sym="${1:?usage: quote SYM}"; curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA/stocks/$sym/quotes/latest" ;;
  orders) status="${1:-open}"; curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/orders?status=$status" ;;
  order)
    if [[ "${DRY_RUN:-true}" == "true" ]]; then echo "DRY_RUN=true: refusing order submit" >&2; exit 4; fi
    body="${1:?usage: order '<json>'}"; curl -fsS -H "$H_KEY" -H "$H_SEC" -H "Content-Type: application/json" -X POST -d "$body" "$API/orders" ;;
  cancel)
    if [[ "${DRY_RUN:-true}" == "true" ]]; then echo "DRY_RUN=true: refusing cancel" >&2; exit 4; fi
    oid="${1:?usage: cancel ORDER_ID}"; curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders/$oid" ;;
  cancel-all)
    if [[ "${DRY_RUN:-true}" == "true" ]]; then echo "DRY_RUN=true: refusing cancel-all" >&2; exit 4; fi
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders" ;;
  close)
    if [[ "${DRY_RUN:-true}" == "true" ]]; then echo "DRY_RUN=true: refusing close" >&2; exit 4; fi
    sym="${1:?usage: close SYM}"; curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions/$sym" ;;
  close-all)
    if [[ "${DRY_RUN:-true}" == "true" ]]; then echo "DRY_RUN=true: refusing close-all" >&2; exit 4; fi
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions" ;;
  *) echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|order|cancel|cancel-all|close|close-all> [args]" >&2; exit 1 ;;
esac
echo
