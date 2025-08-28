from .qdi import QDI as QDI
from _typeshed import Incomplete
from torch import nn

class HLSTM(nn.Module):
    hidden_layers: Incomplete
    input_size: Incomplete
    hidden_size: Incomplete
    num_classes: Incomplete
    type: Incomplete
    lstm: Incomplete
    linear: Incomplete
    qlayer: Incomplete
    def __init__(self, num_classes, input_size, hidden_size, hidden_layers, nn_type: str = 'Classic', n_qubits: Incomplete | None = None, depth: int = 1, rotation: str = 'X', entangling: str = 'basic', measure: str = 'Z') -> None: ...
    def forward(self, y): ...
    def draw_circuit(self) -> None: ...
