from __future__ import annotations

import json
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .wrappers import ScriptResult, run_script


@dataclass(frozen=True)
class PaperOrderResult:
    symbol: str
    qty: int
    buy_ok: bool
    stop_ok: bool
    buy_response: str
    stop_response: str


def _order_id(raw: str) -> str | None:
    try:
        data = json.loads(raw)
    except Exception:
        return None
    oid = data.get("id")
    return str(oid) if oid else None


def _filled_qty(raw: str, requested_qty: int) -> int:
    try:
        data = json.loads(raw)
    except Exception:
        return requested_qty
    for key in ("filled_qty", "qty"):
        val = data.get(key)
        if val is not None:
            try:
                parsed = int(Decimal(str(val)))
                return parsed if parsed > 0 else requested_qty
            except Exception:
                pass
    return requested_qty


def submit_market_buy_with_trailing_stop(
    root: Path,
    *,
    symbol: str,
    qty: int,
    trail_percent: Decimal = Decimal("10"),
    stop_attempts: int = 3,
    stop_retry_delay: float = 1.0,
) -> PaperOrderResult:
    if qty <= 0:
        raise ValueError("qty must be positive")
    buy_body = json.dumps({
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    })
    buy = run_script(root, "alpaca.sh", "order", buy_body)
    if not buy.ok:
        return PaperOrderResult(symbol.upper(), qty, False, False, buy.stderr or buy.stdout, "skipped_stop_due_to_buy_failure")

    stop_qty = _filled_qty(buy.stdout, qty)
    stop_body = json.dumps({
        "symbol": symbol.upper(),
        "qty": str(stop_qty),
        "side": "sell",
        "type": "trailing_stop",
        "trail_percent": str(trail_percent),
        "time_in_force": "gtc",
    })
    attempts = max(1, stop_attempts)
    stop: ScriptResult | None = None
    stop_errors: list[str] = []
    for attempt in range(1, attempts + 1):
        stop = run_script(root, "alpaca.sh", "order", stop_body)
        if stop.ok:
            break
        stop_errors.append(f"attempt {attempt}: {stop.stderr or stop.stdout}")
        if attempt < attempts and stop_retry_delay > 0:
            time.sleep(stop_retry_delay)
    assert stop is not None
    stop_response = stop.stdout if stop.ok else "; ".join(stop_errors)
    return PaperOrderResult(
        symbol=symbol.upper(),
        qty=stop_qty,
        buy_ok=buy.ok,
        stop_ok=stop.ok,
        buy_response=buy.stdout if buy.ok else (buy.stderr or buy.stdout),
        stop_response=stop_response,
    )


def paper_submission_enabled() -> bool:
    import os
    return os.environ.get("PAPER_ORDER_SUBMISSION", "false").lower() == "true" and os.environ.get("DRY_RUN", "true").lower() == "false"
