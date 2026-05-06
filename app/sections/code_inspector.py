"""Annotated code view for the canonical "Counter" component.

We render the Python source as a styled ``<pre>`` with two highlight
classes:

* ``.tok-once`` — bits that run **once** at mount.
* ``.tok-hole`` — bits that become **reactive holes** at runtime.

The intent is to make the framework's contract immediately legible:
function bodies execute exactly once; the highlighted holes are the only
things that stream signal updates into the DOM.
"""

from __future__ import annotations

from typing import Any

from wybthon import code, component, div, h, h2, p, pre, section, span  # noqa: F401

from app.ui import Eyebrow, Legend

__all__ = ["CodeInspector"]


# ---------------------------------------------------------------------------
# Tiny token helpers
# ---------------------------------------------------------------------------


def _t(value: str) -> str:
    return value


def _kw(value: str) -> Any:
    return span(value, class_="tok-kw")


def _fn(value: str) -> Any:
    return span(value, class_="tok-fn")


def _s(value: str) -> Any:
    return span(value, class_="tok-str")


def _num(value: str) -> Any:
    return span(value, class_="tok-num")


def _cmt(value: str) -> Any:
    return span(value, class_="tok-cmt")


def _slf(value: str) -> Any:
    return span(value, class_="tok-self")


def _hole(*children: Any) -> Any:
    """Mark a span of tokens as a reactive hole (purple background)."""
    return span(*children, class_="tok-hole")


def _once(*children: Any) -> Any:
    """Mark a span of tokens as run-once (teal background)."""
    return span(*children, class_="tok-once")


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------


@component
def CodeInspector():
    return section(
        div(
            h(Eyebrow, {"text": "How this works"}),
            h2("One body. Many holes."),
            p(
                "This is the same code that powers the playground. Highlighted ",
                "in ", span("teal", style={"color": "var(--cool)", "fontWeight": "600"}),
                " is what runs ",
                _once("exactly once"),
                " at mount time. Highlighted in ",
                span("purple", style={"color": "var(--accent-2)", "fontWeight": "600"}),
                " is each ",
                _hole("reactive hole"),
                " — every signal accessor that the reconciler will wire up to its own ",
                "fine-grained effect.",
                class_="lede",
            ),
            div(
                h(Legend, {"text": "Run once at mount", "tone": "good"}),
                span("\u00a0\u00a0"),
                h(Legend, {"text": "Reactive hole · own effect", "tone": "good"}),
                style={
                    "display": "inline-flex",
                    "gap": "0.6rem",
                    "alignItems": "center",
                    "marginBottom": "1rem",
                    "color": "var(--text-3)",
                },
            ),
            pre(
                code(
                    _kw("from"), _t(" wybthon "), _kw("import"),
                    _t(" component, create_signal, button, div, p, span\n\n"),
                    _t("@"), _fn("component"), _t("\n"),
                    _kw("def"), _t(" "), _fn("Counter"), _t("(initial="), _num("0"), _t("):\n"),
                    _t("    "), _cmt("# Body runs once at mount.\n"),
                    _t("    "), _once("count, set_count "), _t("= "),
                    _once(_fn("create_signal"), _t("(initial)\n")),
                    _t("\n"),
                    _t("    "), _kw("return"), _t(" "), _fn("div"), _t("(\n"),
                    _t("        "), _fn("p"), _t("("), _s("\"Count: \""), _t(", "),
                    _fn("span"), _t("("),
                    _hole(_t("count")),
                    _t(")),  "), _cmt("# `count` is a getter → reactive hole\n"),
                    _t("        "), _fn("button"), _t("(\n"),
                    _t("            "), _s("\"Increment\""), _t(",\n"),
                    _t("            on_click="), _kw("lambda"), _t(" e: "),
                    _t("set_count("),
                    _hole(_t("count()")),
                    _t(" + "), _num("1"), _t("),  "),
                    _cmt("# read inside handler\n"),
                    _t("        ),\n"),
                    _t("    )\n"),
                ),
                class_="code-surface",
            ),
            div(
                h(
                    _Insight,
                    {
                        "title": "Run once",
                        "body": (
                            "The function body of `Counter` executes a single time. "
                            "After that, signal updates never re-invoke it — "
                            "there are no virtual-DOM diffs above the leaves."
                        ),
                    },
                ),
                h(
                    _Insight,
                    {
                        "title": "Holes are getters",
                        "body": (
                            "Anywhere you embed a zero-arg callable (a signal "
                            "accessor or `lambda`), Wybthon turns it into a reactive "
                            "hole and patches just the resulting node when it changes."
                        ),
                    },
                ),
                h(
                    _Insight,
                    {
                        "title": "Same model for props",
                        "body": (
                            "Reactive props use the exact same machinery. Pass a "
                            "getter as `class_=`, `style=`, or `value=` and only "
                            "that attribute updates."
                        ),
                    },
                ),
                class_="figure-grid",
                style={"marginTop": "1.4rem"},
            ),
            class_="container",
        ),
        id="why",
        class_="section",
    )


@component
def _Insight(title: str = "", body: str = ""):
    return div(
        span(title, class_="col-tag is-good"),
        p(body, class_="muted", style={"fontSize": "0.92rem"}),
        class_="panel",
        style={"padding": "1.1rem 1.2rem"},
    )
