from ._reuploading.layer_creation import ReturnLayer as ReturnLayer
from _typeshed import Incomplete
from torch.nn import Module

class ReuploadingQuantumLayer(Module):
    encoding: Incomplete
    reuploading: Incomplete
    reuploading_mode: Incomplete
    n_reuploadings: Incomplete
    encoding_size: Incomplete
    reuploading_order: Incomplete
    n_reuploadings_depth: Incomplete
    n_reuploadings_width: Incomplete
    reuploading_mode_depth: Incomplete
    reuploading_mode_width: Incomplete
    reuploading_order_depth: Incomplete
    reuploading_order_width: Incomplete
    layer: Incomplete
    def __init__(self, in_features, encoding: str = 'both', reuploading: str = 'None', reuploading_mode: str = 'linear', reuploading_order: str = 'repeating', n_reuploadings: int = 1, encoding_size: int = 4, n_reuploadings_depth: int = 1, n_reuploadings_width: int = 1, reuploading_mode_depth: str = 'linear', reuploading_mode_width: str = 'linear', reuploading_order_depth: str = 'repeating', reuploading_order_width: str = 'repeating', depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default') -> None: ...
    def extra_repr(self) -> str: ...
    def draw_circuit(self, x: Incomplete | None = None) -> None: ...
    def forward(self, x): ...
