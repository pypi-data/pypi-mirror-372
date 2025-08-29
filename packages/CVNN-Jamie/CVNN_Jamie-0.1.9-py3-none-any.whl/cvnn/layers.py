import numpy as np
from . import initialisations, activations

class ComplexDense:
    """
    A fully connected complex-valued layer.
    Args:
        input_dim (int): Number of input features
        output_dim (int): Number of output features
        weight_init (callable): Initialisation function for weights
        bias_init (callable): Initialisation function for biases
    """
    def __init__(self, input_dim, output_dim, weight_init=None, bias_init=None):
        self.input_dim = input_dim
        self.output_dim = output_dim

        def resolve_init(init, shape):
            if init is None:
                return np.random.randn(*shape) + 1j * np.random.randn(*shape)
            if isinstance(init, str):
                # Try to get from initialisations module
                if hasattr(initialisations, init):
                    return getattr(initialisations, init)(shape)
                else:
                    raise ValueError(f"Unknown initialisation method: {init}")
            if callable(init):
                return init(shape)
            raise ValueError("weight_init and bias_init must be a callable or string name of an initialisation method.")

        self.W = resolve_init(weight_init, (input_dim, output_dim))
        self.b = resolve_init(bias_init, (1, output_dim))
        self.x_cache = None

    def forward(self, x):
        self.x_cache = x
        return x @ self.W + self.b

    def backward(self, grad_output, lr=0.01):
        # grad_output: gradient w.r.t. output of this layer
        x = self.x_cache
        dW = x.conj().T @ grad_output
        db = np.sum(grad_output, axis=0, keepdims=True)
        dx = grad_output @ self.W.conj().T
        # Update weights
        self.W -= lr * dW
        self.b -= lr * db
        return dx

class Sequential:
    def __init__(self, layers):
        self.layers = []
        for l in layers:
            # Allow string activations
            if isinstance(l, str) and hasattr(activations, l):
                act = getattr(activations, l)
                self.layers.append((act, getattr(activations, l + "_deriv", None)))
            elif isinstance(l, tuple) and len(l) == 2:
                self.layers.append(l)
            else:
                self.layers.append(l)

    def forward(self, x):
        self.cache = []
        for l in self.layers:
            if hasattr(l, "forward"):
                x = l.forward(x)
                self.cache.append(("layer", l))
            elif isinstance(l, tuple) and callable(l[0]):
                x = l[0](x)
                self.cache.append(("activation", l))
            else:
                raise ValueError("Unknown layer/activation type")
        return x

    def backward(self, grad, lr=0.01):
        for kind, l in reversed(self.cache):
            if kind == "activation":
                # l is (activation, derivative)
                if l[1] is not None:
                    grad = l[1](self.cache[self.cache.index((kind, l))-1][1].x_cache, grad)
                else:
                    raise ValueError("Activation missing derivative")
            else:
                grad = l.backward(grad, lr=lr)

    def fit(self, x, y, epochs=1000, lr=0.01, verbose=False):
        losses = []
        for epoch in range(epochs):
            out = self.forward(x)
            loss = np.mean(np.abs(out - y) ** 2)
            grad = 2 * (out - y) / y.shape[0]
            self.backward(grad, lr=lr)
            losses.append(loss)
            if verbose and (epoch % (epochs // 10) == 0 or epoch == epochs - 1):
                print(f"Epoch {epoch+1}/{epochs}, Loss: {loss:.4f}")
        return losses
