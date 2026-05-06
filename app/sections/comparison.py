"""Wybthon (fine-grained holes) versus a naive whole-component re-render.

Two cards bound to the same source signal:

* The **Wybthon** card embeds reactive holes via :class:`Island`. When the
  source ticks, only the affected text nodes update and only the relevant
  islands flash.
* The **Naive** card simulates the React-style "rebuild everything" path —
  on every update its whole inner ``innerHTML`` is rewritten and the
  surrounding panel flashes red. We bump :data:`naive_dom_mutations` by
  the static node count so visitors can see the difference accumulate.

A slider drives the source continuously and a "Burst" button schedules a
short asyncio sequence of updates so the difference is unmistakable even on
fast machines.
"""

from __future__ import annotations

import asyncio
from typing import Any

from wybthon import (
    Ref,
    button,
    component,
    create_signal,
    div,
    h,
    h2,
    h3,
    input_,
    on,
    on_mount,
    p,
    section,
    span,
    untrack,
)

from app.profiler import (
    Island,
    fmt_number,
    register_component_run,
    register_naive_mutation,
    reset_counters,
    tracked_signal,
)
from app.ui import Eyebrow, FieldLabel, Stat

__all__ = ["Comparison"]


# Roughly how many DOM nodes the naive card replaces on every redraw.
# Keep this in sync with ``_naive_inner_html``.
NAIVE_NODE_COUNT = 16


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _status(value: int) -> str:
    if value < 25:
        return "low"
    if value > 75:
        return "high"
    return "ok"


def _stars(value: int) -> str:
    n = (value % 5) + 1
    return ("\u2605" * n) + ("\u2606" * (5 - n))


