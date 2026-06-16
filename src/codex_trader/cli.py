from __future__ import annotations

import argparse
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from .broker import paper_submission_enabled, submit_market_buy_with_trailing_stop
from .memory import MemoryStore, initialize_memory
from .premarket import CANDIDATES_FILE, filter_signals_by_liquidity, load_premarket_signals
from .research import render_liquidity_filter_markdown, top_volume_candidates
from .rules import (
    AccountState,
    Position,
    TradeIdea,
    quantity_for_portfolio_risk,
    should_cut_loss,
    trailing_stop_percent_for_position,
    validate_buy_gate,
)
from .sanitize import account_summary, positions_summary
from .wrappers import run_script


def _root() -> Path:
    return Path.cwd()


def cmd_init(args: argparse.Namespace) -> int:
    initialize_memory(_root())
    print("initialized memory files")
    return 0


def cmd_portfolio(args: argparse.Namespace) -> int:
    root = _root()
    acct = run_script(root, "alpaca.sh", "account")
    pos = run_script(root, "alpaca.sh", "positions")
    orders = run_script(root, "alpaca.sh", "orders")
    print("# Portfolio Snapshot")
    for label, result in [("account", acct), ("positions", pos), ("orders", orders)]:
        print(f"\n## {label}")
        print(result.stdout if result.ok else (result.stderr or result.stdout))
    return 0 if acct.ok and pos.ok and orders.ok else 2


def cmd_check_trade(args: argparse.Namespace) -> int:
    account = AccountState(
        equity=Decimal(args.equity),
        cash=Decimal(args.cash),
        buying_power=Decimal(args.cash),
        daytrade_count=args.daytrade_count,
    )
    positions = [
        Position(symbol=f"P{i}", qty=Decimal("1"), market_value=Decimal("1"), avg_entry_price=Decimal("1"), current_price=Decimal("1"), unrealized_plpc=Decimal("0"))
        for i in range(args.current_positions)
    ]
    idea = TradeIdea(
        symbol=args.symbol.upper(),
        qty=Decimal(args.qty),
        estimated_price=Decimal(args.price),
        catalyst=args.catalyst,
        instrument_class=args.instrument_class,
    )
    result = validate_buy_gate(account=account, positions=positions, idea=idea, trade_log_text=args.trade_log_text)
    payload = {
        "approved": result.approved,
        "reasons": list(result.reasons),
        "estimated_cost": str(idea.estimated_cost),
        "symbol": idea.symbol,
    }
    print(json.dumps(payload, indent=2))
    return 0 if result.approved else 1


def cmd_midday_scan(args: argparse.Namespace) -> int:
    root = _root()
    positions_result = run_script(root, "alpaca.sh", "positions")
    if not positions_result.ok:
        print(positions_result.stderr or positions_result.stdout)
        return positions_result.returncode
    raw_positions = json.loads(positions_result.stdout or "[]")
    actions: list[str] = []
    for raw in raw_positions:
        p = Position.from_api(raw)
        if should_cut_loss(p):
            actions.append(f"CUT {p.symbol}: unrealized P/L {p.unrealized_plpc:.2%} <= -7%")
        trail = trailing_stop_percent_for_position(p)
        if trail is not None:
            actions.append(f"TIGHTEN {p.symbol}: trail_percent={trail} due to unrealized P/L {p.unrealized_plpc:.2%}")
    if not actions:
        print("No midday actions required.")
        return 0
    print("\n".join(actions))
    if not args.dry_run:
        print("Order submission intentionally not implemented in v1 CLI; use scripts/alpaca.sh after explicit approval.")
        return 3
    return 0


def cmd_pre_market(args: argparse.Namespace) -> int:
    root = _root()
    store = MemoryStore(root)
    top, _legacy_selected = top_volume_candidates(limit=args.limit, picks=args.picks)
    markdown = render_liquidity_filter_markdown(top)
    store.append("RESEARCH-LOG.md", markdown)
    message = (
        f"Codex pre-market liquidity filter: top-volume universe refreshed ({len(top)} symbols). "
        f"TradingView MCP agent must write memory/{CANDIDATES_FILE} before market-open."
    )
    run_script(root, "telegram.sh", message)
    print(message)
    return 0


