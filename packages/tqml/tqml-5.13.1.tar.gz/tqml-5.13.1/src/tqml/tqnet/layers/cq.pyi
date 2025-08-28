from _typeshed import Incomplete
from tqml.tqnet._base import CertainLayer as CertainLayer

class CQ(CertainLayer):
    diff_method: Incomplete
    qubit_type: Incomplete
    n_qubits: Incomplete
    weight_shapes: Incomplete
    dev: Incomplete
    circuit: Incomplete
    qnode: Incomplete
    weights: Incomplete
    def __init__(self, in_features: int, circuit, n_qubits: int, weight_shapes: tuple, qubit_type: str = 'lightning.qubit', diff_method: str = 'adjoint') -> None: ...
    def extra_repr(self) -> str: ...
    def forward(self, x): ...
    def draw_circuit(self) -> None: ...
