"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import torch
from sapiens_transformers import (PreTrainedModel, StaticCache)
from sapiens_transformers.pytorch_utils import is_torch_greater_or_equal_than_2_3
class TorchExportableModuleWithStaticCache(torch.nn.Module):
    def __init__(self, model: PreTrainedModel):
        super().__init__()
        if model.generation_config is None: raise AssertionError("The model must have a generation config to be exported with static caching. Please set `generation_config`.")
        if not model.generation_config.use_cache: raise AssertionError("The model must have caching enabled to be exported with static caching. Please set `generation_config.use_cache=True`.")
        if model.generation_config.cache_implementation != "static": raise AssertionError("The model must use a 'static' caching implementation to be exported with static caching. Please set `generation_config.cache_implementation='static'`.")
        self.model = model
        self.static_cache = StaticCache(config=self.model.config, batch_size=self.model.generation_config.cache_config.batch_size, max_cache_len=self.model.generation_config.cache_config.max_cache_len, dtype=self.model.config.torch_dtype)
        self.is_causal = any("CausalLM" in arch for arch in self.model.config.architectures)
        if self.is_causal:
            causal_mask = torch.tril(torch.ones(self.static_cache.max_cache_len, self.static_cache.max_cache_len, dtype=torch.bool))
            self.register_buffer("mask", causal_mask, persistent=False)
    def forward(self, input_ids: torch.Tensor, cache_position: torch.Tensor):
        _, seqlen = input_ids.shape
        attn_mask = self.mask[cache_position, :seqlen] if self.is_causal else None
        outs = self.model(input_ids=input_ids, attention_mask=attn_mask, position_ids=cache_position.unsqueeze(0), cache_position=cache_position, past_key_values=self.static_cache, use_cache=True)
        return outs.logits
def convert_and_export_with_cache(model: PreTrainedModel, example_input_ids: torch.Tensor = None, example_cache_position: torch.Tensor = None):
    if not is_torch_greater_or_equal_than_2_3: raise ImportError("torch >= 2.3 is required.")
    import torch.export._trace
    with torch.no_grad():
        example_input_ids = (example_input_ids if example_input_ids is not None else torch.tensor([[1]], dtype=torch.long))
        example_cache_position = (example_cache_position if example_cache_position is not None else torch.tensor([0], dtype=torch.long))
        exported_program = torch.export._trace._export(TorchExportableModuleWithStaticCache(model), args=(example_input_ids,), kwargs={"cache_position": example_cache_position}, pre_dispatch=False, strict=True)
        return exported_program
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
