"""Small visual primitives: eyebrows, pills, stat cards, legends.

Each of these is a tiny ``@component``. Static visual variants (``tone``,
``locked``, etc.) are read once via :func:`untrack`; reactive content
(``value``, ``text``) is passed straight through as a prop accessor so the
reconciler can wire up its own fine-grained hole.
"""

from __future__ import annotations

from typing import Any

from wybthon import component, div, span, untrack
from wybthon import label as label_el

__all__ = ["Eyebrow", "Pill", "Stat", "Legend", "FieldLabel"]


@component
def Eyebrow(text: str = ""):
    """Small uppercase pill rendered above section headings."""

    return span(text, class_="eyebrow")


@component
def Pill(text: Any = "", tone: str = "neutral"):
    """A monospace status pill. ``tone`` is one of ``neutral|good|bad``."""

    tone_static = untrack(tone) or "neutral"
    cls = "pill" if tone_static == "neutral" else f"pill {tone_static}"
    return span(text, class_=cls)


@component
def Stat(
    label: str = "",
    value: Any = "",
    sub: Any = "",
    tone: str = "default",
    locked: bool = False,
):
    """A stat card displaying a label, a (typically reactive) value, and a
    secondary line.

    Args:
        label: All-caps label rendered at the top of the card. Read once.
        value: A getter or static value rendered as the big number.
            Embedded as a hole, so passing a getter wires up reactivity.
        sub: Optional secondary line rendered below the value. Same rules
            as ``value``.
        tone: Visual variant; ``"default" | "highlight" | "cool" | "hot" | "warn"``.
        locked: When True, the card is rendered in dashed-border "fixed" style
            (used for the "Component bodies executed" stat which is locked at 1).
    """

    tone_static = untrack(tone) or "default"
    locked_static = bool(untrack(locked))

    classes = ["stat"]
    if tone_static == "highlight":
        classes.append("is-highlight")
    elif tone_static in {"cool", "hot", "warn"}:
        classes.append(f"is-{tone_static}")
    if locked_static:
        classes.append("locked")

    return div(
        span(label, class_="stat-label"),
        div(value, class_="stat-value"),
        div(sub, class_="stat-sub"),
        class_=" ".join(classes),
    )


@component
def Legend(text: str = "", tone: str = "good"):
    """Inline colored legend dot + caption."""

    tone_static = untrack(tone) or "good"
    dot_class = "legend-dot bad" if tone_static == "bad" else "legend-dot"
    return span(span(class_=dot_class), text, class_="legend")


@component
def FieldLabel(text: str = "", html_for: Any = None):
    """Tiny field label rendered above an input."""

    target = untrack(html_for)
    if target is not None:
        return label_el(text, html_for=target, class_="col-tag")
    return span(text, class_="col-tag")
