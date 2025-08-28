from tqml.tqnet.operations import ExponentialEmbedding as ExponentialEmbedding
from tqml.tqnet.speedy_layers import SpeedyEFQ as SpeedyEFQ, SpeedyPQN as SpeedyPQN, SpeedyQDI as SpeedyQDI

def fisher_analyze(layer, num_samples: int = 10, ev_samples: int = 10, trainability_prob_boundary: float = 0.1, min_grad_value: float = 0.0001, trainability: bool = True, redundancy: bool = True, overparameterization: bool = True, save: bool = True, model_name: str = 'model'): ...
