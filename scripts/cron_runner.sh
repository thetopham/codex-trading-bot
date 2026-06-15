#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export TRADING_MODE="${TRADING_MODE:-paper}"
export DRY_RUN="${DRY_RUN:-true}"

if [[ "$TRADING_MODE" != "paper" ]]; then
  echo "Refusing cron run: TRADING_MODE must be paper for automated v1 routines" >&2
  exit 5
fi

if [[ "${ALLOW_LIVE_TRADING:-false}" == "true" ]]; then
  echo "Refusing cron run: ALLOW_LIVE_TRADING=true is not permitted for automated v1 routines" >&2
  exit 5
fi

if [[ "${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}" != https://paper-api.alpaca.markets/v2* ]]; then
  echo "Refusing cron run: ALPACA_ENDPOINT must be Alpaca paper endpoint" >&2
  exit 5
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv; run: uv venv .venv && . .venv/bin/activate && uv pip install -e '.[test]'" >&2
  exit 2
fi

# Ensure console script points at the current checkout after renames or host moves.
. .venv/bin/activate
python -m pip show codex-trading-bot >/dev/null 2>&1 || uv pip install -q -e '.[test]'

workflow="${1:?usage: scripts/cron_runner.sh <pre-market|market-open|midday|daily-summary|weekly-review|smoke>}"
stamp="$(date +%Y-%m-%d)"

case "$workflow" in
  smoke)
    pytest -q
    codex-trader portfolio
    ;;
  pre-market)
    codex-trader portfolio >/tmp/codex_pre_market_portfolio.out
    echo "Codex Trader pre-market ${stamp}: account read succeeded; research automation scaffold active."
    bash scripts/telegram.sh "Codex Trader pre-market check ${stamp}: account read succeeded; research automation scaffold active."
    ;;
  market-open)
    codex-trader check-trade SPY 1 1 --equity 50000 --cash 50000 --catalyst "cron gate smoke" >/tmp/codex_market_open_gate.json
    echo "Codex Trader market-open gate ${stamp}: dry-run gate checked; no order submission in v1."
    bash scripts/telegram.sh "Codex Trader market-open gate ${stamp}: dry-run gate checked; no order submission in v1."
    ;;
  midday)
    codex-trader midday-scan | tee /tmp/codex_midday_scan.out
    if ! grep -q "No midday actions required" /tmp/codex_midday_scan.out; then
      bash scripts/telegram.sh "Codex Trader midday ${stamp}: action required. $(tr '\n' '; ' </tmp/codex_midday_scan.out)"
    fi
    ;;
  daily-summary)
    codex-trader daily-summary
    ;;
  weekly-review)
    codex-trader portfolio >/tmp/codex_weekly_portfolio.out
    echo "Codex Trader weekly review ${stamp}: portfolio snapshot succeeded; write-up scaffold active."
    bash scripts/telegram.sh "Codex Trader weekly review ${stamp}: portfolio snapshot succeeded; write-up scaffold active."
    ;;
  *)
    echo "unknown workflow: $workflow" >&2
    exit 1
    ;;
esac

# Persist append-only memory changes when present; keep this best-effort so cron does not fail on no-op.
if git diff --quiet -- memory; then
  exit 0
fi

git add memory
git commit -m "codex trader ${workflow} ${stamp}" || true
git pull --rebase origin main || true
git push origin main || true
