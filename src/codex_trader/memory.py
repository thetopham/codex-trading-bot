from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT_MEMORY_FILES = [
    "TRADING-STRATEGY.md",
    "TRADE-LOG.md",
    "RESEARCH-LOG.md",
    "WEEKLY-REVIEW.md",
    "PROJECT-CONTEXT.md",
    "PREMARKET-CANDIDATES.json",
]


@dataclass(frozen=True)
class MemoryStore:
    root: Path

    @property
    def memory_dir(self) -> Path:
        return self.root / "memory"

    def read(self, name: str) -> str:
        return (self.memory_dir / name).read_text()

    def append(self, name: str, text: str) -> None:
        path = self.memory_dir / name
        with path.open("a") as f:
            f.write(text.rstrip() + "\n")

    def tail(self, name: str, lines: int = 80) -> str:
        parts = self.read(name).splitlines()
        return "\n".join(parts[-lines:])


def initialize_memory(root: Path) -> None:
    mem = root / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    defaults = {
        "TRADING-STRATEGY.md": """# Trading Strategy\n\nSafety boundary: paper/dry-run by default. Stocks only; no options.\n\n## Hard Rules\n- Take every qualified TradingView MCP opportunity while cash is available and per-position risk gates pass; there is no fixed max-position or weekly-trade-count cap.\n- Max per-position risk: 1% of portfolio equity at the required 10% stop.\n- Position sizing formula: `floor((equity * 0.01 / 0.10) / entry_price)`.\n- Every new position requires a documented catalyst.\n- Every new position gets a 10% GTC trailing stop in paper/live-approved modes.\n- Cut losers at -7%.\n- Tighten trail to 7% at +15%, 5% at +20%.\n- Never move a stop down.\n- Telegram notifications are sparse: action taken or required daily/weekly summary.\n""",
        "TRADE-LOG.md": """# Trade Log\n\n## Day 0 Baseline\n- Equity: unknown\n- Cash: unknown\n- Note: seed this with a real paper account EOD snapshot before scheduled daily summaries.\n""",
        "RESEARCH-LOG.md": """# Research Log\n\nNo research yet. Pre-market workflow appends dated entries.\n""",
        "WEEKLY-REVIEW.md": """# Weekly Review\n\n## Template\n- Starting equity:\n- Ending equity:\n- Return:\n- Grade:\n- Lessons:\n""",
        "PROJECT-CONTEXT.md": """# Project Context\n\nCodex-style AI trading agent adapted for Hermes/local operation. Uses Alpaca paper by default, Yahoo/yfinance as the liquidity filter, TradingView MCP as the primary screener, Telegram notifications, and git-backed markdown memory. Live trading is out of scope unless explicitly approved later.\n""",
        "PREMARKET-CANDIDATES.json": """{\n  \"date\": null,\n  \"source\": \"TradingView MCP screening over top-100-volume liquidity filter\",\n  \"candidates\": []\n}\n""",
    }
    for name, content in defaults.items():
        path = mem / name
        if not path.exists():
            path.write_text(content)