def cmd_market_open_intents(args: argparse.Namespace) -> int:
    root = _root()
    store = MemoryStore(root)
    acct_result = run_script(root, "alpaca.sh", "account")
    pos_result = run_script(root, "alpaca.sh", "positions")
    if not acct_result.ok or not pos_result.ok:
        print(acct_result.stderr or acct_result.stdout)
        print(pos_result.stderr or pos_result.stdout)
        return 2
    account = AccountState.from_api(json.loads(acct_result.stdout))
    positions = [Position.from_api(p) for p in json.loads(pos_result.stdout or "[]")]
    top_by_volume, _legacy_selected = top_volume_candidates(limit=args.limit, picks=args.picks)
    signals, signal_status = load_premarket_signals(root)
    selected_pairs, liquidity_skips = filter_signals_by_liquidity(signals, top_by_volume, limit=args.picks)
    trade_log_text = store.read("TRADE-LOG.md")
    lines = [f"\n## Market-open TradingView MCP Candidates — {date.today().isoformat()}", ""]
    lines += [
        f"- Candidate source: memory/{CANDIDATES_FILE}",
        f"- Candidate file status: {signal_status}",
        f"- Liquidity filter: current top {len(top_by_volume)} stocks by reported volume",
        f"- Liquidity skips: {', '.join(liquidity_skips) if liquidity_skips else 'none'}",
        "",
    ]
    approved = []
    submitted = []
    submit_enabled = paper_submission_enabled()
    max_submit = args.max_submit
    if not selected_pairs:
        lines += [
            "No market-open candidates passed the TradingView MCP + top-volume liquidity intersection. No broker submissions attempted.",
            "",
        ]
    for signal, c in selected_pairs:
        qty = quantity_for_portfolio_risk(account, price=c.last_price)
        idea = TradeIdea(symbol=c.symbol, qty=qty, estimated_price=c.last_price, catalyst=signal.catalyst, sector=c.sector)
        gate = validate_buy_gate(account=account, positions=positions, idea=idea, trade_log_text=trade_log_text)
        status = "APPROVED_DRY_RUN" if gate.approved else "SKIPPED"
        if gate.approved:
            approved.append(c.symbol)
        broker_action = "none; DRY_RUN intent only"
        if gate.approved and submit_enabled and len(submitted) < max_submit:
            result = submit_market_buy_with_trailing_stop(root, symbol=c.symbol, qty=int(qty))
            if result.buy_ok:
                submitted.append(c.symbol)
            broker_action = f"paper_submit buy_ok={result.buy_ok} trailing_stop_ok={result.stop_ok} qty={result.qty}"
        lines += [
            f"### {c.symbol} — {status}",
            f"- Qty: {qty}",
            f"- Reference price: {c.last_price}",
            f"- Estimated cost: {idea.estimated_cost}",
            f"- Risk at 10% stop: {idea.estimated_stop_loss}",
            f"- Stop: 10% trailing stop; paper order uses trail_percent=10",
            f"- Target: {c.target}",
            f"- MCP score: {signal.mcp_score}",
            f"- MCP sources: {', '.join(signal.sources) if signal.sources else 'unspecified'}",
            f"- MCP notes: {signal.notes or 'none'}",
            f"- Catalyst: {signal.catalyst}",
            f"- Gate reasons: {', '.join(gate.reasons) if gate.reasons else 'none'}",
            f"- Broker action: {broker_action}.",
            "",
        ]
    store.append("TRADE-LOG.md", "\n".join(lines))
    mode = "paper orders submitted" if submitted else "dry-run/no submissions"
    message = f"Codex market-open: approved={', '.join(approved) if approved else 'none'}; submitted={', '.join(submitted) if submitted else 'none'}; mode={mode}."
    run_script(root, "telegram.sh", message)
    print(message)
    return 0


def cmd_daily_summary(args: argparse.Namespace) -> int:
    root = _root()
    store = MemoryStore(root)
    acct = run_script(root, "alpaca.sh", "account")
    positions = run_script(root, "alpaca.sh", "positions")
    stamp = date.today().isoformat()
    entry = f"""
\n## EOD Snapshot — {stamp}

### Account
```json
{account_summary(acct.stdout) if acct.ok else acct.stderr.strip()}
```

### Positions
```json
{positions_summary(positions.stdout) if positions.ok else positions.stderr.strip()}
```
"""
    store.append("TRADE-LOG.md", entry)
    message = f"Codex paper bot EOD {stamp}: snapshot appended. Account ok={acct.ok}; positions ok={positions.ok}."
    run_script(root, "telegram.sh", message)
    print(message)
    return 0 if acct.ok and positions.ok else 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="codex-trader")
    sub = p.add_subparsers(required=True)

    init = sub.add_parser("init-memory")
    init.set_defaults(func=cmd_init)

    portfolio = sub.add_parser("portfolio")
    portfolio.set_defaults(func=cmd_portfolio)

    check = sub.add_parser("check-trade")
    check.add_argument("symbol")
    check.add_argument("qty")
    check.add_argument("price")
    check.add_argument("--equity", default="10000")
    check.add_argument("--cash", default="10000")
    check.add_argument("--daytrade-count", type=int, default=0)
    check.add_argument("--current-positions", type=int, default=0)
    check.add_argument("--catalyst", default="")
    check.add_argument("--instrument-class", default="stock")
    check.add_argument("--trade-log-text", default="")
    check.set_defaults(func=cmd_check_trade)

    midday = sub.add_parser("midday-scan")
    midday.add_argument("--dry-run", action="store_true", default=True)
    midday.set_defaults(func=cmd_midday_scan)

    pre = sub.add_parser("pre-market-research")
    pre.add_argument("--limit", type=int, default=100)
    pre.add_argument("--picks", type=int, default=5)
    pre.set_defaults(func=cmd_pre_market)

    intents = sub.add_parser("market-open-intents")
    intents.add_argument("--limit", type=int, default=100)
    intents.add_argument("--picks", type=int, default=3)
    intents.add_argument("--max-submit", type=int, default=3)
    intents.set_defaults(func=cmd_market_open_intents)

    daily = sub.add_parser("daily-summary")
    daily.set_defaults(func=cmd_daily_summary)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
