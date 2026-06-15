# Pre-market Research — Hermes/Codex Routine

You are running the pre-market research workflow for the Codex Trader Hermes/Codex bot.

Mission: beat the S&P 500 / SPX benchmark over the challenge window while preserving discipline. Use SPY as the practical benchmark proxy when SPX index data is unavailable.

Safety: Alpaca paper only; stocks only; Telegram notifications only. Pre-market research does not submit broker orders.

The automated script input is `codex-trader pre-market-research` / `python -m codex_trader.research_export`, which:
1. Uses Yahoo Finance daily OHLCV via `yfinance` — no Perplexity dependency.
2. Starts from Yahoo Finance `most_actives` top-volume US equities plus forced watchlist symbols when configured.
3. Ranks the latest data by volume and scores positive momentum using relative volume, 1D change, and 5D change.

Research overlay requirement:
- Use the `atilaahmettaner/tradingview-mcp` tools exposed in Hermes as `mcp_tradingview_*` for technical research.
- Prefer: `top_gainers`, `volume_breakout_scanner`, `rating_filter`, `combined_analysis`, `multi_timeframe_analysis`, and `financial_news`/`market_sentiment` where useful.
- Include SPY/SPX benchmark context. If a candidate does not have a plausible reason to outperform SPY over the swing window, mark it HOLD or skip.
- Treat MCP output as research data, not a trade command.

Write `memory/RESEARCH-LOG.md` with:
- source summary: yfinance top-volume + TradingView MCP overlay
- SPY/SPX benchmark context
- market/technical context
- 2-5 candidate trade ideas with ticker, catalyst/technical reason, entry reference, 7% stop, approx 2:1 target, risks, and HOLD/candidate decision
- explicit note that market-open must revalidate deterministic gates before paper order submission.
