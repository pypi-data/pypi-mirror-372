import numpy as np

import neurograd as ng
from neurograd.tensor import Tensor
from neurograd.functions.activations import ReLU6
from neurograd.utils.aliases import ACTIVATIONS


def test_relu6_forward():
    x = Tensor(np.array([-2.0, 0.0, 3.0, 7.0], dtype=np.float32))
    y = ReLU6()(x)
    np.testing.assert_allclose(y.data, np.array([0.0, 0.0, 3.0, 6.0], dtype=np.float32))


def test_relu6_backward():
    x = Tensor(np.array([-2.0, 0.0, 3.0, 7.0], dtype=np.float32), requires_grad=True)
    y = x.relu6()
    loss = y.sum()
    loss.backward()
    np.testing.assert_allclose(x.grad, np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32))


def test_relu6_alias():
    act = ACTIVATIONS["relu6"]()
    x = Tensor(np.array([-1.0, 2.5, 9.0], dtype=np.float32))
    y = act(x)
    np.testing.assert_allclose(y.data, np.array([0.0, 2.5, 6.0], dtype=np.float32))

