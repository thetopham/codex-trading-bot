from codex_trader.memory import initialize_memory


def test_initialize_memory_creates_expected_files(tmp_path):
    initialize_memory(tmp_path)
    for name in ["TRADING-STRATEGY.md", "TRADE-LOG.md", "RESEARCH-LOG.md", "WEEKLY-REVIEW.md", "PROJECT-CONTEXT.md"]:
        assert (tmp_path / "memory" / name).exists()
