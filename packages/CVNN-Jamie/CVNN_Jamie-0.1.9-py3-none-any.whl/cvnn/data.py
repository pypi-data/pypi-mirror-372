import numpy as np

def generate_xor(n_samples=100, complex_data=False, seed=None):
    """
    Generate a real or complex XOR dataset without noise.

    Args:
        n_samples (int): Number of samples to generate (should be even).
        complex_data (bool): If True, generate complex-valued features.
        seed (int or None): Random seed for reproducibility.

    Returns:
        X (np.ndarray): Features, shape (n_samples, 2)
        y (np.ndarray): Labels, shape (n_samples,)
    """
    if seed is not None:
        np.random.seed(seed)
    n_samples = n_samples if n_samples % 4 == 0 else n_samples + (4 - n_samples % 4)
    if complex_data:
        # Four XOR corners in complex: (+1+1j), (+1-1j), (-1+1j), (-1-1j)
        corners = np.array([
            [1+1j],
            [-1+1j],
            [1-1j],
            [-1-1j]
        ])
        X = np.vstack([np.tile(c, (n_samples // 4, 1)) for c in corners])
        # XOR label: 1 if real and imag have different signs, else 0, for each feature
        y = np.logical_xor(X.real > 0, X.imag > 0).astype(int)
        # If X has more than one feature, reduce to a single label per sample (e.g., XOR across features)
        if y.shape[1] > 1:
            y = np.logical_xor.reduce(y, axis=1).astype(int)
    else:
        X = np.vstack([
            np.tile([0, 0], (n_samples // 4, 1)),
            np.tile([0, 1], (n_samples // 4, 1)),
            np.tile([1, 0], (n_samples // 4, 1)),
            np.tile([1, 1], (n_samples // 4, 1)),
        ])
        y = np.logical_xor(X[:, 0], X[:, 1]).astype(int)
    idx = np.random.permutation(n_samples)
    return X[idx], y[idx]

# # Example usage:
# if __name__ == "__main__":
#     X_real, y_real = generate_xor(n_samples=100, complex_data=False, seed=42)
#     X_complex, y_complex = generate_xor(n_samples=100, complex_data=True, seed=42)
#     print("Real XOR X shape:", X_real.shape, "y shape:", y_real.shape)
#     print("Complex XOR X dtype:", X_complex.dtype)