"""Profiler primitives: shared state, instrumentation helpers, and the
``Island`` wrapper that visualises reactive holes.
"""

from .island import Island, island_value
from .state import (
    component_body_runs,
    fmt_number,
    hole_runs,
    naive_dom_mutations,
    register_component_run,
    register_naive_mutation,
    register_signal_write,
    reset_counters,
    signal_writes,
    tracked_signal,
    wybthon_dom_mutations,
)

__all__ = [
    "Island",
    "island_value",
    "component_body_runs",
    "hole_runs",
    "naive_dom_mutations",
    "register_component_run",
    "register_naive_mutation",
    "register_signal_write",
    "reset_counters",
    "signal_writes",
    "tracked_signal",
    "wybthon_dom_mutations",
    "fmt_number",
]
