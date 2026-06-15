import json
from decimal import Decimal

from codex_trader.broker import submit_market_buy_with_trailing_stop


class FakeResult:
    def __init__(self, ok=True, stdout="", stderr="", returncode=0):
        self.ok = ok
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_submit_market_buy_with_trailing_stop_places_buy_then_stop(tmp_path, monkeypatch):
    calls = []

    def fake_run_script(root, script, *args):
        calls.append((script, args))
        if len(calls) == 1:
            return FakeResult(stdout=json.dumps({"id": "buy1", "filled_qty": "3"}))
        return FakeResult(stdout=json.dumps({"id": "stop1"}))

    monkeypatch.setattr("codex_trader.broker.run_script", fake_run_script)
    result = submit_market_buy_with_trailing_stop(tmp_path, symbol="xom", qty=3, trail_percent=Decimal("10"))

    assert result.buy_ok
    assert result.stop_ok
    assert result.qty == 3
    assert calls[0][0] == "alpaca.sh"
    buy_body = json.loads(calls[0][1][1])
    stop_body = json.loads(calls[1][1][1])
    assert buy_body == {"symbol": "XOM", "qty": "3", "side": "buy", "type": "market", "time_in_force": "day"}
    assert stop_body == {"symbol": "XOM", "qty": "3", "side": "sell", "type": "trailing_stop", "trail_percent": "10", "time_in_force": "gtc"}
