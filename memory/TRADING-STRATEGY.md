# Trading Strategy

Mission: beat the S&P 500 / SPX benchmark over the challenge window while preserving paper-account discipline. Use SPY as the practical benchmark proxy for daily/weekly comparisons when SPX index data is unavailable from the active data source.

Safety boundary: Alpaca paper only unless explicitly changed later. Stocks only; no options.

## Benchmark Discipline
- Compare daily and weekly performance against SPY/SPX.
- A trade idea should have a plausible reason to outperform simply holding SPY over the same swing window.
- If the top-volume opportunity set is weak versus SPY momentum, default to HOLD or SPY-like benchmark exposure rather than forcing single-name risk.
- Weekly review must note whether the bot is ahead/behind SPY and why.

## Research Stack
- Primary liquidity filter: top 100 US equities by traded volume using Yahoo Finance/yfinance `most_actives`, plus forced watchlist symbols when needed.
- Top-volume is not the alpha engine; it only decides whether a name is liquid enough to consider.
- Primary alpha/screening layer: `atilaahmettaner/tradingview-mcp` via Hermes MCP tools.
- Use TradingView MCP for top gainers/losers, volume breakouts, smart volume, Bollinger/rating filters, combined analysis, multi-timeframe analysis, news/sentiment where useful, and SPY/SPX benchmark context.
- Write final pre-market trade candidates to `memory/PREMARKET-CANDIDATES.json`; market-open must order only from that file after intersecting with the current top-volume liquidity filter.
- Treat MCP outputs as research data, not automatic trade commands.

## Hard Rules
- Take every qualified TradingView MCP opportunity while cash is available and per-position risk gates pass; there is no fixed max-position or weekly-trade-count cap.
- Max per-position risk: 1% of portfolio equity at the required 10% stop.
- Position sizing formula: `floor((equity * 0.01 / 0.10) / entry_price)`, so a 10% stop risks at most ~1% of portfolio equity before slippage.
- Every new position requires a documented TradingView MCP-backed catalyst in today's `memory/PREMARKET-CANDIDATES.json`.
- Every new position gets a 10% GTC trailing stop in paper/live-approved modes.
- Cut losers at -7%.
- Tighten trail to 7% at +15%, 5% at +20%.
- Never move a stop down.
- Telegram notifications are sparse: action taken or required daily/weekly summary.
