"""Hero playground, the "wow factor" of the page.

The visitor lands here and immediately gets to:

* poke buttons, drag a slider, and type into a text field, and
* watch precisely which on-screen *islands* light up in response, while the
  component body counter stays locked at ``1`` because Wybthon never re-runs
  it.

All the controls and their islands live in this single ``Hero`` component;
its body runs **once** at mount and the rest is reactive holes flowing into
the DOM as the local signals change.
"""

from __future__ import annotations

from typing import Any

from wybthon import (
    a,
    button,
    component,
    div,
    h,
    h1,
    input_,
    p,
    section,
    span,
)

from app.profiler import (
    Island,
    component_body_runs,
    fmt_number,
    hole_runs,
    naive_dom_mutations,
    register_component_run,
    reset_counters,
    signal_writes,
    tracked_signal,
    wybthon_dom_mutations,
)
from app.ui import Eyebrow, FieldLabel, Pill, Stat

__all__ = ["Hero"]


# ---------------------------------------------------------------------------
# Sub-views
# ---------------------------------------------------------------------------


@component
def _Playground():
    register_component_run()

    count, set_count = tracked_signal(0)
    slider, set_slider = tracked_signal(48)
    name, set_name = tracked_signal("Ada")

    # --- handlers (all are setters: each write fires the dependent holes) ---

    def inc_count(_evt: Any) -> None:
        set_count(count() + 1)

    def dec_count(_evt: Any) -> None:
        set_count(count() - 1)

    def reset_count(_evt: Any) -> None:
        set_count(0)

    def on_slider_input(evt: Any) -> None:
        try:
            set_slider(int(evt.target.value))
        except Exception:
            set_slider(0)

    def on_name_input(evt: Any) -> None:
        set_name(str(evt.target.value or ""))

    # --- derived getters ---

    def double() -> str:
        return fmt_number(count() * 2)

    def parity() -> str:
        return "even" if count() % 2 == 0 else "odd"

    def slider_pct() -> str:
        return f"{slider()}%"

    def slider_bucket() -> str:
        v = slider()
        if v < 33:
            return "low"
        if v < 67:
            return "mid"
        return "high"

    def greeting() -> str:
        n = (name() or "").strip()
        return f"Hello, {n or 'friend'}!"

    def name_length() -> str:
        return fmt_number(len(name() or ""))

    return div(
        div(
            h(Eyebrow, {"text": "Live playground"}),
            span("\u00a0"),
            span("Component bodies have run ", class_="muted"),
            h(Pill, {"text": lambda: fmt_number(component_body_runs()), "tone": "good"}),
            span(" · only reactive holes update from here on", class_="muted"),
            class_="panel-header",
        ),
        # --- counter row ---
        div(
            h(FieldLabel, {"text": "Counter"}),
            div(
                button("−", on_click=dec_count, class_="btn btn-icon", aria_label="Decrement"),
                button("+", on_click=inc_count, class_="btn btn-icon", aria_label="Increment"),
                button("Reset", on_click=reset_count, class_="btn btn-sm btn-ghost"),
                style={"display": "inline-flex", "gap": "0.4rem", "alignItems": "center"},
            ),
            div(
                span("count = ", class_="muted"),
                h(Island, {"getter": count, "kind": "primary", "label": "count signal"}),
                span(" · double = ", class_="muted"),
                h(Island, {"getter": double, "kind": "cool", "label": "derived: count * 2"}),
                span(" · parity = ", class_="muted"),
                h(Island, {"getter": parity, "kind": "warn", "label": "derived: even/odd"}),
                style={"marginTop": "0.6rem", "fontSize": "0.95rem"},
            ),
            style={"marginBottom": "1.4rem"},
        ),
        # --- slider row ---
        div(
            h(FieldLabel, {"text": "Slider", "html_for": "rp-slider"}),
            input_(
                type="range",
                min="0",
                max="100",
                step="1",
                id="rp-slider",
                value=slider,
                on_input=on_slider_input,
            ),
            div(
                span("value = ", class_="muted"),
                h(Island, {"getter": slider, "kind": "primary", "label": "slider value"}),
                span(" · percent = ", class_="muted"),
                h(Island, {"getter": slider_pct, "kind": "cool", "label": "value as percent"}),
                span(" · bucket = ", class_="muted"),
                h(Island, {"getter": slider_bucket, "kind": "warn", "label": "low / mid / high"}),
                style={"marginTop": "0.4rem", "fontSize": "0.95rem"},
            ),
            style={"marginBottom": "1.4rem"},
        ),
        # --- text input row ---
        div(
            h(FieldLabel, {"text": "Name", "html_for": "rp-name"}),
            input_(
                type="text",
                id="rp-name",
                value=name,
                placeholder="Type a name…",
                on_input=on_name_input,
                spellcheck="false",
                autocomplete="off",
                style={"maxWidth": "320px"},
            ),
            div(
                h(Island, {"getter": greeting, "kind": "primary", "label": "greeting"}),
                span(" · letters = ", class_="muted"),
                h(Island, {"getter": name_length, "kind": "cool", "label": "len(name)"}),
                style={"marginTop": "0.55rem", "fontSize": "0.95rem"},
            ),
        ),
        class_="panel",
        id="playground",
    )


