"""Privacy-safe research primitives for the weekly A-share loop."""

from .decision import BollEvidence, Decision, ResearchEvidence, decide
from .flows import FlowWindow, aggregate_flows
from .freshness import is_fresh_event

__all__ = [
    "BollEvidence",
    "Decision",
    "FlowWindow",
    "ResearchEvidence",
    "aggregate_flows",
    "decide",
    "is_fresh_event",
]
