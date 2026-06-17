# Codex Trader — Hermes/Codex Edition

A safe, repo-backed swing-trading agent scaffold. Mission: beat the S&P 500 / SPX benchmark over the challenge window using Alpaca paper trading; use SPY as the practical benchmark proxy when needed.

**Key adaptations:**
- **Hermes cron jobs** replace Claude cloud routines.
- **Codex/Hermes agents** replace Claude Code as the operator/researcher.
- **Telegram** replaces ClickUp for notifications.
- **Alpaca paper + `DRY_RUN=true`** is the default. Live order submission is not enabled by default.

## Safety Boundary

This repo is currently a **dry-run / paper-trading scaffold**:
- Read-only Alpaca calls work with paper credentials.
- Mutating Alpaca wrapper commands (`order`, `cancel`, `close`) refuse to run while `DRY_RUN=true`.
- The Python CLI's `midday-scan` only prints intended actions in v1.

## Quickstart

```bash
cd /home/matt/workspace/codex-trading-bot
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[test]'
cp env.template .env   # fill paper Alpaca + Telegram if desired
codex-trader init-memory
codex-trader check-trade XOM 10 100 --equity 10000 --cash 5000 --catalyst 'example catalyst'
bash scripts/telegram.sh 'Codex Trader smoke test'
```

If Telegram env vars are missing, the notification script appends to `DAILY-SUMMARY.md` instead of failing.

## Repo Layout

```text
AGENTS.md                 # Codex/Hermes agent rulebook
README.md
pyproject.toml
scripts/
  alpaca.sh               # Alpaca wrapper; dry-run guards mutating calls
  perplexity.sh           # optional cited market/news research wrapper
  telegram.sh             # Telegram notification wrapper with local fallback
src/codex_trader/
  cli.py                  # CLI commands
  benchmark.py            # bot-vs-SPY ledger/report/judgment logic
  research.py             # top-volume Yahoo Finance scanner and candidate renderer
  split_tests.py          # shadow split-test variant loader/validator
  memory.py               # markdown memory helpers
configs/split_tests/      # shadow-only strategy variants; never submit broker orders
memory/                   # git-backed agent memory
routines/                 # Hermes cron prompt templates
.claude/commands/         # compatibility aliases for local slash-style docs
```

## Core CLI

```bash
codex-trader pre-market-research     # refresh top-volume liquidity filter for MCP screening
codex-trader market-open-intents     # use today's TradingView MCP candidates + liquidity/risk gates
codex-trader portfolio              # account/positions/orders via Alpaca wrapper
codex-trader check-trade ...         # deterministic buy-side gate check
codex-trader midday-scan             # dry-run action scan from positions
codex-trader daily-summary           # append EOD snapshot, SPY benchmark row/report, Telegram/fallback notify
codex-trader benchmark-report        # manual/backfill bot-vs-SPY ledger/report update
codex-trader weekly-review           # append weekly benchmark judgment to WEEKLY-REVIEW.md
codex-trader split-tests             # list shadow split-test variants and sizing math
```

## Automation Runner

Hermes cron jobs should call the guarded runner, not raw broker commands:

```bash
bash scripts/cron_runner.sh smoke
bash scripts/cron_runner.sh pre-market
bash scripts/cron_runner.sh market-open
bash scripts/cron_runner.sh midday
bash scripts/cron_runner.sh daily-summary
bash scripts/cron_runner.sh weekly-review
```

The runner refuses automated execution unless `TRADING_MODE=paper`, the Alpaca endpoint is the paper endpoint, and `ALLOW_LIVE_TRADING` is not enabled. Mutating Alpaca commands are still blocked while `DRY_RUN=true`.

## Research Inputs

Automated research now uses these layers:

