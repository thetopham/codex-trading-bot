# Trading Strategy

Safety boundary: paper/dry-run by default. Stocks only; no options.

## Hard Rules
- Max 6 open positions.
- Max 20% of equity per position.
- Max 3 new trades per week.
- Every new position requires a documented catalyst.
- Every new position gets a 10% GTC trailing stop in paper/live-approved modes.
- Cut losers at -7%.
- Tighten trail to 7% at +15%, 5% at +20%.
- Never move a stop down.
- Telegram notifications are sparse: action taken or required daily/weekly summary.
