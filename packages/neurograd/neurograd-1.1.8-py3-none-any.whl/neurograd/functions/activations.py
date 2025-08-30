from neurograd import xp
from neurograd.functions.base import Function
from neurograd.nn.module import Module

### Activation functions classes for Functional API
# These classes implement common activation functions used in neural networks.
class ReLU(Function, Module):
    name = "ReLU"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.maximum(0, x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        x_grad = grad_output * (x.data > 0) if x.requires_grad else None
        return x_grad

class ReLU6(Function, Module):
    name = "ReLU6"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        output = xp.empty_like(x)
        xp.clip(x, 0, 6, out=output)
        return output
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            mask = (x.data > 0) & (x.data < 6)
            x_grad = grad_output * mask
        else:
            x_grad = None
        return x_grad


class Sigmoid(Function, Module):
    name = "Sigmoid"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        output = xp.empty_like(x)
        xp.multiply(x, -1, out=output)
        xp.exp(output, out=output)
        output += 1
        xp.reciprocal(output, out=output)
        return output
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            x_grad = xp.empty_like(x.data)
            xp.multiply(x.data, -1, out=x_grad)
            xp.exp(x_grad, out=x_grad)
            x_grad += 1
            xp.reciprocal(x_grad, out=x_grad)
            sigmoid_complement = 1 - x_grad
            x_grad *= sigmoid_complement
            x_grad *= grad_output
        else:
            x_grad = None
        return x_grad


class Softmax(Function, Module):
    name = "Softmax"
    def __init__(self, axis: int = -1):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        x_max = xp.max(x, axis=self.axis, keepdims=True)
        output = xp.empty_like(x)
        xp.subtract(x, x_max, out=output)
        xp.exp(output, out=output)
        exp_sum = xp.sum(output, axis=self.axis, keepdims=True)
        output /= exp_sum
        return output
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            x_max = xp.max(x.data, axis=self.axis, keepdims=True)
            softmax_x = xp.empty_like(x.data)
            xp.subtract(x.data, x_max, out=softmax_x)
            xp.exp(softmax_x, out=softmax_x)
            exp_sum = xp.sum(softmax_x, axis=self.axis, keepdims=True)
            softmax_x /= exp_sum
            dot_product = xp.sum(softmax_x * grad_output, axis=self.axis, keepdims=True)
            x_grad = xp.empty_like(x.data)
            xp.subtract(grad_output, dot_product, out=x_grad)
            x_grad *= softmax_x
        else:
            x_grad = None
        return x_grad


class Tanh(Function, Module):
    name = "Tanh"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.tanh(x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if x.requires_grad:
            tanh_x = xp.tanh(x.data)
            x_grad = grad_output * (1 - tanh_x * tanh_x)
        else:
            x_grad = None
        return x_grad

class LeakyReLU(Function, Module):
    name = "LeakyReLU"
    def __init__(self, negative_slope: float = 0.01):
        Function.__init__(self)
        Module.__init__(self)
        self.negative_slope = negative_slope
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return xp.where(x >= 0, x, self.negative_slope * x)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        x_grad = grad_output * xp.where(x.data >= 0, 1, self.negative_slope) if x.requires_grad else None
        return x_grad
    

class Passthrough(Function, Module):
    name = "Passthrough"
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        return x
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        x_grad = grad_output if x.requires_grad else None
        return x_grad
    

### Activation functions for user convenience
# These functions are designed to be used directly with tensors, providing a more intuitive interface.
def relu(x):
    return ReLU()(x) 
def relu6(x):
    return ReLU6()(x)   
def sigmoid(x):
    return Sigmoid()(x)   
def softmax(x , axis: int = -1):
        return Softmax(axis = axis)(x)   
def tanh(x):
        return Tanh()(x)
def leaky_relu(x, negative_slope: float = 0.01):
        return LeakyReLU(negative_slope=negative_slope)(x)