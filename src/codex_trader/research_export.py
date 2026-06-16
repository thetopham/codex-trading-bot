from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

from .premarket import CANDIDATES_FILE
from .research import top_volume_candidates


def main() -> int:
    top, legacy_momentum = top_volume_candidates(limit=100, picks=12)
    liquidity_symbols = [c.symbol for c in top[:100]]
    payload = {
        "date": date.today().isoformat(),
        "source": "yfinance most_actives/direct OHLCV top-volume liquidity filter",
        "purpose": "Liquidity filter only. Final candidates must be selected by TradingView MCP scanners, then intersected with liquidity_symbols.",
        "forced_watchlist_note": "FORCED_WATCHLIST symbols such as SPCX are fetched directly and can enter the top-100 filter if actual volume qualifies.",
        "candidate_output_file": f"memory/{CANDIDATES_FILE}",
        "tradingview_mcp_required_tools": [
            "mcp_tradingview_top_gainers(exchange=NASDAQ/NYSE, timeframe=1D)",
            "mcp_tradingview_volume_breakout_scanner(exchange=NASDAQ/NYSE, timeframe=1D)",
            "mcp_tradingview_smart_volume_scanner(exchange=NASDAQ/NYSE)",
            "mcp_tradingview_rating_filter(exchange=NASDAQ/NYSE, timeframe=1D, rating=2 or 3)",
            "mcp_tradingview_bollinger_scan(exchange=NASDAQ/NYSE, timeframe=1D)",
            "mcp_tradingview_combined_analysis(symbol, exchange, timeframe=1D) for finalists",
            "mcp_tradingview_multi_timeframe_analysis(symbol, exchange) for finalists",
            "mcp_tradingview_compare_strategies / walk_forward_backtest_strategy where practical",
            "mcp_tradingview_financial_news / market_sentiment for catalyst validation",
        ],
        "candidate_schema": {
            "date": date.today().isoformat(),
            "source": "TradingView MCP screening over top-100-volume liquidity filter",
            "candidates": [
                {
                    "symbol": "NVDA",
                    "exchange": "NASDAQ",
                    "decision": "candidate",
                    "mcp_score": "0-100 numeric score from the pre-market agent",
                    "sources": ["top_gainers", "volume_breakout", "rating_filter", "combined_analysis", "multi_timeframe"],
                    "catalyst": "Concrete TradingView MCP-backed thesis; required for market-open gate",
                    "notes": "Risks, SPY/SPX relative thesis, backtest/walk-forward notes if available",
                }
            ],
        },
        "liquidity_symbols": liquidity_symbols,
        "top_volume": [asdict(c) for c in top[:100]],
        "legacy_momentum_reference_only": [asdict(c) for c in legacy_momentum],
    }
    print(json.dumps(payload, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
