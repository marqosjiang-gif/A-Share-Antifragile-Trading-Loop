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
"""Public, privacy-safe research primitives."""

from .decision import boll_position_wording
from .flows import classify_stock_flow
from .freshness import evaluate_scan_coverage

__all__ = [
    "boll_position_wording",
    "classify_stock_flow",
    "evaluate_scan_coverage",
]
