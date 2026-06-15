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
  perplexity.sh           # optional cited research wrapper
  telegram.sh             # Telegram notification wrapper with local fallback
src/codex_trader/
  cli.py                  # CLI commands
  rules.py                # strategy hard gates
  memory.py               # markdown memory helpers
memory/                   # git-backed agent memory
routines/                 # Hermes cron prompt templates
.claude/commands/         # compatibility aliases for local slash-style docs
```

## Core CLI

```bash
codex-trader portfolio              # account/positions/orders via Alpaca wrapper
codex-trader check-trade ...         # deterministic buy-side gate check
codex-trader midday-scan             # dry-run action scan from positions
codex-trader daily-summary           # append EOD snapshot + Telegram/fallback notify
```

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
