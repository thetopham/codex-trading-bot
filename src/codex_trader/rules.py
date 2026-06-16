from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Any, Iterable


@dataclass(frozen=True)
class AccountState:
    equity: Decimal
    cash: Decimal
    buying_power: Decimal
    daytrade_count: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "AccountState":
        return cls(
            equity=Decimal(str(data.get("equity", "0"))),
            cash=Decimal(str(data.get("cash", "0"))),
            buying_power=Decimal(str(data.get("buying_power", data.get("cash", "0")))),
            daytrade_count=int(data.get("daytrade_count", 0) or 0),
        )


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: Decimal
    market_value: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    unrealized_plpc: Decimal
    sector: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Position":
        return cls(
            symbol=str(data["symbol"]).upper(),
            qty=Decimal(str(data.get("qty", "0"))),
            market_value=Decimal(str(data.get("market_value", "0"))),
            avg_entry_price=Decimal(str(data.get("avg_entry_price", "0"))),
            current_price=Decimal(str(data.get("current_price", data.get("lastday_price", "0")))),
            unrealized_plpc=Decimal(str(data.get("unrealized_plpc", "0"))),
            sector=data.get("sector"),
        )


@dataclass(frozen=True)
class TradeIdea:
    symbol: str
    qty: Decimal
    estimated_price: Decimal
    catalyst: str
    instrument_class: str = "stock"
    sector: str | None = None
    stop_loss_pct: Decimal = Decimal("0.10")

    @property
    def estimated_cost(self) -> Decimal:
        return self.qty * self.estimated_price

    @property
    def estimated_stop_loss(self) -> Decimal:
        return self.estimated_cost * self.stop_loss_pct


def max_position_notional_for_risk(
    account: AccountState,
    *,
    max_portfolio_risk_pct: Decimal = Decimal("0.01"),
    stop_loss_pct: Decimal = Decimal("0.10"),
) -> Decimal:
    if account.equity <= 0 or stop_loss_pct <= 0:
        return Decimal("0")
    return account.equity * max_portfolio_risk_pct / stop_loss_pct


def quantity_for_portfolio_risk(
    account: AccountState,
    *,
    price: Decimal,
    max_portfolio_risk_pct: Decimal = Decimal("0.01"),
    stop_loss_pct: Decimal = Decimal("0.10"),
) -> Decimal:
    if price <= 0:
        return Decimal("0")
    notional = max_position_notional_for_risk(
        account,
        max_portfolio_risk_pct=max_portfolio_risk_pct,
        stop_loss_pct=stop_loss_pct,
    )
    qty = (notional / price).to_integral_value(rounding=ROUND_DOWN)
    return max(Decimal("0"), qty)


@dataclass(frozen=True)
class GateResult:
    approved: bool
    reasons: tuple[str, ...]


def validate_buy_gate(
    *,
    account: AccountState,
    positions: Iterable[Position],
    idea: TradeIdea,
    trade_log_text: str = "",
    max_portfolio_risk_pct: Decimal = Decimal("0.01"),
    stop_loss_pct: Decimal = Decimal("0.10"),
    max_daytrade_count_under_25k: int = 3,
) -> GateResult:
    reasons: list[str] = []
    # `positions` and `trade_log_text` are accepted for call-site compatibility and future
    # portfolio analytics, but they no longer cap opportunity count. Risk is managed per
    # position through stop-loss sizing and by the available-cash gate.
    _ = (positions, trade_log_text)

    if idea.qty <= 0:
        reasons.append("invalid_quantity")
    if idea.instrument_class.lower() != "stock":
        reasons.append("instrument_not_stock")
    if not idea.catalyst.strip():
        reasons.append("missing_documented_catalyst")
    if account.equity <= 0:
        reasons.append("invalid_equity")
    else:
        max_cost = max_position_notional_for_risk(
            account,
            max_portfolio_risk_pct=max_portfolio_risk_pct,
            stop_loss_pct=stop_loss_pct,
        )
        if idea.estimated_cost > max_cost:
            reasons.append("position_risk_exceeds_1pct_portfolio_at_10pct_stop")
    if idea.estimated_cost > account.cash:
        reasons.append("insufficient_cash")
    if account.equity < Decimal("25000") and account.daytrade_count >= max_daytrade_count_under_25k:
        reasons.append("pdt_daytrade_count_full")

    return GateResult(approved=not reasons, reasons=tuple(reasons))


def trailing_stop_percent_for_position(position: Position) -> Decimal | None:
    if position.unrealized_plpc >= Decimal("0.20"):
        return Decimal("5")
    if position.unrealized_plpc >= Decimal("0.15"):
        return Decimal("7")
    return None


def should_cut_loss(position: Position, loss_cut_pct: Decimal = Decimal("-0.07")) -> bool:
    return position.unrealized_plpc <= loss_cut_pct
