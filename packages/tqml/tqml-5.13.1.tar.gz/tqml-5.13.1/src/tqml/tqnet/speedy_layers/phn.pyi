from ._base import SpeedyLayer as SpeedyLayer
from .qdi import SpeedyQDI as SpeedyQDI
from _typeshed import Incomplete

class SpeedyPHN(SpeedyLayer):
    hidden_dim: Incomplete
    from_classic: Incomplete
    quantum: Incomplete
    out_features: Incomplete
    weights: Incomplete
    embedding_layers: Incomplete
    classical: Incomplete
    last: Incomplete
    def __init__(self, in_features, n_qubits, hidden_dim, depth: int = 1, from_classic: Incomplete | None = None, rotation: str = 'Z', entangling: str = 'strong', measure: str = 'Y', device: Incomplete | None = None) -> None: ...
    def forward(self, x): ...