@component
def _ProfilerPanel():
    register_component_run()

    def hole_text() -> str:
        return fmt_number(hole_runs())

    def writes_text() -> str:
        return fmt_number(signal_writes())

    def wyb_dom_text() -> str:
        return fmt_number(wybthon_dom_mutations())

    def naive_dom_text() -> str:
        return fmt_number(naive_dom_mutations())

    def body_text() -> str:
        return fmt_number(component_body_runs())

    def saved_text() -> str:
        saved = max(0, naive_dom_mutations() - wybthon_dom_mutations())
        return fmt_number(saved)

    return div(
        div(
            h(Eyebrow, {"text": "Profiler"}),
            span("\u00a0"),
            span("Live counters update through their own reactive holes.", class_="muted"),
            class_="panel-header",
        ),
        div(
            h(
                Stat,
                {
                    "label": "Component bodies executed",
                    "value": body_text,
                    "sub": "Locked; Wybthon runs each body once at mount.",
                    "locked": True,
                },
            ),
            h(
                Stat,
                {
                    "label": "Signal writes",
                    "value": writes_text,
                    "sub": "Every setter call from the playground.",
                    "tone": "highlight",
                },
            ),
            h(
                Stat,
                {
                    "label": "Reactive holes evaluated",
                    "value": hole_text,
                    "sub": "Only the dependent holes re-ran.",
                    "tone": "cool",
                },
            ),
            h(
                Stat,
                {
                    "label": "DOM mutations · Wybthon",
                    "value": wyb_dom_text,
                    "sub": "≈ 1 patched node per hole.",
                    "tone": "cool",
                },
            ),
            h(
                Stat,
                {
                    "label": "DOM mutations · naive",
                    "value": naive_dom_text,
                    "sub": "Whole-card innerHTML rewrites; see comparison.",
                    "tone": "hot",
                },
            ),
            h(
                Stat,
                {
                    "label": "Mutations avoided",
                    "value": saved_text,
                    "sub": "Naive minus Wybthon (this session).",
                    "tone": "warn",
                },
            ),
            class_="stat-grid",
        ),
        div(
            button(
                "Reset counters",
                on_click=lambda e: reset_counters(),
                class_="btn btn-sm",
            ),
            a(
                "View source on GitHub",
                href="https://github.com/wybthon/reactive-profiler/blob/main/app/sections/hero.py",
                target="_blank",
                rel="noopener",
                class_="btn btn-sm btn-ghost",
            ),
            style={
                "display": "flex",
                "gap": "0.5rem",
                "marginTop": "1rem",
                "flexWrap": "wrap",
            },
        ),
        class_="panel",
        id="profiler",
    )


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------


@component
def Hero():
    register_component_run()

    return section(
        div(
            div(
                h(Eyebrow, {"text": "Wybthon · run once · update fine-grained"}),
                h1(
                    span("Reactive ", class_="grad"),
                    span("Profiler", class_="grad"),
                ),
                p(
                    "Wybthon is a Python SPA framework that runs in your browser. "
                    "Component bodies execute exactly once at mount; signals flow "
                    "through reactive holes that patch single DOM nodes. ",
                    "Drive the controls below and watch the islands light up; only "
                    "the bits that depend on your input change.",
                    class_="lede",
                ),
                div(
                    a(
                        "Open on GitHub",
                        href="https://github.com/wybthon/reactive-profiler",
                        target="_blank",
                        rel="noopener",
                        class_="btn btn-primary",
                    ),
                    a(
                        "Read the docs",
                        href="https://docs.wybthon.com/",
                        target="_blank",
                        rel="noopener",
                        class_="btn",
                    ),
                    a(
                        "Install · pip install wybthon",
                        href="https://pypi.org/project/wybthon/",
                        target="_blank",
                        rel="noopener",
                        class_="btn btn-ghost",
                    ),
                    class_="hero-actions",
                ),
                div(
                    span("Powered by "),
                    span("Wybthon 0.23", class_="pill good"),
                    span("\u00a0\u00a0Pyodide 0.27", class_="pill"),
                    span("\u00a0\u00a0Pure Python, no JavaScript build", class_="pill"),
                    class_="hero-meta",
                ),
                class_="hero-copy",
            ),
            h(_Playground, {}),
            class_="hero-grid",
        ),
        div(
            h(_ProfilerPanel, {}),
            style={"marginTop": "1.4rem"},
        ),
        class_="hero container",
    )
