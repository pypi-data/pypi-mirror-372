try:
    from .memory import memory_tracer, trace_memory, summary
except Exception:  # pragma: no cover
    # Optional; keep utils import-light if tracing isn't available
    pass
