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
class XGLMConfig(PretrainedConfig):
    model_type = "xglm"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'num_attention_heads': 'attention_heads', 'hidden_size': 'd_model', 'num_hidden_layers': 'num_layers'}
    def __init__(self, vocab_size=256008, max_position_embeddings=2048, d_model=1024, ffn_dim=4096, num_layers=24, attention_heads=16, activation_function="gelu",
    dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, layerdrop=0.0, init_std=0.02, scale_embedding=True, use_cache=True, decoder_start_token_id=2,
    pad_token_id=1, bos_token_id=0, eos_token_id=2, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.ffn_dim = ffn_dim
        self.num_layers = num_layers
        self.attention_heads = attention_heads
        self.activation_function = activation_function
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.layerdrop = layerdrop
        self.init_std = init_std
        self.scale_embedding = scale_embedding
        self.use_cache = use_cache
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, decoder_start_token_id=decoder_start_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
