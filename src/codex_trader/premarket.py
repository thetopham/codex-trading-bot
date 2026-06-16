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


def _haystack(sources: tuple[str, ...], catalyst: str, notes: str) -> str:
    return " ".join((*sources, catalyst, notes)).lower().replace("-", "_").replace(" ", "_")


def _has_tradingview_mcp_evidence(sources: tuple[str, ...], catalyst: str, notes: str) -> bool:
    """One MCP hard gate: any TradingView/MCP technical setup is enough.

    We deliberately do not require combined_analysis + multi-timeframe + news + backtest.
    Those are optional score/context fields that may improve confidence, not veto points.
    """
    haystack = _haystack(sources, catalyst, notes)
    has_mcp_or_tradingview = "mcp" in haystack or "tradingview" in haystack
    has_named_setup = any(hint in haystack for hint in MCP_SCANNER_HINTS | MCP_CONFIRMATION_HINTS)
    has_technical_language = any(hint in haystack for hint in ("technical", "breakout", "bullish", "strong_buy", "buy"))
    return has_named_setup or (has_mcp_or_tradingview and has_technical_language)


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
    haystack = _haystack(sources, catalyst, notes)
    parts: list[str] = []
    if any(hint in haystack for hint in MCP_SCANNER_HINTS):
        parts.append("scanner_hit")
    if "combined_analysis" in haystack:
        parts.append("combined_analysis")
    if "multi_timeframe" in haystack:
        parts.append("multi_timeframe")
    if "volume_breakout" in haystack or "smart_volume" in haystack or "volume_confirmation" in haystack:
        parts.append("volume_confirmation")
    if any(hint in haystack for hint in MCP_OPTIONAL_CONTEXT_HINTS):
        parts.append("optional_context")
    if any(hint in haystack for hint in MCP_RISK_WARNING_HINTS):
        parts.append("risk_warning")
    return ",".join(parts) if parts else "single_mcp_setup"


def _score_mcp_evidence(raw: Mapping[str, object]) -> Decimal:
    """Score MCP evidence for ranking only; it is not a market-open hard gate."""
    catalyst = str(raw.get("catalyst") or raw.get("thesis") or raw.get("reason") or "").strip()
    notes = str(raw.get("notes") or "").strip()
    sources = _split_sources(raw.get("sources") or raw.get("mcp_sources") or [])
    haystack = _haystack(sources, catalyst, notes)
    score = Decimal("0")

    if any(hint in haystack for hint in MCP_SCANNER_HINTS):
        score += Decimal("25")
    if "combined_analysis" in haystack:
        score += Decimal("25")
    if "multi_timeframe" in haystack:
        score += Decimal("15")
    if "volume_breakout" in haystack or "smart_volume" in haystack or "volume_confirmation" in haystack:
        score += Decimal("15")

    rel_1d = _extract_relative_strength(raw, "relative_strength_1d_pct")
    rel_5d = _extract_relative_strength(raw, "relative_strength_5d_pct")
    if rel_1d > 0 and rel_5d > 0:
        score += Decimal("20")
    elif rel_1d > 0 or rel_5d > 0:
        score += Decimal("10")

    if len(catalyst) >= 25:
        score += Decimal("10")
    if any(hint in haystack for hint in ("financial_news", "market_sentiment", "news", "catalyst")):
        score += Decimal("10")
    if any(hint in haystack for hint in ("backtest", "walk_forward", "compare_strategies")):
        score += Decimal("10")
    if any(hint in haystack for hint in MCP_RISK_WARNING_HINTS):
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
    if not _has_tradingview_mcp_evidence(sources, catalyst, notes):
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
        "mcp_requirement": "One TradingView MCP technical setup is enough; additional MCP tools are score/context, not hard gates.",
        "benchmark_requirement": "Each candidate must include a SPY/SPX outperformance thesis; market-open rejects benchmark-free beta trades.",
        "candidates": [],
    }
