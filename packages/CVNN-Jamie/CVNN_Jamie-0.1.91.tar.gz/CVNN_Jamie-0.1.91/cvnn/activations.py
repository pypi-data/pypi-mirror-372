import numpy as np

# JAM activation: outputs 1 where im(sigmoid(z)) > 0, else 0
def jam(z):
    s = 1 / (1 + np.exp(-z))
    return (s.imag > 0).astype(np.float64)

# Derivative for jam: use sigmoid' (real part)
def jam_derivative(z, grad_output):
    s = 1 / (1 + np.exp(-z))
    ds = s * (1 - s)
    return grad_output * ds




def complex_relu(z):
    return np.maximum(z.real, 0) + 1j * np.maximum(z.imag, 0)

def complex_relu_backward(z, grad_output):
    grad_real = grad_output.real * (z.real > 0)
    grad_imag = grad_output.imag * (z.imag > 0)
    return grad_real + 1j * grad_imag

# Additional complex activation functions

# Separable (real/imag) sigmoid
def complex_sigmoid(z, fully_complex=False):
    if not fully_complex:
        s_real = 1 / (1 + np.exp(-z.real))
        s_imag = 1 / (1 + np.exp(-z.imag))
        return s_real + 1j * s_imag
    else:
        return 1 / (1 + np.exp(-z))

def complex_sigmoid_backward(z, grad_output, fully_complex=False):
    if not fully_complex:
        s_real = 1 / (1 + np.exp(-z.real))
        s_imag = 1 / (1 + np.exp(-z.imag))
        grad_real = grad_output.real * s_real * (1 - s_real)
        grad_imag = grad_output.imag * s_imag * (1 - s_imag)
        return grad_real + 1j * grad_imag
    else:
        s = 1 / (1 + np.exp(-z))
        return grad_output * s * (1 - s)


# Separable (real/imag) tanh
def complex_tanh(z, fully_complex=False):
    if not fully_complex:
        t_real = np.tanh(z.real)
        t_imag = np.tanh(z.imag)
        return t_real + 1j * t_imag
    else:
        return np.tanh(z)

def complex_tanh_backward(z, grad_output, fully_complex=False):
    if not fully_complex:
        t_real = np.tanh(z.real)
        t_imag = np.tanh(z.imag)
        grad_real = grad_output.real * (1 - t_real ** 2)
        grad_imag = grad_output.imag * (1 - t_imag ** 2)
        return grad_real + 1j * grad_imag
    else:
        t = np.tanh(z)
        return grad_output * (1 - t ** 2)


def modrelu(z, bias=0):
    # modReLU: relu on modulus, keep phase
    modulus = np.abs(z)
    phase = np.angle(z)
    return np.maximum(modulus + bias, 0) * np.exp(1j * phase)

# Initialisation methods
def complex_glorot_uniform(shape):
    # Glorot uniform for complex weights
    limit = np.sqrt(6 / np.sum(shape))
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_he_normal(shape):
    # He normal for complex weights
    stddev = np.sqrt(2 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag
