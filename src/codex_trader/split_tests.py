from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

CONFIG_DIR = Path("configs/split_tests")


@dataclass(frozen=True)
class ResearchConfig:
    primary: str
    allow_fallback: bool
    require_citations: bool
    notes: str = ""


@dataclass(frozen=True)
class RiskConfig:
    max_open_positions: int
    max_new_trades_per_week: int
    max_position_equity_pct: Decimal
    stop_loss_pct: Decimal
    position_sizing: str
    max_account_risk_pct: Decimal | None = None
    target_deployed_equity_pct_min: Decimal | None = None
    target_deployed_equity_pct_max: Decimal | None = None


@dataclass(frozen=True)
class ExecutionConfig:
    mode: str
    ledger_path: str
    submit_orders: bool


@dataclass(frozen=True)
class SplitTestVariant:
    variant_id: str
    name: str
    description: str
    enabled: bool
    objective: str
    operator_stack: tuple[str, ...]
    benchmark_symbol: str
    research: ResearchConfig
    risk: RiskConfig
    execution: ExecutionConfig

    def position_notional_cap(self, equity: Decimal) -> Decimal:
        """Maximum notional for one new position under this variant."""
        if equity <= 0:
            return Decimal("0")
        equity_pct_cap = equity * self.risk.max_position_equity_pct
        if self.risk.position_sizing == "account_risk":
            if self.risk.max_account_risk_pct is None or self.risk.stop_loss_pct <= 0:
                return Decimal("0")
            account_risk_cap = equity * self.risk.max_account_risk_pct / self.risk.stop_loss_pct
            if self.risk.max_position_equity_pct > 0:
                return min(equity_pct_cap, account_risk_cap)
            return account_risk_cap
        return equity_pct_cap

    def account_risk_at_stop(self, equity: Decimal) -> Decimal:
        return self.position_notional_cap(equity) * self.risk.stop_loss_pct

    def account_risk_pct_at_stop(self, equity: Decimal) -> Decimal:
        if equity <= 0:
            return Decimal("0")
        return self.account_risk_at_stop(equity) / equity


def _decimal(value: Any, default: str = "0") -> Decimal:
    if value is None:
        return Decimal(default)
    return Decimal(str(value))


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(v) for v in value)


def variant_from_dict(data: dict[str, Any]) -> SplitTestVariant:
    research = data.get("research", {})
    risk = data.get("risk", {})
    execution = data.get("execution", {})
    broker = data.get("broker", {})
    benchmark = data.get("benchmark", {})
    return SplitTestVariant(
        variant_id=str(data["id"]),
        name=str(data.get("name", data["id"])),
        description=str(data.get("description", "")),
        enabled=bool(data.get("enabled", True)),
        objective=str(data.get("objective", "beat_spx")),
        operator_stack=_list(data.get("operator_stack", ("Hermes", "Codex"))),
        benchmark_symbol=str(benchmark.get("symbol", "SPY")),
        research=ResearchConfig(
            primary=str(research.get("primary", "perplexity")),
            allow_fallback=bool(research.get("allow_fallback", True)),
            require_citations=bool(research.get("require_citations", True)),
            notes=str(research.get("notes", "")),
        ),
        risk=RiskConfig(
            max_open_positions=int(risk.get("max_open_positions", 6)),
            max_new_trades_per_week=int(risk.get("max_new_trades_per_week", 3)),
            max_position_equity_pct=_decimal(risk.get("max_position_equity_pct", "0.20")),
            stop_loss_pct=_decimal(risk.get("stop_loss_pct", "0.10")),
            position_sizing=str(risk.get("position_sizing", "equity_pct_cap")),
            max_account_risk_pct=_optional_decimal(risk.get("max_account_risk_pct")),
            target_deployed_equity_pct_min=_optional_decimal(risk.get("target_deployed_equity_pct_min")),
            target_deployed_equity_pct_max=_optional_decimal(risk.get("target_deployed_equity_pct_max")),
        ),
        execution=ExecutionConfig(
            mode=str(execution.get("mode", "shadow_paper")),
            ledger_path=str(execution.get("ledger_path", f"local_state/split_tests/{data['id']}/ledger.jsonl")),
            submit_orders=bool(broker.get("submit_orders", False)),
        ),
    )


