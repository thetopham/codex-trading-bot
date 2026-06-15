from datetime import date
from decimal import Decimal

from codex_trader.research import Candidate, render_research_markdown


def test_render_research_markdown_contains_top_volume_and_candidate_fields():
    c = Candidate(
        symbol="NVDA",
        last_price=Decimal("100.00"),
        volume=1000000,
        avg_volume=500000,
        day_change_pct=Decimal("2.00"),
        five_day_change_pct=Decimal("5.00"),
        score=Decimal("8.50"),
        sector="technology",
    )
    md = render_research_markdown([c], [c], today=date(2026, 1, 2))
    assert "Pre-market Research — 2026-01-02" in md
    assert "Yahoo Finance" in md
    assert "| 1 | NVDA" in md
    assert "Sizing note: market-open computes qty from live equity" in md
    assert "Reference stop discipline: 10% trailing stop" in md
    assert "Reference target: 120.00" in md
