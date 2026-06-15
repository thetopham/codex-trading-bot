# Market Open — Hermes/Codex Routine

Safety: paper/dry-run by default. Stocks only. Do not submit live orders.

1. Read `AGENTS.md`, today's `memory/RESEARCH-LOG.md`, `memory/TRADING-STRATEGY.md`, and tail of `memory/TRADE-LOG.md`.
2. If today's research is missing, run pre-market research first. Never trade without documented catalyst.
3. Pull account, positions, and quotes for planned tickers via `scripts/alpaca.sh`.
4. Run deterministic buy gates with `codex-trader check-trade` or `codex_trader.rules.validate_buy_gate`.
5. With `DRY_RUN=true`, log approved order intents only. Do not call `scripts/alpaca.sh order` unless user explicitly approved paper order submission and `DRY_RUN=false`.
6. Append skipped/approved intents to `memory/TRADE-LOG.md`.
7. Telegram notification only if a paper order or approved dry-run intent exists.
8. Commit memory changes if any; never force-push.
