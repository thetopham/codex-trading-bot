# Daily Summary — Hermes/Codex Routine

Safety: read-only account snapshot plus benchmark ledger/report update and Telegram/fallback notification.

1. Read tail of `memory/TRADE-LOG.md` for yesterday's EOD equity and `memory/BENCHMARK-REPORT.md` for current benchmark context.
2. Run `codex-trader daily-summary`.
3. Verify `memory/TRADE-LOG.md` has today's EOD snapshot and a `### Benchmark` section.
4. Verify `memory/BENCHMARK-LEDGER.csv` has today's row with bot equity, cash, SPY close, daily/cumulative bot-vs-SPY returns, alpha, drawdown, and exposure.
5. Verify `memory/BENCHMARK-REPORT.md` renders the current self-judgment: baseline/ahead/behind.
6. Commit changed memory files if this repo is connected to GitHub; never force-push.
