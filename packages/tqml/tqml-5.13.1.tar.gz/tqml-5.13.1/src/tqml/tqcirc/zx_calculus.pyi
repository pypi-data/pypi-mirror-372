from _typeshed import Incomplete
from tqml.tqnet.layers import CQ as CQ, EFQ as EFQ, PQN as PQN, QDI as QDI, VQ as VQ

def get_zx_graph(layer, fullreduce: bool = False, feedback: bool = False, loss_check: bool = True, weights: Incomplete | None = None, input: Incomplete | None = None): ...

class VertexType:
    BOUNDARY: int
    Z: int
    X: int
    H_BOX: int

class EdgeType:
    SIMPLE: int
    HADAMARD: int
