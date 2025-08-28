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
class GPTBigCodeConfig(PretrainedConfig):
    model_type = "gpt_bigcode"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'n_embd', 'max_position_embeddings': 'n_positions', 'num_attention_heads': 'n_head', 'num_hidden_layers': 'n_layer'}
    def __init__(self, vocab_size=50257, n_positions=1024, n_embd=768, n_layer=12, n_head=12, n_inner=None, activation_function="gelu_pytorch_tanh", resid_pdrop=0.1,
    embd_pdrop=0.1, attn_pdrop=0.1, layer_norm_epsilon=1e-5, initializer_range=0.02, scale_attn_weights=True, use_cache=True, bos_token_id=50256, eos_token_id=50256,
    attention_softmax_in_fp32=True, scale_attention_softmax_in_fp32=True, multi_query=True, **kwargs):
        self.vocab_size = vocab_size
        self.n_positions = n_positions
        self.n_embd = n_embd
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_inner = n_inner
        self.activation_function = activation_function
        self.resid_pdrop = resid_pdrop
        self.embd_pdrop = embd_pdrop
        self.attn_pdrop = attn_pdrop
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_range = initializer_range
        self.scale_attn_weights = scale_attn_weights
        self.use_cache = use_cache
        self.attention_softmax_in_fp32 = attention_softmax_in_fp32
        self.scale_attention_softmax_in_fp32 = scale_attention_softmax_in_fp32
        self.multi_query = multi_query
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        super().__init__(bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