def _naive_inner_html(v: int) -> str:
    """Render the inner content of the naive card as a single HTML string.

    The values are all integers / float-formatted ints / fixed strings so
    no HTML escaping is needed. Markers in ``__init__.py`` keep the
    structure stable so :data:`NAIVE_NODE_COUNT` stays accurate.
    """

    return (
        '<div class="cmp-grid">'
        '  <div class="cmp-row">'
        f'    <span class="cmp-label">Tick</span>'
        f'    <span class="cmp-value">{v}</span>'
        '  </div>'
        '  <div class="cmp-row">'
        f'    <span class="cmp-label">Price</span>'
        f'    <span class="cmp-value">${v * 0.32:.2f}</span>'
        '  </div>'
        '  <div class="cmp-row">'
        f'    <span class="cmp-label">Stock</span>'
        f'    <span class="cmp-value">{v * 7 + 12}</span>'
        '  </div>'
        '  <div class="cmp-row">'
        f'    <span class="cmp-label">Status</span>'
        f'    <span class="cmp-value">{_status(v)}</span>'
        '  </div>'
        '  <div class="cmp-row">'
        f'    <span class="cmp-label">Rating</span>'
        f'    <span class="cmp-value">{_stars(v)}</span>'
        '  </div>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Sub-views
# ---------------------------------------------------------------------------


@component
def _WybthonCard(source: Any = None):
    """Fine-grained hole-based card. Body runs once; islands update."""

    register_component_run()

    def tick_value() -> str:
        return fmt_number(source())

    def price_value() -> str:
        return f"${source() * 0.32:.2f}"

    def stock_value() -> str:
        return fmt_number(source() * 7 + 12)

    def status_value() -> str:
        return _status(source())

    def rating_value() -> str:
        return _stars(source())

    def row(label: str, getter: Any, kind: str = "primary") -> Any:
        return div(
            span(label, class_="cmp-label"),
            h(Island, {"getter": getter, "kind": kind, "label": f"{label.lower()} hole"}),
            class_="cmp-row",
        )

    return div(
        div(
            h(Eyebrow, {"text": "Wybthon · holes only"}),
            span(" · only the changed islands flash", class_="muted"),
            class_="panel-header",
        ),
        div(
            row("Tick", tick_value, kind="primary"),
            row("Price", price_value, kind="cool"),
            row("Stock", stock_value, kind="cool"),
            row("Status", status_value, kind="warn"),
            row("Rating", rating_value, kind="primary"),
            class_="cmp-grid",
        ),
        p(
            "The component body executed exactly once at mount. ",
            "Five reactive holes — one per row — are the only DOM nodes that update.",
            class_="muted",
            style={"marginTop": "1rem", "fontSize": "0.85rem"},
        ),
        class_="panel cmp-card cmp-card--good",
    )


@component
def _NaiveCard(source: Any = None):
    """Naive whole-component re-render. Card flashes; every node is replaced."""

    register_component_run()

    inner_ref = Ref()
    rev_counter = [0]
    rev_signal, set_rev = create_signal(0)

    def update(value: Any = None) -> None:
        target = inner_ref.current
        if target is None:
            return
        v = int(value) if value is not None else int(untrack(source))
        target.set_html(_naive_inner_html(v))
        register_naive_mutation(NAIVE_NODE_COUNT)
        rev_counter[0] += 1
        untrack(lambda: set_rev(rev_counter[0]))

    def init() -> None:
        target = inner_ref.current
        if target is None:
            return
        target.set_html(_naive_inner_html(int(untrack(source))))

    on_mount(init)
    on(source, update, defer=True)

    return div(
        div(
            h(Eyebrow, {"text": "Naive · innerHTML rewrite"}),
            span(" · the whole card is replaced on every change", class_="muted"),
            class_="panel-header",
        ),
        div(ref=inner_ref, class_="cmp-grid"),
        p(
            "Every update rewrites all ",
            span(str(NAIVE_NODE_COUNT), class_="pill bad"),
            " DOM nodes inside this card and the surrounding panel flashes red.",
            class_="muted",
            style={"marginTop": "1rem", "fontSize": "0.85rem"},
        ),
        class_=lambda: f"panel cmp-card cmp-card--bad naive-card flash-{rev_signal() % 2}",
    )


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------


def _spawn_burst(set_tick: Any, source: Any, total: int = 60, delay: float = 0.014) -> None:
    """Schedule ``total`` source updates spread across animation frames."""

    async def runner() -> None:
        cur = int(untrack(source) or 0)
        for i in range(total):
            set_tick((cur + i + 1) % 101)
            await asyncio.sleep(delay)

    asyncio.ensure_future(runner())


@component
def Comparison():
    register_component_run()

    tick, set_tick = tracked_signal(48)

    def on_slider(evt: Any) -> None:
        try:
            set_tick(int(evt.target.value))
        except Exception:
            set_tick(0)

    def burst(_evt: Any) -> None:
        _spawn_burst(set_tick, tick, total=60, delay=0.014)

    def reset(_evt: Any) -> None:
        reset_counters()
        set_tick(48)

    return section(
        div(
            h(Eyebrow, {"text": "Comparison"}),
            h2("Same data. Wildly different work."),
            p(
                "Both cards below subscribe to a single ", span("tick", class_="pill"),
                " signal. Drag the slider or hit ",
                span("Burst", class_="pill good"),
                " to fire 60 sequential updates and watch each side respond.",
                class_="lede",
            ),
            div(
                div(
                    h(FieldLabel, {"text": "tick", "html_for": "cmp-slider"}),
                    input_(
                        type="range",
                        min="0",
                        max="100",
                        step="1",
                        id="cmp-slider",
                        value=tick,
                        on_input=on_slider,
                    ),
                    style={"flex": "1", "minWidth": "240px"},
                ),
                div(
                    button("Burst · 60 updates", on_click=burst, class_="btn btn-primary"),
                    button("Reset", on_click=reset, class_="btn"),
                    style={"display": "inline-flex", "gap": "0.5rem"},
                ),
                style={
                    "display": "flex",
                    "gap": "1rem",
                    "alignItems": "flex-end",
                    "flexWrap": "wrap",
                    "marginBottom": "1.4rem",
                },
            ),
            div(
                h(_WybthonCard, {"source": tick}),
                h(_NaiveCard, {"source": tick}),
                class_="two-col",
            ),
            div(
                h(
                    Stat,
                    {
                        "label": "Current tick",
                        "value": lambda: fmt_number(tick()),
                        "sub": "Source signal driving both cards.",
                        "tone": "highlight",
                    },
                ),
                h3(
                    "Why the right-hand side feels heavier",
                    style={"gridColumn": "1 / -1", "marginTop": "0.4rem"},
                ),
                p(
                    "The naive card has no concept of which value changed — it ",
                    "rebuilds and re-attaches every node on each update. Browsers ",
                    "must re-parse the HTML, recompute layout, and repaint the whole ",
                    "panel. Wybthon, by contrast, patches a single text node per ",
                    "reactive hole; layout work outside that node is skipped entirely.",
                    class_="muted",
                    style={"gridColumn": "1 / -1", "fontSize": "0.92rem"},
                ),
                class_="stat-grid",
                style={"marginTop": "1.4rem"},
            ),
            class_="container",
        ),
        id="comparison",
        class_="section",
    )
