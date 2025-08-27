Torchling is a minimal neural network library inspired by [PyTorch](https://github.com/pytorch/pytorch/tree/main), [Keras](https://github.com/keras-team/keras), and [micrograd](https://github.com/karpathy/micrograd), created for educational purposes. Vectorisation and N-dimensional array handling is powered by `NumPy`.

**`torchling` is a work in progress.**

## Installation
![PyPI](https://img.shields.io/pypi/v/torchling) ![License](https://img.shields.io/github/license/pbrut/torchling)
```bash
pip install torchling
```

## Initial Roadmap

- Reverse-mode automatic differentiation
    - ✅ Basic arithmetic operations
    - ✅ Matrix multiplication
- Layers 
    - ✅ Linear
    - [ ] Convolutional (2D)
    - [ ] Batch normalisation
    - ✅ Softmax
    - ✅ Relu
    - ✅ Sigmoid
    - ✅ Tanh
- Models
    - ✅ Sequential
    - [ ] Decoder-only Transformer
- Losses
    - ✅ Mean Squared Error
    - ✅ Categorical Cross-Entropy
- Optimisers
    - ✅ Stochastic gradient descent
    - [ ] Adam
- Weight initialisation
    - ✅ Drawn from normal distribution
    - [ ] Xavier/Glorot initialisation
- Regularisation
    - [ ] L1
    - [ ] L2
    - [ ] Dropout
- Miscellaneous
    - [ ] Skip connections

## Example
Simple example of training on the MNIST dataset. 
```python
import numpy as np
import tensorflow as tf

from torchling.models import Sequential
from torchling.layers import Linear, Relu, Softmax
from torchling.losses import CCE
from torchling.optimisers import SGD


def load_mnist():
    (X_train, Y_train), (X_test, Y_test) = tf.keras.datasets.mnist.load_data()

    # Preprocess data
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1]*X_train.shape[2]).astype(np.float64) / 255.0
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1]*X_test.shape[2]).astype(np.float64) / 255.0
    Y_train_one_hot = np.eye(10)[Y_train]

    return X_train, Y_train_one_hot, X_test, Y_test


X, Y, X_test, Y_test = load_mnist()

input_size = X.shape[1]
num_classes = Y.shape[1]
epochs = 30
batch_size = 256
layers = [256, 256]
print_every = 5
lr = 0.09

model = Sequential(
    Linear(layers[0], input_size=input_size),
    Relu(),
    Linear(layers[1]),
    Relu(),
    Linear(num_classes),
    Softmax(),
)

optimizer = SGD(alpha=lr)
loss = CCE()
model.train(X, Y, optimizer, loss, epochs=epochs, batch_size=batch_size, print_every=print_every)

probabilities = model.predict(X_test)
prediction = np.argmax(probabilities, axis=0)

accuracy = np.mean(prediction == Y_test)
print(f"Prediction accuracy: {accuracy * 100:.2f}%")
```

## License
MIT