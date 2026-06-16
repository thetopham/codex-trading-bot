from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

from .premarket import CANDIDATES_FILE
from .research import BENCHMARK_SYMBOL, Candidate, top_volume_candidates


def _benchmark_proxy(top: list[Candidate]) -> dict[str, str]:
    if not top:
        return {
            "symbol": BENCHMARK_SYMBOL,
            "day_change_pct": "0",
            "five_day_change_pct": "0",
            "note": "benchmark unavailable from current yfinance pull",
        }
    sample = top[0]
    return {
        "symbol": sample.benchmark_symbol,
        "day_change_pct": str(sample.benchmark_day_change_pct),
        "five_day_change_pct": str(sample.benchmark_five_day_change_pct),
        "rule": "Final candidates must include a specific thesis for why the stock can outperform this benchmark proxy over the swing window.",
    }


def _candidate_schema(today: date) -> dict[str, object]:
    return {
        "date": today.isoformat(),
        "source": "TradingView MCP simplified screen over top-100-volume liquidity filter",
        "candidates": [
            {
                "symbol": "NVDA",
                "exchange": "NASDAQ",
                "decision": "candidate",
                "mcp_score": "0-100 score; optional because market-open can auto-score source evidence for ordering",
                "sources": ["volume_breakout"],
                "catalyst": "Concrete TradingView MCP-backed technical setup; required for market-open gate",
                "benchmark": {
                    "symbol": BENCHMARK_SYMBOL,
                    "candidate_1d_pct": "candidate 1D return from top_volume table if available",
                    "benchmark_1d_pct": "SPY 1D return from benchmark_proxy",
                    "relative_strength_1d_pct": "candidate_1d_pct - benchmark_1d_pct",
                    "candidate_5d_pct": "candidate 5D return from top_volume table if available",
                    "benchmark_5d_pct": "SPY 5D return from benchmark_proxy",
                    "relative_strength_5d_pct": "candidate_5d_pct - benchmark_5d_pct",
                    "outperformance_thesis": "Why this can beat SPY/SPX; market-open rejects generic beta trades without this.",
                },
                "notes": "Risks plus optional MCP confirmation/news/backtest context only when useful; do not require every MCP tool.",
            }
        ],
    }


def main() -> int:
    today = date.today()
    top, legacy_momentum = top_volume_candidates(limit=100, picks=12)
    liquidity_symbols = [c.symbol for c in top[:100]]
    payload = {
        "date": today.isoformat(),
        "source": "yfinance most_actives/direct OHLCV top-volume liquidity filter with SPY-relative context",
        "purpose": "Liquidity filter only. Final candidates need one TradingView MCP technical setup, liquidity intersection, and a SPY/SPX outperformance thesis. Additional MCP tools are score/context, not hard gates.",
        "forced_watchlist_note": "FORCED_WATCHLIST symbols such as SPCX are fetched directly and can enter the top-100 filter if actual volume qualifies.",
        "benchmark_proxy": _benchmark_proxy(top),
        "candidate_output_file": f"memory/{CANDIDATES_FILE}",
        "market_open_rejection_rules": [
            "Reject candidates not in liquidity_symbols at market open.",
            "Reject candidates without at least one TradingView MCP technical setup.",
            "Reject candidates without a specific SPY/SPX outperformance thesis.",
            "Reject candidates whose deterministic risk sizing/gates fail.",
        ],
        "tradingview_mcp_minimal_gate": {
            "required": "one TradingView MCP technical setup",
            "examples": [
                "volume_breakout",
                "smart_volume",
                "rating_filter",
                "bollinger",
                "top_gainers",
                "combined_analysis",
                "multi_timeframe",
            ],
            "not_required": [
                "news",
                "sentiment",
                "backtest",
                "walk_forward",
                "multiple scan agreement",
                "both NYSE and NASDAQ scans every day",
            ],
        },
        "mcp_score_guidance": {
            "scanner_hit": 25,
            "combined_analysis": 25,
            "multi_timeframe": 15,
            "volume_confirmation": 15,
            "positive_relative_strength_vs_spy": "10-20",
            "clear_catalyst_or_news_context": 10,
            "supportive_backtest_or_walk_forward": 10,
            "major_risk_warning": -20,
            "candidate_band": ">=70",
            "watch_band": "50-69",
            "reject_band": "<50",
        },
        "candidate_schema": _candidate_schema(today),
        "liquidity_symbols": liquidity_symbols,
        "top_volume": [asdict(c) for c in top[:100]],
        "benchmark_relative_momentum_reference_only": [asdict(c) for c in legacy_momentum],
    }
    print(json.dumps(payload, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
