import numpy as np

class Sequential:
    """
    Simple sequential model for stacking layers and activations.
    Supports training with mean squared error and SGD for 1-layer networks.
    """
    def __init__(self, layers):
        self.layers = layers

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

    def fit(self, x, y, epochs=100, lr=0.01, return_history=False, track=None, verbose = False):
        """
        Trains the model using full backpropagation.
        Args:
            x: input data
            y: target data
            epochs: number of epochs
            lr: learning rate
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
        for epoch in range(epochs):
            out = self.forward(x, store_cache=True)
            loss = np.mean(np.abs(out - y) ** 2)
            loss_history.append(loss)
            if track is not None:
                if 'predictions' in track:
                    pred_history.append(out.copy())
                if 'weights' in track:
                    weights_history.append([layer.W.copy() for layer in self.layers if hasattr(layer, 'W')])
                if 'biases' in track:
                    biases_history.append([layer.b.copy() for layer in self.layers if hasattr(layer, 'b')])
            grad = 2 * (out - y) / y.size
            pre_acts = self._cache['pre_activations']
            activs = self._cache['activations']
            for i in reversed(range(len(self.layers))):
                layer = self.layers[i]
                pre_act = pre_acts[i]
                act_layer = activs[i]
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
                        grad = act.complex_sigmoid_backward(pre_act, grad)
                    elif lname == 'complex_tanh':
                        grad = act.complex_tanh_backward(pre_act, grad)
                    else:
                        raise NotImplementedError(f"No backward for activation {lname}")
            if epoch % 10 == 0 and verbose:
                print(f"Epoch {epoch}, Loss: {loss}")
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
