"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class FunnelConfig(PretrainedConfig):
    model_type = "funnel"
    attribute_map = {'hidden_size': 'd_model', 'num_attention_heads': 'n_head'}
    def __init__(self, vocab_size=30522, block_sizes=[4, 4, 4], block_repeats=None, num_decoder_layers=2, d_model=768, n_head=12, d_head=64, d_inner=3072,
    hidden_act="gelu_new", hidden_dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, initializer_range=0.1, initializer_std=None, layer_norm_eps=1e-9,
    pooling_type="mean", attention_type="relative_shift", separate_cls=True, truncate_seq=True, pool_q_only=True, **kwargs):
        self.vocab_size = vocab_size
        self.block_sizes = block_sizes
        self.block_repeats = [1] * len(block_sizes) if block_repeats is None else block_repeats
        assert len(block_sizes) == len(self.block_repeats), "`block_sizes` and `block_repeats` should have the same length."
        self.num_decoder_layers = num_decoder_layers
        self.d_model = d_model
        self.n_head = n_head
        self.d_head = d_head
        self.d_inner = d_inner
        self.hidden_act = hidden_act
        self.hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.initializer_range = initializer_range
        self.initializer_std = initializer_std
        self.layer_norm_eps = layer_norm_eps
        assert pooling_type in ["mean", "max"], f"Got {pooling_type} for `pooling_type` but only 'mean' and 'max' are supported."
        self.pooling_type = pooling_type
        assert attention_type in ["relative_shift", "factorized"], f"Got {attention_type} for `attention_type` but only 'relative_shift' and 'factorized' are supported."
        self.attention_type = attention_type
        self.separate_cls = separate_cls
        self.truncate_seq = truncate_seq
        self.pool_q_only = pool_q_only
        super().__init__(**kwargs)
    @property
    def num_hidden_layers(self): return sum(self.block_sizes)
    @num_hidden_layers.setter
    def num_hidden_layers(self, value): raise NotImplementedError("This model does not support the setting of `num_hidden_layers`. Please set `block_sizes`.")
    @property
    def num_blocks(self): return len(self.block_sizes)
    @num_blocks.setter
    def num_blocks(self, value): raise NotImplementedError("This model does not support the setting of `num_blocks`. Please set `block_sizes`.")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
