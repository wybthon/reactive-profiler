"""Sticky page header with brand mark and primary navigation links."""

from __future__ import annotations

from wybthon import a, component, div, header, span
from wybthon import nav as nav_el

__all__ = ["Header"]


@component
def Header():
    return header(
        div(
            div(
                span("W", class_="mark"),
                span("Wybthon", class_="name"),
                span("Reactive Profiler", class_="tag"),
                class_="brand",
            ),
            nav_el(
                a("Playground", href="#playground"),
                a("Comparison", href="#comparison"),
                a("Why holes?", href="#why"),
                a("Docs", href="https://docs.wybthon.com/", target="_blank", rel="noopener"),
                a(
                    "GitHub",
                    href="https://github.com/wybthon/wybthon",
                    target="_blank",
                    rel="noopener",
                    class_="cta",
                ),
                class_="nav-links",
            ),
            class_="row container",
        ),
        class_="site-header",
    )
