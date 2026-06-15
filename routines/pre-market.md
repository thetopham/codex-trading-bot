# Pre-market Research — Hermes/Codex Routine

You are running the pre-market research workflow for the Codex Trader Hermes/Codex bot.

Safety: paper/dry-run by default. Stocks only. Telegram notifications only.

The automated implementation is `codex-trader pre-market-research`, which:
1. Uses Yahoo Finance daily OHLCV via `yfinance` — no Perplexity dependency.
2. Starts from a static high-liquidity universe representing the top ~100 commonly traded stocks/ETFs by volume.
3. Ranks the latest data by volume and scores positive momentum using relative volume, 1D change, and 5D change.
4. Appends the top-volume table and 2-5 candidate trade ideas to `memory/RESEARCH-LOG.md`.
5. Includes catalyst text based on volume/momentum, entry reference, suggested dry-run qty, 7% stop, 2:1 target, and risk-gate reminder.
6. Sends a concise Telegram summary.

Default decision: HOLD unless market-open revalidation confirms a candidate and deterministic gates pass.
