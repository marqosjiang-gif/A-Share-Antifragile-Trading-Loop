#!/usr/bin/env python3
"""Compatibility entry point for the public, research-only runner.

The public repository intentionally does not embed a venue-specific data client,
portfolio loader, account integration, or credential. Use ``quant_loop.py`` for
the portable scaffold and implement any market adapter locally.
"""

from __future__ import annotations

from quant_loop import main


if __name__ == "__main__":
    raise SystemExit(main())
