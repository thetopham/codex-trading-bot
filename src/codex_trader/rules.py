from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
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

    @property
    def estimated_cost(self) -> Decimal:
        return self.qty * self.estimated_price


@dataclass(frozen=True)
class GateResult:
    approved: bool
    reasons: tuple[str, ...]


def _weekly_trade_count(trade_log_text: str) -> int:
    # Count only submitted paper/new trade markers for the current ISO week.
    current_year, current_week, _ = date.today().isocalendar()
    count = 0
    current_heading_date: date | None = None
    for line in trade_log_text.splitlines():
        if line.startswith("## ") and "—" in line:
            maybe_date = line.rsplit("—", 1)[-1].strip()
            try:
                current_heading_date = date.fromisoformat(maybe_date)
            except ValueError:
                current_heading_date = None
        if "Broker action: paper_submit buy_ok=True" in line or line.startswith("New trade:"):
            if current_heading_date is None:
                count += 1
                continue
            year, week, _ = current_heading_date.isocalendar()
            if year == current_year and week == current_week:
                count += 1
    return count


def validate_buy_gate(
    *,
    account: AccountState,
    positions: Iterable[Position],
    idea: TradeIdea,
    trade_log_text: str = "",
    max_positions: int = 6,
    max_trades_per_week: int = 3,
    max_position_equity_pct: Decimal = Decimal("0.20"),
    max_daytrade_count_under_25k: int = 3,
) -> GateResult:
    reasons: list[str] = []
    current_positions = list(positions)

    if idea.instrument_class.lower() != "stock":
        reasons.append("instrument_not_stock")
    if not idea.catalyst.strip():
        reasons.append("missing_documented_catalyst")
    if len(current_positions) + 1 > max_positions:
        reasons.append("too_many_open_positions_after_fill")
    if _weekly_trade_count(trade_log_text) + 1 > max_trades_per_week:
        reasons.append("weekly_trade_cap_exceeded")
    if account.equity <= 0:
        reasons.append("invalid_equity")
    else:
        max_cost = account.equity * max_position_equity_pct
        if idea.estimated_cost > max_cost:
            reasons.append("position_cost_exceeds_20pct_equity")
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
