# Pre-market Research — Hermes/Codex Routine

You are running the pre-market research workflow for the Codex Trader Hermes/Codex bot.

Mission: beat the S&P 500 / SPX benchmark over the challenge window while preserving discipline. Use SPY as the practical benchmark proxy when SPX index data is unavailable.

Safety: Alpaca paper only; stocks only; Telegram notifications only. Pre-market research does not submit broker orders.

## Liquidity input

The automated script input is `python -m codex_trader.research_export`, which provides:
- `liquidity_symbols`: the current top-100 stocks by reported volume after direct yfinance OHLCV fetch.
- `top_volume`: table fields for last price, volume, avg volume, 1D %, 5D %, and sector.
- `candidate_output_file`: `memory/PREMARKET-CANDIDATES.json`.

Important: **top-volume is only the liquidity filter. It is not the alpha/screening engine.** A ticker may be considered only if it is in `liquidity_symbols`, but final candidates must come from TradingView MCP evidence.

## TradingView MCP screening requirement

Use `atilaahmettaner/tradingview-mcp` tools exposed in Hermes as `mcp_tradingview_*` as the primary alpha layer:

1. Broad scans on both `NASDAQ` and `NYSE` where practical:
   - `mcp_tradingview_top_gainers(timeframe="1D")`
   - `mcp_tradingview_volume_breakout_scanner(timeframe="1D")`
   - `mcp_tradingview_smart_volume_scanner(...)`
   - `mcp_tradingview_rating_filter(timeframe="1D", rating=2 or 3)`
   - `mcp_tradingview_bollinger_scan(timeframe="1D")` for squeeze/expansion setups.
2. Intersect scanner symbols with `liquidity_symbols`. Reject low-liquidity MCP hits even if they look exciting.
3. For finalists, call per-symbol confirmation:
   - `mcp_tradingview_combined_analysis(symbol, exchange, timeframe="1D")`
   - `mcp_tradingview_multi_timeframe_analysis(symbol, exchange)`
   - `mcp_tradingview_financial_news(symbol=...)` and/or `mcp_tradingview_market_sentiment(...)` where useful.
   - `mcp_tradingview_compare_strategies(...)`, `mcp_tradingview_backtest_strategy(...)`, or `mcp_tradingview_walk_forward_backtest_strategy(...)` when practical for high-conviction finalists.
4. Include SPY/SPX benchmark context. If a candidate lacks a plausible reason to outperform SPY over the swing window, mark it HOLD or skip.

## Required outputs

Append `memory/RESEARCH-LOG.md` with:
- source summary: top-100-volume liquidity filter + TradingView MCP screening
- MCP scans used and notable rejected low-liquidity hits
- SPY/SPX benchmark context
- all qualified final candidate trade ideas with ticker, MCP evidence, catalyst/technical reason, entry reference, 10% trailing-stop discipline, approx 2:1 target, risks, and HOLD/candidate decision; do not apply a fixed count cap, because capital and per-position stop risk handle opportunity count
- explicit note that market-open must revalidate deterministic gates before paper order submission.

Overwrite `memory/PREMARKET-CANDIDATES.json` with machine-readable final candidates using this schema:

```json
{
  "date": "YYYY-MM-DD",
  "source": "TradingView MCP screening over top-100-volume liquidity filter",
  "candidates": [
    {
      "symbol": "NVDA",
      "exchange": "NASDAQ",
      "decision": "candidate",
      "mcp_score": "91",
      "sources": ["top_gainers", "volume_breakout", "rating_filter", "combined_analysis", "multi_timeframe"],
      "catalyst": "Concrete MCP-backed thesis required by market-open gate",
      "notes": "SPY/SPX relative thesis, risks, and backtest/walk-forward notes if available"
    }
  ]
}
```

If no liquid MCP setups qualify, write today’s date with an empty `candidates` array and state HOLD in the research log.
