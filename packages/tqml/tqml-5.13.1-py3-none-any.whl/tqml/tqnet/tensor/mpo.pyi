import torch
import torch.nn as nn
from ._utils import compute_param_len as compute_param_len, get_mps as get_mps, measure_z_all_qubits as measure_z_all_qubits
from _typeshed import Incomplete

class MPOLayer(nn.Module):
    box_size: Incomplete
    box_depth: Incomplete
    box_shift: Incomplete
    n_qubits: Incomplete
    params: Incomplete
    def __init__(self, box_size: int, box_depth: int, box_shift: int, n_qubits: int, param_requires_grad: bool = True) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
