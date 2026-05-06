"""Global profiler counters used to visualise Wybthon's update model.

These signals are read by the on-page profiler panel and written to by the
instrumentation helpers in this module. Keeping them in a single place makes
the comparison between fine-grained reactive holes and naive whole-component
re-renders explicit.

The counters are intentionally simple Python ints wrapped in Wybthon
signals, exactly the kind of state the framework is designed to render
reactively. Updating them inside ``batch(...)`` keeps coalescing semantics
intact when many writes occur in a tight loop.
"""

from __future__ import annotations

from typing import Any, Callable, Tuple

from wybthon import batch, create_signal, untrack

# ---------------------------------------------------------------------------
# Public counters (read these in your view to display live numbers)
# ---------------------------------------------------------------------------

component_body_runs, _set_component_body_runs = create_signal(0)
"""How many times any ``@component`` body has executed.

In Wybthon, function bodies run **once per mount**. We bump this from inside
component bodies (via :func:`register_component_run`) so visitors can see the
counter sit firmly at ``N`` while signals fly by underneath.
"""

signal_writes, _set_signal_writes = create_signal(0)
"""Total signal-setter invocations observed via :func:`tracked_signal`."""

hole_runs, _set_hole_runs = create_signal(0)
"""Total reactive-hole evaluations triggered by signal updates.

Bumped by :class:`app.profiler.island.Island` whenever the wrapped getter
re-runs in response to one of its dependencies changing.
"""

wybthon_dom_mutations, _set_wybthon_dom_mutations = create_signal(0)
"""Estimated DOM mutations attributable to fine-grained Wybthon updates.

We approximate this as one mutation per hole evaluation because Wybthon's
reconciler patches a single text node (or attribute) per hole.
"""

naive_dom_mutations, _set_naive_dom_mutations = create_signal(0)
"""DOM mutations that a naive whole-component re-render would have done.

Bumped by the comparison demo each time the "naive" path rewrites the
container's ``innerHTML``; every element inside is effectively replaced.
"""

# ---------------------------------------------------------------------------
# Instrumentation helpers
# ---------------------------------------------------------------------------


def register_component_run(n: int = 1) -> None:
    """Increment the component-body-run counter from inside a component body.

    Call this on the very first line of the component you want to instrument.
    Because Wybthon component bodies run once per mount, the counter freezes
    at the number of mounted components for the lifetime of the page.
    """

    untrack(lambda: _set_component_body_runs(component_body_runs() + n))


def register_signal_write(n: int = 1) -> None:
    """Bump :data:`signal_writes` without subscribing the caller to it."""

    untrack(lambda: _set_signal_writes(signal_writes() + n))


def register_hole_run(n: int = 1) -> None:
    """Bump :data:`hole_runs` and :data:`wybthon_dom_mutations` together.

    Each Wybthon reactive-hole evaluation results in approximately one DOM
    mutation (a single text or attribute patch). We deliberately avoid
    wrapping the two writes in :func:`batch` here: this helper is invoked
    from inside the ``Island.watch`` effect, which itself runs during a
    flush. ``batch.__exit__`` triggers a synchronous flush of pending
    computations, and re-entering the same flush corrupts the queue. The
    two writes are already coalesced by the surrounding flush via
    ``_pending_set`` deduplication.
    """

    def _bump() -> None:
        _set_hole_runs(hole_runs() + n)
        _set_wybthon_dom_mutations(wybthon_dom_mutations() + n)

    untrack(_bump)


def register_naive_mutation(n: int = 1) -> None:
    """Bump :data:`naive_dom_mutations` by *n* without tracking."""

    untrack(lambda: _set_naive_dom_mutations(naive_dom_mutations() + n))


def reset_counters() -> None:
    """Reset every profiler counter to zero in a single batch."""

    def _zero() -> None:
        with batch():
            _set_component_body_runs(0)
            _set_signal_writes(0)
            _set_hole_runs(0)
            _set_wybthon_dom_mutations(0)
            _set_naive_dom_mutations(0)

    untrack(_zero)


# ---------------------------------------------------------------------------
# Tracked signals (a ``create_signal`` whose setter bumps ``signal_writes``)
# ---------------------------------------------------------------------------


def tracked_signal(initial: Any) -> Tuple[Callable[[], Any], Callable[[Any], None]]:
    """Return a ``(getter, setter)`` pair that also bumps :data:`signal_writes`.

    Use this everywhere the profiler should observe writes. The returned
    getter is a regular Wybthon signal accessor; pass it directly into
    :class:`app.profiler.island.Island` to create a reactive hole.
    """

    sig, raw_set = create_signal(initial)

    def setter(value: Any) -> None:
        raw_set(value)
        register_signal_write(1)

    return sig, setter


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def fmt_number(value: int) -> str:
    """Format an int with thousands separators (``1,234``)."""

    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)
