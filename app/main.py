"""Browser entry point for the Reactive Profiler.

``bootstrap.js`` calls ``await main()`` once Wybthon has been installed
into Pyodide. We render into ``<body>`` (the loading overlay is
removed by the JS bootstrap once we return) and let the rest of the
app reactive-itself into existence.
"""

from __future__ import annotations

from wybthon import Element, h, render

from app.app import App


async def main() -> None:
    """Mount the root :class:`App` component into ``<body>``."""

    container = Element("body", existing=True)
    render(h(App, {}), container)
