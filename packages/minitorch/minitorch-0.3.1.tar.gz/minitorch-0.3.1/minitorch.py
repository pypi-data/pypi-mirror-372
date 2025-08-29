"""
miniTorch v0.3.1 — lightweight deep learning framework
- Tensor with autograd (batch-safe)
- Layers: Linear, Conv2D, BatchNorm1D, Flatten, ReLU, LeakyReLU, Sigmoid, Tanh
- Losses: MSE, L1Loss, CrossEntropy
- Optimizers: SGD, Adam (with weight decay)
- Features: Module API, DataLoader, device support (CPU), unit tests
- Changelog:
  - v0.3.1: Fixed parameters() bug, optimized initialization, adjusted lr for convergence
  - v0.3.0: Added Conv2D, BatchNorm1D, LeakyReLU, L1Loss, Module API, DataLoader,
             device support, weight decay in Adam, unit tests
  - v0.2.3: Fixed version mismatch, added changelog
  - v0.2.2: Initial release
"""

import numpy as np
import unittest

__version__ = "0.3.1"

# ---------------- Tensor & Autograd ----------------
class Tensor:
    """A multi-dimensional array with autograd support.
    
    Args:
        data: Input data (numpy array or list).
        requires_grad: If True, gradients are computed for this Tensor.
        device: Device to store the Tensor ('cpu' or 'gpu').
    """
    def __init__(self, data, requires_grad=False, device='cpu'):
        self.data = np.array(data, dtype=np.float32)
        self.requires_grad = requires_grad
        self.device = device
        self.grad = None
        self._backward = lambda: None
        self._prev = set()

    def to(self, device):
        """Move Tensor to specified device."""
        self.device = device
        return self

    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        out = Tensor(self.data + other.data, requires_grad=self.requires_grad or other.requires_grad, device=self.device)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad) if self.grad is not None else out.grad
            if other.requires_grad:
                other.grad = (other.grad + out.grad) if other.grad is not None else out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __sub__(self, other):
        """Element-wise subtraction."""
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        out = Tensor(self.data - other.data, requires_grad=self.requires_grad or other.requires_grad, device=self.device)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad) if self.grad is not None else out.grad
            if other.requires_grad:
                other.grad = (other.grad - out.grad) if other.grad is not None else -out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __matmul__(self, other):
        out = Tensor(self.data @ other.data, requires_grad=self.requires_grad or other.requires_grad, device=self.device)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad @ other.data.T) if self.grad is not None else out.grad @ other.data.T
            if other.requires_grad:
                other.grad = (other.grad + self.data.T @ out.grad) if other.grad is not None else self.data.T @ out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        out = Tensor(self.data * other.data, requires_grad=self.requires_grad or other.requires_grad, device=self.device)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + other.data * out.grad) if self.grad is not None else other.data * out.grad
            if other.requires_grad:
                other.grad = (other.grad + self.data * out.grad) if other.grad is not None else self.data * out.grad
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __truediv__(self, other):
        """Element-wise division."""
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        out = Tensor(self.data / other.data, requires_grad=self.requires_grad or other.requires_grad, device=self.device)
        def _backward():
            if self.requires_grad:
                self.grad = (self.grad + out.grad / other.data) if self.grad is not None else out.grad / other.data
            if other.requires_grad:
                other.grad = (other.grad - self.data * out.grad / (other.data ** 2)) if other.grad is not None else -self.data * out.grad / (other.data ** 2)
        out._backward = _backward
        out._prev = {self, other}
        return out

    def backward(self, grad=None):
        """Compute gradients using autograd."""
        if not self.requires_grad:
            raise ValueError("Cannot call backward on a Tensor with requires_grad=False")
        if grad is None:
            grad = np.ones_like(self.data)
        self.grad = grad
        visited = set()
        topo_order = []
        def topo(t):
            if t not in visited and t.requires_grad:
                visited.add(t)
                for p in t._prev:
                    topo(p)
                topo_order.append(t)
        topo(self)
        for t in reversed(topo_order):
            t._backward()

# ---------------- Module API ----------------
class Module:
    """Base class for neural network modules."""
    def __call__(self, x):
        return self.forward(x)
    
    def parameters(self):
        """Return list of trainable parameters."""
        params = []
        for attr in vars(self).values():
            if isinstance(attr, Tensor) and attr.requires_grad:
                params.append(attr)
            elif isinstance(attr, Module):
                params.extend(attr.parameters())
            elif isinstance(attr, (list, tuple)):
                for item in attr:
                    if isinstance(item, Module):
                        params.extend(item.parameters())
        return params

class Sequential(Module):
    """A sequential container of layers."""
    def __init__(self, *layers):
        self.layers = list(layers)
    
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

