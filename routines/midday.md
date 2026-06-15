# Midday Scan — Hermes/Codex Routine

Safety: paper/dry-run by default.

1. Read `AGENTS.md`, `memory/TRADING-STRATEGY.md`, tail of `memory/TRADE-LOG.md`, and today's research.
2. Run `codex-trader midday-scan`.
3. If it reports CUT or TIGHTEN actions, append a dated dry-run action section to `memory/TRADE-LOG.md`.
4. Do not submit orders while `DRY_RUN=true`.
5. Notify via `bash scripts/telegram.sh` only if action was required/taken.
6. Commit memory changes if any; never force-push.
