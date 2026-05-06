"""Page footer with attribution links."""

from __future__ import annotations

from wybthon import a, component, div, footer, span

__all__ = ["Footer"]


@component
def Footer():
    return footer(
        div(
            div(
                span("Built with "),
                a("Wybthon", href="https://github.com/wybthon/wybthon", target="_blank", rel="noopener"),
                span(" · Python in your browser via "),
                a("Pyodide", href="https://pyodide.org/", target="_blank", rel="noopener"),
                span(" · "),
                a(
                    "Source",
                    href="https://github.com/wybthon/reactive-profiler",
                    target="_blank",
                    rel="noopener",
                ),
            ),
            div(
                a("Docs", href="https://docs.wybthon.com/", target="_blank", rel="noopener"),
                span(" · "),
                a("PyPI", href="https://pypi.org/project/wybthon/", target="_blank", rel="noopener"),
                span(" · "),
                a(
                    "Changelog",
                    href="https://github.com/wybthon/wybthon/blob/main/CHANGELOG.md",
                    target="_blank",
                    rel="noopener",
                ),
            ),
            class_="row container",
        ),
        class_="site-footer",
    )
