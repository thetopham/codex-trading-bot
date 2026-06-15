from codex_trader.sanitize import account_summary, positions_summary


def test_account_summary_removes_account_identifiers():
    raw = '{"id":"secret-id","account_number":"PA123","status":"ACTIVE","equity":"50000","cash":"50000","created_at":"today"}'
    summary = account_summary(raw)
    assert "secret-id" not in summary
    assert "PA123" not in summary
    assert "created_at" not in summary
    assert '"status": "ACTIVE"' in summary
    assert '"equity": "50000"' in summary


def test_positions_summary_keeps_position_metrics():
    raw = '[{"asset_id":"secret","symbol":"XOM","qty":"10","market_value":"1000","unrealized_plpc":"0.1"}]'
    summary = positions_summary(raw)
    assert "asset_id" not in summary
    assert "XOM" in summary
    assert "unrealized_plpc" in summary
