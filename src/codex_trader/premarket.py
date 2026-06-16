from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Mapping

from .research import Candidate

CANDIDATES_FILE = "PREMARKET-CANDIDATES.json"
TRADE_DECISIONS = {"candidate", "trade_candidate", "approved", "buy", "paper_trade_candidate"}
BENCHMARK_SYMBOL = "SPY"

# One hard MCP gate: a candidate needs at least one TradingView MCP technical setup.
# Everything else below is score/context, not an additional veto.
MCP_TECHNICAL_SETUP_HINTS = {
    "mcp",
    "tradingview",
    "top_gainers",
    "volume_breakout",
    "smart_volume",
    "rating_filter",
    "bollinger",
    "combined_analysis",
    "multi_timeframe",
    "volume_confirmation",
    "technical",
    "breakout",
    "strong_buy",
    "buy",
    "bullish",
}
MCP_SCANNER_HINTS = {
    "top_gainers",
    "volume_breakout",
    "smart_volume",
    "rating_filter",
    "bollinger",
}
MCP_CONFIRMATION_HINTS = {
    "combined_analysis",
    "multi_timeframe",
    "volume_confirmation",
}
MCP_OPTIONAL_CONTEXT_HINTS = {
    "financial_news",
    "market_sentiment",
    "compare_strategies",
    "backtest",
    "walk_forward",
}
MCP_RISK_WARNING_HINTS = (
    "strong sell",
    "bearish",
    "downtrend",
    "overextended",
    "overextension",
    "high risk",
    "avoid",
)
BENCHMARK_HINTS = ("spy", "spx", "s&p", "benchmark")
OUTPERFORMANCE_HINTS = (
    "outperform",
    "beat",
    "alpha",
    "relative strength",
    "stronger than spy",
    "stronger than spx",
    "stronger than the benchmark",
    "ahead of spy",
    "ahead of spx",
)
PLACEHOLDER_THESIS_HINTS = ("tbd", "todo", "n/a", "none", "required", "placeholder")
MCP_RETRYABLE_ERROR_HINTS = (
    "expecting value: line 1 column 1",
    "empty response",
    "empty_or_non_json",
    "non-json",
    "non_json",
    "invalid json",
    "json parse",
    "parser error",
    "parse error",
    "data error",
    "data errors",
    "timeout",
    "timed out",
    "temporarily unavailable",
    "connection reset",
    "too many requests",
    "rate limit",
    "rate_limited",
    "429",
)
MCP_FAILED_STATUS_HINTS = (
    "error",
    "failed",
    "failure",
    "retryable_error",
    "rate_limited",
    "timeout",
    "empty",
)
MCP_NEGATIVE_RECOMMENDATION_HINTS = (
    "hold/no_trade",
    "hold_no_trade",
    "no_trade",
    "wait_for_alignment",
    "avoid",
    "strong_sell",
)
MCP_CONSTRUCTIVE_HINTS = (
    "bullish",
    "buy",
    "cautious_buy",
    "lean_bullish",
    "constructive",
    "breakout",
    "top_gainers",
    "positive",
    "price_above",
)


@dataclass(frozen=True)
class PremarketSignal:
    symbol: str
    catalyst: str
    mcp_score: Decimal = Decimal("0")
    sources: tuple[str, ...] = ()
    exchange: str | None = None
    decision: str = "candidate"
    notes: str = ""
    benchmark_symbol: str = BENCHMARK_SYMBOL
    benchmark_thesis: str = ""
    relative_strength_1d_pct: Decimal = Decimal("0")
    relative_strength_5d_pct: Decimal = Decimal("0")
    mcp_evidence_summary: str = ""


def normalize_symbol(value: object) -> str:
    """Normalize MCP symbols such as NASDAQ:NVDA to Alpaca/Yahoo-style NVDA."""
    symbol = str(value or "").upper().strip()
    if ":" in symbol:
        symbol = symbol.rsplit(":", 1)[-1]
    return symbol.replace("/", "-").strip()


def candidates_path(root: Path) -> Path:
    return root / "memory" / CANDIDATES_FILE


def _as_decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _split_sources(raw_sources: object) -> tuple[str, ...]:
    if isinstance(raw_sources, str):
        return tuple(s.strip() for s in raw_sources.split(",") if s.strip())
    try:
        return tuple(str(s).strip() for s in raw_sources if str(s).strip())  # type: ignore[union-attr]
    except TypeError:
        return ()


