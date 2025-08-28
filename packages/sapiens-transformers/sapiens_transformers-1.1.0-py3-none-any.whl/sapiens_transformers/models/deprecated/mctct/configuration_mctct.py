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
class MCTCTConfig(PretrainedConfig):
    model_type = "mctct"
    def __init__(self, vocab_size=8065, hidden_size=1536, num_hidden_layers=36, intermediate_size=6144, num_attention_heads=4, attention_head_dim=384, max_position_embeddings=920,
    layer_norm_eps=1e-5, layerdrop=0.3, hidden_act="relu", initializer_range=0.02, hidden_dropout_prob=0.3, attention_probs_dropout_prob=0.3, pad_token_id=1, bos_token_id=0,
    eos_token_id=2, conv_glu_dim=1, conv_dropout=0.3, num_conv_layers=1, conv_kernel=(7,), conv_stride=(3,), input_feat_per_channel=80, input_channels=1, conv_channels=None,
    ctc_loss_reduction="sum", ctc_zero_infinity=False, **kwargs):
        super().__init__(**kwargs, pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.intermediate_size = intermediate_size
        self.num_attention_heads = num_attention_heads
        self.attention_head_dim = attention_head_dim
        self.max_position_embeddings = max_position_embeddings
        self.layer_norm_eps = layer_norm_eps
        self.layerdrop = layerdrop
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.pad_token_id = pad_token_id
        self.bos_token_id = bos_token_id
        self.eos_token_id = eos_token_id
        self.conv_glu_dim = conv_glu_dim
        self.conv_dropout = conv_dropout
        self.num_conv_layers = num_conv_layers
        self.input_feat_per_channel = input_feat_per_channel
        self.input_channels = input_channels
        self.conv_channels = conv_channels
        self.ctc_loss_reduction = ctc_loss_reduction
        self.ctc_zero_infinity = ctc_zero_infinity
        self.conv_kernel = list(conv_kernel)
        self.conv_stride = list(conv_stride)
        if len(self.conv_kernel) != self.num_conv_layers:
            raise ValueError(f"Configuration for convolutional module is incorrect. It is required that `len(config.conv_kernel)` == `config.num_conv_layers` but is `len(config.conv_kernel) = {len(self.conv_kernel)}`, `config.num_conv_layers = {self.num_conv_layers}`.")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
