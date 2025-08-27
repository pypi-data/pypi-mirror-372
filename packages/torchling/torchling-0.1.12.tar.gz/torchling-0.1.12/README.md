# torchling

A minimal neural network library. `torchling` is a work in progress.

## Installation
```bash
pip install torchling
```

## Example: Boston Housing Regression
```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from torchling.models import Sequential
from torchling.layers import Linear, Tanh
from torchling.losses import MSE
from torchling.optimisers import SGD


def load_dataset():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/housing/housing.data"
    df = pd.read_csv(url, sep=r'\s+')
    X = df.iloc[:, :-1].values.astype(np.float64)
    Y = df.iloc[:, -1].values.astype(np.float64)
    return X, Y


def normalize(X, Y):
    scaler_X = StandardScaler()
    scaler_Y = StandardScaler()
    X_norm = scaler_X.fit_transform(X)
    Y_norm = scaler_Y.fit_transform(Y.reshape(-1, 1)).flatten()
    return X_norm, Y_norm, scaler_X, scaler_Y


def denormalize(scaler, arr):
    return scaler.inverse_transform(np.array(arr).reshape(-1, 1)).flatten()


X, Y = load_dataset()
X, Y, _, Y_metadata = normalize(X, Y)

X_TRAIN, Y_TRAIN = X[1:], Y[1:]
X_TEST, Y_TEST = X[:1], Y[0]

epochs = 3000
lr = 0.6
input_size = X_TRAIN.shape[1]

model = Sequential(
    Linear(50, input_size=input_size),
    Tanh(),
    Linear(50),
    Tanh(),
    Linear(1),
)

optimizer = SGD(alpha=lr)
loss = MSE()
model.train(X_TRAIN, Y_TRAIN, optimizer, loss, epochs=epochs, print_every=250)

pred = model.predict(X_TEST)
print(f"Prediction - {denormalize(Y_metadata, pred)} | Actual - {denormalize(Y_metadata, [Y_TEST])}")
```

## License
MIT