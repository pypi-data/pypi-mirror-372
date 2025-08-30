from neurograd import xp
from .base import Function
from neurograd.nn.module import Module

### Element-wise operations classes for Functional API
class Add(Function, Module):
    name = "Add"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, a: xp.ndarray, b: xp.ndarray) -> xp.ndarray:
        return a + b
    def backward(self, grad_output: xp.ndarray) -> tuple[xp.ndarray, xp.ndarray]:
        a, b = self.parent_tensors
        
        if a.requires_grad:
            go_a = self._cast_like(grad_output, a.data)
            a_grad = self._handle_broadcasting(go_a, a.data.shape)
        else:
            a_grad = None
        if b.requires_grad:
            go_b = self._cast_like(grad_output, b.data)
            b_grad = self._handle_broadcasting(go_b, b.data.shape)
        else:
            b_grad = None
        
        return a_grad, b_grad

class Sub(Function, Module):
    name = "Sub"    
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, a: xp.ndarray, b: xp.ndarray) -> xp.ndarray:
        return a - b
    def backward(self, grad_output: xp.ndarray) -> tuple[xp.ndarray, xp.ndarray]:
        a, b = self.parent_tensors
        
        if a.requires_grad:
            go_a = self._cast_like(grad_output, a.data)
            a_grad = self._handle_broadcasting(go_a, a.data.shape)
        else:
            a_grad = None
        if b.requires_grad:
            go_b = self._cast_like(-grad_output, b.data)
            b_grad = self._handle_broadcasting(go_b, b.data.shape)
        else:
            b_grad = None
        
        return a_grad, b_grad

class Mul(Function, Module):
    name = "Mul"
    """Element-wise multiplication."""
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, a: xp.ndarray, b: xp.ndarray) -> xp.ndarray:
        return a * b
    def backward(self, grad_output: xp.ndarray) -> tuple[xp.ndarray, xp.ndarray]:
        a, b = self.parent_tensors
        
        if a.requires_grad:
            go = self._cast_like(grad_output, b.data)
            a_grad = self._handle_broadcasting(go * b.data, a.data.shape)
        else:
            a_grad = None
        if b.requires_grad:
            go = self._cast_like(grad_output, a.data)
            b_grad = self._handle_broadcasting(go * a.data, b.data.shape)
        else:
            b_grad = None
        
        return a_grad, b_grad

class Div(Function, Module):
    name = "Div"
    """Element-wise division."""
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, a: xp.ndarray, b: xp.ndarray) -> xp.ndarray:
        return a / b
    def backward(self, grad_output: xp.ndarray) -> tuple[xp.ndarray, xp.ndarray]:
        a, b = self.parent_tensors
        
        if a.requires_grad:
            go = self._cast_like(grad_output, b.data)
            a_grad = self._handle_broadcasting(go / b.data, a.data.shape)
        else:
            a_grad = None
        if b.requires_grad:
            go = self._cast_like(grad_output, a.data)
            b_grad = self._handle_broadcasting(-go * a.data / (b.data ** 2), b.data.shape)
        else:
            b_grad = None
        
        return a_grad, b_grad

class Pow(Function, Module):
    name = "Pow"
    """Element-wise power."""
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, a: xp.ndarray, b: xp.ndarray) -> xp.ndarray:
        return a ** b
    def backward(self, grad_output: xp.ndarray) -> tuple[xp.ndarray, xp.ndarray]:
        a, b = self.parent_tensors
        
        if a.requires_grad:
            go = self._cast_like(grad_output, a.data)
            a_grad = self._handle_broadcasting(go * b.data * a.data ** (b.data - 1), a.data.shape)
        else:
            a_grad = None
        if b.requires_grad:
            go = self._cast_like(grad_output, b.data)
            b_grad = self._handle_broadcasting(go * xp.log(a.data) * (a.data ** b.data), b.data.shape)
        else:
            b_grad = None
        
        return a_grad, b_grad
    

# Convenience functions for arithmetic operations
# These functions are designed to be used directly with Tensor objects.
def add(a, b):
    return Add()(a, b)
def sub(a, b):
    return Sub()(a, b)
def mul(a, b):
    return Mul()(a, b)
def div(a, b):
    return Div()(a, b)
def pow(a, b):
    return Pow()(a, b)
