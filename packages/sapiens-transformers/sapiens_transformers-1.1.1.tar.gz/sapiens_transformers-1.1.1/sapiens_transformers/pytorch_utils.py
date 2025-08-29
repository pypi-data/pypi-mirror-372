from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing import Callable, List, Optional, Set, Tuple, Union
from safetensors.torch import storage_ptr, storage_size
from .utils import is_torch_xla_available, logging
from packaging import version
from torch import nn
import inspect
import torch
ALL_LAYERNORM_LAYERS = [nn.LayerNorm]
logger = logging.get_logger(__name__)
parsed_torch_version_base = version.parse(version.parse(torch.__version__).base_version)
is_torch_greater_or_equal_than_2_4 = parsed_torch_version_base >= version.parse("2.4")
is_torch_greater_or_equal_than_2_3 = parsed_torch_version_base >= version.parse("2.3")
is_torch_greater_or_equal_than_2_2 = parsed_torch_version_base >= version.parse("2.2")
is_torch_greater_or_equal_than_2_1 = parsed_torch_version_base >= version.parse("2.1")
is_torch_greater_or_equal_than_2_0 = parsed_torch_version_base >= version.parse("2.0")
is_torch_greater_or_equal_than_1_13 = parsed_torch_version_base >= version.parse("1.13")
is_torch_greater_or_equal_than_1_12 = parsed_torch_version_base >= version.parse("1.12")
def softmax_backward_data(parent, grad_output, output, dim, self):
    from torch import _softmax_backward_data
    return _softmax_backward_data(grad_output, output, parent.dim, self.dtype)
def prune_linear_layer(layer: nn.Linear, index: torch.LongTensor, dim: int = 0) -> nn.Linear:
    index = index.to(layer.weight.device)
    W = layer.weight.index_select(dim, index).clone().detach()
    if layer.bias is not None:
        if dim == 1: b = layer.bias.clone().detach()
        else: b = layer.bias[index].clone().detach()
    new_size = list(layer.weight.size())
    new_size[dim] = len(index)
    new_layer = nn.Linear(new_size[1], new_size[0], bias=layer.bias is not None).to(layer.weight.device)
    new_layer.weight.requires_grad = False
    new_layer.weight.copy_(W.contiguous())
    new_layer.weight.requires_grad = True
    if layer.bias is not None:
        new_layer.bias.requires_grad = False
        new_layer.bias.copy_(b.contiguous())
        new_layer.bias.requires_grad = True
    return new_layer
class Conv1D(nn.Module):
    def __init__(self, nf, nx):
        super().__init__()
        self.nf = nf
        self.nx = nx
        self.weight = nn.Parameter(torch.empty(nx, nf))
        self.bias = nn.Parameter(torch.zeros(nf))
        nn.init.normal_(self.weight, std=0.02)
    def __repr__(self) -> str: return "Conv1D(nf={nf}, nx={nx})".format(**self.__dict__)
    def forward(self, x):
        size_out = x.size()[:-1] + (self.nf,)
        x = torch.addmm(self.bias, x.view(-1, x.size(-1)), self.weight)
        x = x.view(size_out)
        return x
def prune_conv1d_layer(layer: Conv1D, index: torch.LongTensor, dim: int = 1) -> Conv1D:
    index = index.to(layer.weight.device)
    W = layer.weight.index_select(dim, index).clone().detach()
    if dim == 0: b = layer.bias.clone().detach()
    else: b = layer.bias[index].clone().detach()
    new_size = list(layer.weight.size())
    new_size[dim] = len(index)
    new_layer = Conv1D(new_size[1], new_size[0]).to(layer.weight.device)
    new_layer.weight.requires_grad = False
    new_layer.weight.copy_(W.contiguous())
    new_layer.weight.requires_grad = True
    new_layer.bias.requires_grad = False
    new_layer.bias.copy_(b.contiguous())
    new_layer.bias.requires_grad = True
    return new_layer
def prune_layer(layer: Union[nn.Linear, Conv1D], index: torch.LongTensor, dim: Optional[int] = None) -> Union[nn.Linear, Conv1D]:
    if isinstance(layer, nn.Linear): return prune_linear_layer(layer, index, dim=0 if dim is None else dim)
    elif isinstance(layer, Conv1D): return prune_conv1d_layer(layer, index, dim=1 if dim is None else dim)
    else: raise ValueError(f"Can't prune layer of class {layer.__class__}")
def apply_chunking_to_forward(forward_fn: Callable[..., torch.Tensor], chunk_size: int, chunk_dim: int, *input_tensors) -> torch.Tensor:
    assert len(input_tensors) > 0, f"{input_tensors} has to be a tuple/list of tensors"
    num_args_in_forward_chunk_fn = len(inspect.signature(forward_fn).parameters)
    if num_args_in_forward_chunk_fn != len(input_tensors): raise ValueError(f"forward_chunk_fn expects {num_args_in_forward_chunk_fn} arguments, but only {len(input_tensors)} input tensors are given")
    if chunk_size > 0:
        tensor_shape = input_tensors[0].shape[chunk_dim]
        for input_tensor in input_tensors:
            if input_tensor.shape[chunk_dim] != tensor_shape: raise ValueError(f"All input tenors have to be of the same shape: {tensor_shape}, found shape {input_tensor.shape[chunk_dim]}")
        if input_tensors[0].shape[chunk_dim] % chunk_size != 0: raise ValueError(f"The dimension to be chunked {input_tensors[0].shape[chunk_dim]} has to be a multiple of the chunk size {chunk_size}")
        num_chunks = input_tensors[0].shape[chunk_dim] // chunk_size
        input_tensors_chunks = tuple(input_tensor.chunk(num_chunks, dim=chunk_dim) for input_tensor in input_tensors)
        output_chunks = tuple(forward_fn(*input_tensors_chunk) for input_tensors_chunk in zip(*input_tensors_chunks))
        return torch.cat(output_chunks, dim=chunk_dim)
    return forward_fn(*input_tensors)
def find_pruneable_heads_and_indices(heads: List[int], n_heads: int, head_size: int, already_pruned_heads: Set[int]) -> Tuple[Set[int], torch.LongTensor]:
    mask = torch.ones(n_heads, head_size)
    heads = set(heads) - already_pruned_heads
    for head in heads:
        head = head - sum(1 if h < head else 0 for h in already_pruned_heads)
        mask[head] = 0
    mask = mask.view(-1).contiguous().eq(1)
    index: torch.LongTensor = torch.arange(len(mask))[mask].long()
    return heads, index
def meshgrid(*tensors: Union[torch.Tensor, List[torch.Tensor]], indexing: Optional[str] = None) -> Tuple[torch.Tensor, ...]: return torch.meshgrid(*tensors, indexing=indexing)
def id_tensor_storage(tensor: torch.Tensor) -> Tuple[torch.device, int, int]:
    if tensor.device.type == "xla" and is_torch_xla_available():
        import torch_xla
        unique_id = torch_xla._XLAC._xla_get_tensor_id(tensor)
    else: unique_id = storage_ptr(tensor)
    return tensor.device, unique_id, storage_size(tensor)
def isin_mps_friendly(elements: torch.Tensor, test_elements: torch.Tensor | int) -> torch.Tensor:
    if elements.device.type == "mps" and not is_torch_greater_or_equal_than_2_4: return elements.tile(test_elements.shape[0], 1).eq(test_elements.unsqueeze(1)).sum(dim=0).bool().squeeze()
    else: return torch.isin(elements, test_elements)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
