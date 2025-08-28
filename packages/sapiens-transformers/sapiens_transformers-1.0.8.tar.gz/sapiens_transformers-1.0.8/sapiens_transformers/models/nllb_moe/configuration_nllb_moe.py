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
class NllbMoeConfig(PretrainedConfig):
    model_type = "nllb-moe"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"num_attention_heads": "encoder_attention_heads", "hidden_size": "d_model"}
    def __init__(self, vocab_size=128112, max_position_embeddings=1024, encoder_layers=12, encoder_ffn_dim=4096, encoder_attention_heads=16, decoder_layers=12,
    decoder_ffn_dim=4096, decoder_attention_heads=16, encoder_layerdrop=0.05, decoder_layerdrop=0.05, use_cache=True, is_encoder_decoder=True, activation_function="relu",
    d_model=1024, dropout=0.1, attention_dropout=0.1, activation_dropout=0.0, init_std=0.02, decoder_start_token_id=2, scale_embedding=True, router_bias=False,
    router_dtype="float32", router_ignore_padding_tokens=False, num_experts=128, expert_capacity=64, encoder_sparse_step=4, decoder_sparse_step=4,
    router_z_loss_coef=0.001, router_aux_loss_coef=0.001, second_expert_policy="all", normalize_router_prob_before_dropping=False, batch_prioritized_routing=False,
    moe_eval_capacity_token_fraction=1.0, moe_token_dropout=0.2, pad_token_id=1, bos_token_id=0, eos_token_id=2, output_router_logits=False, **kwargs):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.d_model = d_model
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.encoder_layerdrop = encoder_layerdrop
        self.decoder_layerdrop = decoder_layerdrop
        self.use_cache = use_cache
        self.num_hidden_layers = encoder_layers
        self.scale_embedding = scale_embedding
        self.router_z_loss_coef = router_z_loss_coef
        self.router_aux_loss_coef = router_aux_loss_coef
        self.decoder_sparse_step = decoder_sparse_step
        self.encoder_sparse_step = encoder_sparse_step
        self.num_experts = num_experts
        self.expert_capacity = expert_capacity
        self.router_bias = router_bias
        if router_dtype not in ["float32", "float16", "bfloat16"]: raise ValueError(f"`router_dtype` must be one of 'float32', 'float16' or 'bfloat16', got {router_dtype}")
        self.router_dtype = router_dtype
        self.router_ignore_padding_tokens = router_ignore_padding_tokens
        self.batch_prioritized_routing = batch_prioritized_routing
        self.second_expert_policy = second_expert_policy
        self.normalize_router_prob_before_dropping = normalize_router_prob_before_dropping
        self.moe_eval_capacity_token_fraction = moe_eval_capacity_token_fraction
        self.moe_token_dropout = moe_token_dropout
        self.output_router_logits = output_router_logits
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, is_encoder_decoder=is_encoder_decoder,
        decoder_start_token_id=decoder_start_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
