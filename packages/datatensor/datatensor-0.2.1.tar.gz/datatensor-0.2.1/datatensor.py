"""
DataTensor v0.2 — Upgrade dengan data 10.000+ baris dan multi-layer
Features:
- DataFrameLite & SeriesLite (basic)
- DataTensor (tensor + autograd)
- Multi-layer LinearLite + ReLU
- Optimizer: AdamLite
"""

import numpy as np

__version__ = "0.2"

# ---------------- DataTensor / TensorLite ----------------
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

    def __call__(self, x):
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

def relu(x):
    data = np.maximum(0, x.data)
    out = DataTensor(data, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = (x.grad if x.grad is not None else 0) + out.grad * (x.data > 0)
    out._backward = _backward
    out._prev = {x}
    return out

# ---------------- Optimizer ----------------
class AdamLite:
    def __init__(self, params, lr=0.001, betas=(0.9,0.999), eps=1e-8):
        self.params = params
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.m = [np.zeros_like(p.data) for p in params]
        self.v = [np.zeros_like(p.data) for p in params]
        self.t = 0

    def step(self):
        self.t +=1
        for i, p in enumerate(self.params):
            if p.grad is None: continue
            g = p.grad
            self.m[i] = self.betas[0]*self.m[i] + (1-self.betas[0])*g
            self.v[i] = self.betas[1]*self.v[i] + (1-self.betas[1])*(g**2)
            m_hat = self.m[i]/(1-self.betas[0]**self.t)
            v_hat = self.v[i]/(1-self.betas[1]**self.t)
            p.data -= self.lr * m_hat/(np.sqrt(v_hat)+self.eps)

    def zero_grad(self):
        for p in self.params:
            p.grad = None

# ---------------- Demo / Training ----------------
if __name__=="__main__":
    # Sintesis data 10.000+ baris
    np.random.seed(42)
    X_data = np.random.rand(10000,1)*10
    Y_data = 3*X_data + 5 + np.random.randn(10000,1)*2  # linear + noise

    X = DataTensor(X_data)
    Y = DataTensor(Y_data)

    # Model 3-layer
    layer1 = LinearLite(1,64)
    layer2 = LinearLite(64,64)
    layer3 = LinearLite(64,1)

    optimizer = AdamLite([layer1.W, layer1.b, layer2.W, layer2.b, layer3.W, layer3.b], lr=0.001)

    # Training loop sederhana
    for epoch in range(50):
        out1 = relu(layer1(X))
        out2 = relu(layer2(out1))
        pred = layer3(out2)

        loss = ((pred.data - Y.data)**2).mean()
        loss_tensor = DataTensor(loss, requires_grad=True)
        optimizer.zero_grad()
        loss_tensor.backward()
        optimizer.step()

        if epoch % 5==0:
            print(f"Epoch {epoch}, Loss: {loss:.4f}")

    # Test prediksi
    X_test = DataTensor(np.array([[12],[15],[20]]))
    out1 = relu(layer1(X_test))
    out2 = relu(layer2(out1))
    pred_test = layer3(out2)
    print("Prediksi test:", pred_test.data)
