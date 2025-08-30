from neurograd import xp
from .base import Function
from neurograd.nn.module import Module

# Mathematical functions classes for Functional API
class Log(Function, Module):
    name = "Log"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.log(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / x.data
        else:
            x_grad = None
        return x_grad

class Exp(Function, Module):
    name = "Exp"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.exp(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go * xp.exp(x.data)
        else:
            x_grad = None
        return x_grad
    
class Sqrt(Function, Module):
    name = "Sqrt"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.sqrt(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / (2 * xp.sqrt(x.data))
        else:
            x_grad = None
        return x_grad
    
class Cbrt(Function, Module):
    name = "Cbrt"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.cbrt(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / (3 * xp.cbrt(x.data ** 2))
        else:
            x_grad = None
        return x_grad    
    
class Sin(Function, Module):
    name = "Sin"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.sin(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go * xp.cos(x.data)
        else:
            x_grad = None
        return x_grad

class Cos(Function, Module):
    name = "Cos"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.cos(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = -go * xp.sin(x.data)
        else:
            x_grad = None
        return x_grad

class Tan(Function, Module):
    name = "Tan"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.tan(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / (xp.cos(x.data) ** 2)
        else:
            x_grad = None
        return x_grad

class Log10(Function, Module):
    name = "Log10"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.log10(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / (x.data * xp.log(10))
        else:
            x_grad = None
        return x_grad
    
class Log2(Function, Module):
    name = "Log2"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.log2(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go / (x.data * xp.log(2))
        else:
            x_grad = None
        return x_grad
    
class Abs(Function, Module):
    name = "Abs"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.abs(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            go = self._cast_like(grad_output, x.data)
            x_grad = go * xp.sign(x.data)
        else:
            x_grad = None
        return x_grad
    
class Clip(Function, Module):
    name = "Clip"
    def __init__(self, min_val=None, max_val=None):
        Function.__init__(self)
        Module.__init__(self)
        self.min_val = min_val
        self.max_val = max_val
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.clip(x, self.min_val, self.max_val)
        
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
        
        # Gradient is 1 where x is within bounds, 0 where it's clipped
        mask = xp.ones_like(x.data)
        if self.min_val is not None:
            mask = mask * (x.data >= self.min_val)
        if self.max_val is not None:
            mask = mask * (x.data <= self.max_val)
        
        go = self._cast_like(grad_output, x.data)
        x_grad = go * mask
        return x_grad
    

# Convenience functions for arithmetic operations
# These functions are designed to be used directly with Tensor objects.
def log(x):
    return Log()(x)
def exp(x):
    return Exp()(x)
def sin(x):
    return Sin()(x)
def cos(x):
    return Cos()(x)
def tan(x):
    return Tan()(x) 
def sqrt(x):
    return Sqrt()(x)
def cbrt(x):
    return Cbrt()(x) 
def log10(x):
    return Log10()(x) 
def log2(x):
    return Log2()(x)
def abs(x):
    return Abs()(x)
def clip(x, min_val=None, max_val=None):
    return Clip(min_val, max_val)(x)
