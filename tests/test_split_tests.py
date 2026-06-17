from decimal import Decimal
from pathlib import Path

from codex_trader.split_tests import load_split_test_variants, render_variants_table, validate_variant

ROOT = Path(__file__).resolve().parents[1]


def variant_by_id(variant_id: str):
    variants = load_split_test_variants(ROOT)
    return {variant.variant_id: variant for variant in variants}[variant_id]


def test_opus_split_test_configs_are_shadow_only_and_valid():
    variants = load_split_test_variants(ROOT)
    ids = {variant.variant_id for variant in variants}

    assert "opus_original_hermes_codex_perplexity" in ids
    assert "opus_original_hermes_codex_perplexity_1pct_risk" in ids
    assert len(ids) == len(variants)
    assert all(validate_variant(variant) == [] for variant in variants)
    assert all(not variant.execution.submit_orders for variant in variants)
    assert all(variant.execution.mode == "shadow_paper" for variant in variants)


def test_original_opus_variant_uses_20pct_position_cap_and_10pct_stop():
    variant = variant_by_id("opus_original_hermes_codex_perplexity")
    equity = Decimal("50000")

    assert variant.objective == "beat_spx"
    assert set(variant.operator_stack) == {"Hermes", "Codex"}
    assert variant.research.primary == "perplexity"
    assert variant.risk.position_sizing == "equity_pct_cap"
    assert variant.position_notional_cap(equity) == Decimal("10000.00")
    assert variant.account_risk_at_stop(equity) == Decimal("1000.0000")
    assert variant.account_risk_pct_at_stop(equity) == Decimal("0.0200")


def test_one_percent_risk_variant_changes_only_sizing_risk():
    original = variant_by_id("opus_original_hermes_codex_perplexity")
    safer = variant_by_id("opus_original_hermes_codex_perplexity_1pct_risk")
    equity = Decimal("50000")

    assert safer.objective == original.objective == "beat_spx"
    assert safer.operator_stack == original.operator_stack
    assert safer.research.primary == original.research.primary == "perplexity"
    assert safer.risk.stop_loss_pct == original.risk.stop_loss_pct == Decimal("0.10")
    assert safer.risk.max_account_risk_pct == Decimal("0.01")
    assert safer.position_notional_cap(equity) == Decimal("5000.0")
    assert safer.account_risk_at_stop(equity) == Decimal("500.000")
    assert safer.account_risk_pct_at_stop(equity) == Decimal("0.010")


def test_render_variants_table_shows_both_new_split_tests():
    table = render_variants_table(load_split_test_variants(ROOT), equity=Decimal("10000"))

    assert "opus_original_hermes_codex_perplexity" in table
    assert "opus_original_hermes_codex_perplexity_1pct_risk" in table
    assert "OK shadow-only" in table
