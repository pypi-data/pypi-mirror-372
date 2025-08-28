from ._base import SpeedyLayer as SpeedyLayer
from ._speedy_qml import rz_eigenvals as rz_eigenvals
from _typeshed import Incomplete

class SpeedyQMR(SpeedyLayer):
    pad_len: Incomplete
    in_features_bb: Incomplete
    n_reuploadings_depth: Incomplete
    n_reuploadings_width: Incomplete
    reuploading_mode_depth: Incomplete
    reuploading_mode_width: Incomplete
    reuploading_order_depth: Incomplete
    reuploading_order_width: Incomplete
    encoding_size: Incomplete
    encoding_weights_depth: Incomplete
    encoding_weights_width: Incomplete
    embedding_layers: Incomplete
    embedding_bb: Incomplete
    n_qubits_bb: Incomplete
    embed_rot: Incomplete
    entangler_forward: Incomplete
    weights: Incomplete
    def __init__(self, in_features, n_reuploadings_depth: int = 1, n_reuploadings_width: int = 1, reuploading_mode_depth: str = 'linear', reuploading_mode_width: str = 'linear', reuploading_order_depth: str = 'repeating', reuploading_order_width: str = 'repeating', encoding_size: int = 4, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'strong', measure: str = 'Y', device: Incomplete | None = None) -> None: ...
    def A_depth_width(self, x, encoding_weights_depth, encoding_weights_width, index): ...
    def bb_preproc(self, x): ...
    def forward(self, x): ...
    def extra_repr(self) -> str: ...
