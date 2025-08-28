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
class SwitchTransformersConfig(PretrainedConfig):
    model_type = "switch_transformers"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"hidden_size": "d_model", "num_attention_heads": "num_heads", "num_hidden_layers": "num_layers"}
    def __init__(self, vocab_size=32128, d_model=768, d_kv=64, d_ff=2048, expert_capacity=64, num_layers=12, num_sparse_encoder_layers=3, num_decoder_layers=12, num_sparse_decoder_layers=3,
    num_heads=12, num_experts=8, router_bias=False, router_jitter_noise=0.01, router_dtype="float32", router_ignore_padding_tokens=False, relative_attention_num_buckets=32,
    relative_attention_max_distance=128, dropout_rate=0.1, layer_norm_epsilon=1e-6, router_z_loss_coef=0.001, router_aux_loss_coef=0.001, initializer_factor=1.0, dense_act_fn="relu",
    is_encoder_decoder=True, add_router_probs=False, use_cache=True, pad_token_id=0, eos_token_id=1, **kwargs):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_kv = d_kv
        self.d_ff = d_ff
        self.num_sparse_encoder_layers = num_sparse_encoder_layers
        self.num_layers = num_layers
        self.num_decoder_layers = (num_decoder_layers if num_decoder_layers is not None else self.num_layers)
        self.num_sparse_decoder_layers = num_sparse_decoder_layers
        if self.num_sparse_encoder_layers > 0: self.encoder_sparse_step = self.num_layers // self.num_sparse_encoder_layers
        else: self.encoder_sparse_step = self.num_layers
        if self.num_sparse_decoder_layers > 0: self.decoder_sparse_step = self.num_decoder_layers // self.num_sparse_decoder_layers
        else: self.decoder_sparse_step = self.num_decoder_layers
        self.num_heads = num_heads
        self.num_experts = num_experts
        self.expert_capacity = expert_capacity
        self.router_bias = router_bias
        self.router_jitter_noise = router_jitter_noise
        if router_dtype not in ["float32", "float16", "bfloat16"]: raise ValueError(f"`router_dtype` must be one of 'float32', 'float16' or 'bfloat16', got {router_dtype}")
        self.router_dtype = router_dtype
        self.router_ignore_padding_tokens = router_ignore_padding_tokens
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.dropout_rate = dropout_rate
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_factor = initializer_factor
        self.use_cache = use_cache
        self.add_router_probs = add_router_probs
        self.router_z_loss_coef = router_z_loss_coef
        self.router_aux_loss_coef = router_aux_loss_coef
        self.dense_act_fn = dense_act_fn
        super().__init__(pad_token_id=pad_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
