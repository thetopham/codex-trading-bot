from datetime import date
from decimal import Decimal

from codex_trader.premarket import filter_signals_by_liquidity, is_retryable_mcp_error, load_premarket_signals, normalize_symbol
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
            {
              "symbol": "NASDAQ:NVDA",
              "decision": "candidate",
              "mcp_score": "91",
              "sources": ["top_gainers", "combined_analysis"],
              "catalyst": "TradingView MCP bullish volume breakout",
              "benchmark": {
                "symbol": "SPY",
                "relative_strength_1d_pct": "1.25",
                "relative_strength_5d_pct": "4.50",
                "outperformance_thesis": "NVDA shows relative strength versus SPY and can outperform the benchmark if the MCP volume breakout follows through."
              }
            },
            {"symbol": "TSLA", "decision": "hold", "mcp_score": "88", "sources": ["rating_filter"], "catalyst": "MCP says hold"},
            {"symbol": "AAPL", "decision": "candidate", "mcp_score": "70", "sources": ["rating_filter"], "catalyst": ""}
          ]
        }
        """
    )
    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))
    assert status.startswith("ok")
    assert [s.symbol for s in signals] == ["NVDA"]
    assert signals[0].mcp_score == Decimal("91")
    assert signals[0].sources == ("top_gainers", "combined_analysis")
    assert signals[0].benchmark_symbol == "SPY"
    assert signals[0].relative_strength_5d_pct == Decimal("4.50")
    assert "outperform" in signals[0].benchmark_thesis


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
            {
              "symbol": "NVDA",
              "decision": "candidate",
              "mcp_score": "80",
              "sources": ["combined_analysis"],
              "catalyst": "confirmed TradingView MCP setup",
              "benchmark_thesis": "NVDA has relative strength versus SPY and may outperform SPY if AI semis keep leading."
            },
            {
              "symbol": "ILLIQ",
              "decision": "candidate",
              "mcp_score": "99",
              "sources": ["top_gainers"],
              "catalyst": "not liquid but TradingView MCP says strong",
              "benchmark_thesis": "ILLIQ has relative strength versus SPY and may outperform the SPY benchmark."
            },
            {
              "symbol": "AMD",
              "decision": "candidate",
              "mcp_score": "90",
              "sources": ["volume_breakout"],
              "catalyst": "confirmed TradingView MCP volume breakout",
              "benchmark": {"symbol": "SPY", "relative_strength_5d_pct": "2.10", "thesis": "AMD has relative strength versus SPY and can beat the benchmark if the breakout holds."}
            }
          ]
        }
        """
    )
    signals, _ = load_premarket_signals(tmp_path, today=date(2026, 6, 16))
    selected, skipped = filter_signals_by_liquidity(signals, [candidate("NVDA"), candidate("AMD")], limit=2)
    assert [signal.symbol for signal, _ in selected] == ["AMD", "NVDA"]
    assert skipped == ["ILLIQ:not_in_top_volume_liquidity_filter"]


def test_load_premarket_signals_rejects_no_benchmark_thesis_or_no_mcp_evidence(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {"symbol": "BETA", "decision": "candidate", "mcp_score": "80", "sources": ["combined_analysis"], "catalyst": "TradingView MCP says bullish"},
            {"symbol": "NEWS", "decision": "candidate", "mcp_score": "85", "sources": ["perplexity"], "catalyst": "news says bullish", "benchmark_thesis": "NEWS may outperform SPY because of cited news."}
          ]
        }
        """
    )

    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))

    assert signals == []
    assert "BETA:missing_spy_outperformance_thesis" in status
    assert "NEWS:missing_tradingview_mcp_setup" in status


def test_single_mcp_setup_is_enough_and_optional_context_is_only_scoring(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {
              "symbol": "LEAN",
              "decision": "candidate",
              "sources": ["volume_breakout"],
              "catalyst": "TradingView MCP volume breakout with strong participation",
              "benchmark": {
                "symbol": "SPY",
                "relative_strength_1d_pct": "0.80",
                "relative_strength_5d_pct": "2.20",
                "outperformance_thesis": "LEAN has relative strength versus SPY and can outperform the benchmark if the volume breakout continues."
              }
            },
            {
              "symbol": "CONFIRM",
              "decision": "candidate",
              "sources": ["combined_analysis"],
              "catalyst": "TradingView MCP combined analysis says bullish technical setup",
              "benchmark_thesis": "CONFIRM can beat SPY because the setup has stronger relative strength than the benchmark."
            }
          ]
        }
        """
    )

    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))

    assert status == "ok"
    assert [s.symbol for s in signals] == ["LEAN", "CONFIRM"]
    assert signals[0].mcp_score > 0
    assert "volume_confirmation" in signals[0].mcp_evidence_summary
    assert signals[1].mcp_score > 0
    assert "combined_analysis" in signals[1].mcp_evidence_summary


