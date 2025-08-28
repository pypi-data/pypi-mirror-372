from .both import BothLayer as BothLayer
from .both_both import BothBothLayer as BothBothLayer
from .both_parallel import BothParallelLayer as BothParallelLayer
from .both_sequential import BothSequentialLayer as BothSequentialLayer
from .depth import DepthLayer as DepthLayer
from .depth_both import DepthBothLayer as DepthBothLayer
from .depth_parallel import DepthParallelLayer as DepthParallelLayer
from .depth_sequential import DepthSequentialLayer as DepthSequentialLayer
from .width import WidthLayer as WidthLayer
from .width_both import WidthBothLayer as WidthBothLayer
from .width_parallel import WidthParallelLayer as WidthParallelLayer
from .width_sequential import WidthSequentialLayer as WidthSequentialLayer

def ReturnLayer(in_features, encoding: str = 'both', reuploading: str = 'None', reuploading_mode: str = 'linear', reuploading_order: str = 'repeating', n_reuploadings: int = 1, encoding_size: int = 4, n_reuploadings_depth: int = 1, n_reuploadings_width: int = 1, reuploading_mode_depth: str = 'linear', reuploading_mode_width: str = 'linear', reuploading_order_depth: str = 'repeating', reuploading_order_width: str = 'repeating', depth: int = 1, measurement_mode: str = 'None', rotation: str = 'Z', entangling: str = 'basic', measure: str = 'Y', diff_method: str = 'adjoint', qubit_type: str = 'lightning.qubit', interface: str = 'torch', learn_frequency: bool = False, ranges: str = 'default'): ...
