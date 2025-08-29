"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from torch.utils.data import DataLoader
from ..utils import is_torch_xla_available
def tpu_spmd_dataloader(dataloader: DataLoader):
    if is_torch_xla_available():
        import torch_xla.distributed.parallel_loader as pl
        assert isinstance(dataloader, pl.MpDeviceLoader), "The dataloader must be a `torch_xla.distributed.parallel_loader.MpDeviceLoader`."
        import torch_xla.distributed.spmd as xs
        sharding_spec = xs.ShardingSpec(xs.get_global_mesh(), ("fsdp", None))
        dataloader._parallel_loader_kwargs["input_sharding"] = sharding_spec
        return dataloader
    else: return dataloader
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
