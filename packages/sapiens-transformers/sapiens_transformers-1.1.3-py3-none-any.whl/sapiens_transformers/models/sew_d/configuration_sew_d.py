"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import functools
import operator
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class SEWDConfig(PretrainedConfig):
    model_type = "sew-d"
    def __init__(self, vocab_size=32, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, squeeze_factor=2, max_position_embeddings=512,
    position_buckets=256, share_att_key=True, relative_attention=True, pos_att_type=("p2c", "c2p"), norm_rel_ebd="layer_norm", hidden_act="gelu_python", hidden_dropout=0.1,
    activation_dropout=0.1, attention_dropout=0.1, feat_proj_dropout=0.0, final_dropout=0.1, initializer_range=0.02, layer_norm_eps=1e-7, feature_layer_norm_eps=1e-5,
    feat_extract_norm="group", feat_extract_activation="gelu", conv_dim=(64, 128, 128, 128, 128, 256, 256, 256, 256, 512, 512, 512, 512), conv_stride=(5, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1),
    conv_kernel=(10, 3, 1, 3, 1, 3, 1, 3, 1, 2, 1, 2, 1), conv_bias=False, num_conv_pos_embeddings=128, num_conv_pos_embedding_groups=16, apply_spec_augment=True,
    mask_time_prob=0.05, mask_time_length=10, mask_time_min_masks=2, mask_feature_prob=0.0, mask_feature_length=10, mask_feature_min_masks=0, ctc_loss_reduction="mean",
    ctc_zero_infinity=False, use_weighted_layer_sum=False, classifier_proj_size=256, pad_token_id=0, bos_token_id=1, eos_token_id=2, **kwargs):
        super().__init__(**kwargs, pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id)
        self.hidden_size = hidden_size
        self.feat_extract_norm = feat_extract_norm
        self.feat_extract_activation = feat_extract_activation
        self.conv_dim = list(conv_dim)
        self.conv_stride = list(conv_stride)
        self.conv_kernel = list(conv_kernel)
        self.conv_bias = conv_bias
        self.num_conv_pos_embeddings = num_conv_pos_embeddings
        self.num_conv_pos_embedding_groups = num_conv_pos_embedding_groups
        self.num_feat_extract_layers = len(self.conv_dim)
        self.num_hidden_layers = num_hidden_layers
        self.intermediate_size = intermediate_size
        self.squeeze_factor = squeeze_factor
        self.max_position_embeddings = max_position_embeddings
        self.position_buckets = position_buckets
        self.share_att_key = share_att_key
        self.relative_attention = relative_attention
        self.norm_rel_ebd = norm_rel_ebd
        self.pos_att_type = list(pos_att_type)
        self.hidden_act = hidden_act
        self.num_attention_heads = num_attention_heads
        self._hidden_dropout = hidden_dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.feat_proj_dropout = feat_proj_dropout
        self.final_dropout = final_dropout
        self.layer_norm_eps = layer_norm_eps
        self.feature_layer_norm_eps = feature_layer_norm_eps
        self.initializer_range = initializer_range
        self.vocab_size = vocab_size
        if ((len(self.conv_stride) != self.num_feat_extract_layers) or (len(self.conv_kernel) != self.num_feat_extract_layers) or (len(self.conv_dim) != self.num_feat_extract_layers)): raise ValueError(f"Configuration for convolutional layers is incorrect. It is required that `len(config.conv_dim)` == `len(config.conv_stride)` == `len(config.conv_kernel)`, but is `len(config.conv_dim) = {len(self.conv_dim)}`, `len(config.conv_stride) = {len(self.conv_stride)}`, `len(config.conv_kernel) = {len(self.conv_kernel)}`.")
        self.apply_spec_augment = apply_spec_augment
        self.mask_time_prob = mask_time_prob
        self.mask_time_length = mask_time_length
        self.mask_time_min_masks = mask_time_min_masks
        self.mask_feature_prob = mask_feature_prob
        self.mask_feature_length = mask_feature_length
        self.mask_feature_min_masks = mask_feature_min_masks
        self.ctc_loss_reduction = ctc_loss_reduction
        self.ctc_zero_infinity = ctc_zero_infinity
        self.use_weighted_layer_sum = use_weighted_layer_sum
        self.classifier_proj_size = classifier_proj_size
    @property
    def inputs_to_logits_ratio(self): return functools.reduce(operator.mul, self.conv_stride, 1)
    def to_dict(self):
        output = super().to_dict()
        output["hidden_dropout"] = output.pop("_hidden_dropout")
        return output
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
