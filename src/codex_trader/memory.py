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
        "TRADING-STRATEGY.md": """# Trading Strategy\n\nSafety boundary: paper/dry-run by default. Stocks only; no options.\n\n## Hard Rules\n- Max 6 open positions.\n- Max 20% of equity per position.\n- Max 3 new trades per week.\n- Every new position requires a documented catalyst.\n- Every new position gets a 10% GTC trailing stop in paper/live-approved modes.\n- Cut losers at -7%.\n- Tighten trail to 7% at +15%, 5% at +20%.\n- Never move a stop down.\n- Telegram notifications are sparse: action taken or required daily/weekly summary.\n""",
        "TRADE-LOG.md": """# Trade Log\n\n## Day 0 Baseline\n- Equity: unknown\n- Cash: unknown\n- Note: seed this with a real paper account EOD snapshot before scheduled daily summaries.\n""",
        "RESEARCH-LOG.md": """# Research Log\n\nNo research yet. Pre-market workflow appends dated entries.\n""",
        "WEEKLY-REVIEW.md": """# Weekly Review\n\n## Template\n- Starting equity:\n- Ending equity:\n- Return:\n- Grade:\n- Lessons:\n""",
        "PROJECT-CONTEXT.md": """# Project Context\n\nCodex-style AI trading agent adapted for Hermes/local operation. Uses Alpaca paper by default, optional Perplexity research, Telegram notifications, and git-backed markdown memory. Live trading is out of scope unless explicitly approved later.\n""",
    }
    for name, content in defaults.items():
        path = mem / name
        if not path.exists():
            path.write_text(content)
