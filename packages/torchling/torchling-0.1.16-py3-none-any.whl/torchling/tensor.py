import numpy as np

class Tensor:
    def __init__(self, data, parents=(), operation=None):
        data = np.array(data, dtype=np.float64) if not isinstance(data, np.ndarray) else data
        self.data = data
        self.parents = set(parents)
        self.grad = np.zeros_like(data)
        self.operation = operation
        self._backward = lambda: None
    
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, parents=(self, other), operation='+')
        def _backward():
            if len(self.parents) != 0:
                self.grad += 1.0 * out.grad
            if len(other.parents) != 0:    
                other.grad += 1.0 * out.grad
        out._backward = _backward
        return out
    
    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, parents=(self, other), operation='*')
        def _backward():
            if len(self.parents) != 0:
                self.grad += other.data * out.grad
            if len(other.parents) != 0:
                other.grad += self.data * out.grad
        out._backward = _backward
        return out
    
    def __matmul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data @ other.data, parents=(self, other), operation='@')
        def _backward():
            self.grad += out.grad @ other.data.T
            other.grad += self.data.T @ out.grad
        out._backward = _backward
        return out
    
    def __rmul__(self, other):
        return self * other
    
    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return Tensor(other) - self

    def __truediv__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data / other.data, parents=(self, other), operation='/')
        def _backward():
            if len(self.parents) != 0:
                self.grad += (1.0 / other.data) * out.grad

            if len(other.parents) != 0:
                other.grad += (-self.data / (other.data ** 2)) * out.grad

        out._backward = _backward
        return out

    def __rtruediv__(self, other):
        return Tensor(other) / self
    
    def __pow__(self, other):
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = Tensor(self.data**other, (self,), operation='**')
        def _backward():
            self.grad += (other * self.data**(other-1)) * out.grad
        out._backward = _backward
        return out
    
    def relu(self):
        out = Tensor(np.maximum(0, self.data), parents=(self,), operation='relu')
        def _backward():
            self.grad += (self.data > 0).astype(self.data.dtype) * out.grad
        out._backward = _backward
        return out
    
    def sigmoid(self):
        s = 1 / (1 + np.exp(-self.data))
        out = Tensor(s, parents=(self,), operation='sigmoid')
        def _backward():
            self.grad += s * (1 - s) * out.grad
        out._backward = _backward
        return out
    
    def tanh(self):
        t = np.tanh(self.data)
        out = Tensor(t, parents=(self,), operation='tanh')
        def _backward():
            self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward
        return out
    
    def __neg__(self):
        return self * -1
    
    def backward(self):
        topology = []
        visited = set()
        def build_topology(tensor):
            if tensor not in visited:
                visited.add(tensor)
                for parent in tensor.parents:
                    build_topology(parent)
                topology.append(tensor)
        build_topology(self)
        
        self.grad = np.ones_like(self.data)
        for tensor in reversed(topology):
            tensor._backward()

    def mean(self):
        n = self.data.size
        out = Tensor(np.array(self.data.mean()), parents=(self,), operation='mean')
        def _backward():
            self.grad += (1.0 / n) * np.ones_like(self.data) * out.grad
        out._backward = _backward
        return out