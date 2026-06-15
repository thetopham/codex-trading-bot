from __future__ import annotations

import json
from typing import Any

SENSITIVE_ACCOUNT_FIELDS = {
    "id",
    "account_number",
    "admin_configurations",
    "user_configurations",
    "created_at",
}

ACCOUNT_SUMMARY_FIELDS = [
    "status",
    "currency",
    "equity",
    "cash",
    "portfolio_value",
    "buying_power",
    "daytrading_buying_power",
    "long_market_value",
    "short_market_value",
    "position_market_value",
    "pattern_day_trader",
    "daytrade_count",
    "trading_blocked",
    "transfers_blocked",
    "account_blocked",
    "trade_suspended_by_user",
]


def account_summary(raw: str) -> str:
    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    summary = {k: data.get(k) for k in ACCOUNT_SUMMARY_FIELDS if k in data}
    return json.dumps(summary, sort_keys=True)


def positions_summary(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip()
    if not isinstance(data, list):
        return json.dumps(data, sort_keys=True)
    keep = [
        "symbol",
        "qty",
        "market_value",
        "avg_entry_price",
        "current_price",
        "unrealized_pl",
        "unrealized_plpc",
    ]
    out = []
    for row in data:
        if isinstance(row, dict):
            out.append({k: row.get(k) for k in keep if k in row})
        else:
            out.append(row)
    return json.dumps(out, sort_keys=True)
