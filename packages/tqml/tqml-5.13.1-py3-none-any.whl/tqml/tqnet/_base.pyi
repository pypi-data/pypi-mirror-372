import abc
from _typeshed import Incomplete
from abc import ABCMeta, abstractmethod
from torch.nn import Module

class CertainLayer(Module, metaclass=ABCMeta):
    in_features: Incomplete
    out_features: Incomplete
    def __init__(self, in_features, out_features) -> None: ...
    @abstractmethod
    def draw_circuit(self): ...
    @abstractmethod
    def forward(self, x): ...

class QuantumLayer(CertainLayer, metaclass=abc.ABCMeta):
    weights: Incomplete
    n_qubits: Incomplete
    depth: Incomplete
    __constants__: Incomplete
    entanglers: Incomplete
    rotations: Incomplete
    rotators: Incomplete
    measurement_mods: Incomplete
    measurers: Incomplete
    diff_methods: Incomplete
    qubit_types: Incomplete
    interfaces: Incomplete
    ranges_list: Incomplete
    measurement_mode: Incomplete
    rotation: Incomplete
    rotation_op: Incomplete
    entangling: Incomplete
    measurement: Incomplete
    measurement_n: Incomplete
    diff_method: Incomplete
    qubit_type: Incomplete
    interface: Incomplete
    learn_frequency: Incomplete
    ranges: Incomplete
    dev: Incomplete
    def __init__(self, in_features, out_features, n_qubits, depth, measurement_mode, rotation, entangling, measure, diff_method, qubit_type, interface, learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    @abstractmethod
    def draw_circuit(self): ...
    @abstractmethod
    def forward(self, x): ...
    def reset_parameters(self) -> None: ...
    def get_hyperparameters(self): ...
