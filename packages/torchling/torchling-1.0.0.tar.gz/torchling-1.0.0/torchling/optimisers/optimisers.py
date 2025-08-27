from ..layers.layers import Activation
import numpy as np

class SGD:
    def __init__(self, alpha=0.01, model=None, auto_zero_grad=True):
        self.model = model
        self.alpha = alpha
        self.auto_zero_grad = auto_zero_grad

    def step(self):
        assert self.model_is_set(), "Model must be set before calling the step function."
        for layer in self.model.layers:
            if isinstance(layer, Activation):
                continue
            layer.weights.data -= self.alpha * layer.weights.grad
            layer.bias.data -= self.alpha * layer.bias.grad
            if self.auto_zero_grad:
                layer.weights.grad = np.zeros_like(layer.weights.data)
                layer.bias.grad = np.zeros_like(layer.bias.data)

    def zero_grad(self):
        assert self.model_is_set(), "Model must be set before calling the zero_grad function."
        for layer in self.model.layers:
            layer.weights.grad = np.zeros_like(layer.weights.data)
            layer.bias.grad = np.zeros_like(layer.bias.data)
            
    def model_is_set(self):
        return self.model is not None
