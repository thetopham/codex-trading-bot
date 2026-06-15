from __future__ import annotations

import json
from dataclasses import asdict

from .research import top_volume_candidates


def main() -> int:
    top, selected = top_volume_candidates(limit=100, picks=8)
    payload = {
        "source": "yfinance most_actives + daily OHLCV",
        "top_volume": [asdict(c) for c in top[:100]],
        "selected_candidates": [asdict(c) for c in selected],
    }
    print(json.dumps(payload, default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
