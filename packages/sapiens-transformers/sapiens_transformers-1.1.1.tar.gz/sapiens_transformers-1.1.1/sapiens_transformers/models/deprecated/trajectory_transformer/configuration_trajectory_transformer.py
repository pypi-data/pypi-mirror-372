"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ....configuration_utils import PretrainedConfig
from ....utils import logging
logger = logging.get_logger(__name__)
class TrajectoryTransformerConfig(PretrainedConfig):
    model_type = "trajectory_transformer"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {'hidden_size': 'n_embd', 'num_attention_heads': 'n_head', 'num_hidden_layers': 'n_layer'}
    def __init__(self, vocab_size=100, action_weight=5, reward_weight=1, value_weight=1, block_size=249, action_dim=6, observation_dim=17, transition_dim=25, n_layer=4,
    n_head=4, n_embd=128, embd_pdrop=0.1, attn_pdrop=0.1, resid_pdrop=0.1, learning_rate=0.0006, max_position_embeddings=512, initializer_range=0.02, layer_norm_eps=1e-12,
    kaiming_initializer_range=1, use_cache=True, pad_token_id=1, bos_token_id=50256, eos_token_id=50256, **kwargs):
        self.vocab_size = vocab_size
        self.action_weight = action_weight
        self.reward_weight = reward_weight
        self.value_weight = value_weight
        self.max_position_embeddings = max_position_embeddings
        self.block_size = block_size
        self.action_dim = action_dim
        self.observation_dim = observation_dim
        self.transition_dim = transition_dim
        self.learning_rate = learning_rate
        self.n_layer = n_layer
        self.n_head = n_head
        self.n_embd = n_embd
        self.embd_pdrop = embd_pdrop
        self.attn_pdrop = attn_pdrop
        self.resid_pdrop = resid_pdrop
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.kaiming_initializer_range = kaiming_initializer_range
        self.use_cache = use_cache
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
