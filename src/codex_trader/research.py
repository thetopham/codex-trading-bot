from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from typing import Iterable

BENCHMARK_SYMBOL = "SPY"

TOP_VOLUME_UNIVERSE = [
    "NVDA", "TSLA", "AAPL", "AMD", "PLTR", "AMZN", "MSFT", "META", "GOOGL", "GOOG",
    "AVGO", "NFLX", "INTC", "MARA", "RIOT", "SMCI", "MU", "COIN", "SOFI", "HOOD",
    "BAC", "F", "T", "PFE", "NIO", "LCID", "RIVN", "CCL", "AAL", "NCLH",
    "WBD", "PARA", "DIS", "UBER", "LYFT", "SHOP", "SNAP", "RBLX", "AI", "SOUN",
    "BBAI", "IONQ", "QBTS", "QS", "CHPT", "PLUG", "FCEL", "RUN", "ENPH", "SEDG",
    "XOM", "CVX", "OXY", "SLB", "HAL", "JPM", "WFC", "C", "GS", "MS",
    "V", "MA", "PYPL", "SQ", "AFRM", "WMT", "COST", "TGT", "HD", "LOW",
    "UNH", "LLY", "MRK", "ABBV", "JNJ", "BMY", "GILD", "AMGN", "BA", "CAT",
    "DE", "GE", "GM", "ORCL", "CRM", "ADBE", "NOW", "PANW", "CRWD", "DDOG",
]

DEFAULT_FORCED_WATCHLIST = ["SPCX"]

SECTOR_ETFS = {
    "XLK": "technology",
    "XLF": "financials",
    "XLE": "energy",
    "XLV": "healthcare",
    "XLI": "industrials",
    "XLY": "consumer_discretionary",
    "XLP": "consumer_staples",
    "XLC": "communication_services",
    "XLU": "utilities",
    "XLB": "materials",
    "XLRE": "real_estate",
}

SYMBOL_SECTOR = {
    "NVDA": "technology", "AAPL": "technology", "AMD": "technology", "MSFT": "technology",
    "META": "communication_services", "GOOGL": "communication_services", "GOOG": "communication_services",
    "AVGO": "technology", "INTC": "technology", "MU": "technology", "SMCI": "technology",
    "PANW": "technology", "CRWD": "technology", "DDOG": "technology", "ORCL": "technology",
    "CRM": "technology", "ADBE": "technology", "NOW": "technology",
    "TSLA": "consumer_discretionary", "AMZN": "consumer_discretionary", "NFLX": "communication_services",
    "UBER": "industrials", "LYFT": "industrials", "SHOP": "technology",
    "XOM": "energy", "CVX": "energy", "OXY": "energy", "SLB": "energy", "HAL": "energy",
    "JPM": "financials", "BAC": "financials", "WFC": "financials", "C": "financials", "GS": "financials",
    "MS": "financials", "V": "financials", "MA": "financials", "PYPL": "financials", "SQ": "financials", "AFRM": "financials", "SOFI": "financials", "HOOD": "financials", "COIN": "financials",
    "WMT": "consumer_staples", "COST": "consumer_staples", "TGT": "consumer_discretionary", "HD": "consumer_discretionary", "LOW": "consumer_discretionary",
    "UNH": "healthcare", "LLY": "healthcare", "MRK": "healthcare", "ABBV": "healthcare", "JNJ": "healthcare", "BMY": "healthcare", "GILD": "healthcare", "AMGN": "healthcare", "PFE": "healthcare",
    "BA": "industrials", "CAT": "industrials", "DE": "industrials", "GE": "industrials", "GM": "consumer_discretionary", "F": "consumer_discretionary",
}


@dataclass(frozen=True)
class Candidate:
    symbol: str
    last_price: Decimal
    volume: int
    avg_volume: int
    day_change_pct: Decimal
    five_day_change_pct: Decimal
    score: Decimal
    sector: str
    benchmark_symbol: str = BENCHMARK_SYMBOL
    benchmark_day_change_pct: Decimal = Decimal("0")
    benchmark_five_day_change_pct: Decimal = Decimal("0")
    relative_day_change_pct: Decimal = Decimal("0")
    relative_five_day_change_pct: Decimal = Decimal("0")

    @property
    def suggested_qty(self) -> int:
        if self.last_price <= 0:
            return 0
        # Conservative dry-run sizing: target around $2k per idea, never fractional here.
        return max(1, int((Decimal("2000") / self.last_price).to_integral_value(rounding=ROUND_DOWN)))

    @property
    def stop(self) -> Decimal:
        return (self.last_price * Decimal("0.90")).quantize(Decimal("0.01"))

    @property
    def target(self) -> Decimal:
        # 2:1 against the required 10% trailing-stop discipline.
        return (self.last_price * Decimal("1.20")).quantize(Decimal("0.01"))

    @property
    def catalyst(self) -> str:
        return (
            f"Liquidity/relative-strength reference: volume {self.volume:,} vs avg {self.avg_volume:,}; "
            f"1D {self.day_change_pct:.2f}% vs {self.benchmark_symbol} {self.benchmark_day_change_pct:.2f}% "
            f"(rel {self.relative_day_change_pct:.2f}%), 5D {self.five_day_change_pct:.2f}% vs "
            f"{self.benchmark_symbol} {self.benchmark_five_day_change_pct:.2f}% "
            f"(rel {self.relative_five_day_change_pct:.2f}%)."
        )


