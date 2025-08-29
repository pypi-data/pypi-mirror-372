"""
DataTensor v0.1.1 — Lightweight library 
Features:
- DataFrameLite: manipulasi
- SeriesLite: kolom tunggal
- DataTensor: tensor dengan autograd sederhana
- Layers & Optimizers: LinearLite, ReLU, SGD Lite
"""

import numpy as np

__version__ = "0.1.1"

# ---------------- SeriesLite ----------------
class SeriesLite:
    def __init__(self, data):
        self.data = list(data)

    def mean(self):
        return sum(self.data) / len(self.data)

    def sum(self):
        return sum(self.data)

    def __repr__(self):
        return f"SeriesLite({self.data})"

# ---------------- DataFrameLite ----------------
class DataFrameLite:
    def __init__(self, data: dict):
        self.data = {k: SeriesLite(v) for k, v in data.items()}

    def head(self, n=5):
        return {k: v.data[:n] for k, v in self.data.items()}

    def describe(self):
        desc = {}
        for k, series in self.data.items():
            desc[k] = {
                "mean": series.mean(),
                "sum": series.sum(),
                "count": len(series.data)
            }
        return desc

    def __repr__(self):
        return f"DataFrameLite({self.data})"

# ---------------- DataTensor (TensorLite) ----------------
class DataTensor:
    def __init__(self, data, requires_grad=False):
        self.data = np.array(data, dtype=np.float32)
        self.requires_grad = requires_grad
        self.grad = None
        self._backward = lambda: None
        self._prev = set()

    # Basic arithmetic
    def __add__(self, other):
        other = other if isinstance(other, DataTensor) else DataTensor(other)
        out = DataTensor(self.data + other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad) if self.grad is not None else out.grad
            if other.requires_grad:
                other.grad = (other.grad + out.grad) if other.grad is not None else out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __matmul__(self, other):
        out = DataTensor(self.data @ other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad @ other.data.T) if self.grad is not None else out.grad @ other.data.T
            if other.requires_grad:
                other.grad = (other.grad + self.data.T @ out.grad) if other.grad is not None else self.data.T @ out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __mul__(self, other):
        other = other if isinstance(other, DataTensor) else DataTensor(other)
        out = DataTensor(self.data * other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + other.data * out.grad) if self.grad is not None else other.data * out.grad
            if other.requires_grad:
                other.grad = (other.grad + self.data * out.grad) if other.grad is not None else self.data * out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def backward(self, grad=None):
        if grad is None:
            grad = np.ones_like(self.data)
        self.grad = grad
        visited = set()
        topo_order = []
        def topo(t):
            if t not in visited:
                visited.add(t)
                for p in t._prev:
                    topo(p)
                topo_order.append(t)
        topo(self)
        for t in reversed(topo_order):
            t._backward()

# ---------------- Layers ----------------
class LinearLite:
    def __init__(self, in_features, out_features):
        self.W = DataTensor(np.random.randn(in_features, out_features)*0.01, requires_grad=True)
        self.b = DataTensor(np.zeros(out_features), requires_grad=True)
        self.x = None

    def __call__(self, x: DataTensor):
        self.x = x
        out_data = x.data @ self.W.data + self.b.data
        out = DataTensor(out_data, requires_grad=x.requires_grad or self.W.requires_grad or self.b.requires_grad)
        def _backward():
            if self.W.requires_grad:
                self.W.grad = self.x.data.T @ out.grad
            if self.b.requires_grad:
                self.b.grad = out.grad.sum(axis=0)
            if self.x.requires_grad:
                self.x.grad = out.grad @ self.W.data.T
        out._backward = _backward
        out._prev = {self.W, self.b, x}
        return out

# ---------------- Activations ----------------
def ReLU(x: DataTensor):
    data = np.maximum(0, x.data)
    out = DataTensor(data, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = (x.grad if x.grad is not None else 0) + out.grad * (x.data > 0)
    out._backward = _backward
    out._prev = {x}
    return out

# ---------------- Optimizers ----------------
class SGD:
    def __init__(self, params, lr=0.01):
        self.params = params
        self.lr = lr

    def step(self):
        for p in self.params:
            if p.grad is not None:
                p.data -= self.lr * p.grad

    def zero_grad(self):
        for p in self.params:
            p.grad = None

# ---------------- Demo ----------------
if __name__ == "__main__":
    # DataFrameLite demo
    df = DataFrameLite({"A":[1,2,3,4,5],"B":[5,4,3,2,1]})
    print("Head:", df.head())
    print("Describe:", df.describe())

    # DataTensor demo
    X = DataTensor([[1],[2],[3],[4],[5]])
    Y = DataTensor([[2],[4],[6],[8],[10]])

    model = LinearLite(1,1)
    optimizer = SGD([model.W, model.b], lr=0.01)

    for epoch in range(200):
        pred = model(X)
        loss = ((pred.data - Y.data)**2).mean()
        optimizer.zero_grad()
        # backward manual
        grad = 2*(pred.data - Y.data)/Y.data.size
        pred.backward(grad)
        optimizer.step()
        if epoch % 20 == 0:
            print(f"Epoch {epoch}: Loss = {loss}")

    # Test
    X_test = DataTensor([[6],[7]])
    Y_test = model(X_test)
    print("Prediksi:", Y_test.data)

