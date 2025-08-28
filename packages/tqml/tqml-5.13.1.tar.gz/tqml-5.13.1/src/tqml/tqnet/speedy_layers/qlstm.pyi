from .qdi import SpeedyQDI as SpeedyQDI
from _typeshed import Incomplete
from torch import nn

class SpeedyQLSTM(nn.Module):
    n_inputs: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    n_qubits: Incomplete
    depth: Incomplete
    measurement_mode: Incomplete
    rotation: Incomplete
    entangling: Incomplete
    measure: Incomplete
    embedding_layers: Incomplete
    batch_first: Incomplete
    bidirectional: Incomplete
    inversward: Incomplete
    device: Incomplete
    inputs_dim: Incomplete
    VQC: Incomplete
    clayer_out: Incomplete
    W_h: Incomplete
    W_x: Incomplete
    directward_layer: Incomplete
    inversward_layer: Incomplete
    def __init__(self, input_size, hidden_size, n_qubits: int = 4, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', embedding_layers: int = 1, batch_first: bool = True, bidirectional: bool = False, inversward: bool = False, device: Incomplete | None = None) -> None: ...
    def forward(self, x, init_states: Incomplete | None = None): ...
