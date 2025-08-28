import torch
from torch import Tensor
from lt_utils.common import *


def normal(
    x: Tensor,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    eps: float = 1e-9,
) -> Tensor:
    """Normalizes tensor by mean and std."""

    if mean is None:
        mean = x.mean() * 0.5
    if std is None:
        std = x.std() * 0.5
    return (x - mean) / (std + eps)


def normal_minmax(x: Tensor, min_val: float = -1.0, max_val: float = 1.0) -> Tensor:
    """Scales tensor to [min_val, max_val] range."""
    x_min, x_max = x.min(), x.max()
    return (x - x_min) / (x_max - x_min + 1e-8) * (max_val - min_val) + min_val


def spectral_norm(x: Tensor, c: int = 1, eps: float = 1e-5) -> Tensor:
    return torch.log(torch.clamp(x, min=eps) * c)


def spectral_de_norm(x: Tensor, c: int = 1) -> Tensor:
    return torch.exp(x) / c
