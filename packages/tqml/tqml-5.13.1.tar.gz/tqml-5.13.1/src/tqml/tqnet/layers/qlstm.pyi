from .qdi import QDI as QDI
from _typeshed import Incomplete
from torch import nn

class QLSTM(nn.Module):
    n_inputs: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    n_qubits: Incomplete
    depth: Incomplete
    measurement_mode: Incomplete
    rotation: Incomplete
    entangling: Incomplete
    measure: Incomplete
    diff_method: Incomplete
    qubit_type: Incomplete
    interface: Incomplete
    learn_frequency: Incomplete
    ranges: Incomplete
    embedding_layers: Incomplete
    batch_first: Incomplete
    bidirectional: Incomplete
    inversward: Incomplete
    inputs_dim: Incomplete
    VQC: Incomplete
    W_h: Incomplete
    W_x: Incomplete
    clayer_out: Incomplete
    directward_layer: Incomplete
    inversward_layer: Incomplete
    def __init__(self, input_size, hidden_size, n_qubits: int = 4, depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default', embedding_layers: int = 1, batch_first: bool = True, bidirectional: bool = False, inversward: bool = False) -> None: ...
    def forward(self, x, init_states: Incomplete | None = None): ...
    def draw_circuit(self) -> None: ...
