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

## Stop Repair — 2026-06-17T15:52:04Z

- CPNG paper position was open with 261 shares and no open protective sell stop.
- Cause: market-open buy succeeded, but the immediate trailing-stop submit returned `trailing_stop_ok=False`; no CPNG stop order existed in Alpaca open orders.
- Repair submitted a 10% GTC trailing stop for 261 CPNG shares.
- Alpaca paper stop order: `a5fbce82-68e4-48b3-8d6d-1b5bdee52e88`, status `new`, HWM 19.345, stop_price 17.4105.


## EOD Snapshot — 2026-06-17

### Account
```json
{"account_blocked": false, "buying_power": "187938.6", "cash": "40034.96", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "187938.6", "equity": "49963.09", "long_market_value": "9928.13", "pattern_day_trader": false, "portfolio_value": "49963.09", "position_market_value": "9928.13", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[{"avg_entry_price": "19.093563", "current_price": "18.88", "market_value": "4927.68", "qty": "261", "symbol": "CPNG", "unrealized_pl": "-55.739943", "unrealized_plpc": "-0.01119"}, {"avg_entry_price": "31.73", "current_price": "31.85", "market_value": "5000.45", "qty": "157", "symbol": "HIMS", "unrealized_pl": "18.84", "unrealized_plpc": "0.00378"}]
```

### Benchmark
- Benchmark: SPY close $740.96
- Bot daily return: +0.03%
- SPY daily return: -1.25%
- Bot cumulative return: +0.03%
- SPY cumulative return: -1.25%
- Alpha vs SPY: +1.28%
- Drawdown: 0.00%
- Judgment: AHEAD: Codex is beating SPY by +1.28% cumulative alpha.

## Market-open TradingView MCP Candidates — 2026-06-18

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: ok
- Liquidity filter: current top 96 stocks by reported volume
- Liquidity skips: AMC:not_in_top_volume_liquidity_filter

No market-open candidates passed the TradingView MCP + top-volume liquidity intersection. No broker submissions attempted.


## EOD Snapshot — 2026-06-18

### Account
```json
{"account_blocked": false, "buying_power": "188841.31", "cash": "40034.95", "currency": "USD", "daytrade_count": 0, "daytrading_buying_power": "188841.31", "equity": "50285.49", "long_market_value": "10250.54", "pattern_day_trader": false, "portfolio_value": "50285.49", "position_market_value": "10250.54", "short_market_value": "0", "status": "ACTIVE", "trade_suspended_by_user": false, "trading_blocked": false, "transfers_blocked": false}
```

### Positions
```json
[{"avg_entry_price": "19.093563", "current_price": "18.04", "market_value": "4708.44", "qty": "261", "symbol": "CPNG", "unrealized_pl": "-274.979943", "unrealized_plpc": "-0.05518"}, {"avg_entry_price": "31.73", "current_price": "35.3", "market_value": "5542.1", "qty": "157", "symbol": "HIMS", "unrealized_pl": "560.49", "unrealized_plpc": "0.11251"}]
```

### Benchmark
- Benchmark: SPY close $746.74
- Bot daily return: +0.65%
- SPY daily return: +0.78%
- Bot cumulative return: +0.67%
- SPY cumulative return: -0.48%
- Alpha vs SPY: +1.15%
- Drawdown: 0.00%
- Judgment: AHEAD: Codex is beating SPY by +1.15% cumulative alpha.

## Market-open TradingView MCP Candidates — 2026-06-19

- Candidate source: memory/PREMARKET-CANDIDATES.json
- Candidate file status: ok
- Liquidity filter: current top 100 stocks by reported volume
- Liquidity skips: none

### BFLY — APPROVED_DRY_RUN
- Qty: 565
- Reference price: 8.90
- Estimated cost: 5028.50
- Risk at 10% stop: 502.8500
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 10.68
- MCP score: 84
- MCP evidence summary: scanner_hit,volume_confirmation,optional_context,retryable_mcp_error
- MCP sources: top_gainers, compare_strategies
- MCP notes: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows BFLY 1D +55.87% and 5D +94.75%, relative to SPY +55.09% 1D and +93.50% 5D. Outperformance thesis: BFLY can beat SPY/SPX over the swing window because it has a fresh MCP-confirmed upper-band breakout with exceptional single-name volume/relative momentum rather than generic market beta. Optional 6mo daily compare_strategies context favored RSI at +90.59% over 2 trades vs buy-and-hold +60.39%. Risks: RSI >84 and the 5D move is extremely extended, so reversal/slippage risk is high; combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Catalyst: TradingView MCP NYSE top_gainers 1D scan found BFLY +23.440% with close 8.90 above SMA20 5.153, EMA50 4.886, and BB_upper 7.112; RSI 84.59 and TradingView volume 60.5M confirm an upper-band volume breakout.
- Benchmark thesis: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows BFLY 1D +55.87% and 5D +94.75%, relative to SPY +55.09% 1D and +93.50% 5D. Outperformance thesis: BFLY can beat SPY/SPX over the swing window because it has a fresh MCP-confirmed upper-band breakout with exceptional single-name volume/relative momentum rather than generic market beta. Optional 6mo daily compare_strategies context favored RSI at +90.59% over 2 trades vs buy-and-hold +60.39%. Risks: RSI >84 and the 5D move is extremely extended, so reversal/slippage risk is high; combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Relative strength vs SPY: 1D 0%, 5D 0%
- Gate reasons: none
- Broker action: paper_submit buy_ok=True trailing_stop_ok=False qty=565 stop_response=attempt 1: curl: (22) The requested URL returned error: 403
; attempt 2: curl: (22) The requested URL returned error: 403
; attempt 3: curl: (22) The requested URL returned error: 403
.

