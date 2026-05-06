"""Brief "why fine-grained reactivity matters" capsule."""

from __future__ import annotations

from wybthon import a, component, div, h, h2, h3, p, section

from app.ui import Eyebrow

__all__ = ["WhyItMatters"]


def _Highlight(title: str, body: str, kicker: str):
    return div(
        div(kicker, class_="col-tag is-good"),
        h3(title, style={"marginTop": "0.2rem"}),
        p(body, class_="muted", style={"fontSize": "0.92rem"}),
        class_="panel",
        style={"padding": "1.2rem 1.3rem"},
    )


@component
def WhyItMatters():
    return section(
        div(
            h(Eyebrow, {"text": "Why this design"}),
            h2("Predictable, fast, and Pythonic."),
            p(
                "Wybthon's run-once / reactive-hole model gives you the ergonomics ",
                "of React-style components and the update model of SolidJS — entirely ",
                "in Python. ",
                a(
                    "Read the mental model in the docs",
                    href="https://docs.wybthon.com/concepts/mental-model/",
                    target="_blank",
                    rel="noopener",
                ),
                ".",
                class_="lede",
            ),
            div(
                _Highlight(
                    title="No reconciler-thrash on every keystroke",
                    body=(
                        "Component bodies don't run again when state changes. "
                        "There is no diffing tree to walk; only the holes that "
                        "depend on the signal you wrote actually do work."
                    ),
                    kicker="Predictable",
                ),
                _Highlight(
                    title="Fine-grained DOM patches",
                    body=(
                        "Each reactive hole owns its own effect. Updating a "
                        "signal touches a single text node or attribute, not the "
                        "subtree around it."
                    ),
                    kicker="Fast",
                ),
                _Highlight(
                    title="Native-feeling Python",
                    body=(
                        "div(p(\"Count: \", span(count)), button(\"+\", on_click=…)) "
                        "reads like Python. No JSX, no JavaScript build step, no "
                        "transpiler — just functions and signals."
                    ),
                    kicker="Pythonic",
                ),
                _Highlight(
                    title="Plays well with the platform",
                    body=(
                        "Standard browser APIs are right there via Pyodide: "
                        "fetch, IndexedDB, WebGL, Web Audio, file inputs — all "
                        "callable from Python with normal async/await."
                    ),
                    kicker="Open",
                ),
                class_="figure-grid",
            ),
            class_="container",
        ),
        class_="section",
    )
