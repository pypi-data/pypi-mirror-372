from .qdi import QDI as QDI
from _typeshed import Incomplete
from tqml.tqnet._base import CertainLayer as CertainLayer

class PHN(CertainLayer):
    hidden_dim: Incomplete
    from_classic: Incomplete
    quantum: Incomplete
    out_features: Incomplete
    classical: Incomplete
    last: Incomplete
    def __init__(self, in_features, n_qubits, hidden_dim, depth: int = 1, from_classic: Incomplete | None = None, rotation: str = 'Z', entangling: str = 'strong', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def forward(self, x): ...
    def draw_circuit(self) -> None: ...
