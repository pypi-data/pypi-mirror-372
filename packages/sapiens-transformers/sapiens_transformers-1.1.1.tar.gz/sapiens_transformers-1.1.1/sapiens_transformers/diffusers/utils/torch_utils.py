'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from typing import List, Optional, Tuple, Union
from .import_utils import is_torch_available, is_torch_version
if is_torch_available():
    import torch
    from torch.fft import fftn, fftshift, ifftn, ifftshift
try: from torch._dynamo import allow_in_graph as maybe_allow_in_graph
except (ImportError, ModuleNotFoundError):
    def maybe_allow_in_graph(cls): return cls
def randn_tensor(shape: Union[Tuple, List], generator: Optional[Union[List['torch.Generator'], 'torch.Generator']]=None, device: Optional['torch.device']=None,
dtype: Optional['torch.dtype']=None, layout: Optional['torch.layout']=None):
    rand_device = device
    batch_size = shape[0]
    layout = layout or torch.strided
    device = device or torch.device('cpu')
    if generator is not None:
        gen_device_type = generator.device.type if not isinstance(generator, list) else generator[0].device.type
        if gen_device_type != device.type and gen_device_type == 'cpu': rand_device = 'cpu'
        elif gen_device_type != device.type and gen_device_type == 'cuda': raise ValueError(f'Cannot generate a {device} tensor from a generator of type {gen_device_type}.')
    if isinstance(generator, list) and len(generator) == 1: generator = generator[0]
    if isinstance(generator, list):
        shape = (1,) + shape[1:]
        latents = [torch.randn(shape, generator=generator[i], device=rand_device, dtype=dtype, layout=layout) for i in range(batch_size)]
        latents = torch.cat(latents, dim=0).to(device)
    else: latents = torch.randn(shape, generator=generator, device=rand_device, dtype=dtype, layout=layout).to(device)
    return latents
def is_compiled_module(module) -> bool:
    if is_torch_version('<', '2.0.0') or not hasattr(torch, '_dynamo'): return False
    return isinstance(module, torch._dynamo.eval_frame.OptimizedModule)
def fourier_filter(x_in: 'torch.Tensor', threshold: int, scale: int) -> 'torch.Tensor':
    x = x_in
    B, C, H, W = x.shape
    if W & W - 1 != 0 or H & H - 1 != 0: x = x.to(dtype=torch.float32)
    elif x.dtype == torch.bfloat16: x = x.to(dtype=torch.float32)
    x_freq = fftn(x, dim=(-2, -1))
    x_freq = fftshift(x_freq, dim=(-2, -1))
    B, C, H, W = x_freq.shape
    mask = torch.ones((B, C, H, W), device=x.device)
    crow, ccol = (H // 2, W // 2)
    mask[..., crow - threshold:crow + threshold, ccol - threshold:ccol + threshold] = scale
    x_freq = x_freq * mask
    x_freq = ifftshift(x_freq, dim=(-2, -1))
    x_filtered = ifftn(x_freq, dim=(-2, -1)).real
    return x_filtered.to(dtype=x_in.dtype)
def apply_freeu(resolution_idx: int, hidden_states: 'torch.Tensor', res_hidden_states: 'torch.Tensor', **freeu_kwargs) -> Tuple['torch.Tensor', 'torch.Tensor']:
    """Args:"""
    if resolution_idx == 0:
        num_half_channels = hidden_states.shape[1] // 2
        hidden_states[:, :num_half_channels] = hidden_states[:, :num_half_channels] * freeu_kwargs['b1']
        res_hidden_states = fourier_filter(res_hidden_states, threshold=1, scale=freeu_kwargs['s1'])
    if resolution_idx == 1:
        num_half_channels = hidden_states.shape[1] // 2
        hidden_states[:, :num_half_channels] = hidden_states[:, :num_half_channels] * freeu_kwargs['b2']
        res_hidden_states = fourier_filter(res_hidden_states, threshold=1, scale=freeu_kwargs['s2'])
    return (hidden_states, res_hidden_states)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
