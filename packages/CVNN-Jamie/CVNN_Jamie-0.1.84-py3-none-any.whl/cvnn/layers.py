
import numpy as np
from . import initialisations

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
