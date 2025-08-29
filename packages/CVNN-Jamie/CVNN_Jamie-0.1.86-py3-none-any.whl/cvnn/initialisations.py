import numpy as np
string_inits = [
    "complex_zeros",
    "complex_ones",
    "complex_normal",
    "complex_glorot_uniform",
    "complex_he_normal",
    "jamie"
]
def jamie(shape):
    phases = np.random.choice([np.pi/4, 5*np.pi/4], size=shape)
    modulus = np.abs(np.random.normal(1.0, 0.1, size=shape))
    return modulus * np.exp(1j * phases)

def complex_zeros(shape):
    return np.zeros(shape, dtype=np.complex128)

def complex_ones(shape):
    return np.ones(shape, dtype=np.complex128)

def complex_normal(shape, mean=0.0, std=1.0):
    real = np.random.normal(mean, std, size=shape)
    imag = np.random.normal(mean, std, size=shape)
    return real + 1j * imag

def complex_glorot_uniform(shape):
    limit = np.sqrt(6 / np.sum(shape))
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_he_normal(shape):
    stddev = np.sqrt(2 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag

def complex_uniform(shape, low=-1.0, high=1.0):
    real = np.random.uniform(low, high, size=shape)
    imag = np.random.uniform(low, high, size=shape)
    return real + 1j * imag

def complex_lecun_normal(shape):
    stddev = np.sqrt(1 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag

def complex_lecun_uniform(shape):
    limit = np.sqrt(3 / shape[0])
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_rand_phase(shape, modulus=1.0):
    phases = np.random.uniform(0, 2 * np.pi, size=shape)
    return modulus * np.exp(1j * phases)