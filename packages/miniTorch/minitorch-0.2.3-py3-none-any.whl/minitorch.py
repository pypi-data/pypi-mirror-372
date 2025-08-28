"""
miniTorch v0.2.2 — lightweight PyTorch-like library for Termux / Python
Features:
- Tensor with autograd (batch-safe)
- Layers: Linear, Activation (ReLU, Sigmoid, Tanh), Flatten
- Losses: MSE, CrossEntropy
- Optimizers: SGD, Adam
"""

import numpy as np

__version__ = "0.2.3"

# ---------------- Tensor & Autograd ----------------
class Tensor:
    def __init__(self, data, requires_grad=False):
        self.data = np.array(data, dtype=np.float32)
        self.requires_grad = requires_grad
        self.grad = None
        self._backward = lambda: None
        self._prev = set()

    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad) if self.grad is not None else out.grad
            if other.requires_grad:
                other.grad = (other.grad + out.grad) if other.grad is not None else out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __matmul__(self, other):
        out = Tensor(self.data @ other.data, requires_grad=self.requires_grad or other.requires_grad)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad @ other.data.T) if self.grad is not None else out.grad @ other.data.T
            if other.requires_grad:
                other.grad = (other.grad + self.data.T @ out.grad) if other.grad is not None else self.data.T @ out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, requires_grad=self.requires_grad or other.requires_grad)
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
class Linear:
    def __init__(self, in_features, out_features):
        self.W = Tensor(np.random.randn(in_features, out_features)*0.01, requires_grad=True)
        self.b = Tensor(np.zeros(out_features), requires_grad=True)
        self.x = None

    def __call__(self, x: Tensor):
        self.x = x
        out_data = x.data @ self.W.data + self.b.data
        out = Tensor(out_data, requires_grad=x.requires_grad or self.W.requires_grad or self.b.requires_grad)
        def _backward():
            if self.W.requires_grad:
                self.W.grad = self.x.data.T @ out.grad  # batch-safe
            if self.b.requires_grad:
                self.b.grad = out.grad.sum(axis=0)
            if self.x.requires_grad:
                self.x.grad = out.grad @ self.W.data.T
        out._backward = _backward
        out._prev = {self.W, self.b, x}
        return out

class Flatten:
    def __call__(self, x):
        x.data = x.data.reshape(x.data.shape[0], -1)
        return x

# ---------------- Activations ----------------
def relu(x):
    data = np.maximum(0, x.data)
    out = Tensor(data, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = (x.grad if x.grad is not None else 0) + out.grad * (x.data > 0)
    out._backward = _backward
    out._prev = {x}
    return out

def sigmoid(x):
    s = 1 / (1 + np.exp(-x.data))
    out = Tensor(s, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = (x.grad if x.grad is not None else 0) + out.grad * s * (1 - s)
    out._backward = _backward
    out._prev = {x}
    return out

def tanh(x):
    t = np.tanh(x.data)
    out = Tensor(t, requires_grad=x.requires_grad)
    def _backward():
        if x.requires_grad:
            x.grad = (x.grad if x.grad is not None else 0) + out.grad * (1 - t**2)
    out._backward = _backward
    out._prev = {x}
    return out

# ---------------- Losses ----------------
def mse(pred, target):
    diff = pred.data - target.data
    loss_val = (diff**2).mean()
    out = Tensor(loss_val, requires_grad=True)
    def _backward():
        if pred.requires_grad:
            pred.grad = 2 * diff / diff.size
    out._backward = _backward
    out._prev = {pred}
    return out

def cross_entropy(pred, target):
    eps = 1e-12
    p = np.clip(pred.data, eps, 1-eps)
    loss_val = -np.sum(target.data * np.log(p)) / p.shape[0]
    out = Tensor(loss_val, requires_grad=True)
    def _backward():
        if pred.requires_grad:
            pred.grad = (p - target.data) / p.shape[0]
    out._backward = _backward
    out._prev = {pred}
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

class Adam:
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
            if p.grad is None:
                continue
            g = p.grad
            self.m[i] = self.betas[0]*self.m[i] + (1-self.betas[0])*g
            self.v[i] = self.betas[1]*self.v[i] + (1-self.betas[1])*(g**2)
            m_hat = self.m[i]/(1-self.betas[0]**self.t)
            v_hat = self.v[i]/(1-self.betas[1]**self.t)
            p.data -= self.lr * m_hat / (np.sqrt(v_hat)+self.eps)
    def zero_grad(self):
        for p in self.params:
            p.grad = None

# ---------------- Demo / Test ----------------
if __name__ == "__main__":
    # Dataset lebih besar (linear y = 2x + 1 + noise)
    X_data = np.linspace(-10, 10, 200).reshape(-1, 1).astype(np.float32)
    Y_data = 2 * X_data + 1 + np.random.randn(*X_data.shape).astype(np.float32) * 0.5

    X = Tensor(X_data, requires_grad=True)
    Y = Tensor(Y_data, requires_grad=False)

    # Model 2 layer: Linear(1, hidden) -> ReLU -> Linear(hidden, 1)
    hidden_size = 16
    layer1 = Linear(1, hidden_size)
    layer2 = Linear(hidden_size, 1)

    def model(x):
        return layer2(relu(layer1(x)))

    # Optimizer (Adam biar cepat konvergen)
    optimizer = Adam([layer1.W, layer1.b, layer2.W, layer2.b], lr=0.01)

    # Training loop
    epochs = 500
    for epoch in range(epochs):
        pred = model(X)
        loss = mse(pred, Y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 50 == 0:
            print(f"Epoch {epoch:03d} | Loss = {loss.data:.6f}")

    # Test dengan data baru
    X_test = Tensor([[12.0], [15.0], [20.0]])
    Y_test = model(X_test)
    print("Prediksi untuk input [12, 15, 20]:", Y_test.data)

