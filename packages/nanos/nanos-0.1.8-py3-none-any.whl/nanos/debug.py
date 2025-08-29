import resource
import sys
import traceback
import typing as t
from contextlib import contextmanager
from string import Template

from nanos import fmt

MEMORY_PROFILER_TPL = Template("Memory Profiler $description $start -> $end (Δ$delta)")


def print_stack_trace() -> None:
    """Prints stack trace to stdout."""
    stack_trace = traceback.format_stack()
    # Remove the last frame (this function call itself)
    stack_trace = stack_trace[:-1]
    print("".join(stack_trace))


def get_memory_usage() -> float:
    """Get current memory usage in bytes using resource module.

    Returns:
        bytes as `float`.
    """

    # Note: resource.getrusage() returns memory in different units
    # on different systems, Linux: kilobytes; macOS: bytes
    usage = resource.getrusage(resource.RUSAGE_SELF)
    if sys.platform == "darwin":  # macOS
        return usage.ru_maxrss
    return usage.ru_maxrss * 1024  # kilobytes to bytes


@contextmanager
def memory_profiler(
    description: str = "", writer: t.Callable[[str], None] = print
) -> t.Generator[None, None, None]:
    """Context manager to measure memory usage of a code block.

    Prints a short summary of memory consumption to stdout. Uses `print`
    by default, custom writer function can be provided.
    """

    start_memory = get_memory_usage()

    yield

    end_memory = get_memory_usage()
    tpl_data = {
        "description": description,
        "start": fmt.size(start_memory),
        "end": fmt.size(end_memory),
        "delta": fmt.size(end_memory - start_memory),
    }
    writer(MEMORY_PROFILER_TPL.substitute(tpl_data))
