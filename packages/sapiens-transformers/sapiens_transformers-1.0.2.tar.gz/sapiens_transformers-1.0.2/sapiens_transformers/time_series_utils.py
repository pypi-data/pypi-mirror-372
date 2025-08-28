"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch.distributions import (AffineTransform, Distribution, Independent, NegativeBinomial, Normal, StudentT, TransformedDistribution)
from typing import Callable, Dict, Optional, Tuple
from torch import nn
import torch
class AffineTransformed(TransformedDistribution):
    def __init__(self, base_distribution: Distribution, loc=None, scale=None, event_dim=0):
        self.scale = 1.0 if scale is None else scale
        self.loc = 0.0 if loc is None else loc
        super().__init__(base_distribution, [AffineTransform(loc=self.loc, scale=self.scale, event_dim=event_dim)])
    @property
    def mean(self): return self.base_dist.mean * self.scale + self.loc
    @property
    def variance(self): return self.base_dist.variance * self.scale**2
    @property
    def stddev(self): return self.variance.sqrt()
class ParameterProjection(nn.Module):
    def __init__(self, in_features: int, args_dim: Dict[str, int], domain_map: Callable[..., Tuple[torch.Tensor]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.args_dim = args_dim
        self.proj = nn.ModuleList([nn.Linear(in_features, dim) for dim in args_dim.values()])
        self.domain_map = domain_map
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor]:
        params_unbounded = [proj(x) for proj in self.proj]
        return self.domain_map(*params_unbounded)
class LambdaLayer(nn.Module):
    def __init__(self, function):
        super().__init__()
        self.function = function
    def forward(self, x, *args): return self.function(x, *args)
class DistributionOutput:
    distribution_class: type
    in_features: int
    args_dim: Dict[str, int]
    def __init__(self, dim: int = 1) -> None:
        self.dim = dim
        self.args_dim = {k: dim * self.args_dim[k] for k in self.args_dim}
    def _base_distribution(self, distr_args):
        if self.dim == 1: return self.distribution_class(*distr_args)
        else: return Independent(self.distribution_class(*distr_args), 1)
    def distribution(self, distr_args, loc: Optional[torch.Tensor] = None, scale: Optional[torch.Tensor] = None) -> Distribution:
        distr = self._base_distribution(distr_args)
        if loc is None and scale is None: return distr
        else: return AffineTransformed(distr, loc=loc, scale=scale, event_dim=self.event_dim)
    @property
    def event_shape(self) -> Tuple: return () if self.dim == 1 else (self.dim,)
    @property
    def event_dim(self) -> int: return len(self.event_shape)
    @property
    def value_in_support(self) -> float: return 0.0
    def get_parameter_projection(self, in_features: int) -> nn.Module: return ParameterProjection(in_features=in_features, args_dim=self.args_dim, domain_map=LambdaLayer(self.domain_map))
    def domain_map(self, *args: torch.Tensor): raise NotImplementedError()
    @staticmethod
    def squareplus(x: torch.Tensor) -> torch.Tensor: return (x + torch.sqrt(torch.square(x) + 4.0)) / 2.0
class StudentTOutput(DistributionOutput):
    args_dim: Dict[str, int] = {"df": 1, "loc": 1, "scale": 1}
    distribution_class: type = StudentT
    @classmethod
    def domain_map(cls, df: torch.Tensor, loc: torch.Tensor, scale: torch.Tensor):
        scale = cls.squareplus(scale).clamp_min(torch.finfo(scale.dtype).eps)
        df = 2.0 + cls.squareplus(df)
        return df.squeeze(-1), loc.squeeze(-1), scale.squeeze(-1)
class NormalOutput(DistributionOutput):
    args_dim: Dict[str, int] = {"loc": 1, "scale": 1}
    distribution_class: type = Normal
    @classmethod
    def domain_map(cls, loc: torch.Tensor, scale: torch.Tensor):
        scale = cls.squareplus(scale).clamp_min(torch.finfo(scale.dtype).eps)
        return loc.squeeze(-1), scale.squeeze(-1)
class NegativeBinomialOutput(DistributionOutput):
    args_dim: Dict[str, int] = {"total_count": 1, "logits": 1}
    distribution_class: type = NegativeBinomial
    @classmethod
    def domain_map(cls, total_count: torch.Tensor, logits: torch.Tensor):
        total_count = cls.squareplus(total_count)
        return total_count.squeeze(-1), logits.squeeze(-1)
    def _base_distribution(self, distr_args) -> Distribution:
        total_count, logits = distr_args
        if self.dim == 1: return self.distribution_class(total_count=total_count, logits=logits)
        else: return Independent(self.distribution_class(total_count=total_count, logits=logits), 1)
    def distribution(self, distr_args, loc: Optional[torch.Tensor] = None, scale: Optional[torch.Tensor] = None) -> Distribution:
        total_count, logits = distr_args
        if scale is not None: logits += scale.log()
        return self._base_distribution((total_count, logits))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
