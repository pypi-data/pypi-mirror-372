from ..tensor import Tensor
import numpy as np

class Linear:
    def __init__(self, size, input_size=None):
        self.n = size
        self.input_size = input_size
        self.weights = None
        self.bias = None

    def __call__(self, x):
        return self.weights @ x + self.bias
    
    def compile(self):
        self.weights = Tensor(np.random.uniform(-1, 1, size=(self.n, self.input_size)))
        self.bias = Tensor(np.random.uniform(-1, 1, size=(self.n, 1)))

class Activation:
    def __init__(self):
        self.n = None

class Tanh(Activation):
    def __init__(self):
        super().__init__()

    def __call__(self, x):
        return x.tanh()
    
class Relu(Activation):
    def __init__(self):
        super().__init__()

    def __call__(self, x):
        return x.relu()
