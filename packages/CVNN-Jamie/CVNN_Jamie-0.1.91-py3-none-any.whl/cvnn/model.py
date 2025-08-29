import numpy as np

class Sequential:
    """
    Simple sequential model for stacking layers and activations.
    Supports training with mean squared error and SGD for 1-layer networks.
    """
    def __init__(self, layers):
        self.layers = layers

    def summary(self):
        for i, layer in enumerate(self.layers):
            if hasattr(layer, 'W'):
                print(f"Layer {i}: {layer.__class__.__name__}, Weights: {layer.W.shape}, Biases: {layer.b.shape}")
            else:
                print(f"Layer {i}: {layer.__class__.__name__}")
                if hasattr(layer, 'b'):
                    print(f"  Biases: {layer.b.shape}")

    def forward(self, x, store_cache=False):
        activations = []
        pre_activations = []
        for layer in self.layers:
            if hasattr(layer, 'forward'):
                x = layer.forward(x)
                pre_activations.append(x)
                activations.append(None)
            elif isinstance(layer, tuple) and len(layer) == 2:
                # (activation, derivative)
                pre_activations.append(x)
                x = layer[0](x)
                activations.append(layer)
            else:
                # Activation function
                pre_activations.append(x)
                x = layer(x)
                activations.append(layer)
        if store_cache:
            self._cache = {'pre_activations': pre_activations, 'activations': activations}
        return x

    def predict(self, x):
        return self.forward(x)

    def fit(self, x, y, epochs=100, lr=0.01, batch_size=None, return_history=False, track=None, verbose=False):
        """
        Trains the model using full backpropagation.
        Args:
            x: input data
            y: target data
            epochs: number of epochs
            lr: learning rate
            batch_size: number of samples per batch (None for full-batch)
            return_history: if True, returns a dict with loss and optionally tracked variables
            track: list of variables to track, e.g. ['predictions', 'weights']
        Returns:
            None or dict with 'loss', 'predictions', 'weights' (if requested)
        """
        import cvnn.activations as act
        loss_history = []
        pred_history = []
        weights_history = []
        biases_history = []
        n_samples = x.shape[0]
        for epoch in range(epochs):
            # Shuffle indices for each epoch
            indices = np.arange(n_samples)
            np.random.shuffle(indices)
            batch_losses = []
            for start in range(0, n_samples, batch_size or n_samples):
                end = start + (batch_size or n_samples)
                batch_idx = indices[start:end]
                xb = x[batch_idx]
                yb = y[batch_idx]
                out = self.forward(xb, store_cache=True)
                loss = np.mean(np.abs(out - yb) ** 2)
                batch_losses.append(loss)
                grad = 2 * (out - yb) / yb.size
                pre_acts = self._cache['pre_activations']
                activs = self._cache['activations']
                for i in reversed(range(len(self.layers))):
                    layer = self.layers[i]
                    pre_act = pre_acts[i]
                    act_layer = activs[i]
                    fully_complex = hasattr(layer, 'W') and layer.W.dtype == np.complex128
                    if hasattr(layer, 'backward'):
                        grad = layer.backward(grad, lr=lr)
                    elif isinstance(act_layer, tuple) and len(act_layer) == 2:
                        # Use custom derivative
                        grad = act_layer[1](pre_act, grad)
                    else:
                        # Activation function: use corresponding backward
                        if hasattr(layer, '__name__'):
                            lname = layer.__name__
                        elif isinstance(layer, tuple) and hasattr(layer[0], '__name__'):
                            lname = layer[0].__name__
                        else:
                            lname = str(layer)
                        if lname == 'complex_relu':
                            grad = act.complex_relu_backward(pre_act, grad)
                        elif lname == 'complex_sigmoid':
                            grad = act.complex_sigmoid_backward(pre_act, grad, fully_complex=fully_complex)
                        elif lname == 'complex_tanh':
                            grad = act.complex_tanh_backward(pre_act, grad, fully_complex=fully_complex)
                        else:
                            raise NotImplementedError(f"No backward for activation {lname}")
            epoch_loss = np.mean(batch_losses)
            loss_history.append(epoch_loss)
            if track is not None:
                if 'predictions' in track:
                    pred_history.append(self.forward(x).copy())
                if 'weights' in track:
                    weights_history.append([layer.W.copy() for layer in self.layers if hasattr(layer, 'W')])
                if 'biases' in track:
                    biases_history.append([layer.b.copy() for layer in self.layers if hasattr(layer, 'b')])
            if epoch % 10 == 0 and verbose:
                print(f"Epoch {epoch}, Loss: {epoch_loss}")
        if return_history:
            history = {'loss': np.array(loss_history)}
            if track is not None:
                if 'predictions' in track:
                    history['predictions'] = pred_history
                if 'weights' in track:
                    history['weights'] = weights_history
                if 'biases' in track:
                    history['biases'] = biases_history
            return history