def _normalized_text(value: object) -> str:
    return str(value or "").lower().replace("-", "_").replace(" ", "_")


def _mcp_tool_name(value: object) -> str:
    return _normalized_text(value).replace("mcp_tradingview_", "").replace("tradingview_", "")


def _haystack(sources: tuple[str, ...], catalyst: str, notes: str) -> str:
    return " ".join((*sources, catalyst, notes)).lower().replace("-", "_").replace(" ", "_")


def is_retryable_mcp_error(text: object) -> bool:
    """Return True for flaky TradingView/Yahoo/MCP upstream failures worth retrying.

    The MCP server often surfaces empty upstream responses as JSON parser errors
    instead of explicit HTTP status codes. Treat those as retryable health data,
    not as bullish/bearish evidence.
    """
    haystack = _normalized_text(text).replace(":", "_").replace("/", "_")
    return any(_normalized_text(hint).replace(":", "_").replace("/", "_") in haystack for hint in MCP_RETRYABLE_ERROR_HINTS)


def _mcp_checks(raw: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    checks = raw.get("mcp_checks") or raw.get("tradingview_mcp_checks") or []
    if isinstance(checks, Mapping):
        # Accept either a single check object or a {tool: check} mapping.
        if any(isinstance(v, Mapping) for v in checks.values()):
            normalized: list[Mapping[str, object]] = []
            for key, value in checks.items():
                if isinstance(value, Mapping):
                    enriched = dict(value)
                    enriched.setdefault("tool", key)
                    normalized.append(enriched)
            return tuple(normalized)
        return (checks,)
    try:
        return tuple(check for check in checks if isinstance(check, Mapping))  # type: ignore[union-attr]
    except TypeError:
        return ()


def _mcp_check_text(check: Mapping[str, object]) -> str:
    fields = (
        "tool",
        "source",
        "status",
        "summary",
        "evidence",
        "error",
        "recommendation",
        "action",
        "notes",
        "breakout_type",
    )
    return _normalized_text(" ".join(str(check.get(field) or "") for field in fields))


def _mcp_check_failed(check: Mapping[str, object]) -> bool:
    status = _normalized_text(check.get("status"))
    text = _mcp_check_text(check)
    return (
        any(hint in status for hint in MCP_FAILED_STATUS_HINTS)
        or is_retryable_mcp_error(text)
        or "returned_all_timeframe_errors" in text
    )


def _mcp_check_negative(check: Mapping[str, object]) -> bool:
    text = _mcp_check_text(check)
    return any(hint in text for hint in MCP_NEGATIVE_RECOMMENDATION_HINTS) or "breakout_type_bearish" in text


def _mcp_check_is_successful_setup(check: Mapping[str, object]) -> bool:
    if _mcp_check_failed(check) or _mcp_check_negative(check):
        return False
    tool = _mcp_tool_name(check.get("tool") or check.get("source"))
    text = _mcp_check_text(check)
    if any(hint in tool or hint in text for hint in MCP_SCANNER_HINTS):
        return True
    if any(hint in tool or hint in text for hint in MCP_CONFIRMATION_HINTS):
        return any(hint in text for hint in MCP_CONSTRUCTIVE_HINTS)
    return ("mcp" in text or "tradingview" in text) and "technical" in text and any(
        hint in text for hint in MCP_CONSTRUCTIVE_HINTS
    )


def _successful_mcp_setup_tools(raw: Mapping[str, object]) -> tuple[str, ...]:
    tools: list[str] = []
    for check in _mcp_checks(raw):
        if _mcp_check_is_successful_setup(check):
            tool = _mcp_tool_name(check.get("tool") or check.get("source") or "mcp")
            tools.append(tool or "mcp")
    return tuple(dict.fromkeys(tools))


def _failed_mcp_tools(raw: Mapping[str, object]) -> tuple[str, ...]:
    tools: list[str] = []
    for check in _mcp_checks(raw):
        if _mcp_check_failed(check):
            tool = _mcp_tool_name(check.get("tool") or check.get("source") or "mcp")
            tools.append(tool or "mcp")
    return tuple(dict.fromkeys(tools))


def _has_tradingview_mcp_evidence(sources: tuple[str, ...], catalyst: str, notes: str) -> bool:
    """One MCP hard gate: any TradingView/MCP technical setup is enough.

    We deliberately do not require combined_analysis + multi-timeframe + news + backtest.
    Those are optional score/context fields that may improve confidence, not veto points.
    """
    # Count source/catalyst as the successful-evidence surface. Notes often contain
    # failed optional confirmations; those should not accidentally satisfy the hard gate.
    haystack = _haystack(sources, catalyst, "")
    has_mcp_or_tradingview = "mcp" in haystack or "tradingview" in haystack
    has_named_setup = any(hint in haystack for hint in MCP_SCANNER_HINTS | MCP_CONFIRMATION_HINTS)
    has_technical_language = any(hint in haystack for hint in ("technical", "breakout", "bullish", "strong_buy", "buy"))
    return has_named_setup or (has_mcp_or_tradingview and has_technical_language)


def _candidate_has_tradingview_mcp_evidence(raw: Mapping[str, object]) -> bool:
    successful_tools = _successful_mcp_setup_tools(raw)
    if successful_tools:
        return True

    catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
    notes = str(raw.get("notes") or "").strip()
    sources = _split_sources(raw.get("sources") or raw.get("mcp_sources") or [])
    source_setup_tools = {
        _mcp_tool_name(source)
        for source in sources
        if any(hint in _mcp_tool_name(source) for hint in MCP_SCANNER_HINTS | MCP_CONFIRMATION_HINTS)
    }
    failed_tools = set(_failed_mcp_tools(raw))
    checked_setup_tools = {
        _mcp_tool_name(check.get("tool") or check.get("source"))
        for check in _mcp_checks(raw)
        if any(hint in _mcp_tool_name(check.get("tool") or check.get("source")) for hint in MCP_SCANNER_HINTS | MCP_CONFIRMATION_HINTS)
    }
    if source_setup_tools and (source_setup_tools <= failed_tools or source_setup_tools <= checked_setup_tools):
        return False
    return _has_tradingview_mcp_evidence(sources, catalyst, notes)


def _extract_benchmark_thesis(raw: Mapping[str, object]) -> str:
    benchmark = _as_mapping(raw.get("benchmark"))
    keys = (
        "benchmark_thesis",
        "spy_outperformance_thesis",
        "spx_outperformance_thesis",
        "outperformance_thesis",
        "relative_thesis",
        "thesis",
        "notes",
    )
    benchmark_keys = (
        "outperformance_thesis",
        "benchmark_thesis",
        "spy_outperformance_thesis",
        "spx_outperformance_thesis",
        "relative_thesis",
        "thesis",
        "notes",
    )
    for key in benchmark_keys:
        value = str(benchmark.get(key) or "").strip()
        if value:
            return value
    for key in keys:
        value = str(raw.get(key) or "").strip()
        if value:
            return value
    return ""


def _valid_benchmark_thesis(thesis: str) -> bool:
    text = thesis.strip().lower()
    if len(text) < 25:
        return False
    if text in PLACEHOLDER_THESIS_HINTS or any(text == hint for hint in PLACEHOLDER_THESIS_HINTS):
        return False
    if any(hint in text for hint in PLACEHOLDER_THESIS_HINTS) and len(text) < 80:
        return False
    mentions_benchmark = any(hint in text for hint in BENCHMARK_HINTS)
    mentions_outperformance = any(hint in text for hint in OUTPERFORMANCE_HINTS)
    return mentions_benchmark and mentions_outperformance


def _extract_benchmark_symbol(raw: Mapping[str, object]) -> str:
    benchmark = _as_mapping(raw.get("benchmark"))
    symbol = str(benchmark.get("symbol") or raw.get("benchmark_symbol") or BENCHMARK_SYMBOL).upper().strip()
    return symbol or BENCHMARK_SYMBOL


def _extract_relative_strength(raw: Mapping[str, object], field: str) -> Decimal:
    benchmark = _as_mapping(raw.get("benchmark"))
    candidates = (
        benchmark.get(field),
        benchmark.get(field.replace("relative_strength", "relative")),
        raw.get(field),
        raw.get(field.replace("relative_strength", "relative")),
    )
    for value in candidates:
        if value not in (None, ""):
            return _as_decimal(value)
    return Decimal("0")


def _mcp_evidence_summary(raw: Mapping[str, object]) -> str:
    catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
    notes = str(raw.get("notes") or "").strip()
    sources = _split_sources(raw.get("sources") or raw.get("mcp_sources") or [])
    checks = _mcp_checks(raw)
    successful_tools = _successful_mcp_setup_tools(raw)
    parts: list[str] = []

    if checks:
        successful_haystack = " ".join(successful_tools)
    else:
        # Legacy candidate rows do not have structured check statuses. Use
        # sources+catalyst as positive evidence and reserve notes for risk/errors.
        successful_haystack = _haystack(sources, catalyst, "")

    if any(hint in successful_haystack for hint in MCP_SCANNER_HINTS):
        parts.append("scanner_hit")
    if "combined_analysis" in successful_haystack:
        parts.append("combined_analysis")
    if "multi_timeframe" in successful_haystack:
        parts.append("multi_timeframe")
    if "volume_breakout" in successful_haystack or "smart_volume" in successful_haystack or "volume_confirmation" in successful_haystack:
        parts.append("volume_confirmation")

    full_haystack = _haystack(sources, catalyst, notes)
    if any(hint in full_haystack for hint in MCP_OPTIONAL_CONTEXT_HINTS):
        parts.append("optional_context")
    if any(hint in full_haystack for hint in MCP_RISK_WARNING_HINTS):
        parts.append("risk_warning")
    failed_checks = [check for check in checks if _mcp_check_failed(check)]
    retryable_text = " ".join(_mcp_check_text(check) for check in failed_checks) + " " + notes
    if failed_checks or is_retryable_mcp_error(notes):
        parts.append("retryable_mcp_error" if is_retryable_mcp_error(retryable_text) else "mcp_error")
    return ",".join(dict.fromkeys(parts)) if parts else "single_mcp_setup"


def _score_mcp_evidence(raw: Mapping[str, object]) -> Decimal:
    """Score MCP evidence for ranking only; it is not a market-open hard gate."""
    catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
    notes = str(raw.get("notes") or "").strip()
    sources = _split_sources(raw.get("sources") or raw.get("mcp_sources") or [])
    checks = _mcp_checks(raw)
    successful_tools = _successful_mcp_setup_tools(raw)
    if checks:
        success_haystack = " ".join(successful_tools)
    else:
        # Legacy rows: count source/catalyst as positive evidence, but do not
        # award confirmation points for failed optional checks mentioned in notes.
        success_haystack = _haystack(sources, catalyst, "")
    full_haystack = _haystack(sources, catalyst, notes)
    score = Decimal("0")

    if any(hint in success_haystack for hint in MCP_SCANNER_HINTS):
        score += Decimal("25")
    if "combined_analysis" in success_haystack:
        score += Decimal("25")
    if "multi_timeframe" in success_haystack:
        score += Decimal("15")
    if "volume_breakout" in success_haystack or "smart_volume" in success_haystack or "volume_confirmation" in success_haystack:
        score += Decimal("15")

    rel_1d = _extract_relative_strength(raw, "relative_strength_1d_pct")
    rel_5d = _extract_relative_strength(raw, "relative_strength_5d_pct")
    if rel_1d > 0 and rel_5d > 0:
        score += Decimal("20")
    elif rel_1d > 0 or rel_5d > 0:
        score += Decimal("10")

    if len(catalyst) >= 25:
        score += Decimal("10")
    if any(hint in full_haystack for hint in ("financial_news", "market_sentiment", "news", "catalyst")):
        score += Decimal("10")
    if any(hint in full_haystack for hint in ("backtest", "walk_forward", "compare_strategies")):
        score += Decimal("10")
    if any(hint in full_haystack for hint in MCP_RISK_WARNING_HINTS):
        score -= Decimal("20")

    return max(Decimal("0"), min(Decimal("100"), score))


def _extract_mcp_score(raw: Mapping[str, object]) -> Decimal:
    provided = _as_decimal(raw.get("mcp_score", raw.get("score", "0")))
    if provided > 0:
        return provided
    return _score_mcp_evidence(raw)


def _candidate_rejection_reasons(raw: Mapping[str, object]) -> tuple[str, ...]:
    symbol = normalize_symbol(raw.get("symbol"))
    decision = str(raw.get("decision", "candidate")).lower().strip()
    catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
    notes = str(raw.get("notes") or "").strip()
    sources = _split_sources(raw.get("sources") or raw.get("mcp_sources") or [])
    benchmark_thesis = _extract_benchmark_thesis(raw)

    reasons: list[str] = []
    if not symbol:
        reasons.append("missing_symbol")
    if decision not in TRADE_DECISIONS:
        reasons.append("not_trade_decision")
    if not catalyst:
        reasons.append("missing_documented_catalyst")
    if not _candidate_has_tradingview_mcp_evidence(raw):
        reasons.append("missing_tradingview_mcp_setup")
    if not _valid_benchmark_thesis(benchmark_thesis):
        reasons.append("missing_spy_outperformance_thesis")
    return tuple(reasons)


def load_premarket_signals(root: Path, *, today: date | None = None) -> tuple[list[PremarketSignal], str]:
    today = today or date.today()
    path = candidates_path(root)
    if not path.exists():
        return [], f"missing {path.relative_to(root)}"
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        return [], f"invalid candidate json: {exc}"
    payload_date = str(payload.get("date") or "")
    if payload_date != today.isoformat():
        return [], f"candidate file date {payload_date or 'missing'} != today {today.isoformat()}"

    signals: list[PremarketSignal] = []
    rejected: list[str] = []
    for idx, raw_candidate in enumerate(payload.get("candidates", []), start=1):
        raw = _as_mapping(raw_candidate)
        symbol = normalize_symbol(raw.get("symbol"))
        decision = str(raw.get("decision", "candidate")).lower().strip()
        # HOLD rows are allowed for documentation but must not become market-open signals.
        if decision and decision not in TRADE_DECISIONS:
            continue

        reasons = _candidate_rejection_reasons(raw)
        if reasons:
            label = symbol or f"row{idx}"
            rejected.append(f"{label}:{'+'.join(reasons)}")
            continue

        catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
        raw_sources = raw.get("sources") or raw.get("mcp_sources") or []
        sources = _split_sources(raw_sources)
        benchmark_thesis = _extract_benchmark_thesis(raw)
        signals.append(PremarketSignal(
            symbol=symbol,
            catalyst=catalyst,
            mcp_score=_extract_mcp_score(raw),
            sources=sources,
            exchange=str(raw.get("exchange") or "").upper().strip() or None,
            decision=decision,
            notes=str(raw.get("notes") or "").strip(),
            benchmark_symbol=_extract_benchmark_symbol(raw),
            benchmark_thesis=benchmark_thesis,
            relative_strength_1d_pct=_extract_relative_strength(raw, "relative_strength_1d_pct"),
            relative_strength_5d_pct=_extract_relative_strength(raw, "relative_strength_5d_pct"),
            mcp_evidence_summary=_mcp_evidence_summary(raw),
        ))
    status = "ok" if signals else "no trade candidates in candidate file"
    if rejected:
        status = f"{status}; rejected {', '.join(rejected)}"
    return signals, status


def filter_signals_by_liquidity(
    signals: Iterable[PremarketSignal],
    top_by_volume: Iterable[Candidate],
    *,
    limit: int | None = None,
) -> tuple[list[tuple[PremarketSignal, Candidate]], list[str]]:
    liquidity_by_symbol = {c.symbol: c for c in top_by_volume}
    selected: list[tuple[PremarketSignal, Candidate]] = []
    skipped: list[str] = []
    for signal in signals:
        liquid = liquidity_by_symbol.get(signal.symbol)
        if liquid is None:
            skipped.append(f"{signal.symbol}:not_in_top_volume_liquidity_filter")
            continue
        selected.append((signal, liquid))
    selected.sort(key=lambda pair: pair[0].mcp_score, reverse=True)
    if limit is not None and limit > 0:
        return selected[:limit], skipped
    return selected, skipped


def empty_candidate_payload(today: date | None = None) -> dict[str, object]:
    today = today or date.today()
    return {
        "date": today.isoformat(),
        "source": "TradingView MCP screening over top-100-volume liquidity filter",
        "liquidity_filter": "generated by python -m codex_trader.research_export",
        "mcp_requirement": "One successful TradingView MCP technical setup is enough; failed/retryable MCP checks are health context only and do not count as evidence.",
        "mcp_retry_policy": "Call MCP serially, use 1-2 broad scans, retry parser/empty-response/429-style errors with 10-30s backoff, then fail closed if no successful setup remains.",
        "benchmark_requirement": "Each candidate must include a SPY/SPX outperformance thesis; market-open rejects benchmark-free beta trades.",
        "candidates": [],
    }
