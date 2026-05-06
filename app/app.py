"""Root application component for the Reactive Profiler page."""

from __future__ import annotations

from wybthon import component, div, h, main_

from app.profiler import register_component_run
from app.sections import (
    CodeInspector,
    Comparison,
    Footer,
    Header,
    Hero,
    WhyItMatters,
)

__all__ = ["App"]


@component
def App():
    register_component_run()

    return div(
        h(Header, {}),
        main_(
            h(Hero, {}),
            h(Comparison, {}),
            h(CodeInspector, {}),
            h(WhyItMatters, {}),
        ),
        h(Footer, {}),
        id="app",
    )
