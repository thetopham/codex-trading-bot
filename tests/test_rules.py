from decimal import Decimal

from codex_trader.rules import (
    AccountState,
    Position,
    TradeIdea,
    max_position_notional_for_risk,
    quantity_for_portfolio_risk,
    should_cut_loss,
    trailing_stop_percent_for_position,
    validate_buy_gate,
)


def account(equity="10000", cash="10000", daytrade_count=0):
    return AccountState(equity=Decimal(equity), cash=Decimal(cash), buying_power=Decimal(cash), daytrade_count=daytrade_count)


def pos(symbol="ABC", plpc="0"):
    return Position(symbol=symbol, qty=Decimal("1"), market_value=Decimal("100"), avg_entry_price=Decimal("100"), current_price=Decimal("100"), unrealized_plpc=Decimal(plpc))


def test_buy_gate_approves_stock_with_catalyst_under_caps():
    idea = TradeIdea(symbol="XOM", qty=Decimal("10"), estimated_price=Decimal("100"), catalyst="oil breakout")
    result = validate_buy_gate(account=account(), positions=[], idea=idea)
    assert result.approved
    assert result.reasons == ()


def test_buy_gate_rejects_options_and_missing_catalyst():
    idea = TradeIdea(symbol="SPY240101C", qty=Decimal("1"), estimated_price=Decimal("100"), catalyst="", instrument_class="option")
    result = validate_buy_gate(account=account(), positions=[], idea=idea)
    assert not result.approved
    assert "instrument_not_stock" in result.reasons
    assert "missing_documented_catalyst" in result.reasons


def test_buy_gate_enforces_position_cash_weekly_and_pdt_caps():
    idea = TradeIdea(symbol="MSFT", qty=Decimal("30"), estimated_price=Decimal("100"), catalyst="earnings")
    positions = [pos(str(i)) for i in range(6)]
    result = validate_buy_gate(
        account=account(equity="10000", cash="500", daytrade_count=3),
        positions=positions,
        idea=idea,
        trade_log_text="New trade:\nNew trade:\nNew trade:\n",
    )
    assert not result.approved
    for reason in [
        "too_many_open_positions_after_fill",
        "weekly_trade_cap_exceeded",
        "position_risk_exceeds_1pct_portfolio_at_10pct_stop",
        "insufficient_cash",
        "pdt_daytrade_count_full",
    ]:
        assert reason in result.reasons


def test_risk_sizing_limits_10pct_stop_to_1pct_of_portfolio():
    acct = account(equity="50000", cash="50000")
    assert max_position_notional_for_risk(acct) == Decimal("5000")
    assert quantity_for_portfolio_risk(acct, price=Decimal("192.50")) == Decimal("25")

    idea = TradeIdea(symbol="SPCX", qty=Decimal("25"), estimated_price=Decimal("192.50"), catalyst="top volume")
    assert idea.estimated_cost == Decimal("4812.50")
    assert idea.estimated_stop_loss == Decimal("481.2500")
    assert idea.estimated_stop_loss <= acct.equity * Decimal("0.01")


def test_buy_gate_rejects_position_whose_10pct_stop_exceeds_1pct_portfolio():
    idea = TradeIdea(symbol="SPCX", qty=Decimal("26"), estimated_price=Decimal("192.50"), catalyst="top volume")
    result = validate_buy_gate(account=account(equity="50000", cash="50000"), positions=[], idea=idea)
    assert not result.approved
    assert "position_risk_exceeds_1pct_portfolio_at_10pct_stop" in result.reasons


def test_buy_gate_rejects_zero_quantity():
    idea = TradeIdea(symbol="BRK.A", qty=Decimal("0"), estimated_price=Decimal("600000"), catalyst="top volume")
    result = validate_buy_gate(account=account(equity="50000", cash="50000"), positions=[], idea=idea)
    assert not result.approved
    assert "invalid_quantity" in result.reasons


def test_midday_loss_and_trailing_rules():
    assert should_cut_loss(pos(plpc="-0.071"))
    assert not should_cut_loss(pos(plpc="-0.05"))
    assert trailing_stop_percent_for_position(pos(plpc="0.151")) == Decimal("7")
    assert trailing_stop_percent_for_position(pos(plpc="0.20")) == Decimal("5")
    assert trailing_stop_percent_for_position(pos(plpc="0.10")) is None
