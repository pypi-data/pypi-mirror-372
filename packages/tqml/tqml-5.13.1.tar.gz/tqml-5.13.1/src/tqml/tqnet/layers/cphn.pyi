from _typeshed import Incomplete
from tqml.tqnet._base import CertainLayer as CertainLayer

class CPHN(CertainLayer):
    quantum: Incomplete
    classical: Incomplete
    last: Incomplete
    def __init__(self, quantum_part: CertainLayer, hidden_dim: list[int]) -> None: ...
    def forward(self, x): ...
    def draw_circuit(self) -> None: ...
