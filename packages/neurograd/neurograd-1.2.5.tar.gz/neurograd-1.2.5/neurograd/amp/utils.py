"""
Utility functions for automatic mixed precision

This module contains utility functions used by the AMP system for
determining precision, casting tensors, and managing operation types.
"""
import neurograd as ng
from typing import Set
from .autocast import autocast


# Ops that should **always** run in FP32 for numerical stability
_FP32_OPS: Set[str] = {
    # math with steep/ill-conditioned curves
    "log", "exp", "sqrt", "cbrt", "log10", "log2",
    "sin", "cos", "tan",
    # softmax & reductions that accumulate / are variance-based
    "softmax",
    # norms / stats
    "batchnorm", "batchnorm2d", "layernorm", "groupnorm", "instancenorm",
    "var", "variance", "logsumexp",
    "sum", "mean", "std",
    # losses (compute entirely in fp32)
    "mse", "rmse", "mae", "binarycrossentropy", "categoricalcrossentropy",
    # casting decisions shouldn’t be overridden by autocast
    "cast",
    # pow is risky in fp16 except for tiny integer exponents
    "pow",
}

# Ops that are **safe** to run in FP16 (or BF16) by default
_FP16_SAFE_OPS: Set[str] = {
    # arithmetic
    "add", "sub", "mul", "div",
    # linalg (prefer fp32 accumulation inside the kernel)
    "matmul", "tensordot", "transpose",
    # tensor reshapes / views
    "reshape", "flatten", "squeeze", "expanddims", "slidingwindowview",
    # padding and elementwise
    "pad", "abs", "clip", "max", "min",
    # activations (excluding softmax)
    "relu", "relu6", "leakyrelu", "sigmoid", "tanh", "passthrough",
}



def should_cast_to_fp16(op_name: str) -> bool:
    """
    Determine if an operation should be cast to FP16 in autocast context.
    
    Args:
        op_name: Name of the operation
        
    Returns:
        True if the operation should be cast to FP16, False otherwise
    """
    if not autocast.is_enabled():
        return False
    
    # Handle None or empty op_name
    if not op_name:
        return True  # Default to allowing FP16
    
    op_name_lower = op_name.lower()
    
    # Force certain ops to stay in FP32
    if op_name_lower in _FP32_OPS:
        return False
        
    # Allow safe ops to use FP16
    if op_name_lower in _FP16_SAFE_OPS:
        return True
        
    # Default behavior: keep unknown ops in FP32 for safety
    return False
def maybe_cast_data(tensor, target_dtype=None, op_name: str = "unknown"):
    """
    Cast underlying array for compute without inserting Cast nodes.

    Returns an xp.ndarray suitable for the op's forward, following autocast policy.
    This mirrors PyTorch's behavior by selecting compute dtype per-op without
    modifying the input Tensor's dtype or graph.
    """
    from neurograd.tensor import Tensor

    # If input isn't a Tensor or autocast disabled, just return raw data
    if not isinstance(tensor, Tensor):
        return tensor
    if not autocast.is_enabled():
        return tensor.data

    # Avoid recursion/casts for explicit Cast operations
    if op_name and op_name.lower() == 'cast':
        return tensor.data

    # Decide target dtype
    if target_dtype is None:
        if should_cast_to_fp16(op_name):
            target_dtype = autocast.get_autocast_dtype()
        else:
            # Force FP32 for sensitive ops
            import neurograd as ng
            target_dtype = ng.float32

    # No-op if already correct dtype
    if tensor.data.dtype == target_dtype:
        return tensor.data

    # Use per-context cache to reuse cast arrays within region
    cache = autocast.get_cache()
    if cache is not None:
        key = ('data', id(tensor), target_dtype)
        cached = cache.get(key)
        if cached is not None:
            return cached
        arr = tensor.data.astype(target_dtype, copy=False)
        cache[key] = arr
        return arr

    return tensor.data.astype(target_dtype, copy=False)


def get_fp32_ops() -> Set[str]:
    """Get the set of operations that should stay in FP32."""
    return _FP32_OPS.copy()


def get_fp16_safe_ops() -> Set[str]:
    """Get the set of operations that are safe for FP16."""
    return _FP16_SAFE_OPS.copy()


def add_fp32_op(op_name: str) -> None:
    """Add an operation to the FP32 operations set."""
    _FP32_OPS.add(op_name.lower())


def add_fp16_safe_op(op_name: str) -> None:
    """Add an operation to the FP16-safe operations set."""
    _FP16_SAFE_OPS.add(op_name.lower())


def remove_fp32_op(op_name: str) -> None:
    """Remove an operation from the FP32 operations set."""
    _FP32_OPS.discard(op_name.lower())


def remove_fp16_safe_op(op_name: str) -> None:
    """Remove an operation from the FP16-safe operations set."""
    _FP16_SAFE_OPS.discard(op_name.lower())
