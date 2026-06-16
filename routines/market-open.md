# Market Open — Hermes/Codex Routine

Safety: Alpaca paper/dry-run by default. Stocks only. Do not submit live orders.

1. Read `AGENTS.md`, today's `memory/PREMARKET-CANDIDATES.json`, `memory/TRADING-STRATEGY.md`, and tail of `memory/TRADE-LOG.md`.
2. If today's `memory/PREMARKET-CANDIDATES.json` is missing, stale, or empty, fail closed: log HOLD/no submissions. Do **not** recompute top-volume momentum candidates as a replacement.
3. Pull account and positions via `scripts/alpaca.sh`.
4. Refresh the top-100-volume liquidity filter with `codex-trader market-open-intents`; it recomputes yfinance top volume internally.
5. Intersect today's TradingView MCP candidates with the current top-volume filter. Reject any candidate not still liquid.
6. Reject candidate rows that lack one TradingView MCP technical setup or a specific SPY/SPX outperformance thesis; extra MCP confirmations are score/context, not hard gates, and Perplexity-only ideas are not sufficient.
7. Size every candidate with `floor((equity * 0.01 / 0.10) / entry_price)` so the required 10% stop risks at most ~1% of portfolio equity before slippage.
8. Do not apply fixed max-position or weekly-trade-count caps; take every qualified candidate while cash is available and all per-position gates pass.
9. Run deterministic buy gates with `codex_trader.rules.validate_buy_gate`; reject any candidate whose 10% stop risk exceeds 1% of portfolio equity.
10. With `DRY_RUN=true`, log approved order intents only. Only call `scripts/alpaca.sh order` when paper order submission is explicitly enabled and the runner has set `DRY_RUN=false`.
11. Append skipped/approved intents to `memory/TRADE-LOG.md`, including qty, notional, 10% stop risk, MCP score/sources, benchmark thesis, liquidity skips, and broker action.
12. Telegram notification only if a paper order or approved dry-run intent exists.
13. Commit memory changes if any; never force-push.
