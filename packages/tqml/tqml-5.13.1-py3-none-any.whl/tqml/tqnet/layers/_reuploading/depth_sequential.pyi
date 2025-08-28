from _typeshed import Incomplete
from tqml.tqnet._base import QuantumLayer as QuantumLayer

class DepthSequentialLayer(QuantumLayer):
    reuploading_mode: Incomplete
    reuploading_order: Incomplete
    n_reuploadings: Incomplete
    n_qubits: int
    weights: Incomplete
    encoding_weights: Incomplete
    trainable_frequency: Incomplete
    qnode: Incomplete
    def __init__(self, in_features, reuploading_mode: str = 'linear', reuploading_order: str = 'repeating', n_reuploadings: int = 1, depth: int = 1, rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def extra_repr(self) -> str: ...
    def circuit(self, weights, x: Incomplete | None = None, measurement_basis: Incomplete | None = None): ...
    def draw_circuit(self, x: Incomplete | None = None) -> None: ...
    def forward(self, x): ...
