# TQml

![python](https://img.shields.io/badge/python-%5E3.9.0-blue)
![torch](https://img.shields.io/badge/torch-%5E2.0.0-blue)

This Python module provides essential quantum tools for building and integrating hybrid quantum neural networks, including quantum circuit simulations, parameterized gates, and custom quantum layers compatible with popular ML frameworks. It simplifies the development of quantum-classical models for advanced machine learning tasks.


## About TQml

![png](https://storage.googleapis.com/test-bucket-18021720/pipeline.png)

TQml is library designed for developers in quantum machine learning, as well as beginers in the field. This library includes several modules, each of which is responsible for a different stage of model training. By working together, these modules enable users to build quantum or hybrid quantum-classical models from scratch, resulting in highly accurate solutions while saving time on code development.

TQml includes the following modules:

- **TQnet**: Creating quantum and classical layers with a unified interface.

- **TQcirc**: Analysis of quantum circuits, including the calculation of Fisher information, ZX calculus and other metrics.

- **TQtune**: Optimization of hyperparameters of models to maximize their effectiveness.

- **TQbench**: Training and estimation of the operating time of models on quantum computers or simulators.

## Installation

1) Create new `conda` environment to prevent conflicts with previous versions of your packages
    ```bash
    conda create -n tqml python=3.9
    conda activate tqml
    ```

2) Use pip or poetry to install the package (optionally with a specific version).
   ```bash
   pip install tqml==5.9.1
   ```

   **NOTE**: This currently only includes any package versions starting from version 5.9.1

3) You need to provide a valid license key via the env variable `TQML_LICENSE_KEY`. To retrieve your (previously requested) license keys please go to [TQ License portal](https://terraquantum.io/licenses).

   **NOTE**: You need to be assigned a license key by the TQ team to use this package. Please get in touch with [support@terraquantum.swiss](mailto:support@terraquantum.swiss).

4) You can now use the package as usual.

## Documentation

You can find documentation and API reference for this package
[here](https://tqml-docs.terraquantum.io/).

## Usage

```python
from tqml.tqnet.layers import QDI
import torch

layer = QDI(
   in_features=20,
   n_qubits=4,
   depth=4,
   entangling='basic',
   rotation='Y',
   measurement_mode='single',
   measure='Y'
)

inputs = torch.rand((10, 20))
outputs = layer(inputs)

assert outputs.shape == (10, 1)
```

## License

`tqml` was created by Terra Quantum. For a full and updated view on the license, please take a look [here](https://terraquantum.io/content/legal/eula-tq42-tqml/).
