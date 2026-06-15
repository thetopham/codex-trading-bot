# Pre-market Research — Hermes/Codex Routine

You are running the pre-market research workflow for the Codex Trader Hermes/Codex bot.

Safety: paper/dry-run by default. Stocks only. Telegram notifications only.

1. Read `AGENTS.md`, `memory/TRADING-STRATEGY.md`, tails of `memory/TRADE-LOG.md` and `memory/RESEARCH-LOG.md`.
2. Check env without printing secrets: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`; optional `PERPLEXITY_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
3. Pull paper account state: `bash scripts/alpaca.sh account`, `positions`, `orders`.
4. Research market context using `bash scripts/perplexity.sh "<query>"`; if it exits 3, use Hermes web search and mark fallback.
5. Append a dated entry to `memory/RESEARCH-LOG.md` with account snapshot, market context, 2-3 stock-only ideas, catalyst, entry, stop, target, risks, and default HOLD decision.
6. Notify via `bash scripts/telegram.sh` only for urgent held-position/thesis risk.
7. Commit memory changes if this repo has a remote; never force-push.
