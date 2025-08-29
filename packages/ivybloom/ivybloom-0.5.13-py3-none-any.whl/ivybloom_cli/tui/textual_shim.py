from __future__ import annotations

"""
Compatibility shims for Textual widgets across versions.

Exports:
- CompatTextLog: A TextLog-compatible widget. Prefers Textual's TextLog, then Log,
  and finally a minimal fallback built on Static that supports write() and clear().
"""

from typing import List


# Try modern / common import locations first
try:  # Textual versions where TextLog exists
    from textual.widgets import TextLog as CompatTextLog  # type: ignore
except Exception:  # pragma: no cover - fallback path
    try:  # Some versions expose Log instead of TextLog
        from textual.widgets import Log as CompatTextLog  # type: ignore
    except Exception:  # pragma: no cover - final fallback
        # Minimal implementation based on Static with write/clear API
        from textual.widgets import Static  # type: ignore

        class CompatTextLog(Static):  # type: ignore
            def __init__(
                self,
                highlight: bool = False,
                markup: bool = False,
                wrap: bool = True,
                *args,
                **kwargs,
            ) -> None:
                # Start with empty content
                super().__init__("", *args, **kwargs)
                self._lines: List[str] = []
                self._wrap: bool = wrap

            def write(self, message: str) -> None:
                self._lines.append(message)
                # Simple join; ignore highlight/markup for fallback
                self.update("\n".join(self._lines))

            def clear(self) -> None:
                self._lines.clear()
                self.update("")