def test_retryable_mcp_errors_do_not_count_as_successful_confirmations(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {
              "symbol": "HIMS",
              "decision": "candidate",
              "sources": ["top_gainers"],
              "catalyst": "TradingView MCP top_gainers screen shows a bullish liquid setup",
              "notes": "Optional multi_timeframe returned data errors and should be logged as retryable context only.",
              "mcp_checks": [
                {"tool": "top_gainers", "status": "ok", "evidence": "1D top gainer with constructive price action"},
                {"tool": "multi_timeframe", "status": "retryable_error", "error": "Expecting value: line 1 column 1 (char 0)"}
              ],
              "benchmark": {
                "symbol": "SPY",
                "relative_strength_1d_pct": "5.30",
                "relative_strength_5d_pct": "15.37",
                "outperformance_thesis": "HIMS can outperform SPY because it has stronger relative strength than the benchmark and a liquid MCP top-gainer setup."
              }
            }
          ]
        }
        """
    )

    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))

    assert status == "ok"
    assert [s.symbol for s in signals] == ["HIMS"]
    assert "scanner_hit" in signals[0].mcp_evidence_summary
    assert "retryable_mcp_error" in signals[0].mcp_evidence_summary
    assert "multi_timeframe" not in signals[0].mcp_evidence_summary
    assert signals[0].mcp_score == Decimal("55")


def test_only_failed_mcp_checks_are_rejected_even_when_source_names_a_setup(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "PREMARKET-CANDIDATES.json").write_text(
        """
        {
          "date": "2026-06-16",
          "candidates": [
            {
              "symbol": "FLAKE",
              "decision": "candidate",
              "sources": ["combined_analysis"],
              "catalyst": "TradingView MCP combined_analysis was attempted for this liquid name",
              "mcp_checks": [
                {"tool": "combined_analysis", "status": "retryable_error", "error": "Expecting value: line 1 column 1 (char 0)"}
              ],
              "benchmark_thesis": "FLAKE can outperform SPY if a valid setup appears, but this row intentionally lacks successful MCP evidence."
            },
            {
              "symbol": "NEUTRAL",
              "decision": "candidate",
              "sources": ["combined_analysis"],
              "catalyst": "TradingView MCP combined_analysis returned a neutral read without a constructive setup",
              "mcp_checks": [
                {"tool": "combined_analysis", "status": "ok", "evidence": "Technical NEUTRAL conflicts with neutral sentiment"}
              ],
              "benchmark_thesis": "NEUTRAL can outperform SPY only if a valid setup appears, but this row intentionally lacks successful MCP evidence."
            }
          ]
        }
        """
    )

    signals, status = load_premarket_signals(tmp_path, today=date(2026, 6, 16))

    assert signals == []
    assert "FLAKE:missing_tradingview_mcp_setup" in status
    assert "NEUTRAL:missing_tradingview_mcp_setup" in status


def test_retryable_mcp_error_detector_catches_parse_and_rate_limit_shapes():
    assert is_retryable_mcp_error("Expecting value: line 1 column 1 (char 0)")
    assert is_retryable_mcp_error("HTTP 429 Too Many Requests / rate limit")
    assert is_retryable_mcp_error("TradingView returned empty_or_non_json response")
