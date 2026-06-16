from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

BENCHMARK_LEDGER = "BENCHMARK-LEDGER.csv"
BENCHMARK_REPORT = "BENCHMARK-REPORT.md"
FIELDNAMES = [
    "date",
    "bot_equity",
    "cash",
    "benchmark_symbol",
    "benchmark_close",
    "bot_daily_return_pct",
    "benchmark_daily_return_pct",
    "bot_cumulative_return_pct",
    "benchmark_cumulative_return_pct",
    "alpha_pct",
    "drawdown_pct",
    "exposure_pct",
]

Q4 = Decimal("0.0001")
Q2 = Decimal("0.01")


@dataclass(frozen=True)
class BenchmarkRow:
    date: str
    bot_equity: Decimal
    cash: Decimal
    benchmark_symbol: str
    benchmark_close: Decimal
    bot_daily_return_pct: Decimal
    benchmark_daily_return_pct: Decimal
    bot_cumulative_return_pct: Decimal
    benchmark_cumulative_return_pct: Decimal
    alpha_pct: Decimal
    drawdown_pct: Decimal
    exposure_pct: Decimal

    def as_csv_row(self) -> dict[str, str]:
        return {
            "date": self.date,
            "bot_equity": _money(self.bot_equity),
            "cash": _money(self.cash),
            "benchmark_symbol": self.benchmark_symbol,
            "benchmark_close": _money(self.benchmark_close),
            "bot_daily_return_pct": _pct_value(self.bot_daily_return_pct),
            "benchmark_daily_return_pct": _pct_value(self.benchmark_daily_return_pct),
            "bot_cumulative_return_pct": _pct_value(self.bot_cumulative_return_pct),
            "benchmark_cumulative_return_pct": _pct_value(self.benchmark_cumulative_return_pct),
            "alpha_pct": _pct_value(self.alpha_pct),
            "drawdown_pct": _pct_value(self.drawdown_pct),
            "exposure_pct": _pct_value(self.exposure_pct),
        }

    @classmethod
    def from_csv_row(cls, raw: dict[str, str]) -> "BenchmarkRow":
        return cls(
            date=str(raw["date"]),
            bot_equity=_decimal(raw.get("bot_equity")),
            cash=_decimal(raw.get("cash")),
            benchmark_symbol=str(raw.get("benchmark_symbol") or "SPY"),
            benchmark_close=_decimal(raw.get("benchmark_close")),
            bot_daily_return_pct=_decimal(raw.get("bot_daily_return_pct")),
            benchmark_daily_return_pct=_decimal(raw.get("benchmark_daily_return_pct")),
            bot_cumulative_return_pct=_decimal(raw.get("bot_cumulative_return_pct")),
            benchmark_cumulative_return_pct=_decimal(raw.get("benchmark_cumulative_return_pct")),
            alpha_pct=_decimal(raw.get("alpha_pct")),
            drawdown_pct=_decimal(raw.get("drawdown_pct")),
            exposure_pct=_decimal(raw.get("exposure_pct")),
        )


def memory_path(root: Path, filename: str) -> Path:
    return root / "memory" / filename


def ledger_path(root: Path) -> Path:
    return memory_path(root, BENCHMARK_LEDGER)


def report_path(root: Path) -> Path:
    return memory_path(root, BENCHMARK_REPORT)


def _decimal(value: object, default: Decimal = Decimal("0")) -> Decimal:
    if value is None or value == "":
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


def _ratio_to_pct(current: Decimal, previous: Decimal) -> Decimal:
    if previous <= 0:
        return Decimal("0")
    return ((current / previous) - Decimal("1")) * Decimal("100")


def _pct_value(value: Decimal) -> str:
    return str(value.quantize(Q4, rounding=ROUND_HALF_UP))


def _money(value: Decimal) -> str:
    return str(value.quantize(Q2, rounding=ROUND_HALF_UP))


def parse_account_equity_cash(raw: str) -> tuple[Decimal, Decimal]:
    data = json.loads(raw)
    equity = _decimal(data.get("equity") or data.get("portfolio_value"))
    cash = _decimal(data.get("cash"))
    return equity, cash


def latest_benchmark_close(symbol: str = "SPY") -> Decimal:
    import yfinance as yf

    hist = yf.Ticker(symbol).history(period="7d", interval="1d", auto_adjust=False)
    if hist.empty or "Close" not in hist:
        raise RuntimeError(f"No benchmark close available for {symbol}")
    close = hist["Close"].dropna().iloc[-1]
    price = _decimal(close)
    if price <= 0:
        raise RuntimeError(f"Invalid benchmark close for {symbol}: {close}")
    return price


def load_ledger(path: Path) -> list[BenchmarkRow]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return sorted((BenchmarkRow.from_csv_row(row) for row in reader), key=lambda r: r.date)


