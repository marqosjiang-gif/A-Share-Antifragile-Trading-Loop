"""Auditable decision arbitration with BOLL as the highest weighted signal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


BollAction = Literal["buy", "hold", "sell", "none"]


@dataclass(frozen=True)
class BollEvidence:
    action: BollAction = "none"
    completed_trades: int = 0
    win_rate: float | None = None
    efficiency_per_day: float | None = None
    verified: bool = False

    @property
    def sample_is_actionable(self) -> bool:
        return self.verified and self.completed_trades >= 3


@dataclass(frozen=True)
class ResearchEvidence:
    price_verified: bool
    volume_verified: bool
    boll: BollEvidence = field(default_factory=BollEvidence)
    flow_5d: float | None = None
    flow_20d: float | None = None
    flow_verified: bool = False
    fundamentals_verified: bool = False
    adverse_event_verified: bool = False


@dataclass(frozen=True)
class Decision:
    label: Literal["buy", "hold", "reduce", "observe"]
    action: str
    confidence: Literal["high", "medium", "low"]
    reasons: tuple[str, ...]


def decide(evidence: ResearchEvidence) -> Decision:
    """Apply hard validation, then BOLL > price/volume > flow > fundamentals/events.

    Lower-priority evidence can reduce confidence or tighten risk, but cannot
    silently override an actionable historical BOLL signal.
    """
    if not evidence.price_verified or not evidence.volume_verified:
        return Decision(
            "observe",
            "Do not issue a directional action until price and volume are verified.",
            "low",
            ("price/volume hard gate failed",),
        )

    boll = evidence.boll
    reasons: list[str] = ["price and volume verified"]
    if boll.verified:
        reasons.append(
            f"BOLL={boll.action}, completed_trades={boll.completed_trades}"
        )
    else:
        reasons.append("BOLL unavailable")

    flow_negative = (
        evidence.flow_verified
        and evidence.flow_5d is not None
        and evidence.flow_20d is not None
        and evidence.flow_5d < 0
        and evidence.flow_20d < 0
    )
    if evidence.flow_verified:
        reasons.append("5/20-day capital flow verified")
    else:
        reasons.append("capital flow unverified")

    if boll.sample_is_actionable and boll.action == "sell":
        return Decision(
            "reduce",
            "The historical BOLL sell region is active; reduce exposure by plan.",
            "high" if flow_negative or evidence.adverse_event_verified else "medium",
            tuple(reasons),
        )
    if boll.sample_is_actionable and boll.action == "buy":
        if flow_negative or evidence.adverse_event_verified:
            return Decision(
                "observe",
                "BOLL buy region is active, but conflicting verified risk limits action to observation or a pre-sized probe.",
                "medium",
                tuple(reasons),
            )
        return Decision(
            "buy",
            "The historical BOLL buy region is active; execute only the pre-sized staged plan.",
            "high" if evidence.flow_verified else "medium",
            tuple(reasons),
        )
    if boll.sample_is_actionable and boll.action == "hold":
        return Decision(
            "hold",
            "Keep existing exposure and wait for the historical BOLL exit trigger.",
            "medium",
            tuple(reasons),
        )

    if flow_negative or evidence.adverse_event_verified:
        return Decision(
            "observe",
            "Tighten risk and wait for BOLL plus price/volume confirmation.",
            "low",
            tuple(reasons),
        )
    return Decision(
        "observe",
        "No actionable BOLL signal; keep the conclusion conditional.",
        "low",
        tuple(reasons),
    )
