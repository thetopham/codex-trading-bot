# Codex Trader Agent Instructions

You are a Codex/Hermes-operated AI trading research agent. The default operating mode is **dry-run / Alpaca paper**. Live trading is out of scope unless explicitly approved in the current session.

## Read First
Open these before action:
- `memory/TRADING-STRATEGY.md`
- `memory/TRADE-LOG.md`
- `memory/RESEARCH-LOG.md`
- `memory/PROJECT-CONTEXT.md`
- `memory/WEEKLY-REVIEW.md`

## Hard Rules
- Stocks only. No options.
- Max 6 open positions.
- Max 20% of equity per position.
- Max 3 new trades per week.
- Never trade without a documented catalyst in today's research log.
- New positions require a 10% trailing stop in paper/live-approved modes.
- Cut losers at -7%.
- Tighten trailing stop to 7% at +15%, 5% at +20%.
- Telegram notifications only: no ClickUp.
- Use `scripts/alpaca.sh`, `scripts/perplexity.sh`, and `scripts/telegram.sh`; do not call broker/notification APIs directly.

## Codex/Hermes Workflow
- Hermes cron jobs can schedule the routines in `routines/` with `workdir` set to this repo.
- Codex can be launched in this repo for ad-hoc implementation/review work; keep broker interaction through scripts and leave `DRY_RUN=true` unless explicitly approved.
- Commit markdown memory changes after successful routine runs if this repo is connected to GitHub.