def write_ledger(path: Path, rows: Iterable[BenchmarkRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: r.date)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in ordered:
            writer.writerow(row.as_csv_row())


def build_benchmark_row(
    previous_rows: list[BenchmarkRow],
    *,
    stamp: str,
    bot_equity: Decimal,
    cash: Decimal,
    benchmark_close: Decimal,
    benchmark_symbol: str = "SPY",
) -> BenchmarkRow:
    rows = sorted((r for r in previous_rows if r.date != stamp), key=lambda r: r.date)
    prior = rows[-1] if rows else None
    baseline = rows[0] if rows else None

    bot_daily = _ratio_to_pct(bot_equity, prior.bot_equity) if prior else Decimal("0")
    bench_daily = _ratio_to_pct(benchmark_close, prior.benchmark_close) if prior else Decimal("0")

    base_bot = baseline.bot_equity if baseline else bot_equity
    base_bench = baseline.benchmark_close if baseline else benchmark_close
    bot_cumulative = _ratio_to_pct(bot_equity, base_bot)
    bench_cumulative = _ratio_to_pct(benchmark_close, base_bench)
    alpha = bot_cumulative - bench_cumulative
    max_equity = max([bot_equity] + [r.bot_equity for r in rows])
    drawdown = _ratio_to_pct(bot_equity, max_equity)
    exposure = Decimal("0") if bot_equity <= 0 else ((bot_equity - cash) / bot_equity) * Decimal("100")

    return BenchmarkRow(
        date=stamp,
        bot_equity=bot_equity,
        cash=cash,
        benchmark_symbol=benchmark_symbol.upper(),
        benchmark_close=benchmark_close,
        bot_daily_return_pct=bot_daily,
        benchmark_daily_return_pct=bench_daily,
        bot_cumulative_return_pct=bot_cumulative,
        benchmark_cumulative_return_pct=bench_cumulative,
        alpha_pct=alpha,
        drawdown_pct=drawdown,
        exposure_pct=exposure,
    )


def upsert_benchmark_row(path: Path, row: BenchmarkRow) -> list[BenchmarkRow]:
    rows = [r for r in load_ledger(path) if r.date != row.date]
    rows.append(row)
    rows = sorted(rows, key=lambda r: r.date)
    write_ledger(path, rows)
    return rows


def _format_pct(value: Decimal) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value.quantize(Q2, rounding=ROUND_HALF_UP)}%"


def judge_latest(rows: list[BenchmarkRow]) -> str:
    if not rows:
        return "No benchmark rows yet."
    latest = rows[-1]
    if len(rows) < 2:
        return "BASELINE: first benchmark row recorded; judge alpha after the next EOD snapshot."
    if latest.alpha_pct > Decimal("0"):
        return f"AHEAD: Codex is beating {latest.benchmark_symbol} by {_format_pct(latest.alpha_pct)} cumulative alpha."
    if latest.alpha_pct < Decimal("0"):
        return f"BEHIND: Codex trails {latest.benchmark_symbol} by {_format_pct(abs(latest.alpha_pct))} cumulative alpha."
    return f"TIED: Codex is even with {latest.benchmark_symbol} on cumulative return."


