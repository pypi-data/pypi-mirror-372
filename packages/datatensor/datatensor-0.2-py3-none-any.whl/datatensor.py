import numpy as np

__version__ = "0.2"

# ---------------- TensorLite & Autograd ----------------
class DataTensor:
    def __init__(self, data, requires_grad=False):
        self.data = np.array(data, dtype=np.float32)
        self.requires_grad = requires_grad
        self.grad = None
        self._backward = lambda: None
        self._prev = set()

    def __add__(self, other):
        other = other if isinstance(other, DataTensor) else DataTensor(other)
        out = DataTensor(self.data + other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = self.grad + out.grad if self.grad is not None else out.grad
            if other.requires_grad:
                other.grad = other.grad + out.grad if other.grad is not None else out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __matmul__(self, other):
        out = DataTensor(self.data @ other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = self.grad + out.grad @ other.data.T if self.grad is not None else out.grad @ other.data.T
            if other.requires_grad:
                other.grad = other.grad + self.data.T @ out.grad if other.grad is not None else self.data.T @ out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __mul__(self, other):
        other = other if isinstance(other, DataTensor) else DataTensor(other)
        out = DataTensor(self.data * other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = self.grad + other.data * out.grad if self.grad is not None else other.data * out.grad
            if other.requires_grad:
                other.grad = other.grad + self.data * out.grad if other.grad is not None else self.data * out.grad
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
        self.W = DataTensor(np.random.randn(in_features, out_features) * 0.01, requires_grad=True)
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
def ReLU(x):
    data = np.maximum(0, x.data)
    out = DataTensor(data, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = x.grad + out.grad * (x.data > 0) if x.grad is not None else out.grad * (x.data > 0)
    out._backward = _backward
    out._prev = {x}
    return out

# ---------------- Loss ----------------
def mse(pred, target):
    diff = pred.data - target.data
    loss_val = (diff ** 2).mean()
    out = DataTensor(loss_val, requires_grad=True)
    def _backward():
        if pred.requires_grad:
            pred.grad = 2 * diff / diff.size
    out._backward = _backward
    out._prev = {pred}
    return out

# ---------------- Optimizer ----------------
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

# ---------------- DataFrameLite & SeriesLite ----------------
class SeriesLite:
    def __init__(self, data):
        self.data = np.array(data)

    def mean(self):
        return np.mean(self.data)

    def sum(self):
        return np.sum(self.data)

class DataFrameLite:
    def __init__(self, data_dict):
        self.data = {k: SeriesLite(v) for k, v in data_dict.items()}

    def head(self, n=5):
        return {k: v.data[:n] for k, v in self.data.items()}

# ---------------- Demo ----------------
if __name__ == "__main__":
    # Dataset
    X = DataTensor([[1.0], [2.0], [3.0], [4.0], [5.0]])
    Y = DataTensor([[2.0], [4.0], [6.0], [8.0], [10.0]])

    # Model
    model = LinearLite(1, 1)
    optimizer = SGD([model.W, model.b], lr=0.01)

    # Training
    for epoch in range(200):
        pred = model(X)
        loss = mse(pred, Y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if epoch % 20 == 0:
            print(f"Epoch {epoch}: Loss = {loss.data}")

    # Test
    X_test = DataTensor([[6.0], [7.0]])
    Y_test = model(X_test)
    print("Prediksi untuk input [6,7]:", Y_test.data)

    # DataFrameLite demo
    df = DataFrameLite({'A': [1,2,3,4,5], 'B': [5,4,3,2,1]})
    print("Head DataFrameLite:", df.head())