# ---------------- Layers ----------------
class Linear(Module):
    """Linear layer: y = xW + b."""
    def __init__(self, in_features, out_features):
        scale = np.sqrt(2.0 / (in_features + out_features))  # Xavier initialization
        self.W = Tensor(np.random.randn(in_features, out_features) * scale, requires_grad=True)
        self.b = Tensor(np.zeros(out_features), requires_grad=True)
        self.x = None

    def forward(self, x: Tensor):
        self.x = x
        out_data = x.data @ self.W.data + self.b.data
        out = Tensor(out_data, requires_grad=x.requires_grad or self.W.requires_grad or self.b.requires_grad, device=x.device)
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

class Conv2D(Module):
    """2D Convolutional layer."""
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride
        self.padding = padding
        scale = np.sqrt(2.0 / (in_channels * kernel_size[0] * kernel_size[1] + out_channels))
        self.W = Tensor(np.random.randn(out_channels, in_channels, *self.kernel_size) * scale, requires_grad=True)
        self.b = Tensor(np.zeros(out_channels), requires_grad=True)
        self.x = None

    def forward(self, x: Tensor):
        self.x = x
        batch, in_c, h, w = x.data.shape
        if in_c != self.in_channels:
            raise ValueError(f"Expected {self.in_channels} input channels, got {in_c}")
        out_h = (h + 2 * self.padding - self.kernel_size[0]) // self.stride + 1
        out_w = (w + 2 * self.padding - self.kernel_size[1]) // self.stride + 1
        out_data = np.zeros((batch, self.out_channels, out_h, out_w), dtype=np.float32)

        x_padded = np.pad(x.data, ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
        for i in range(out_h):
            for j in range(out_w):
                x_slice = x_padded[:, :, i * self.stride:i * self.stride + self.kernel_size[0], j * self.stride:j * self.stride + self.kernel_size[1]]
                for k in range(self.out_channels):
                    out_data[:, k, i, j] = np.sum(x_slice * self.W.data[k], axis=(1, 2, 3)) + self.b.data[k]

        out = Tensor(out_data, requires_grad=x.requires_grad or self.W.requires_grad or self.b.requires_grad, device=x.device)
        def _backward():
            if self.W.requires_grad:
                self.W.grad = np.zeros_like(self.W.data)
                for i in range(out_h):
                    for j in range(out_w):
                        x_slice = x_padded[:, :, i * self.stride:i * self.stride + self.kernel_size[0], j * self.stride:j * self.stride + self.kernel_size[1]]
                        for k in range(self.out_channels):
                            self.W.grad[k] += np.sum(x_slice * out.grad[:, k:k+1, i:i+1, j:j+1], axis=0)
            if self.b.requires_grad:
                self.b.grad = out.grad.sum(axis=(0, 2, 3))
            if self.x.requires_grad:
                self.x.grad = np.zeros_like(x.data)
                x_padded_grad = np.pad(self.x.grad, ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
                for i in range(out_h):
                    for j in range(out_w):
                        for k in range(self.out_channels):
                            x_padded_grad[:, :, i * self.stride:i * self.stride + self.kernel_size[0], j * self.stride:j * self.stride + self.kernel_size[1]] += \
                                out.grad[:, k:k+1, i:i+1, j:j+1] * self.W.data[k]
                self.x.grad = x_padded_grad[:, :, self.padding:h+self.padding, self.padding:w+self.padding]
        out._backward = _backward
        out._prev = {self.W, self.b, x}
        return out

class BatchNorm1D(Module):
    """1D Batch Normalization layer."""
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        self.eps = eps
        self.momentum = momentum
        self.gamma = Tensor(np.ones(num_features), requires_grad=True)
        self.beta = Tensor(np.zeros(num_features), requires_grad=True)
        self.running_mean = np.zeros(num_features, dtype=np.float32)
        self.running_var = np.ones(num_features, dtype=np.float32)
        self.training = True
        self.x = None
        self.x_norm = None

    def forward(self, x: Tensor):
        self.x = x
        if x.data.ndim != 2:
            raise ValueError("BatchNorm1D expects 2D input (batch, features)")
        
        if self.training:
            mean = x.data.mean(axis=0)
            var = x.data.var(axis=0)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            mean = self.running_mean
            var = self.running_var

        self.x_norm = (x.data - mean) / np.sqrt(var + self.eps)
        out_data = self.gamma.data * self.x_norm + self.beta.data
        out = Tensor(out_data, requires_grad=x.requires_grad or self.gamma.requires_grad or self.beta.requires_grad, device=x.device)
        def _backward():
            if self.x.requires_grad:
                N = x.data.shape[0]
                x_hat = self.x_norm
                var = self.running_var if not self.training else x.data.var(axis=0)
                std = np.sqrt(var + self.eps)
                d_x_hat = out.grad * self.gamma.data
                d_var = np.sum(d_x_hat * (x.data - mean), axis=0) * -0.5 / (var + self.eps) ** 1.5
                d_mean = np.sum(d_x_hat * -1 / std, axis=0) + d_var * np.mean(-2 * (x.data - mean), axis=0)
                self.x.grad = d_x_hat / std + d_var * 2 * (x.data - mean) / N + d_mean / N
            if self.gamma.requires_grad:
                self.gamma.grad = np.sum(out.grad * self.x_norm, axis=0)
            if self.beta.requires_grad:
                self.beta.grad = out.grad.sum(axis=0)
        out._backward = _backward
        out._prev = {self.gamma, self.beta, x}
        return out

class Flatten(Module):
    """Flatten layer: Reshapes input to (batch, -1)."""
    def forward(self, x):
        x.data = x.data.reshape(x.data.shape[0], -1)
        return x

# ---------------- Activations ----------------
class ReLU(Module):
    """ReLU activation: f(x) = max(0, x)."""
    def forward(self, x):
        data = np.maximum(0, x.data)
        out = Tensor(data, requires_grad=x.requires_grad, device=x.device)
        def _backward():
            if x.requires_grad:
                x.grad = (x.grad if x.grad is not None else 0) + out.grad * (x.data > 0)
        out._backward = _backward
        out._prev = {x}
        return out

class LeakyReLU(Module):
    """LeakyReLU activation: f(x) = x if x > 0 else alpha * x."""
    def __init__(self, alpha=0.01):
        self.alpha = alpha

    def forward(self, x):
        data = np.where(x.data > 0, x.data, self.alpha * x.data)
        out = Tensor(data, requires_grad=x.requires_grad, device=x.device)
        def _backward():
            if x.requires_grad:
                x.grad = (x.grad if x.grad is not None else 0) + out.grad * np.where(x.data > 0, 1, self.alpha)
        out._backward = _backward
        out._prev = {x}
        return out

class Sigmoid(Module):
    """Sigmoid activation: f(x) = 1 / (1 + exp(-x))."""
    def forward(self, x):
        s = 1 / (1 + np.exp(-x.data))
        out = Tensor(s, requires_grad=x.requires_grad, device=x.device)
        def _backward():
            if x.requires_grad:
                x.grad = (x.grad if x.grad is not None else 0) + out.grad * s * (1 - s)
        out._backward = _backward
        out._prev = {x}
        return out

class Tanh(Module):
    """Tanh activation: f(x) = tanh(x)."""
    def forward(self, x):
        t = np.tanh(x.data)
        out = Tensor(t, requires_grad=x.requires_grad, device=x.device)
        def _backward():
            if x.requires_grad:
                x.grad = (x.grad if x.grad is not None else 0) + out.grad * (1 - t**2)
        out._backward = _backward
        out._prev = {x}
        return out

# ---------------- Losses ----------------
def mse(pred, target):
    """Mean Squared Error loss."""
    diff = pred.data - target.data
    loss_val = (diff**2).mean()
    out = Tensor(loss_val, requires_grad=True, device=pred.device)
    def _backward():
        if pred.requires_grad:
            pred.grad = 2 * diff / diff.size
    out._backward = _backward
    out._prev = {pred}
    return out

def l1_loss(pred, target):
    """L1 Loss (Mean Absolute Error)."""
    diff = np.abs(pred.data - target.data)
    loss_val = diff.mean()
    out = Tensor(loss_val, requires_grad=True, device=pred.device)
    def _backward():
        if pred.requires_grad:
            pred.grad = np.sign(pred.data - target.data) / diff.size
    out._backward = _backward
    out._prev = {pred}
    return out

def cross_entropy(pred, target):
    """Cross Entropy Loss."""
    eps = 1e-12
    p = np.clip(pred.data, eps, 1-eps)
    loss_val = -np.sum(target.data * np.log(p)) / p.shape[0]
    out = Tensor(loss_val, requires_grad=True, device=pred.device)
    def _backward():
        if pred.requires_grad:
            pred.grad = (p - target.data) / p.shape[0]
    out._backward = _backward
    out._prev = {pred}
    return out

# ---------------- Optimizers ----------------
class SGD:
    """Stochastic Gradient Descent optimizer."""
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
    """Adam optimizer with weight decay."""
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0):
        self.params = params
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = [np.zeros_like(p.data) for p in params]
        self.v = [np.zeros_like(p.data) for p in params]
        self.t = 0

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad + self.weight_decay * p.data
            self.m[i] = self.betas[0] * self.m[i] + (1 - self.betas[0]) * g
            self.v[i] = self.betas[1] * self.v[i] + (1 - self.betas[1]) * (g**2)
            m_hat = self.m[i] / (1 - self.betas[0]**self.t)
            v_hat = self.v[i] / (1 - self.betas[1]**self.t)
            p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)

    def zero_grad(self):
        for p in self.params:
            p.grad = None