def render_benchmark_report(rows: list[BenchmarkRow]) -> str:
    ordered = sorted(rows, key=lambda r: r.date)
    latest = ordered[-1] if ordered else None
    lines = ["# Benchmark Report", ""]
    if latest is None:
        lines += ["No benchmark data recorded yet.", ""]
        return "\n".join(lines)

    lines += [
        f"Last updated: {latest.date}",
        f"Benchmark: {latest.benchmark_symbol}",
        "",
        "## Scoreboard",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Bot equity | ${_money(latest.bot_equity)} |",
        f"| Cash | ${_money(latest.cash)} |",
        f"| Exposure | {_format_pct(latest.exposure_pct)} |",
        f"| {latest.benchmark_symbol} close | ${_money(latest.benchmark_close)} |",
        f"| Bot daily return | {_format_pct(latest.bot_daily_return_pct)} |",
        f"| {latest.benchmark_symbol} daily return | {_format_pct(latest.benchmark_daily_return_pct)} |",
        f"| Bot cumulative return | {_format_pct(latest.bot_cumulative_return_pct)} |",
        f"| {latest.benchmark_symbol} cumulative return | {_format_pct(latest.benchmark_cumulative_return_pct)} |",
        f"| Alpha vs {latest.benchmark_symbol} | {_format_pct(latest.alpha_pct)} |",
        f"| Bot drawdown | {_format_pct(latest.drawdown_pct)} |",
        "",
        "## Judgment",
        "",
        f"- {judge_latest(ordered)}",
        "- If alpha is positive but drawdown/exposure is high, treat the outperformance as unproven risk-taking until weekly attribution confirms the setup quality.",
        "",
        "## Recent rows",
        "",
        "| Date | Bot % | Benchmark % | Alpha | Drawdown | Exposure |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in ordered[-10:]:
        lines.append(
            f"| {row.date} | {_format_pct(row.bot_cumulative_return_pct)} | {_format_pct(row.benchmark_cumulative_return_pct)} | "
            f"{_format_pct(row.alpha_pct)} | {_format_pct(row.drawdown_pct)} | {_format_pct(row.exposure_pct)} |"
        )
    lines.append("")
    return "\n".join(lines)


def record_benchmark_snapshot(
    root: Path,
    *,
    stamp: str | None = None,
    account_raw: str | None = None,
    bot_equity: Decimal | None = None,
    cash: Decimal | None = None,
    benchmark_symbol: str = "SPY",
    benchmark_close: Decimal | None = None,
) -> tuple[BenchmarkRow, list[BenchmarkRow], str]:
    stamp = stamp or date.today().isoformat()
    if account_raw is not None:
        parsed_equity, parsed_cash = parse_account_equity_cash(account_raw)
        bot_equity = bot_equity if bot_equity is not None else parsed_equity
        cash = cash if cash is not None else parsed_cash
    if bot_equity is None or cash is None:
        raise ValueError("bot_equity and cash are required when account_raw is not provided")
    if benchmark_close is None:
        benchmark_close = latest_benchmark_close(benchmark_symbol)

    path = ledger_path(root)
    existing_rows = load_ledger(path)
    row = build_benchmark_row(
        existing_rows,
        stamp=stamp,
        bot_equity=bot_equity,
        cash=cash,
        benchmark_close=benchmark_close,
        benchmark_symbol=benchmark_symbol,
    )
    rows = upsert_benchmark_row(path, row)
    report = render_benchmark_report(rows)
    report_path(root).write_text(report)
    return row, rows, report


def render_weekly_benchmark_review(rows: list[BenchmarkRow], *, today: str | None = None) -> str:
    today = today or date.today().isoformat()
    ordered = sorted(rows, key=lambda r: r.date)
    if not ordered:
        return "\n".join([
            f"\n## Weekly Benchmark Review — {today}",
            "",
            "No benchmark ledger rows yet. Daily summaries must record bot equity and SPY close before weekly judgment is possible.",
            "",
        ])
    latest = ordered[-1]
    latest_date = date.fromisoformat(latest.date)
    week_rows = [r for r in ordered if date.fromisoformat(r.date).isocalendar()[:2] == latest_date.isocalendar()[:2]]
    first = week_rows[0]
    week_bot = _ratio_to_pct(latest.bot_equity, first.bot_equity)
    week_bench = _ratio_to_pct(latest.benchmark_close, first.benchmark_close)
    week_alpha = week_bot - week_bench
    lines = [
        f"\n## Weekly Benchmark Review — {today}",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Rows this week | {len(week_rows)} |",
        f"| Week bot return | {_format_pct(week_bot)} |",
        f"| Week {latest.benchmark_symbol} return | {_format_pct(week_bench)} |",
        f"| Week alpha | {_format_pct(week_alpha)} |",
        f"| Cumulative bot return | {_format_pct(latest.bot_cumulative_return_pct)} |",
        f"| Cumulative {latest.benchmark_symbol} return | {_format_pct(latest.benchmark_cumulative_return_pct)} |",
        f"| Cumulative alpha | {_format_pct(latest.alpha_pct)} |",
        f"| Current drawdown | {_format_pct(latest.drawdown_pct)} |",
        f"| Exposure | {_format_pct(latest.exposure_pct)} |",
        "",
        "### Judgment",
        f"- {judge_latest(ordered)}",
        "- Do not treat one-week or one-month alpha as proven until setup attribution, drawdown, and execution quality are reviewed.",
        "- Next required analysis: tag winners/losers by setup type and compare TradingView MCP technical picks vs Perplexity/news-catalyst picks.",
        "",
    ]
    return "\n".join(lines)


def render_trade_log_benchmark_section(row: BenchmarkRow, rows: list[BenchmarkRow]) -> str:
    return "\n".join([
        "### Benchmark",
        f"- Benchmark: {row.benchmark_symbol} close ${_money(row.benchmark_close)}",
        f"- Bot daily return: {_format_pct(row.bot_daily_return_pct)}",
        f"- {row.benchmark_symbol} daily return: {_format_pct(row.benchmark_daily_return_pct)}",
        f"- Bot cumulative return: {_format_pct(row.bot_cumulative_return_pct)}",
        f"- {row.benchmark_symbol} cumulative return: {_format_pct(row.benchmark_cumulative_return_pct)}",
        f"- Alpha vs {row.benchmark_symbol}: {_format_pct(row.alpha_pct)}",
        f"- Drawdown: {_format_pct(row.drawdown_pct)}",
        f"- Judgment: {judge_latest(rows)}",
    ])
