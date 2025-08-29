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
class CTRLConfig(PretrainedConfig):
    model_type = "ctrl"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'max_position_embeddings': 'n_positions', 'hidden_size': 'n_embd', 'num_attention_heads': 'n_head', 'num_hidden_layers': 'n_layer'}
    def __init__(self, vocab_size=246534, n_positions=256, n_embd=1280, dff=8192, n_layer=48, n_head=16, resid_pdrop=0.1, embd_pdrop=0.1,
    layer_norm_epsilon=1e-6, initializer_range=0.02, use_cache=True, **kwargs):
        self.vocab_size = vocab_size
        self.n_positions = n_positions
        self.n_embd = n_embd
        self.n_layer = n_layer
        self.n_head = n_head
        self.dff = dff
        self.resid_pdrop = resid_pdrop
        self.embd_pdrop = embd_pdrop
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.use_cache = use_cache
        super().__init__(**kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