# ---------------- DataLoader ----------------
class DataLoader:
    """Simple DataLoader for batch processing."""
    def __init__(self, X, Y, batch_size=32, shuffle=True):
        self.X = X
        self.Y = Y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(X.data.shape[0])

    def __iter__(self):
        if self.shuffle:
            np.random.shuffle(self.indices)
        for start in range(0, len(self.indices), self.batch_size):
            batch_idx = self.indices[start:start + self.batch_size]
            yield Tensor(self.X.data[batch_idx], requires_grad=True, device=self.X.device), Tensor(self.Y.data[batch_idx], device=self.X.device)

    def __len__(self):
        return (len(self.indices) + self.batch_size - 1) // self.batch_size

# ---------------- Unit Tests ----------------
class TestMiniTorch(unittest.TestCase):
    def test_tensor_add(self):
        a = Tensor([1, 2, 3], requires_grad=True)
        b = Tensor([4, 5, 6], requires_grad=True)
        c = a + b
        c.backward()
        self.assertTrue(np.allclose(c.data, [5, 7, 9]))
        self.assertTrue(np.allclose(a.grad, [1, 1, 1]))
        self.assertTrue(np.allclose(b.grad, [1, 1, 1]))

    def test_linear(self):
        x = Tensor(np.ones((2, 3)), requires_grad=True)
        layer = Linear(3, 2)
        out = layer(x)
        out.backward(np.ones_like(out.data))
        self.assertEqual(out.data.shape, (2, 2))
        self.assertIsNotNone(layer.W.grad)
        self.assertIsNotNone(layer.b.grad)

    def test_l1_loss(self):
        pred = Tensor([1, 2, 3], requires_grad=True)
        target = Tensor([2, 2, 2])
        loss = l1_loss(pred, target)
        loss.backward()
        self.assertTrue(np.allclose(loss.data, 0.66666667))
        self.assertTrue(np.allclose(pred.grad, [-1/3, 0, 1/3]))