1. **Top-volume liquidity filter** from Yahoo Finance/yfinance `most_actives`, ranked by latest actual volume after direct OHLCV fetch. This is not the alpha engine; it is a liquidity guard so the bot trades only names with deep participation. Forced watchlist symbols such as `SPCX` are fetched directly and can enter the filter if actual volume qualifies.
2. **TradingView MCP simplified screener** from [`atilaahmettaner/tradingview-mcp`](https://github.com/atilaahmettaner/tradingview-mcp) through Hermes MCP tools. Use one clear technical setup as the hard gate: a scanner hit such as volume breakout/smart volume/rating/Bollinger/top gainers, or a constructive `combined_analysis`/`multi_timeframe` result. News, sentiment, backtests, and extra scan agreement are optional score/context, not daily vetoes. Keep calls serial and small-budgeted; `Expecting value`/empty-response/429-style MCP failures are retryable health events and do not count as evidence.
3. **Liquidity intersection**: pre-market writes final MCP-screened candidates to `memory/PREMARKET-CANDIDATES.json`; market-open rechecks that each candidate is still in the current top-100 volume filter before sizing or submitting.
4. **Benchmark-relative gate** from SPY/SPX. Candidate JSON must include an explicit outperformance thesis and relative-strength context; `market-open-intents` rejects benchmark-free beta trades even if the chart looks bullish.
5. **Lean MCP scoring** ranks candidates after the one-setup hard gate. Suggested bands: `>=70` candidate, `50–69` watch/HOLD, `<50` reject/HOLD. The market-open loader does not require every scoring component.
6. **Optional Perplexity news/citation layer**. The original Opus guide used Perplexity for cited market context. This repo keeps TradingView MCP as the technical screener, but `scripts/perplexity.sh` can add cited macro/news/catalyst context when `PERPLEXITY_API_KEY` is configured. Perplexity-only ideas are rejected unless TradingView MCP evidence and the benchmark thesis are present.

## Benchmark / Self-Judgment

Daily summaries now make the bot judge itself against SPY:

- `memory/BENCHMARK-LEDGER.csv` stores date, bot equity, cash, SPY close, daily returns, cumulative returns, alpha, drawdown, and exposure.
- `memory/BENCHMARK-REPORT.md` renders the latest scoreboard and judgment: baseline/ahead/behind.
- `memory/TRADE-LOG.md` EOD snapshots include a Benchmark section.
- `codex-trader weekly-review` appends a weekly benchmark review to `memory/WEEKLY-REVIEW.md`.

Manual/backfill example:

```bash
codex-trader benchmark-report --date 2026-06-16 --equity 50000 --cash 25000 --benchmark-close 600
```

The market-open step submits Alpaca **paper** broker orders only when `PAPER_ORDER_SUBMISSION=true` and the runner has switched `DRY_RUN=false` for the market-open workflow. It sizes each approved candidate so the required 10% trailing stop risks at most 1% of current portfolio equity: `qty = floor((equity * 0.01 / 0.10) / reference_price)`. It then buys approved candidates and immediately attempts a 10% GTC trailing stop. Other workflows force `DRY_RUN=true`.

## Shadow Split Tests

The repo now defines two additional shadow-only split-test variants under `configs/split_tests/`. They are research/farm configs, not broker-backed bots: `execution.mode = "shadow_paper"` and `broker.submit_orders = false` are required by the validator.

| Variant | What it tests | Risk model |
|---|---|---|
| `opus_original_hermes_codex_perplexity` | Hermes/Codex translation of the original Opus 4.7 bot with Perplexity-led research and the simple objective: beat SPX/SPY. | Original 20% of account per position with a 10% trailing stop, so stop risk is about 2% of account equity per position. |
| `opus_original_hermes_codex_perplexity_1pct_risk` | Same research/objective/operator stack as the original variant. | Position size is reduced so a 10% stop risks at most 1% of account equity. |

Preview the variant sizing math:

```bash
codex-trader split-tests --equity 50000
codex-trader split-tests --equity 50000 --json
```

## Suggested Hermes Cron Mapping

Set `workdir=/home/matt/workspace/codex-trading-bot` and schedule weekdays:

| Workflow | Cron | Routine prompt |
|---|---:|---|
| Pre-market research | `0 6 * * 1-5` | `routines/pre-market.md` |
| Market-open gate | `30 8 * * 1-5` | `routines/market-open.md` |
| Midday scan | `0 12 * * 1-5` | `routines/midday.md` |
| Daily summary | `0 15 * * 1-5` | `routines/daily-summary.md` |
| Weekly review | `0 16 * * 5` | `routines/weekly-review.md` |

Do not schedule live trading until risk gates, broker fill handling, and approval boundaries are reviewed.
