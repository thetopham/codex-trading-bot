# Trading Strategy

Mission: beat the S&P 500 / SPX benchmark over the challenge window while preserving paper-account discipline. Use SPY as the practical benchmark proxy for daily/weekly comparisons when SPX index data is unavailable from the active data source.

Safety boundary: Alpaca paper only unless explicitly changed later. Stocks only; no options.

## Benchmark Discipline
- Compare daily and weekly performance against SPY/SPX.
- A trade idea should have a plausible reason to outperform simply holding SPY over the same swing window.
- If the top-volume opportunity set is weak versus SPY momentum, default to HOLD or SPY-like benchmark exposure rather than forcing single-name risk.
- Weekly review must note whether the bot is ahead/behind SPY and why.

## Research Stack
- Primary universe: top 100 US equities by traded volume using Yahoo Finance/yfinance `most_actives`, plus forced watchlist symbols when needed.
- Primary technical overlay: `atilaahmettaner/tradingview-mcp` via Hermes MCP tools.
- Use TradingView MCP for top gainers/losers, volume breakouts, Bollinger/rating filters, combined analysis, multi-timeframe analysis, news/sentiment where useful, and SPY/SPX benchmark context.
- Treat MCP outputs as research data, not automatic trade commands.

## Hard Rules
- Max 6 open positions.
- Max 20% of equity per position.
- Max 3 new trades per week.
- Every new position requires a documented catalyst or technical reason in today's research log.
- Every new position gets a 10% GTC trailing stop in paper/live-approved modes.
- Cut losers at -7%.
- Tighten trail to 7% at +15%, 5% at +20%.
- Never move a stop down.
- Telegram notifications are sparse: action taken or required daily/weekly summary.
