"""``Island`` — a visual wrapper around a reactive hole.

Wybthon already updates DOM nodes fine-grained when a signal changes; this
component just makes that visible. Whenever the wrapped getter re-evaluates
we briefly highlight the surrounding span and bump the global hole-run
counter so the on-page profiler can show you exactly how much (or how
little) work the framework actually did.

The flash is implemented with two animation-name aliases (``flash-a`` /
``flash-b``) that we alternate between via the ``class`` reactive prop —
the ``animation-name`` change is what restarts the keyframe.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from wybthon import component, create_effect, create_signal, span, untrack

from .state import register_hole_run

__all__ = ["Island", "island_value"]


def island_value(value: Any) -> str:
    """Coerce a value to the string we want to render inside an island."""

    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


@component
def Island(
    getter: Optional[Callable[[], Any]] = None,
    kind: str = "primary",
    label: Optional[str] = None,
    formatter: Optional[Callable[[Any], str]] = None,
) -> Any:
    """Render ``getter()`` as a flashing reactive island.

    Args:
        getter: A zero-arg accessor (typically a signal getter or a
            ``lambda`` reading several signals). Embedded as a hole, so
            Wybthon's reconciler patches just the inner text node when its
            dependencies change.
        kind: Visual variant — one of ``"primary"`` (purple), ``"cool"``
            (teal), or ``"warn"`` (amber). Maps to a CSS modifier class.
        label: Optional ``title`` attribute, useful as a tooltip when
            multiple islands appear in the same view.
        formatter: Function used to stringify the raw value before it
            reaches the DOM. Defaults to :func:`island_value`.

    Returns:
        A ``VNode`` for the wrapping ``<span>``.
    """

    kind_static = untrack(kind) or "primary"
    label_static = untrack(label) or "reactive hole"
    fmt = untrack(formatter) or island_value

    rev_counter = [0]
    rev_signal, set_rev = create_signal(0)

    def watch() -> None:
        getter()
        rev_counter[0] += 1
        register_hole_run(1)
        untrack(lambda: set_rev(rev_counter[0]))

    create_effect(watch)

    def class_for_value() -> str:
        return f"island island--{kind_static} flash-{rev_signal() % 2}"

    def text_value() -> str:
        return fmt(getter())

    return span(
        text_value,
        class_=class_for_value,
        title=label_static,
    )
