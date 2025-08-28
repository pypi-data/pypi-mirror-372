from .pqn import PQN as PQN
from _typeshed import Incomplete
from tqml.tqnet._base import CertainLayer as CertainLayer

class VQ(CertainLayer):
    layer: Incomplete
    n_qubits: Incomplete
    depth: Incomplete
    measurement_mode: Incomplete
    qnode: Incomplete
    weights: Incomplete
    rotation: Incomplete
    entangling: Incomplete
    measurement_n: Incomplete
    diff_method: Incomplete
    qubit_type: Incomplete
    interface: Incomplete
    learn_frequency: Incomplete
    ranges: Incomplete
    trainable_frequency: Incomplete
    def __init__(self, in_features, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'strong', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def forward(self, x): ...
    def draw_circuit(self) -> None: ...
    def extra_repr(self) -> str: ...
    def get_quantum_tape(self, x, weights: Incomplete | None = None): ...
