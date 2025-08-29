from __future__ import annotations

"""
Memory tracing utilities for NeuroGrad.

Features:
- Per-op memory deltas (CuPy pool + driver free bytes when on GPU)
- Per-tensor allocation registry with sizes, dtypes, devices
- Simple context manager to enable/disable tracing and print a summary

Usage:
    from neurograd.utils.memory import trace_memory, summary, memory_tracer

    with trace_memory():
        out = model(X)
        # ...
    print(memory_tracer.summary())

Note:
- GPU stats rely on CuPy if `neurograd.DEVICE == 'cuda'`.
- On CPU, only tensor sizes and op timings are recorded.
"""

import time
import weakref
import threading
from typing import Any, Dict, List, Optional

try:
    # Importing from package root is safe because xp/DEVICE are initialized
    from neurograd import xp, DEVICE  # type: ignore
except Exception:  # pragma: no cover
    xp, DEVICE = None, 'cpu'  # type: ignore


def _now() -> float:
    return time.perf_counter()


def _array_nbytes(arr: Any) -> Optional[int]:
    try:
        return int(arr.nbytes)  # numpy/cupy expose nbytes
    except Exception:
        try:
            return int(arr.size * arr.dtype.itemsize)
        except Exception:
            return None


class MemoryTracer:
    """Collects memory usage at op/tensor granularity."""

    def __init__(self) -> None:
        self._enabled: bool = False
        self._lock = threading.RLock()
        self._op_stack: List[Dict[str, Any]] = []
        self._op_events: List[Dict[str, Any]] = []
        self._live_tensors: Dict[int, Dict[str, Any]] = {}
        self._snapshots: List[Dict[str, Any]] = []

    # ------------- Control -------------
    def is_enabled(self) -> bool:
        return self._enabled

    def start(self) -> None:
        with self._lock:
            self._enabled = True
            self._op_stack.clear()
            self._op_events.clear()
            self._snapshots.clear()

    def stop(self) -> None:
        with self._lock:
            self._enabled = False

    # ------------- GPU/CPU metrics -------------
    def _gpu_mem(self) -> Optional[Dict[str, Optional[int]]]:
        if DEVICE != 'cuda':
            return None
        try:
            import cupy as cp  # type: ignore
            free, total = cp.cuda.runtime.memGetInfo()
            pool = cp.get_default_memory_pool()
            used_pool = int(pool.used_bytes())
            tot_pool = int(pool.total_bytes())
            return {
                'free': int(free),
                'total': int(total),
                'used_pool': used_pool,
                'total_pool_alloc': tot_pool,
            }
        except Exception:
            # Gracefully degrade when driver/pool introspection is unavailable
            return None

    # ------------- Op hooks -------------
    def op_start(self, func: Any, inputs: List[Any]) -> None:
        if not self._enabled:
            return
        with self._lock:
            meta_inputs = []
            for t in inputs:
                try:
                    meta_inputs.append({
                        'name': getattr(t, 'name', None),
                        'requires_grad': getattr(t, 'requires_grad', False),
                        'shape': getattr(getattr(t, 'data', None), 'shape', None),
                        'dtype': str(getattr(getattr(t, 'data', None), 'dtype', '')),
                        'nbytes': _array_nbytes(getattr(t, 'data', None)),
                        'device': 'cuda' if DEVICE == 'cuda' else 'cpu',
                    })
                except Exception:
                    meta_inputs.append({'error': 'input_introspection_failed'})
            info = {
                'ts_start': _now(),
                'op': getattr(func, 'name', None) or func.__class__.__name__,
                'mem_before': self._gpu_mem(),
                'inputs': meta_inputs,
            }
            self._op_stack.append(info)

    def op_end(self, func: Any, output_data: Any) -> None:
        if not self._enabled:
            return
        with self._lock:
            if not self._op_stack:
                return
            info = self._op_stack.pop()
            info['ts_end'] = _now()
            info['duration_ms'] = (info['ts_end'] - info['ts_start']) * 1000.0
            info['output'] = {
                'shape': getattr(output_data, 'shape', None),
                'dtype': str(getattr(output_data, 'dtype', '')),
                'nbytes': _array_nbytes(output_data),
            }
            after = self._gpu_mem()
            info['mem_after'] = after
            # Compute deltas when GPU introspection is available
            if info.get('mem_before') and after:
                before = info['mem_before']
                def _delta(key: str) -> Optional[int]:
                    try:
                        return int(after.get(key, 0)) - int(before.get(key, 0))
                    except Exception:
                        return None
                info['delta'] = {
                    'used_pool': _delta('used_pool'),
                    'total_pool_alloc': _delta('total_pool_alloc'),
                    # Driver free decreases when allocating; keep sign consistent (+ means increase)
                    'driver_free_bytes': _delta('free'),
                }
            self._op_events.append(info)

    # ------------- Tensor hooks -------------
    def on_tensor_init(self, tensor: Any) -> None:
        if not self._enabled:
            return
        with self._lock:
            try:
                tid = id(tensor)
                rec = {
                    'id': tid,
                    'name': getattr(tensor, 'name', None),
                    'requires_grad': getattr(tensor, 'requires_grad', False),
                    'shape': getattr(getattr(tensor, 'data', None), 'shape', None),
                    'dtype': str(getattr(getattr(tensor, 'data', None), 'dtype', '')),
                    'nbytes': _array_nbytes(getattr(tensor, 'data', None)),
                    'device': getattr(tensor, 'device', 'cpu'),
                    'op': getattr(getattr(tensor, 'grad_fn', None), 'name', None),
                    'ts': _now(),
                }
                self._live_tensors[tid] = rec
                try:
                    weakref.finalize(tensor, self._on_tensor_finalize, tid)
                except Exception:
                    pass
            except Exception:
                pass

    def _on_tensor_finalize(self, tid: int) -> None:
        with self._lock:
            self._live_tensors.pop(tid, None)

    # ------------- Snapshots and reporting -------------
    def snapshot(self, tag: Optional[str] = None) -> None:
        with self._lock:
            snap = {
                'ts': _now(),
                'tag': tag,
                'gpu': self._gpu_mem(),
                'live_tensors': len(self._live_tensors),
            }
            self._snapshots.append(snap)

    @property
    def op_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._op_events)

    @property
    def live_tensors(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._live_tensors.values())

    def summary(self, top_ops: int = 15, top_tensors: int = 15) -> str:
        """Human-friendly summary string."""
        lines: List[str] = []
        gpu0 = self._gpu_mem()
        if gpu0:
            used_pool = gpu0.get('used_pool')
            total = gpu0.get('total')
            free = gpu0.get('free')
            lines.append(
                f"GPU pool used={used_pool}B, free={free}B, total={total}B"
            )
        lines.append(f"ops recorded={len(self._op_events)}, live tensors={len(self._live_tensors)}")

        # Aggregate by op name
        agg: Dict[str, Dict[str, Any]] = {}
        for e in self._op_events:
            op = e.get('op', 'Unknown')
            agg.setdefault(op, {'count': 0, 'pool_delta_bytes': 0, 'time_ms': 0.0})
            agg[op]['count'] += 1
            d = (e.get('delta') or {}).get('used_pool')
            if isinstance(d, int):
                agg[op]['pool_delta_bytes'] += d
            agg[op]['time_ms'] += float(e.get('duration_ms') or 0.0)

        lines.append("Top ops by pool delta:")
        top = sorted(agg.items(), key=lambda kv: kv[1]['pool_delta_bytes'], reverse=True)[:top_ops]
        for name, a in top:
            lines.append(f"- {name}: calls={a['count']} pool_delta={a['pool_delta_bytes']}B time={a['time_ms']:.2f}ms")

        # Largest live tensors
        lines.append("Largest live tensors:")
        live_sorted = sorted(self._live_tensors.values(), key=lambda r: (r.get('nbytes') or 0), reverse=True)[:top_tensors]
        for rec in live_sorted:
            lines.append(
                f"- {rec.get('name')} op={rec.get('op')} shape={rec.get('shape')} dtype={rec.get('dtype')} nbytes={rec.get('nbytes')}"
            )
        return "\n".join(lines)


class _TraceContext:
    def __init__(self, tracer: MemoryTracer, snapshot_tag: Optional[str] = None) -> None:
        self.tracer = tracer
        self.snapshot_tag = snapshot_tag
    def __enter__(self):
        self.tracer.start()
        if self.snapshot_tag:
            self.tracer.snapshot(f"begin:{self.snapshot_tag}")
        return self.tracer
    def __exit__(self, exc_type, exc, tb):
        if self.snapshot_tag:
            self.tracer.snapshot(f"end:{self.snapshot_tag}")
        self.tracer.stop()


# Global tracer instance
memory_tracer = MemoryTracer()


def trace_memory(tag: Optional[str] = None) -> _TraceContext:
    """Context manager to enable memory tracing in a scope.

    Example:
        with trace_memory("fwd") as mt:
            out = model(X)
        print(mt.summary())
    """
    return _TraceContext(memory_tracer, snapshot_tag=tag)


def summary(top_ops: int = 15, top_tensors: int = 15) -> str:
    """Convenience function to return current summary string."""
    return memory_tracer.summary(top_ops=top_ops, top_tensors=top_tensors)

