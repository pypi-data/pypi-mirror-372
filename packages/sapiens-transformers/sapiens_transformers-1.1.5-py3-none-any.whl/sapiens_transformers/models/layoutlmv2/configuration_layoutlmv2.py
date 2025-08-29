"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
from ...utils import is_detectron2_available, logging
logger = logging.get_logger(__name__)
if is_detectron2_available(): import detectron2
class LayoutLMv2Config(PretrainedConfig):
    model_type = "layoutlmv2"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=512, type_vocab_size=2, initializer_range=0.02, layer_norm_eps=1e-12, pad_token_id=0, max_2d_position_embeddings=1024,
    max_rel_pos=128, rel_pos_bins=32, fast_qkv=True, max_rel_2d_pos=256, rel_2d_pos_bins=64, convert_sync_batchnorm=True, image_feature_pool_shape=[7, 7, 256],
    coordinate_size=128, shape_size=128, has_relative_attention_bias=True, has_spatial_attention_bias=True, has_visual_segment_embedding=False,
    detectron2_config_args=None, **kwargs):
        super().__init__(vocab_size=vocab_size, hidden_size=hidden_size, num_hidden_layers=num_hidden_layers, num_attention_heads=num_attention_heads, intermediate_size=intermediate_size,
        hidden_act=hidden_act, hidden_dropout_prob=hidden_dropout_prob, attention_probs_dropout_prob=attention_probs_dropout_prob, max_position_embeddings=max_position_embeddings,
        type_vocab_size=type_vocab_size, initializer_range=initializer_range, layer_norm_eps=layer_norm_eps, pad_token_id=pad_token_id, **kwargs)
        self.max_2d_position_embeddings = max_2d_position_embeddings
        self.max_rel_pos = max_rel_pos
        self.rel_pos_bins = rel_pos_bins
        self.fast_qkv = fast_qkv
        self.max_rel_2d_pos = max_rel_2d_pos
        self.rel_2d_pos_bins = rel_2d_pos_bins
        self.convert_sync_batchnorm = convert_sync_batchnorm
        self.image_feature_pool_shape = image_feature_pool_shape
        self.coordinate_size = coordinate_size
        self.shape_size = shape_size
        self.has_relative_attention_bias = has_relative_attention_bias
        self.has_spatial_attention_bias = has_spatial_attention_bias
        self.has_visual_segment_embedding = has_visual_segment_embedding
        self.detectron2_config_args = (detectron2_config_args if detectron2_config_args is not None else self.get_default_detectron2_config())
    @classmethod
    def get_default_detectron2_config(cls): return {'MODEL.MASK_ON': True, 'MODEL.PIXEL_STD': [57.375, 57.12, 58.395], 'MODEL.BACKBONE.NAME': 'build_resnet_fpn_backbone',
    'MODEL.FPN.IN_FEATURES': ['res2', 'res3', 'res4', 'res5'], 'MODEL.ANCHOR_GENERATOR.SIZES': [[32], [64], [128], [256], [512]], 'MODEL.RPN.IN_FEATURES': ['p2', 'p3', 'p4', 'p5', 'p6'],
    'MODEL.RPN.PRE_NMS_TOPK_TRAIN': 2000, 'MODEL.RPN.PRE_NMS_TOPK_TEST': 1000, 'MODEL.RPN.POST_NMS_TOPK_TRAIN': 1000, 'MODEL.POST_NMS_TOPK_TEST': 1000, 'MODEL.ROI_HEADS.NAME': 'StandardROIHeads',
    'MODEL.ROI_HEADS.NUM_CLASSES': 5, 'MODEL.ROI_HEADS.IN_FEATURES': ['p2', 'p3', 'p4', 'p5'], 'MODEL.ROI_BOX_HEAD.NAME': 'FastRCNNConvFCHead', 'MODEL.ROI_BOX_HEAD.NUM_FC': 2,
    'MODEL.ROI_BOX_HEAD.POOLER_RESOLUTION': 14, 'MODEL.ROI_MASK_HEAD.NAME': 'MaskRCNNConvUpsampleHead', 'MODEL.ROI_MASK_HEAD.NUM_CONV': 4, 'MODEL.ROI_MASK_HEAD.POOLER_RESOLUTION': 7,
    'MODEL.RESNETS.DEPTH': 101, 'MODEL.RESNETS.SIZES': [[32], [64], [128], [256], [512]], 'MODEL.RESNETS.ASPECT_RATIOS': [[0.5, 1.0, 2.0]], 'MODEL.RESNETS.OUT_FEATURES': ['res2', 'res3', 'res4', 'res5'],
    'MODEL.RESNETS.NUM_GROUPS': 32, 'MODEL.RESNETS.WIDTH_PER_GROUP': 8, 'MODEL.RESNETS.STRIDE_IN_1X1': False}
    def get_detectron2_config(self):
        detectron2_config = detectron2.config.get_cfg()
        for k, v in self.detectron2_config_args.items():
            attributes = k.split(".")
            to_set = detectron2_config
            for attribute in attributes[:-1]: to_set = getattr(to_set, attribute)
            setattr(to_set, attributes[-1], v)
        return detectron2_config
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