### AMC — APPROVED_DRY_RUN
- Qty: 1891
- Reference price: 2.66
- Estimated cost: 5030.06
- Risk at 10% stop: 503.0060
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 3.19
- MCP score: 77
- MCP evidence summary: scanner_hit,optional_context,retryable_mcp_error
- MCP sources: top_gainers, compare_strategies
- MCP notes: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows AMC 1D +6.39% and 5D +58.10%, relative to SPY +5.61% 1D and +56.85% 5D. Outperformance thesis: AMC can beat SPY/SPX over the swing window if the MCP-confirmed high-volume upper-band breakout and meme/short-squeeze momentum continue; this is stock-specific relative strength, not generic market beta. Optional 6mo daily compare_strategies context ranked MACD best at +34.13% over 3 trades while buy-and-hold was +61.71%. Risks: RSI ~78 is overbought, meme-stock reversal risk is high, combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Catalyst: TradingView MCP NYSE top_gainers 1D scan found AMC +6.792% with close 2.83 above SMA20 2.001, EMA50 1.784, and BB_upper 2.750; RSI 77.72 and TradingView volume 81.4M confirm a liquid upper-band momentum breakout.
- Benchmark thesis: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows AMC 1D +6.39% and 5D +58.10%, relative to SPY +5.61% 1D and +56.85% 5D. Outperformance thesis: AMC can beat SPY/SPX over the swing window if the MCP-confirmed high-volume upper-band breakout and meme/short-squeeze momentum continue; this is stock-specific relative strength, not generic market beta. Optional 6mo daily compare_strategies context ranked MACD best at +34.13% over 3 trades while buy-and-hold was +61.71%. Risks: RSI ~78 is overbought, meme-stock reversal risk is high, combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Relative strength vs SPY: 1D 0%, 5D 0%
- Gate reasons: none
- Broker action: paper_submit buy_ok=True trailing_stop_ok=False qty=1891 stop_response=attempt 1: curl: (22) The requested URL returned error: 403
; attempt 2: curl: (22) The requested URL returned error: 403
; attempt 3: curl: (22) The requested URL returned error: 403
.

### RKT — APPROVED_DRY_RUN
- Qty: 348
- Reference price: 14.42
- Estimated cost: 5018.16
- Risk at 10% stop: 501.8160
- Stop: 10% trailing stop; paper order uses trail_percent=10
- Target: 17.30
- MCP score: 72
- MCP evidence summary: scanner_hit,optional_context,retryable_mcp_error
- MCP sources: top_gainers, compare_strategies
- MCP notes: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows RKT 1D +9.08% and 5D +13.99%, relative to SPY +8.30% 1D and +12.75% 5D. Outperformance thesis: RKT can beat SPY/SPX over the swing window because it has a current MCP top-gainer setup, positive 1D and 5D benchmark-relative strength, and a moderate RSI compared with the more extended squeeze names. Risks: close is still below BB_upper 14.894, optional 6mo daily compare_strategies context was weak (buy-and-hold -24.42% and no positive strategy leader), combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Catalyst: TradingView MCP NYSE top_gainers 1D scan found RKT +7.013% with close 14.42 above SMA20 13.597 and EMA50 14.238; RSI 54.76 and TradingView volume 52.8M show a liquid momentum turn that is less overbought than BFLY/AMC.
- Benchmark thesis: SPY benchmark proxy from the pre-run: 1D +0.78%, 5D +1.25%. Liquidity filter shows RKT 1D +9.08% and 5D +13.99%, relative to SPY +8.30% 1D and +12.75% 5D. Outperformance thesis: RKT can beat SPY/SPX over the swing window because it has a current MCP top-gainer setup, positive 1D and 5D benchmark-relative strength, and a moderate RSI compared with the more extended squeeze names. Risks: close is still below BB_upper 14.894, optional 6mo daily compare_strategies context was weak (buy-and-hold -24.42% and no positive strategy leader), combined_analysis technical block failed with retryable parser errors after retry, sentiment/news had 0 posts/items, and optional Perplexity returned HTTP 401. Market-open must revalidate liquidity/quote/cash and apply the 10% trailing stop / 1% portfolio-risk sizing formula.
- Relative strength vs SPY: 1D 0%, 5D 0%
- Gate reasons: none
- Broker action: paper_submit buy_ok=True trailing_stop_ok=False qty=348 stop_response=attempt 1: curl: (22) The requested URL returned error: 403
; attempt 2: curl: (22) The requested URL returned error: 403
; attempt 3: curl: (22) The requested URL returned error: 403
.