def load_split_test_variants(root: Path | None = None, config_dir: Path | None = None) -> list[SplitTestVariant]:
    base = root or Path.cwd()
    directory = config_dir if config_dir is not None else base / CONFIG_DIR
    variants: list[SplitTestVariant] = []
    for path in sorted(directory.glob("*.toml")):
        with path.open("rb") as handle:
            variants.append(variant_from_dict(tomllib.load(handle)))
    return variants


def validate_variant(variant: SplitTestVariant) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,80}", variant.variant_id):
        errors.append("id_must_be_slug_like")
    if variant.objective != "beat_spx":
        errors.append("objective_must_be_beat_spx")
    lowered_stack = {item.lower() for item in variant.operator_stack}
    if "hermes" not in lowered_stack or "codex" not in lowered_stack:
        errors.append("operator_stack_must_include_hermes_and_codex")
    if variant.benchmark_symbol not in {"SPY", "SPX", "^GSPC"}:
        errors.append("benchmark_symbol_should_be_spy_spx_or_gspc")
    if variant.research.primary != "perplexity":
        errors.append("primary_research_must_be_perplexity_for_original_opus_split_tests")
    if variant.risk.max_open_positions <= 0:
        errors.append("max_open_positions_must_be_positive")
    if variant.risk.max_new_trades_per_week <= 0:
        errors.append("max_new_trades_per_week_must_be_positive")
    if variant.risk.stop_loss_pct <= 0:
        errors.append("stop_loss_pct_must_be_positive")
    if variant.risk.max_position_equity_pct <= 0:
        errors.append("max_position_equity_pct_must_be_positive")
    if variant.risk.position_sizing not in {"equity_pct_cap", "account_risk"}:
        errors.append("unknown_position_sizing")
    if variant.risk.position_sizing == "account_risk" and (variant.risk.max_account_risk_pct is None or variant.risk.max_account_risk_pct <= 0):
        errors.append("account_risk_sizing_requires_positive_max_account_risk_pct")
    if variant.execution.mode != "shadow_paper":
        errors.append("split_tests_must_run_shadow_paper")
    if variant.execution.submit_orders:
        errors.append("split_tests_must_not_submit_broker_orders")
    return errors


def _pct(value: Decimal) -> str:
    return f"{(value * Decimal('100')).quantize(Decimal('0.01'))}%"


def render_variants_table(variants: list[SplitTestVariant], *, equity: Decimal = Decimal("10000")) -> str:
    lines = [
        "# Split Test Variants",
        "",
        f"Assumed equity for sizing preview: ${equity.quantize(Decimal('0.01'))}",
        "",
        "| Variant | Research | Sizing | Position cap | Stop | Account risk at stop | Safety |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for variant in variants:
        notional = variant.position_notional_cap(equity)
        risk = variant.account_risk_at_stop(equity)
        errors = validate_variant(variant)
        safety = "OK shadow-only" if not errors else "ERROR: " + ", ".join(errors)
        lines.append(
            "| "
            f"{variant.variant_id} | "
            f"{variant.research.primary} | "
            f"{variant.risk.position_sizing} | "
            f"${notional.quantize(Decimal('0.01'))} | "
            f"{_pct(variant.risk.stop_loss_pct)} | "
            f"${risk.quantize(Decimal('0.01'))} ({_pct(variant.account_risk_pct_at_stop(equity))}) | "
            f"{safety} |"
        )
    return "\n".join(lines)


def variants_to_json(variants: list[SplitTestVariant], *, equity: Decimal = Decimal("10000")) -> str:
    payload = []
    for variant in variants:
        payload.append(
            {
                "id": variant.variant_id,
                "name": variant.name,
                "enabled": variant.enabled,
                "objective": variant.objective,
                "operator_stack": list(variant.operator_stack),
                "benchmark_symbol": variant.benchmark_symbol,
                "research_primary": variant.research.primary,
                "position_sizing": variant.risk.position_sizing,
                "position_notional_cap": str(variant.position_notional_cap(equity)),
                "stop_loss_pct": str(variant.risk.stop_loss_pct),
                "account_risk_at_stop": str(variant.account_risk_at_stop(equity)),
                "account_risk_pct_at_stop": str(variant.account_risk_pct_at_stop(equity)),
                "execution_mode": variant.execution.mode,
                "ledger_path": variant.execution.ledger_path,
                "submit_orders": variant.execution.submit_orders,
                "validation_errors": validate_variant(variant),
            }
        )
    return json.dumps(payload, indent=2, sort_keys=True)
