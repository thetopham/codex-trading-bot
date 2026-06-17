# Trade Log

## Day 0 Baseline
- Equity: unknown
- Cash: unknown
- Note: seed this with a real paper account EOD snapshot before scheduled daily summaries.

## EOD Snapshot — 2026-06-15

### Account
```json
{"account_blocked": false, "buying_power": "200000", "cash": "50000", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "200000", "equity": "50000", "long_market_value": "0", "pattern_day_trader": false, "portfolio_value": "50000", "position_market_value": "0", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[]
```

## Market-open Dry-run Intents — 2026-06-15

### INTC — APPROVED_DRY_RUN
- Qty: 15
- Reference price: 127.86
- Estimated cost: 1917.90
- Stop: 118.91
- Target: 145.76
- Catalyst: Top-volume momentum candidate: volume 124,565,199 vs avg 132,121,559; 1D 2.64%, 5D 18.47%.
- Gate reasons: none
- Broker action: none; DRY_RUN intent only.

### MU — APPROVED_DRY_RUN
- Qty: 1
- Reference price: 1087.99
- Estimated cost: 1087.99
- Stop: 1011.83
- Target: 1240.31
- Catalyst: Top-volume momentum candidate: volume 43,002,006 vs avg 54,651,240; 1D 10.84%, 5D 2.25%.
- Gate reasons: none
- Broker action: none; DRY_RUN intent only.

## Market-open Dry-run Intents — 2026-06-15

### MRVL — APPROVED_DRY_RUN
- Qty: 6
- Reference price: 308.88
- Estimated cost: 1853.28
- Stop: 287.26
- Target: 352.12
- Catalyst: Top-volume momentum candidate: volume 50,306,597 vs avg 79,218,239; 1D 10.43%, 5D 6.22%.
- Gate reasons: none
- Broker action: none; DRY_RUN intent only.

### POET — APPROVED_DRY_RUN
- Qty: 143
- Reference price: 13.93
- Estimated cost: 1991.99
- Stop: 12.95
- Target: 15.88
- Catalyst: Top-volume momentum candidate: volume 44,043,524 vs avg 38,254,302; 1D 11.17%, 5D 0.80%.
- Gate reasons: none
- Broker action: none; DRY_RUN intent only.


## EOD Snapshot — 2026-06-15

### Account
```json
{"account_blocked": false, "buying_power": "200000", "cash": "50000", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "200000", "equity": "50000", "long_market_value": "0", "pattern_day_trader": false, "portfolio_value": "50000", "position_market_value": "0", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[]
```

## Market-open TradingView MCP Candidates — 2026-06-16

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: no trade candidates in candidate file
- Liquidity filter: current top 65 stocks by reported volume
- Liquidity skips: none

No market-open candidates passed the TradingView MCP + top-volume liquidity intersection. No broker submissions attempted.

## Market-open TradingView MCP Candidates — 2026-06-16

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: ok
- Liquidity filter: current top 100 stocks by reported volume
- Liquidity skips: none

### HIMS — APPROVED_DRY_RUN
- Qty: 157
- Reference price: 31.65
- Estimated cost: 4969.05
- Risk at 10% stop: 496.9050
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 37.98
- MCP score: 65
- MCP evidence summary: scanner_hit,multi_timeframe
- MCP sources: top_gainers
- MCP notes: Simplified gate test candidate: one MCP technical setup plus liquidity plus SPY-relative strength. Optional multi-timeframe MCP returned data errors/low-confidence HOLD, so treat that as a risk note rather than a hard veto. Use 10% trailing stop and 1% portfolio-risk sizing.
- Catalyst: TradingView MCP top_gainers screen shows HIMS +6.304% on the 1D scan with RSI ~64.36 and volume ~16.0M; current Yahoo quote is 31.69, +5.04% on the day.
- Benchmark thesis: HIMS can beat SPY over the swing window because it is showing strong positive relative strength versus a slightly red SPY tape, has a liquid top-volume profile, and has a confirmed TradingView MCP top-gainer technical setup rather than a generic market-beta move.
- Relative strength vs SPY: 1D 5.30%, 5D 15.37%
- Gate reasons: none
- Broker action: paper_submit buy_ok=False trailing_stop_ok=False qty=157.

## Market-open TradingView MCP Candidates — 2026-06-16

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: ok
- Liquidity filter: current top 100 stocks by reported volume
- Liquidity skips: none

