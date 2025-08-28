import numpy as np

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
