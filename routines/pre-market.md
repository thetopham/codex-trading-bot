# Pre-market Research — Hermes/Codex Routine

You are running the pre-market research workflow for the Codex Trader Hermes/Codex bot.

Mission: beat the S&P 500 / SPX benchmark over the challenge window while preserving discipline. Use SPY as the practical benchmark proxy when SPX index data is unavailable.

Safety: Alpaca paper only; stocks only; Telegram notifications only. Pre-market research does not submit broker orders.

## Liquidity input

The automated script input is `python -m codex_trader.research_export`, which provides:
- `liquidity_symbols`: the current top-100 stocks by reported volume after direct yfinance OHLCV fetch.
- `top_volume`: table fields for last price, volume, avg volume, 1D %, 5D %, SPY-relative 1D/5D %, and sector.
- `candidate_output_file`: `memory/PREMARKET-CANDIDATES.json`.

Important: **top-volume is only the liquidity filter. It is not the alpha/screening engine.** A ticker may be considered only if it is in `liquidity_symbols`, but final candidates must come from TradingView MCP evidence.

## Simplified TradingView MCP requirement

Do **not** require a pile of MCP tools to agree. The hard MCP requirement is intentionally small:

1. Candidate is in `liquidity_symbols`.
2. Candidate has **one TradingView MCP technical setup**.
   - Examples: `volume_breakout`, `smart_volume`, `rating_filter`, `bollinger`, `top_gainers`, `combined_analysis`, or `multi_timeframe`.
   - A single strong `combined_analysis` or a single scanner hit is enough to proceed to scoring.
3. Candidate has a specific SPY/SPX outperformance thesis.
4. Market-open risk/safety gates pass later.

Everything else is optional score/context, not a veto.

## Suggested lean daily MCP flow

Pick one of these paths; do not run every tool by default:

- **Scanner path:** run 1–2 broad scans on NASDAQ/NYSE, intersect hits with `liquidity_symbols`, then score finalists.
  - Good defaults: `mcp_tradingview_volume_breakout_scanner(timeframe="1D")`, `mcp_tradingview_smart_volume_scanner(...)`, or `mcp_tradingview_rating_filter(timeframe="1D", rating=2 or 3)`.
- **Known-name path:** for high-priority/forced watchlist names, call `mcp_tradingview_combined_analysis(symbol, exchange, timeframe="1D")` directly.
- **Optional confirmation:** use `multi_timeframe`, news/sentiment, or backtest/walk-forward only when it materially changes conviction or breaks a tie.

## MCP reliability / rate-limit policy

TradingView MCP sometimes returns transient parser shapes such as `Expecting value: line 1 column 1`, empty/non-JSON upstream responses, timeouts, or explicit `429`/rate-limit messages. Treat these as **retryable health events**, not as bearish/bullish evidence.

Operational rules:

1. **No burst fan-out.** Do not call many MCP tools in parallel. Keep `max_parallel_calls=1` for TradingView MCP during pre-market.
2. **Small call budget.** Run only 1–2 broad scanner calls before liquidity intersection. Run `combined_analysis` or `multi_timeframe` only for the top 1–3 liquid finalists or to break ties.
3. **Retry only retryable errors.** If an MCP call returns `Expecting value`, empty/non-JSON content, timeout, or 429/rate-limit text, wait 10–30 seconds and retry at most twice.
4. **Do not count failed checks as evidence.** A failed optional `multi_timeframe`/`combined_analysis` check should be logged as `retryable_error` and must not add score or satisfy the MCP hard gate.
5. **Do not veto a proven setup because optional context failed.** If one successful scanner/setup exists, failed optional checks are risk/health context only.
6. **Fail closed if no successful setup exists.** If every MCP check failed or returned HOLD/NO TRADE, write an empty candidate file and state HOLD.

Use structured `mcp_checks` in candidate JSON when possible:

```json
"mcp_checks": [
  {"tool": "top_gainers", "status": "ok", "evidence": "1D top-gainer hit with liquid volume"},
  {"tool": "multi_timeframe", "status": "retryable_error", "error": "Expecting value: line 1 column 1"}
]
```

Only checks with `status: "ok"` / constructive evidence count as successful MCP evidence.

## MCP score guidance

Use this as a scoring model, not as hard gates:

| Evidence | Points |
|---|---:|
| Any TradingView MCP scanner hit | +25 |
| `combined_analysis` bullish/constructive | +25 |
| Multi-timeframe alignment | +15 |
| Volume breakout / smart volume / volume confirmation | +15 |
| Positive relative strength vs SPY | +10 to +20 |
| Clear catalyst/news/context | +10 |
| Backtest/walk-forward supports setup | +10 |
| Major overextension/bearish risk warning | -20 |

Decision bands:

- `>=70`: candidate if benchmark thesis and liquidity pass.
- `50–69`: watch/HOLD unless there is a very clear benchmark-relative reason.
- `<50`: reject/HOLD.

The Python market-open loader does **not** require every score component. It only enforces one MCP setup + benchmark thesis + liquidity/risk/safety.

## Required outputs

Append `memory/RESEARCH-LOG.md` with:
- source summary: top-100-volume liquidity filter + simplified TradingView MCP screen
- which 1–2 MCP checks were used, retryable MCP errors/retries, and notable rejected low-liquidity hits
- SPY/SPX benchmark context and the reason each candidate can beat the benchmark rather than merely move with market beta
- final candidate trade ideas with ticker, MCP evidence, score, catalyst/technical reason, entry reference, 10% trailing-stop discipline, approx 2:1 target, risks, and HOLD/candidate decision
- explicit note that market-open must revalidate deterministic gates before paper order submission.

Overwrite `memory/PREMARKET-CANDIDATES.json` with machine-readable final candidates using this schema:

```json
{
  "date": "YYYY-MM-DD",
  "source": "TradingView MCP simplified screen over top-100-volume liquidity filter",
  "candidates": [
    {
      "symbol": "NVDA",
      "exchange": "NASDAQ",
      "decision": "candidate",
      "mcp_score": "75",
      "sources": ["volume_breakout"],
      "mcp_checks": [
        {"tool": "volume_breakout", "status": "ok", "evidence": "One successful TradingView MCP technical setup"},
        {"tool": "multi_timeframe", "status": "retryable_error", "error": "Optional retryable parser/empty-response failure, if any"}
      ],
      "catalyst": "Concrete TradingView MCP-backed technical setup required by market-open gate",
      "benchmark": {
        "symbol": "SPY",
        "candidate_1d_pct": "2.30",
        "benchmark_1d_pct": "0.40",
        "relative_strength_1d_pct": "1.90",
        "candidate_5d_pct": "6.10",
        "benchmark_5d_pct": "1.20",
        "relative_strength_5d_pct": "4.90",
        "outperformance_thesis": "Why this can beat SPY/SPX over the intended swing window; required by market-open gate"
      },
      "notes": "Risks, optional MCP confirmation, optional news/Perplexity corroboration, and backtest/walk-forward notes only if useful"
    }
  ]
}
```

If no liquid MCP setups qualify, write today’s date with an empty `candidates` array and state HOLD in the research log.
