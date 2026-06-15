# Market Open — Hermes/Codex Routine

Safety: paper/dry-run by default. Stocks only. Do not submit live orders.

1. Read `AGENTS.md`, today's `memory/RESEARCH-LOG.md`, `memory/TRADING-STRATEGY.md`, and tail of `memory/TRADE-LOG.md`.
2. If today's research is missing, run pre-market research first. Never trade without documented catalyst.
3. Pull account, positions, and quotes for planned tickers via `scripts/alpaca.sh`.
4. Size every candidate with `floor((equity * 0.01 / 0.10) / entry_price)` so the required 10% stop risks at most ~1% of portfolio equity before slippage.
5. Run deterministic buy gates with `codex-trader check-trade` or `codex_trader.rules.validate_buy_gate`; reject any candidate whose 10% stop risk exceeds 1% of portfolio equity.
6. With `DRY_RUN=true`, log approved order intents only. Do not call `scripts/alpaca.sh order` unless user explicitly approved paper order submission and `DRY_RUN=false`.
7. Append skipped/approved intents to `memory/TRADE-LOG.md`, including qty, notional, and 10% stop risk.
8. Telegram notification only if a paper order or approved dry-run intent exists.
9. Commit memory changes if any; never force-push.
