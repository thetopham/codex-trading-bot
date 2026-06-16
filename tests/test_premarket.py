from datetime import date
from decimal import Decimal

from codex_trader.premarket import filter_signals_by_liquidity, load_premarket_signals, normalize_symbol
from codex_trader.research import Candidate


def candidate(symbol: str, volume: int = 1000000) -> Candidate:
    return Candidate(
        symbol=symbol,
        last_price=Decimal("100.00"),
        volume=volume,
        avg_volume=volume,
        day_change_pct=Decimal("1.00"),
        five_day_change_pct=Decimal("2.00"),
        score=Decimal("5.00"),
        sector="technology",
    )


def test_normalize_symbol_strips_exchange_prefix():
    assert normalize_symbol("NASDAQ:NVDA") == "NVDA"
    assert normalize_symbol("nyse:uber") == "UBER"


def test_load_premarket_signals_requires_today_and_candidate_decision(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {"symbol": "NASDAQ:NVDA", "decision": "candidate", "mcp_score": "91", "sources": ["top_gainers"], "catalyst": "MCP bullish volume breakout"},
            {"symbol": "TSLA", "decision": "hold", "mcp_score": "88", "sources": ["rating_filter"], "catalyst": "MCP says hold"},
            {"symbol": "AAPL", "decision": "candidate", "mcp_score": "70", "sources": ["rating_filter"], "catalyst": ""}
          ]
        }
        """
    )
    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))
    assert status == "ok"
    assert [s.symbol for s in signals] == ["NVDA"]
    assert signals[0].mcp_score == Decimal("91")
    assert signals[0].sources == ("top_gainers",)


def test_load_premarket_signals_rejects_stale_file(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text('{"date":"2026-06-15","candidates":[]}')
    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))
    assert signals == []
    assert "!= today" in status


def test_filter_signals_by_liquidity_intersects_top_volume_and_sorts_by_mcp_score(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {"symbol": "NVDA", "decision": "candidate", "mcp_score": "80", "sources": ["combined_analysis"], "catalyst": "confirmed"},
            {"symbol": "ILLIQ", "decision": "candidate", "mcp_score": "99", "sources": ["top_gainers"], "catalyst": "not liquid"},
            {"symbol": "AMD", "decision": "candidate", "mcp_score": "90", "sources": ["volume_breakout"], "catalyst": "confirmed"}
          ]
        }
        """
    )
    signals, _ = load_premarket_signals(tmp_path, today=date(2026, 6, 16))
    selected, skipped = filter_signals_by_liquidity(signals, [candidate("NVDA"), candidate("AMD")], limit=2)
    assert [signal.symbol for signal, _ in selected] == ["AMD", "NVDA"]
    assert skipped == ["ILLIQ:not_in_top_volume_liquidity_filter"]