def _to_decimal(value: object) -> Decimal:
    try:
        if value is None or str(value) == "nan":
            return Decimal("0")
        return Decimal(str(float(str(value))))
    except Exception:
        return Decimal("0")


def _download_market_data(symbols: list[str], period: str = "10d"):
    import yfinance as yf
    return yf.download(symbols, period=period, interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)


def _forced_watchlist_symbols() -> list[str]:
    raw = os.environ.get("FORCED_WATCHLIST", ",".join(DEFAULT_FORCED_WATCHLIST))
    symbols: list[str] = []
    for part in raw.split(","):
        symbol = part.upper().strip()
        if symbol and symbol not in symbols:
            symbols.append(symbol)
    return symbols


def _unique_symbols(symbols: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for symbol in symbols:
        clean = symbol.upper().strip()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def most_active_symbols(limit: int = 100) -> list[str]:
    import yfinance as yf
    try:
        result = yf.screen("most_actives", count=limit)
    except Exception:
        return _unique_symbols(TOP_VOLUME_UNIVERSE + _forced_watchlist_symbols())
    symbols = []
    for quote in result.get("quotes", []):
        if quote.get("quoteType") != "EQUITY":
            continue
        symbol = str(quote.get("symbol") or "").upper().strip()
        # Keep US common-stock style symbols only; avoid warrants/classes/options noise.
        if symbol and symbol.replace("-", "").replace(".", "").isalnum():
            symbols.append(symbol)
    return _unique_symbols((symbols or TOP_VOLUME_UNIVERSE) + _forced_watchlist_symbols())


def _frame_for_symbol(data, symbol: str):
    try:
        return data[symbol].dropna(subset=["Close", "Volume"])
    except Exception:
        # yfinance returns a flat frame when only one symbol is requested. This path is
        # mainly defensive because production calls download many symbols + SPY.
        try:
            return data.dropna(subset=["Close", "Volume"])
        except Exception:
            return None


def _change_pair_for_symbol(data, symbol: str) -> tuple[Decimal, Decimal]:
    frame = _frame_for_symbol(data, symbol)
    if frame is None or len(frame) < 2:
        return Decimal("0"), Decimal("0")
    latest = frame.iloc[-1]
    prev = frame.iloc[-2]
    first = frame.iloc[0]
    latest_close = _to_decimal(latest.get("Close"))
    prev_close = _to_decimal(prev.get("Close"))
    first_close = _to_decimal(first.get("Close"))
    day_change = ((latest_close - prev_close) / prev_close * Decimal("100")) if prev_close else Decimal("0")
    five_day = ((latest_close - first_close) / first_close * Decimal("100")) if first_close else Decimal("0")
    return day_change, five_day


def _extract_rows(data, symbols: Iterable[str], benchmark_symbol: str = BENCHMARK_SYMBOL) -> list[Candidate]:
    rows: list[Candidate] = []
    benchmark_day, benchmark_five = _change_pair_for_symbol(data, benchmark_symbol)
    for symbol in symbols:
        frame = _frame_for_symbol(data, symbol)
        if frame is None or len(frame) < 2:
            continue
        latest = frame.iloc[-1]
        last_price = _to_decimal(latest.get("Close"))
        if last_price <= 0:
            continue
        volume = int(latest.get("Volume") or 0)
        avg_volume = int(frame["Volume"].tail(min(10, len(frame))).mean() or 0)
        day_change, five_day = _change_pair_for_symbol(data, symbol)
        rel_volume = Decimal(volume) / Decimal(avg_volume) if avg_volume else Decimal("0")
        relative_day = day_change - benchmark_day
        relative_five = five_day - benchmark_five
        # Score is a benchmark-relative research hint only; TradingView MCP remains the alpha gate.
        score = (rel_volume * Decimal("2")) + relative_day + (relative_five * Decimal("0.5"))
        rows.append(Candidate(
            symbol=symbol,
            last_price=last_price.quantize(Decimal("0.01")),
            volume=volume,
            avg_volume=avg_volume,
            day_change_pct=day_change.quantize(Decimal("0.01")),
            five_day_change_pct=five_day.quantize(Decimal("0.01")),
            score=score.quantize(Decimal("0.01")),
            sector=SYMBOL_SECTOR.get(symbol, "unknown"),
            benchmark_symbol=benchmark_symbol,
            benchmark_day_change_pct=benchmark_day.quantize(Decimal("0.01")),
            benchmark_five_day_change_pct=benchmark_five.quantize(Decimal("0.01")),
            relative_day_change_pct=relative_day.quantize(Decimal("0.01")),
            relative_five_day_change_pct=relative_five.quantize(Decimal("0.01")),
        ))
    return rows


def top_volume_candidates(limit: int = 100, picks: int = 5) -> tuple[list[Candidate], list[Candidate]]:
    symbols = most_active_symbols(limit)
    data_symbols = _unique_symbols(symbols + [BENCHMARK_SYMBOL])
    data = _download_market_data(data_symbols)
    rows = _extract_rows(data, symbols, benchmark_symbol=BENCHMARK_SYMBOL)
    top_by_volume = sorted(rows, key=lambda r: r.volume, reverse=True)[:limit]
    # Favor SPY-relative momentum; if no positive relative rows, return highest score anyway.
    positive = [r for r in top_by_volume if r.relative_day_change_pct > 0 and r.relative_five_day_change_pct > 0]
    pool = positive if positive else top_by_volume
    selected = sorted(pool, key=lambda r: r.score, reverse=True)[:picks]
    return top_by_volume, selected


def _benchmark_summary(top_by_volume: list[Candidate]) -> str:
    if not top_by_volume:
        return f"{BENCHMARK_SYMBOL} benchmark context unavailable."
    sample = top_by_volume[0]
    return (
        f"{sample.benchmark_symbol}: 1D {sample.benchmark_day_change_pct}%, "
        f"5D {sample.benchmark_five_day_change_pct}%."
    )


def render_liquidity_filter_markdown(top_by_volume: list[Candidate], today: date | None = None) -> str:
    today = today or date.today()
    lines = [
        f"\n## Liquidity Filter — {today.isoformat()}",
        "",
        "Top-volume stocks are a liquidity filter only. Final trade candidates must come from TradingView MCP screening, include a SPY/SPX outperformance thesis, and be written to `memory/PREMARKET-CANDIDATES.json`.",
        f"Benchmark proxy context: {_benchmark_summary(top_by_volume)}",
        "",
        "| Rank | Symbol | Last | Volume | Avg Vol | 1D % | 5D % | Rel 1D vs SPY | Rel 5D vs SPY | Score | Sector |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i, c in enumerate(top_by_volume, 1):
        lines.append(f"| {i} | {c.symbol} | {c.last_price} | {c.volume} | {c.avg_volume} | {c.day_change_pct} | {c.five_day_change_pct} | {c.relative_day_change_pct} | {c.relative_five_day_change_pct} | {c.score} | {c.sector} |")
    lines += [
        "",
        "Decision rule: HOLD unless TradingView MCP scanners confirm a liquid setup with a documented catalyst, an explicit reason to beat SPY/SPX, and market-open risk gates pass.",
        "",
    ]
    return "\n".join(lines)


def render_research_markdown(top_by_volume: list[Candidate], selected: list[Candidate], today: date | None = None) -> str:
    today = today or date.today()
    lines = [
        f"\n## Pre-market Research — {today.isoformat()}",
        "",
        "Research source: Yahoo Finance daily OHLCV via `yfinance`; universe is a static high-liquidity list ranked by latest reported volume. No Perplexity dependency. Top-volume names are benchmark-relative liquidity hints only; TradingView MCP must still supply the trade evidence.",
        f"Benchmark proxy context: {_benchmark_summary(top_by_volume)}",
        "",
        "### Top 100 volume universe snapshot",
        "",
        "| Rank | Symbol | Last | Volume | Avg Vol | 1D % | 5D % | Rel 1D vs SPY | Rel 5D vs SPY | Score | Sector |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i, c in enumerate(top_by_volume, 1):
        lines.append(f"| {i} | {c.symbol} | {c.last_price} | {c.volume} | {c.avg_volume} | {c.day_change_pct} | {c.five_day_change_pct} | {c.relative_day_change_pct} | {c.relative_five_day_change_pct} | {c.score} | {c.sector} |")
    lines += ["", "### Candidate trade ideas", ""]
    if not selected:
        lines.append("Decision: HOLD — no candidates passed the positive SPY-relative momentum reference filter.")
    for c in selected:
        lines += [
            f"#### {c.symbol}",
            f"- Liquidity/relative-strength reference: {c.catalyst}",
            f"- Benchmark gate: pre-market MCP output must explain why {c.symbol} can outperform {c.benchmark_symbol}; market-open rejects benchmark-free beta trades.",
            f"- Sector: {c.sector}",
            f"- Entry reference: {c.last_price}",
            f"- Sizing note: market-open computes qty from live equity so a 10% trailing stop risks at most ~1% of portfolio equity.",
            f"- Reference stop discipline: 10% trailing stop on submitted paper position",
            f"- Reference target: {(c.last_price * Decimal('1.20')).quantize(Decimal('0.01'))}",
            "- Risk/reward: approx 2:1 against the required 10% trailing stop",
            "- Decision: liquidity reference only; candidate requires TradingView MCP confirmation, SPY/SPX outperformance thesis, and market-open gates.",
            "",
        ]
    lines += ["### Default decision", "HOLD unless market-open revalidation confirms a benchmark-relative MCP candidate and risk gates pass.", ""]
    return "\n".join(lines)
