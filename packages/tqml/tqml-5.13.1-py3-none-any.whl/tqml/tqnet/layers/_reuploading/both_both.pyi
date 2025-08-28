from _typeshed import Incomplete
from tqml.tqnet._base import QuantumLayer as QuantumLayer

class BothBothLayer(QuantumLayer):
    n_reuploadings_depth: Incomplete
    n_reuploadings_width: Incomplete
    reuploading_mode_depth: Incomplete
    reuploading_mode_width: Incomplete
    reuploading_order_depth: Incomplete
    reuploading_order_width: Incomplete
    encoding_size: Incomplete
    pad_len: Incomplete
    embedding_layers: Incomplete
    n_qubits: Incomplete
    encoding_weights_depth: Incomplete
    encoding_weights_width: Incomplete
    weights: Incomplete
    trainable_frequency: Incomplete
    qnode: Incomplete
    def __init__(self, in_features, n_reuploadings_depth: int = 1, n_reuploadings_width: int = 1, reuploading_mode_depth: str = 'linear', reuploading_mode_width: str = 'linear', reuploading_order_depth: str = 'repeating', reuploading_order_width: str = 'repeating', encoding_size: int = 4, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def extra_repr(self) -> str: ...
    def trainable_layer(self, weights, step: int = 0, id: int = 0) -> None: ...
    def A_depth_width(self, x, weights, encoding_weights_depth, encoding_weights_width, index) -> None: ...
    def circuit(self, weights, x: Incomplete | None = None, measurement_basis: Incomplete | None = None): ...
    def draw_circuit(self, x: Incomplete | None = None) -> None: ...
    def forward(self, x): ...
