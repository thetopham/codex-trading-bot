from decimal import Decimal

from codex_trader.benchmark import (
    BENCHMARK_LEDGER,
    build_benchmark_row,
    judge_latest,
    load_ledger,
    parse_account_equity_cash,
    record_benchmark_snapshot,
    render_trade_log_benchmark_section,
    render_weekly_benchmark_review,
)


def test_parse_account_equity_cash_from_alpaca_json():
    equity, cash = parse_account_equity_cash('{"equity":"50000.12","cash":"12345.67"}')
    assert equity == Decimal("50000.12")
    assert cash == Decimal("12345.67")


def test_build_benchmark_row_computes_daily_cumulative_alpha_and_drawdown():
    first = build_benchmark_row(
        [],
        stamp="2026-06-01",
        bot_equity=Decimal("50000"),
        cash=Decimal("25000"),
        benchmark_close=Decimal("500"),
    )
    second = build_benchmark_row(
        [first],
        stamp="2026-06-02",
        bot_equity=Decimal("51000"),
        cash=Decimal("20000"),
        benchmark_close=Decimal("505"),
    )
    assert second.bot_daily_return_pct == Decimal("2.00")
    assert second.benchmark_daily_return_pct == Decimal("1.00")
    assert second.bot_cumulative_return_pct == Decimal("2.00")
    assert second.benchmark_cumulative_return_pct == Decimal("1.00")
    assert second.alpha_pct == Decimal("1.00")
    assert second.drawdown_pct == Decimal("0")
    assert second.exposure_pct.quantize(Decimal("0.01")) == Decimal("60.78")


def test_record_benchmark_snapshot_upserts_ledger_and_report(tmp_path):
    row1, rows1, report1 = record_benchmark_snapshot(
        tmp_path,
        stamp="2026-06-01",
        bot_equity=Decimal("50000"),
        cash=Decimal("50000"),
        benchmark_close=Decimal("500"),
    )
    assert row1.alpha_pct == Decimal("0")
    assert "BASELINE" in report1

    row2, rows2, report2 = record_benchmark_snapshot(
        tmp_path,
        stamp="2026-06-02",
        bot_equity=Decimal("54000"),
        cash=Decimal("10000"),
        benchmark_close=Decimal("510"),
    )
    assert len(rows1) == 1
    assert len(rows2) == 2
    assert row2.bot_cumulative_return_pct == Decimal("8.00")
    assert row2.benchmark_cumulative_return_pct == Decimal("2.00")
    assert row2.alpha_pct == Decimal("6.00")
    assert "AHEAD" in report2
    assert (tmp_path / "memory" / BENCHMARK_LEDGER).exists()
    assert (tmp_path / "memory" / "BENCHMARK-REPORT.md").exists()

    loaded = load_ledger(tmp_path / "memory" / BENCHMARK_LEDGER)
    assert [r.date for r in loaded] == ["2026-06-01", "2026-06-02"]


def test_render_trade_log_benchmark_section_includes_judgment():
    first = build_benchmark_row(
        [],
        stamp="2026-06-01",
        bot_equity=Decimal("50000"),
        cash=Decimal("50000"),
        benchmark_close=Decimal("500"),
    )
    second = build_benchmark_row(
        [first],
        stamp="2026-06-02",
        bot_equity=Decimal("49000"),
        cash=Decimal("10000"),
        benchmark_close=Decimal("505"),
    )
    section = render_trade_log_benchmark_section(second, [first, second])
    assert "Alpha vs SPY" in section
    assert judge_latest([first, second]) in section
    assert "BEHIND" in section


def test_render_weekly_benchmark_review_judges_week_and_cumulative_alpha():
    first = build_benchmark_row(
        [],
        stamp="2026-06-15",
        bot_equity=Decimal("50000"),
        cash=Decimal("40000"),
        benchmark_close=Decimal("500"),
    )
    second = build_benchmark_row(
        [first],
        stamp="2026-06-16",
        bot_equity=Decimal("55000"),
        cash=Decimal("10000"),
        benchmark_close=Decimal("510"),
    )
    review = render_weekly_benchmark_review([first, second], today="2026-06-19")
    assert "Weekly Benchmark Review — 2026-06-19" in review
    assert "Week alpha" in review
    assert "+8.00%" in review
    assert "AHEAD" in review
