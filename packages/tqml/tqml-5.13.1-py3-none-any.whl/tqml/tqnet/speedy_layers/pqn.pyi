from ._base import SpeedyLayer as SpeedyLayer
from ._speedy_qml import rz_eigenvals as rz_eigenvals
from _typeshed import Incomplete
from tqml.tqnet.exceptions import DimensionException as DimensionException

class SpeedyPQN(SpeedyLayer):
    embedding_layers: Incomplete
    embed_rot: Incomplete
    entangler_forward: Incomplete
    weights: Incomplete
    out_features: Incomplete
    def __init__(self, in_features, n_qubits, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'strong', measure: str = 'Y', device: Incomplete | None = None) -> None: ...
    def forward(self, x): ...
    def extra_repr(self) -> str: ...