# ---------------- Demo / Test ----------------
if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False)

    # Dataset (linear y = 2x + 1 + noise)
    X_data = np.linspace(-10, 10, 200).reshape(-1, 1).astype(np.float32)
    Y_data = 2 * X_data + 1 + np.random.randn(*X_data.shape).astype(np.float32) * 0.5

    X = Tensor(X_data, requires_grad=True)
    Y = Tensor(Y_data)

    # Model: Linear -> BatchNorm -> ReLU -> Linear -> BatchNorm -> ReLU -> Linear -> BatchNorm -> ReLU -> Linear
    model = Sequential(
        Linear(1, 42),      # 84 parameters
        BatchNorm1D(42),    # 84 parameters
        ReLU(),             # 0 parameters
        Linear(42, 42),     # 1806 parameters
        BatchNorm1D(42),    # 84 parameters
        ReLU(),             # 0 parameters
        Linear(42, 21),     # 903 parameters
        BatchNorm1D(21),    # 42 parameters
        ReLU(),             # 0 parameters
        Linear(21, 1)       # 22 parameters
    )  # Total: 3025 parameters

    # Optimizer with adjusted learning rate
    optimizer = Adam(model.parameters(), lr=0.001, weight_decay=0.001)

    # DataLoader
    data_loader = DataLoader(X, Y, batch_size=32)

    # Training loop with debugging
    epochs = 1000
    for epoch in range(epochs):
        total_loss = 0
        for x_batch, y_batch in data_loader:
            pred = model(x_batch)
            loss = mse(pred, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.data
        if epoch % 50 == 0:
            print(f"Epoch {epoch:03d} | Loss = {total_loss / len(data_loader):.6f}")
            # Debug: Print gradient norm for first layer
            if model.layers[0].W.grad is not None:
                grad_norm = np.linalg.norm(model.layers[0].W.grad)
                print(f"Gradient norm (first layer W): {grad_norm:.6f}")

    # Test with new data
    model.training = False  # Set to eval mode for BatchNorm
    X_test = Tensor([[12.0], [15.0], [20.0]])
    Y_test = model(X_test)
    print("Predictions for input [12, 15, 20]:", Y_test.data)

    # Verify total parameters
    total_params = sum(np.prod(p.data.shape) for p in model.parameters())
    print(f"Total trainable parameters: {total_params}")

