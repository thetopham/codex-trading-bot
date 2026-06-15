# Codex Trader — Hermes/Codex Edition

A safe, repo-backed swing-trading agent scaffold adapted from the uploaded Codex guide.

**Key adaptations:**
- **Hermes cron jobs** replace Claude cloud routines.
- **Codex/Hermes agents** replace Claude Code as the operator/researcher.
- **Telegram** replaces ClickUp for notifications.
- **Alpaca paper + `DRY_RUN=true`** is the default. Live order submission is not enabled by default.

## Safety Boundary

This repo is currently a **dry-run / paper-trading scaffold**:
- Read-only Alpaca calls work with paper credentials.
- Mutating Alpaca wrapper commands (`order`, `cancel`, `close`) refuse to run while `DRY_RUN=true`.
- The Python CLI's `midday-scan` only prints intended actions in v1.

## Quickstart

```bash
cd /home/matt/workspace/codex-trading-bot
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[test]'
cp env.template .env   # fill paper Alpaca + Telegram if desired
codex-trader init-memory
codex-trader check-trade XOM 10 100 --equity 10000 --cash 5000 --catalyst 'example catalyst'
bash scripts/telegram.sh 'Codex Trader smoke test'
```

If Telegram env vars are missing, the notification script appends to `DAILY-SUMMARY.md` instead of failing.

## Repo Layout

```text
AGENTS.md                 # Codex/Hermes agent rulebook
README.md
pyproject.toml
scripts/
  alpaca.sh               # Alpaca wrapper; dry-run guards mutating calls
  perplexity.sh           # legacy optional wrapper; automation uses yfinance instead

  telegram.sh             # Telegram notification wrapper with local fallback
src/codex_trader/
  cli.py                  # CLI commands
  research.py             # top-volume Yahoo Finance scanner and candidate renderer
  memory.py               # markdown memory helpers
memory/                   # git-backed agent memory
routines/                 # Hermes cron prompt templates
.claude/commands/         # compatibility aliases for local slash-style docs
```

## Core CLI

```bash
codex-trader pre-market-research     # rank top-volume universe and write research log
codex-trader market-open-intents     # create dry-run intents from top-volume candidates
codex-trader portfolio              # account/positions/orders via Alpaca wrapper
codex-trader check-trade ...         # deterministic buy-side gate check
codex-trader midday-scan             # dry-run action scan from positions
codex-trader daily-summary           # append EOD snapshot + Telegram/fallback notify
```

## Automation Runner

Hermes cron jobs should call the guarded runner, not raw broker commands:

```bash
bash scripts/cron_runner.sh smoke
bash scripts/cron_runner.sh pre-market
bash scripts/cron_runner.sh market-open
bash scripts/cron_runner.sh midday
bash scripts/cron_runner.sh daily-summary
bash scripts/cron_runner.sh weekly-review
```

The runner refuses automated execution unless `TRADING_MODE=paper`, the Alpaca endpoint is the paper endpoint, and `ALLOW_LIVE_TRADING` is not enabled. Mutating Alpaca commands are still blocked while `DRY_RUN=true`.

## Research Inputs

Automated research now uses two layers:

1. **Top-volume universe** from Yahoo Finance/yfinance `most_actives`, ranked by latest volume and scored by relative volume, 1D momentum, and 5D momentum.
2. **TradingView MCP overlay** in the Hermes pre-market cron agent, used to cross-check top gainers, volume breakouts, Bollinger/rating signals, and technical context before writing final research notes.

The market-open step submits Alpaca **paper** broker orders only when `PAPER_ORDER_SUBMISSION=true` and the runner has switched `DRY_RUN=false` for the market-open workflow. It buys approved candidates and immediately attempts a 10% GTC trailing stop. Other workflows force `DRY_RUN=true`.

## Suggested Hermes Cron Mapping

Set `workdir=/home/matt/workspace/codex-trading-bot` and schedule weekdays:

| Workflow | Cron | Routine prompt |
|---|---:|---|
| Pre-market research | `0 6 * * 1-5` | `routines/pre-market.md` |
| Market-open gate | `30 8 * * 1-5` | `routines/market-open.md` |
| Midday scan | `0 12 * * 1-5` | `routines/midday.md` |
| Daily summary | `0 15 * * 1-5` | `routines/daily-summary.md` |
| Weekly review | `0 16 * * 5` | `routines/weekly-review.md` |

Do not schedule live trading until risk gates, broker fill handling, and approval boundaries are reviewed.
