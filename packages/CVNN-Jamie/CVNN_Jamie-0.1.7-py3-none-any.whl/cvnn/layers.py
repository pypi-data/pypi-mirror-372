import numpy as np

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
        if weight_init is None:
            # Default: complex normal
            self.W = np.random.randn(input_dim, output_dim) + 1j * np.random.randn(input_dim, output_dim)
        else:
            self.W = weight_init((input_dim, output_dim))
        if bias_init is None:
            self.b = np.zeros((1, output_dim), dtype=np.complex128)
        else:
            self.b = bias_init((1, output_dim))
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