### HIMS — APPROVED_DRY_RUN
- Qty: 157
- Reference price: 31.73
- Estimated cost: 4981.61
- Risk at 10% stop: 498.1610
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 38.08
- MCP score: 65
- MCP evidence summary: scanner_hit,multi_timeframe
- MCP sources: top_gainers
- MCP notes: Simplified gate test candidate: one MCP technical setup plus liquidity plus SPY-relative strength. Optional multi-timeframe MCP returned data errors/low-confidence HOLD, so treat that as a risk note rather than a hard veto. Use 10% trailing stop and 1% portfolio-risk sizing.
- Catalyst: TradingView MCP top_gainers screen shows HIMS +6.304% on the 1D scan with RSI ~64.36 and volume ~16.0M; current Yahoo quote is 31.69, +5.04% on the day.
- Benchmark thesis: HIMS can beat SPY over the swing window because it is showing strong positive relative strength versus a slightly red SPY tape, has a liquid top-volume profile, and has a confirmed TradingView MCP top-gainer technical setup rather than a generic market-beta move.
- Relative strength vs SPY: 1D 5.30%, 5D 15.37%
- Gate reasons: none
- Broker action: paper_submit buy_ok=True trailing_stop_ok=False qty=157.


## Protective Stop Repair — 2026-06-16

- HIMS paper buy filled/opened: 157 shares at avg entry ~31.73.
- Initial market-open trailing-stop submit returned `trailing_stop_ok=False`, likely because the buy fill/position was not yet visible when the stop was submitted.
- Manual repair submitted a 10% GTC trailing stop for 157 HIMS shares.
- Alpaca paper stop order: `a91d311a-20ff-455f-870e-87a19a28a917`, status `new`, HWM 31.73, stop_price 28.557.


## EOD Snapshot — 2026-06-16

### Account
```json
{"account_blocked": false, "buying_power": "194017.67", "cash": "45018.39", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "194017.67", "equity": "49998.43", "long_market_value": "4980.04", "pattern_day_trader": false, "portfolio_value": "49998.43", "position_market_value": "4980.04", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[{"avg_entry_price": "31.73", "current_price": "31.72", "market_value": "4980.04", "qty": "157", "symbol": "HIMS", "unrealized_pl": "-1.57", "unrealized_plpc": "-0.00032"}]
```

### Benchmark
- Benchmark: SPY close $752.17
- Bot daily return: 0.00%
- SPY daily return: 0.00%
- Bot cumulative return: 0.00%
- SPY cumulative return: 0.00%
- Alpha vs SPY: 0.00%
- Drawdown: 0.00%
- Judgment: BASELINE: first benchmark row recorded; judge alpha after the next EOD snapshot.


## EOD Snapshot — 2026-06-16

### Account
```json
{"account_blocked": false, "buying_power": "193879.86", "cash": "45018.39", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "193879.86", "equity": "49949.21", "long_market_value": "4930.82", "pattern_day_trader": false, "portfolio_value": "49949.21", "position_market_value": "4930.82", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[{"avg_entry_price": "31.73", "current_price": "31.4065", "market_value": "4930.8205", "qty": "157", "symbol": "HIMS", "unrealized_pl": "-50.7895", "unrealized_plpc": "-0.0102"}]
```

### Benchmark
- Benchmark: SPY close $750.33
- Bot daily return: 0.00%
- SPY daily return: 0.00%
- Bot cumulative return: 0.00%
- SPY cumulative return: 0.00%
- Alpha vs SPY: 0.00%
- Drawdown: 0.00%
- Judgment: BASELINE: first benchmark row recorded; judge alpha after the next EOD snapshot.

## Market-open TradingView MCP Candidates — 2026-06-17

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: ok
- Liquidity filter: current top 59 stocks by reported volume
- Liquidity skips: HIMS:not_in_top_volume_liquidity_filter

### CPNG — APPROVED_DRY_RUN
- Qty: 261
- Reference price: 19.08
- Estimated cost: 4979.88
- Risk at 10% stop: 497.9880
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 22.90
- MCP score: 65
- MCP evidence summary: scanner_hit,optional_context,retryable_mcp_error
- MCP sources: top_gainers, compare_strategies
- MCP notes: SPY/SPX relative thesis: CPNG has MCP-confirmed top-gainer/upper-band expansion and positive 1D/5D relative strength versus a red SPY benchmark. Risks: CPNG's relative strength is weaker than HIMS, news/RSS returned no corroborating catalyst, and optional combined/multi-timeframe MCP checks hit retryable parser failures and did not add score. Perplexity optional corroboration failed with HTTP 401.
- Catalyst: TradingView MCP top_gainers 1D NYSE scan found CPNG +4.948% with close 18.03 above SMA20 16.22/EMA50 17.53 and above BB_upper 17.76, RSI 57.90, volume 23.3M.
- Benchmark thesis: CPNG can outperform SPY/SPX over the swing window because it has a TradingView MCP top-gainer upper-band expansion while SPY is negative on both 1D and 5D, and the liquidity filter shows CPNG positive relative strength versus SPY on both windows (+2.44% 1D and +4.84% 5D); the thesis is benchmark-relative momentum, not broad market beta.
- Relative strength vs SPY: 1D 2.44%, 5D 4.84%
- Gate reasons: none
- Broker action: paper_submit buy_ok=True trailing_stop_ok=False qty=261.
