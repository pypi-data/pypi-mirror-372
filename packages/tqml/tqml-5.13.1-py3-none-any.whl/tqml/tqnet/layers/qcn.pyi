from .vq import VQ as VQ
from _typeshed import Incomplete
from torch import nn

class QCN(nn.Module):
    kernel_size: Incomplete
    n_qubits: Incomplete
    depth: Incomplete
    qlayer: Incomplete
    device: Incomplete
    stride: Incomplete
    padding: Incomplete
    out_channels: Incomplete
    in_channels: Incomplete
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding, depth, device) -> None: ...
    def forward(self, images): ...
