from _typeshed import Incomplete
from pennylane.operation import AnyWires, Operation

class ExponentialEmbedding(Operation):
    ROT: Incomplete
    num_wires = AnyWires
    grad_method: Incomplete
    def __init__(self, features, wires, rotation: str = 'X', id: Incomplete | None = None) -> None: ...
    @property
    def num_params(self): ...
    @property
    def ndim_params(self): ...
    @staticmethod
    def compute_decomposition(features, wires, rotation): ...
